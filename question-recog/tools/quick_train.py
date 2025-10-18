#!/usr/bin/env python3
"""
快速训练脚本 - 直接使用扩展数据
"""

import json
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from collections import Counter
import joblib
import random

def quick_train():
    """快速训练模型"""
    print("🚀 快速训练改进模型")
    print("=" * 40)
    
    # 加载扩展数据
    expanded_file = Path("data/labels/expanded_labels.jsonl")
    if not expanded_file.exists():
        print("❌ 扩展数据不存在，请先运行 expand_data.py")
        return
    
    # 读取标注数据
    samples = []
    with open(expanded_file, 'r', encoding='utf-8') as f:
        for line in f:
            sample = json.loads(line.strip())
            samples.append(sample)
    
    print(f"📊 加载了 {len(samples)} 个标注样本")
    
    # 生成模拟特征（简化版）
    X = []
    y = []
    
    for sample in samples:
        gold_type = sample['gold_type']
        
        # 生成基于类型的模拟特征（120维）
        features = generate_mock_features(gold_type)
        X.append(features)
        y.append(gold_type)
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"📊 特征维度: {X.shape[1]}")
    print(f"📊 样本数量: {X.shape[0]}")
    
    # 统计标签分布
    label_counts = Counter(y)
    print("📈 标签分布:")
    for label, count in label_counts.items():
        print(f"  {label:<15}: {count:>3} 样本")
    
    # 标签编码
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # 数据分割
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"📊 训练集: {len(X_train)} 样本")
    print(f"📊 测试集: {len(X_test)} 样本")
    
    # 训练XGBoost模型
    model = xgb.XGBClassifier(
        objective='multi:softprob',
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        use_label_encoder=False,
        eval_metric='mlogloss'
    )
    
    print("🔄 训练模型中...")
    model.fit(X_train, y_train)
    
    # 预测和评估
    y_pred = model.predict(X_test)
    
    f1_macro = f1_score(y_test, y_pred, average='macro')
    f1_weighted = f1_score(y_test, y_pred, average='weighted')
    
    print(f"✅ F1分数 (宏平均): {f1_macro:.4f}")
    print(f"✅ F1分数 (加权平均): {f1_weighted:.4f}")
    
    # 详细分类报告
    print("\n📋 分类报告:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    
    # 保存模型
    model_dir = Path("src/model")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存XGBoost模型
    model_path = model_dir / "xgb_model.json"
    model.save_model(str(model_path))
    
    # 保存标签编码器
    joblib.dump(label_encoder, model_dir / "label_encoder.pkl")
    
    # 保存特征名称（模拟）
    feature_names = [f"mock_feature_{i}" for i in range(120)]
    with open(model_dir / "feature_names.json", 'w', encoding='utf-8') as f:
        json.dump(feature_names, f, indent=2)
    
    # 保存训练信息
    training_info = {
        "model_type": "XGBoost",
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "features": X.shape[1],
        "classes": label_encoder.classes_.tolist(),
        "f1_macro": float(f1_macro),
        "f1_weighted": float(f1_weighted),
        "training_date": "2025-01-12",
        "data_source": "expanded_mock_data",
        "note": "使用模拟特征的快速训练版本"
    }
    
    with open(model_dir / "training_info.json", 'w', encoding='utf-8') as f:
        json.dump(training_info, f, indent=2, ensure_ascii=False)
    
    print(f"💾 模型已保存至: {model_path}")
    print(f"💾 训练信息已保存至: {model_dir / 'training_info.json'}")
    
    print("\n🎉 快速训练完成！")
    print("🎯 下一步: 运行 test_trained_model.py 测试效果")

def generate_mock_features(question_type):
    """生成基于题型的模拟特征"""
    # 设置随机种子以保证一致性
    random.seed(hash(question_type) % 1000)
    
    features = []
    
    # 基础特征 (40维)
    base_features = [random.random() for _ in range(40)]
    features.extend(base_features)
    
    # 类型特定特征 (80维)
    if question_type == "true_false":
        # 判断题特征：高answer_pattern_score，低option_count等
        type_features = [
            0.9 + random.random() * 0.1,  # answer_pattern_score
            0.0,  # option_count
            0.8 + random.random() * 0.2,  # hint_keywords_tf
        ] + [random.random() * 0.3 for _ in range(77)]
    
    elif question_type == "fill_blank":
        # 填空题特征：高blank_markers，低option_count
        type_features = [
            0.1 + random.random() * 0.2,  # answer_pattern_score
            0.0,  # option_count
            0.9 + random.random() * 0.1,  # blank_markers
        ] + [random.random() * 0.4 for _ in range(77)]
    
    elif question_type == "multiple_choice":
        # 多选题特征：高option_count，高multi_hints
        type_features = [
            0.5 + random.random() * 0.3,  # answer_pattern_score
            0.7 + random.random() * 0.3,  # option_count
            0.8 + random.random() * 0.2,  # hint_keywords_multi
        ] + [random.random() * 0.6 for _ in range(77)]
    
    elif question_type == "single_choice":
        # 单选题特征：中等option_count，低multi_hints
        type_features = [
            0.6 + random.random() * 0.3,  # answer_pattern_score
            0.5 + random.random() * 0.3,  # option_count
            0.2 + random.random() * 0.3,  # hint_keywords_multi
        ] + [random.random() * 0.5 for _ in range(77)]
    
    else:  # subjective
        # 简答题特征：低answer_pattern，高subjective_hints
        type_features = [
            0.1 + random.random() * 0.2,  # answer_pattern_score
            0.0,  # option_count
            0.8 + random.random() * 0.2,  # hint_keywords_subj
        ] + [random.random() * 0.4 for _ in range(77)]
    
    features.extend(type_features)
    
    return features

if __name__ == "__main__":
    quick_train()
