#!/usr/bin/env python
"""
模型概率校准脚本 - 使用Isotonic回归校准模型输出概率
"""

import sys
import json
import jsonlines
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
import xgboost as xgb

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.calibrator.isotonic import IsotonicCalibrator
from src.features.extractor import FeatureExtractor


def calibrate_model():
    """校准模型概率输出"""
    print("📐 开始模型概率校准")
    print("=" * 40)
    
    # 检查模型文件
    model_path = Path("src/model/xgb_model.json")
    if not model_path.exists():
        print("❌ 模型文件不存在，请先运行 train_model.py")
        return
    
    # 检查标注文件
    labels_file = Path("data/labels/manual_labels.jsonl")
    if not labels_file.exists():
        print("❌ 标注文件不存在，请先运行 annotation_tool.py")
        return
    
    # 检查生产结果文件
    results_file = Path("production_results.json")
    if not results_file.exists():
        print("❌ 生产结果文件不存在，请先运行 production_test.py")
        return
    
    print("🔄 准备校准数据...")
    
    # 加载标注数据
    labels = {}
    with jsonlines.open(labels_file) as reader:
        for item in reader:
            labels[item["source_id"]] = item["gold_type"]
    
    # 加载生产结果
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    results = data["results"]
    
    # 加载模型
    model = xgb.XGBClassifier()
    model.load_model(str(model_path))
    
    # 加载特征名称
    feature_names_path = Path("src/model/feature_names.json")
    with open(feature_names_path, 'r', encoding='utf-8') as f:
        feature_names = json.load(f)
    
    # 准备数据
    X = []
    y_true = []
    
    for result in results:
        source_id = result["source_id"]
        if source_id in labels:
            features = result["features"]
            feature_vector = [features[name] for name in feature_names]
            X.append(feature_vector)
            y_true.append(labels[source_id])
    
    X = np.array(X)
    y_true = np.array(y_true)
    
    print(f"📊 校准数据: {len(X)} 个样本")
    
    if len(X) < 10:
        print("❌ 校准数据太少，需要至少10个样本")
        return
    
    # 分割数据 - 用一部分做校准，一部分做验证
    if len(X) >= 20:
        # 检查是否可以进行分层抽样
        from collections import Counter
        label_counts = Counter(y_true)
        min_count = min(label_counts.values())
        
        if min_count >= 2:
            # 可以进行分层抽样
            X_cal, X_val, y_cal, y_val = train_test_split(
                X, y_true, test_size=0.3, random_state=42, stratify=y_true
            )
        else:
            # 不能分层抽样，使用简单随机分割
            print(f"⚠️  数据不平衡，使用简单随机分割 (最少类别只有{min_count}个样本)")
            X_cal, X_val, y_cal, y_val = train_test_split(
                X, y_true, test_size=0.3, random_state=42
            )
    else:
        # 数据太少，全部用于校准
        X_cal, y_cal = X, y_true
        X_val, y_val = X, y_true
    
    print(f"📊 校准集: {len(X_cal)} 样本")
    print(f"📊 验证集: {len(X_val)} 样本")
    
    # 获取模型预测概率
    y_proba_cal = model.predict_proba(X_cal)
    y_proba_val = model.predict_proba(X_val)
    
    # 获取类别名称
    classes = model.classes_.tolist()
    print(f"📋 支持的类别: {classes}")
    
    # 创建并训练校准器
    calibrator = IsotonicCalibrator()
    calibrator.fit(y_cal, y_proba_cal, classes)
    
    print("✅ 校准器训练完成")
    
    # 在验证集上测试校准效果
    y_proba_cal_val = calibrator.predict_proba(y_proba_val)
    
    # 计算校准前后的ECE
    ece_before = calibrator.calculate_ece(y_val, y_proba_val)
    ece_after = calibrator.calculate_ece(y_val, y_proba_cal_val)
    
    print(f"📊 校准效果:")
    print(f"  校准前 ECE: {ece_before:.4f}")
    print(f"  校准后 ECE: {ece_after:.4f}")
    
    if ece_after < ece_before:
        print("✅ 校准效果良好，ECE降低")
    else:
        print("⚠️ 校准效果有限，ECE未显著降低")
    
    # 获取可靠性图数据
    reliability_data = calibrator.get_reliability_diagram_data(y_val, y_proba_cal_val)
    
    print(f"📈 可靠性分析:")
    print(f"  期望校准误差: {reliability_data['ece']:.4f}")
    
    # 保存校准数据
    calibration_data = {
        "version": "1.0",
        "timestamp": "2025-01-12T10:00:00",
        "sample_count": len(X_cal),
        "ece_before": float(ece_before),
        "ece_after": float(ece_after),
        "classes": classes,
        "is_fitted": True,
        "reliability_data": reliability_data,
        "calibration_curves": {},
        "isotonic_mappings": {},
        "metadata": {
            "description": "XGBoost模型Isotonic校准",
            "training_samples": len(X_cal),
            "validation_samples": len(X_val),
            "improvement": float(ece_before - ece_after)
        }
    }
    
    # 保存每个类别的校准映射
    for i, class_name in enumerate(classes):
        calibrator_obj = calibrator.calibrators[class_name]
        calibration_data["isotonic_mappings"][class_name] = {
            "x_thresholds": calibrator_obj.X_thresholds_.tolist(),
            "y_thresholds": calibrator_obj.y_thresholds_.tolist()
        }
    
    # 保存校准文件
    calibration_path = Path("calibration/calibration.json")
    calibration_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(calibration_path, 'w', encoding='utf-8') as f:
        json.dump(calibration_data, f, ensure_ascii=False, indent=2)
    
    # 更新版本元数据
    version_meta = {
        "version": "1.0",
        "created_at": "2025-01-12T10:00:00",
        "last_updated": "2025-01-12T10:00:00",
        "sample_count": len(X_cal),
        "ece_score": float(ece_after),
        "status": "calibrated",
        "notes": f"基于{len(X_cal)}个样本的Isotonic校准，ECE从{ece_before:.4f}降至{ece_after:.4f}"
    }
    
    version_path = Path("calibration/version.meta")
    with open(version_path, 'w', encoding='utf-8') as f:
        json.dump(version_meta, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 校准数据已保存至: {calibration_path}")
    print(f"💾 版本信息已保存至: {version_path}")
    
    # 显示校准效果示例
    print(f"\n🔍 校准效果示例:")
    for i in range(min(5, len(X_val))):
        original_probs = y_proba_val[i]
        calibrated_probs = y_proba_cal_val[i]
        true_label = y_val[i]
        
        print(f"  样本 {i+1} (真实: {true_label}):")
        for j, class_name in enumerate(classes):
            orig_prob = original_probs[j]
            cal_prob = calibrated_probs[j]
            change = cal_prob - orig_prob
            print(f"    {class_name:15}: {orig_prob:.3f} → {cal_prob:.3f} ({change:+.3f})")
    
    print(f"\n🎉 模型校准完成！")
    print(f"🎯 下一步: 运行 test_calibrated_model.py 测试校准后的效果")


if __name__ == "__main__":
    calibrate_model()
