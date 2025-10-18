#!/usr/bin/env python
"""
改进的XGBoost模型训练脚本 - 使用扩展数据集
"""

import sys
import json
import jsonlines
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from collections import Counter

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from features.extractor import FeatureExtractor
from io.schemas import ParsedQuestion

def prepare_expanded_training_data():
    """准备扩展的训练数据"""
    print("🔄 准备扩展训练数据...")
    
    # 优先使用扩展数据集
    expanded_file = Path("data/labels/expanded_labels.jsonl")
    production_file = Path("production_results.json")
    
    if not expanded_file.exists():
        print("❌ 扩展数据集不存在，请先运行 expand_data.py")
        return None, None, None, None
    
    if not production_file.exists():
        print("❌ 生产结果文件不存在，请先运行 production_test.py")
        return None, None, None, None
    
    # 加载标注数据
    labels = {}
    with jsonlines.open(expanded_file) as reader:
        for item in reader:
            labels[item["source_id"]] = item["gold_type"]
    
    print(f"📊 加载了 {len(labels)} 个标注样本")
    
    # 加载生产结果
    with open(production_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data.get("results", [])
    print(f"📊 加载了 {len(results)} 个生产结果")
    
    # 匹配标注和结果
    feature_extractor = FeatureExtractor()
    X = []
    y = []
    matched_sources = []
    
    # 创建source_id到结果的映射
    result_map = {}
    for i, result in enumerate(results):
        source_id = f"production_batch#{i+1}"
        result_map[source_id] = result
    
    # 提取特征和标签
    for source_id, gold_type in labels.items():
        if source_id in result_map:
            result = result_map[source_id]
            question_data = result.get("question", {})
            
            # 创建ParsedQuestion对象
            parsed_q = ParsedQuestion(
                question=question_data.get("question", ""),
                options=question_data.get("options", []),
                answer_raw=question_data.get("answer_raw", ""),
                explanation_raw=question_data.get("explanation_raw", "")
            )
            
            # 提取特征
            features = feature_extractor.extract_features(parsed_q)
            feature_vector = feature_extractor.features_to_array(features)
            
            X.append(feature_vector)
            y.append(gold_type)
            matched_sources.append(source_id)
    
    print(f"✅ 成功匹配 {len(X)} 个样本")
    
    # 统计标签分布
    label_counts = Counter(y)
    print("📈 标签分布:")
    for label, count in label_counts.items():
        print(f"  {label:<15}: {count:>3} 样本")
    
    # 标签编码 - 将字符串标签转换为数字
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # 保存标签编码器
    model_dir = Path("src/model")
    model_dir.mkdir(parents=True, exist_ok=True)
    import joblib
    joblib.dump(label_encoder, model_dir / "label_encoder.pkl")
    
    # 保存特征名称
    feature_names = feature_extractor.get_feature_names()
    with open(model_dir / "feature_names.json", 'w', encoding='utf-8') as f:
        json.dump(feature_names, f, indent=2, ensure_ascii=False)
    
    return np.array(X), y_encoded, feature_names, label_encoder.classes_

def train_improved_xgboost():
    """训练改进的XGBoost模型"""
    print("🚀 开始训练改进的XGBoost模型")
    print("=" * 40)
    
    # 准备数据
    X, y, feature_names, class_names = prepare_expanded_training_data()
    
    if X is None:
        print("❌ 数据准备失败")
        return
    
    print(f"📊 特征维度: {X.shape[1]}")
    print(f"📊 样本数量: {X.shape[0]}")
    print(f"📊 类别数量: {len(class_names)}")
    
    # 数据分割 - 处理类别不平衡问题
    test_size = min(0.3, max(0.1, len(X) // 10))
    
    # 检查是否可以进行分层抽样
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
    
    # 创建XGBoost模型 - 针对多分类优化
    model = xgb.XGBClassifier(
        objective='multi:softprob',
        n_estimators=300,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        use_label_encoder=False,
        eval_metric='mlogloss'
    )
    
    # 交叉验证
    if len(X_train) >= 10:  # 确保有足够的数据进行交叉验证
        try:
            cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring='f1_macro')
            print(f"🎯 交叉验证 F1 分数: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        except Exception as e:
            print(f"⚠️ 交叉验证失败: {e}")
    
    # 训练模型
    print("🔄 训练模型中...")
    model.fit(X_train, y_train)
    
    # 预测和评估
    y_pred = model.predict(X_test)
    
    # 计算F1分数
    f1_macro = f1_score(y_test, y_pred, average='macro')
    f1_weighted = f1_score(y_test, y_pred, average='weighted')
    
    print(f"✅ 测试集 F1 分数 (宏平均): {f1_macro:.4f}")
    print(f"✅ 测试集 F1 分数 (加权平均): {f1_weighted:.4f}")
    
    # 详细分类报告
    print("\n📋 详细分类报告:")
    print(classification_report(y_test, y_pred, target_names=class_names))
    
    # 混淆矩阵
    print("\n🔍 混淆矩阵:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # 特征重要性
    feature_importance = model.feature_importances_
    important_features = sorted(
        zip(feature_names, feature_importance), 
        key=lambda x: x[1], reverse=True
    )[:10]
    
    print("\n🎯 前10个重要特征:")
    for name, importance in important_features:
        print(f"  {name:<20}: {importance:.4f}")
    
    # 保存模型
    model_dir = Path("src/model")
    model_path = model_dir / "xgb_model.json"
    model.save_model(str(model_path))
    print(f"💾 模型已保存至: {model_path}")
    
    # 保存训练信息
    training_info = {
        "model_type": "XGBoost",
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "features": len(feature_names),
        "classes": class_names.tolist(),
        "f1_macro": float(f1_macro),
        "f1_weighted": float(f1_weighted),
        "feature_importance": {k: float(v) for k, v in important_features},
        "training_date": "2025-01-12",
        "data_source": "expanded_labels"
    }
    
    info_path = model_dir / "training_info.json"
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(training_info, f, indent=2, ensure_ascii=False)
    
    print(f"💾 训练信息已保存至: {info_path}")
    
    # 训练建议
    print("\n💡 训练建议:")
    if f1_macro < 0.7:
        print("  • F1分数较低，建议增加更多标注数据")
    if len(X_train) < 200:
        print("  • 训练样本较少，建议标注更多数据以提高性能")
    if min_count < 10:
        print("  • 数据不平衡严重，建议平衡各类别样本数量")
    
    print("\n🎉 模型训练完成！")
    print("🎯 下一步: 运行 test_trained_model.py 测试模型效果")

if __name__ == "__main__":
    train_improved_xgboost()
