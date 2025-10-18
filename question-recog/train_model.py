#!/usr/bin/env python
"""
XGBoost模型训练脚本
"""

import sys
import json
import jsonlines
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import xgboost as xgb
from collections import Counter

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.features.extractor import FeatureExtractor
from src.io.schemas import ParsedQuestion


def prepare_training_data():
    """准备训练数据"""
    print("🔄 准备训练数据...")
    
    # 检查标注文件 - 优先使用扩展数据
    expanded_file = Path("data/labels/expanded_labels.jsonl")
    labels_file = Path("data/labels/manual_labels.jsonl")
    
    if expanded_file.exists():
        labels_file = expanded_file
        print(f"✅ 使用扩展数据集: {labels_file}")
    elif labels_file.exists():
        print(f"✅ 使用手动标注数据: {labels_file}")
    else:
        print("❌ 未找到标注文件，请先运行 expand_data.py 或 annotation_tool.py")
        return None, None, None
    
    # 检查生产结果文件
    results_file = Path("production_results.json")
    if not results_file.exists():
        print("❌ 生产结果文件不存在，请先运行 production_test.py")
        return None, None, None
    
    # 加载标注数据
    labels = {}
    with jsonlines.open(labels_file) as reader:
        for item in reader:
            labels[item["source_id"]] = item["gold_type"]
    
    print(f"📊 加载了 {len(labels)} 个标注样本")
    
    # 加载生产结果
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data["results"]
    
    # 创建特征提取器
    extractor = FeatureExtractor()
    
    # 准备训练数据
    X = []
    y = []
    feature_names = extractor.get_feature_names()
    
    labeled_count = 0
    for result in results:
        source_id = result["source_id"]
        
        if source_id in labels:
            # 有标注的样本
            gold_type = labels[source_id]
            features = result["features"]
            
            # 转换为特征向量
            feature_vector = [features[name] for name in feature_names]
            X.append(feature_vector)
            y.append(gold_type)
            labeled_count += 1
    
    print(f"✅ 准备了 {labeled_count} 个训练样本")
    
    if labeled_count < 10:
        print("❌ 训练样本太少，需要至少10个样本")
        return None, None, None
    
    # 显示标签分布
    label_counts = Counter(y)
    print(f"📈 标签分布:")
    for label, count in label_counts.items():
        print(f"  {label:15}: {count:3} 样本")
    
    # 标签编码 - 将字符串标签转换为数字
    from sklearn.preprocessing import LabelEncoder
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # 保存标签编码器
    import joblib
    model_dir = Path("src/model")
    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(label_encoder, model_dir / "label_encoder.pkl")
    
    return np.array(X), y_encoded, feature_names, label_encoder.classes_


def train_xgboost_model():
    """训练XGBoost模型"""
    print("🚀 开始训练XGBoost模型")
    print("=" * 40)
    
    # 准备数据
    result = prepare_training_data()
    if result is None:
        return
    
    X, y, feature_names, class_names = result
    
    # 数据分割 - 处理类别不平衡问题
    test_size = min(0.3, max(0.1, len(X) // 10))  # 动态调整测试集大小
    
    # 检查是否可以进行分层抽样
    from collections import Counter
    label_counts = Counter(y)
    min_count = min(label_counts.values())
    
    if min_count >= 2:
        # 可以进行分层抽样
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
    else:
        # 不能分层抽样，使用简单随机分割
        print(f"⚠️  数据不平衡，使用简单随机分割 (最少类别只有{min_count}个样本)")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
    
    print(f"📊 训练集: {len(X_train)} 样本")
    print(f"📊 测试集: {len(X_test)} 样本")
    
    # 创建XGBoost模型
    model = xgb.XGBClassifier(
        max_depth=4,           # 降低复杂度防止过拟合
        n_estimators=100,      # 减少树的数量
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='mlogloss',
        use_label_encoder=False
    )
    
    # 交叉验证
    if len(X_train) >= 5:  # 至少5个样本才做交叉验证
        cv_folds = min(3, len(set(y_train)))  # 动态调整折数
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv_folds, scoring='f1_macro')
        print(f"🎯 交叉验证 F1 分数: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    # 训练模型
    print("🔄 训练模型中...")
    model.fit(X_train, y_train)
    
    # 测试集评估
    y_pred = model.predict(X_test)
    
    # 将数字标签转换回字符串用于报告
    from sklearn.preprocessing import LabelEncoder
    import joblib
    label_encoder = joblib.load("src/model/label_encoder.pkl")
    y_test_str = label_encoder.inverse_transform(y_test)
    y_pred_str = label_encoder.inverse_transform(y_pred)
    
    f1_macro = f1_score(y_test, y_pred, average='macro')
    f1_weighted = f1_score(y_test, y_pred, average='weighted')
    
    print(f"✅ 测试集 F1 分数 (宏平均): {f1_macro:.4f}")
    print(f"✅ 测试集 F1 分数 (加权平均): {f1_weighted:.4f}")
    
    # 详细分类报告
    report = classification_report(y_test_str, y_pred_str, zero_division=0)
    print(f"\n📋 详细分类报告:")
    print(report)
    
    # 混淆矩阵
    cm = confusion_matrix(y_test_str, y_pred_str, labels=class_names)
    print(f"\n🔍 混淆矩阵:")
    print(cm)
    
    # 特征重要性
    feature_importance = model.feature_importances_
    important_features = sorted(
        zip(feature_names, feature_importance), 
        key=lambda x: x[1], reverse=True
    )[:10]
    
    print(f"\n🎯 前10个重要特征:")
    for feature, importance in important_features:
        print(f"  {feature:20}: {importance:.4f}")
    
    # 保存模型
    model_dir = Path("src/model")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = model_dir / "xgb_model.json"
    model.save_model(str(model_path))
    
    # 保存特征名称
    feature_info_path = model_dir / "feature_names.json"
    with open(feature_info_path, 'w', encoding='utf-8') as f:
        json.dump(feature_names, f, ensure_ascii=False, indent=2)
    
    # 保存训练信息
    training_info = {
        "model_type": "xgboost",
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "f1_macro": float(f1_macro),
        "f1_weighted": float(f1_weighted),
        "feature_count": len(feature_names),
        "classes": list(class_names),
        "feature_importance": {k: float(v) for k, v in important_features}  # 转换为float
    }
    
    info_path = model_dir / "training_info.json"
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(training_info, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 模型已保存至: {model_path}")
    print(f"💾 训练信息已保存至: {info_path}")
    
    # 给出建议
    print(f"\n💡 训练建议:")
    if f1_macro < 0.7:
        print(f"  • F1分数较低，建议增加更多标注数据")
    if len(X_train) < 50:
        print(f"  • 训练样本较少，建议标注更多数据以提高性能")
    
    print(f"\n🎉 模型训练完成！")
    print(f"🎯 下一步: 运行 test_trained_model.py 测试模型效果")


if __name__ == "__main__":
    train_xgboost_model()
