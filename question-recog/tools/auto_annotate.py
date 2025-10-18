#!/usr/bin/env python
"""
自动标注处理工具 - 根据题目特征自动判断题型
"""

import json
import re
from pathlib import Path


def auto_annotate():
    """自动标注题目类型"""
    print("🤖 自动标注处理工具")
    print("=" * 40)
    
    # 读取待标注文件
    annotation_file = Path("data/labels/annotation_batch.json")
    if not annotation_file.exists():
        print("❌ 标注文件不存在，请先运行 simple_annotation.py")
        return
    
    with open(annotation_file, 'r', encoding='utf-8') as f:
        annotations = json.load(f)
    
    print(f"📚 加载了 {len(annotations)} 个待标注题目")
    
    # 自动标注逻辑
    auto_labeled = 0
    manual_needed = 0
    
    for item in annotations:
        question = item["question"].lower()
        answer = item["answer"].strip()
        
        # 自动判断题型
        if "suggested_type" in item:
            # 根据特征自动标注
            if ("____" in item["question"] or 
                "（）" in item["question"] or 
                "()" in item["question"] or
                "【】" in item["question"] or
                "填空题" in item["question"]):
                item["final_type"] = "4"  # 填空题
                auto_labeled += 1
                
            elif (any(keyword in question for keyword in ['简述', '说明', '论述', '分析', '阐述', '解释', '描述']) or
                  "简答题" in item["question"]):
                item["final_type"] = "5"  # 简答题
                auto_labeled += 1
                
            elif (item["options_count"] >= 3 and 
                  answer and len(answer) == 1 and answer in 'ABCDEF'):
                item["final_type"] = "1"  # 单选题
                auto_labeled += 1
                
            elif (item["options_count"] >= 3 and 
                  answer and len(answer) > 1 and all(c in 'ABCDEF' for c in answer)):
                item["final_type"] = "2"  # 多选题
                auto_labeled += 1
                
            elif (answer in ['对', '错', '√', '×', 'True', 'False', 'T', 'F', '正确', '错误'] or
                  "判断题" in item["question"]):
                item["final_type"] = "3"  # 判断题
                auto_labeled += 1
                
            else:
                # 基于题目内容的启发式判断
                if (len(item["question"]) < 100 and 
                    not any(punct in item["question"] for punct in ['？', '?']) and
                    item["options_count"] == 0):
                    # 短句子，无问号，无选项 -> 可能是判断题
                    item["final_type"] = "3"  # 判断题
                    auto_labeled += 1
                else:
                    item["final_type"] = "unknown"
                    manual_needed += 1
    
    print(f"✅ 自动标注: {auto_labeled} 个")
    print(f"⚠️  需要人工: {manual_needed} 个")
    
    # 显示标注结果统计
    type_counts = {}
    for item in annotations:
        if "final_type" in item:
            ftype = item["final_type"]
            if ftype not in type_counts:
                type_counts[ftype] = 0
            type_counts[ftype] += 1
    
    print(f"\n📊 标注结果统计:")
    type_names = {"1": "单选题", "2": "多选题", "3": "判断题", "4": "填空题", "5": "简答题", "unknown": "未知"}
    for ftype, count in type_counts.items():
        name = type_names.get(ftype, ftype)
        print(f"  {name}: {count} 个")
    
    # 保存自动标注结果
    auto_file = Path("data/labels/auto_labeled.json")
    with open(auto_file, 'w', encoding='utf-8') as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 自动标注结果保存至: {auto_file}")
    
    # 生成训练格式的标注文件
    training_labels = []
    for item in annotations:
        if "final_type" in item and item["final_type"] != "unknown":
            # 转换为训练格式
            type_mapping = {"1": "single_choice", "2": "multiple_choice", "3": "true_false", "4": "fill_blank", "5": "subjective"}
            gold_type = type_mapping.get(item["final_type"], "unknown")
            
            training_labels.append({
                "source_id": item["source_id"],
                "gold_type": gold_type,
                "predicted_type": "unknown",  # 将被模型预测覆盖
                "confidence": 0.0,
                "question_preview": item["question"][:100] + "..." if len(item["question"]) > 100 else item["question"]
            })
    
    # 保存训练标注文件
    labels_file = Path("data/labels/manual_labels.jsonl")
    with open(labels_file, 'w', encoding='utf-8') as f:
        for label in training_labels:
            f.write(json.dumps(label, ensure_ascii=False) + '\n')
    
    print(f"💾 训练标注文件保存至: {labels_file}")
    print(f"📊 可用于训练的样本: {len(training_labels)} 个")
    
    if len(training_labels) >= 30:
        print(f"\n🎉 标注完成！可以开始训练模型了")
        print(f"🚀 下一步运行: python train_model.py")
    else:
        print(f"\n⚠️  标注样本较少，建议增加到30个以上")
    
    return training_labels


if __name__ == "__main__":
    auto_annotate()
