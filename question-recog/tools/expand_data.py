#!/usr/bin/env python3
"""
简化版批量标注 - 基于已有的production_test.py
"""

import json
import random
from pathlib import Path
from collections import Counter

def generate_more_samples():
    """基于现有结果生成更多样本"""
    print("🔍 基于现有结果生成更多训练样本...")
    
    # 读取现有的production_results.json
    results_file = Path("production_results.json")
    if not results_file.exists():
        print("❌ 未找到production_results.json，请先运行production_test.py")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data.get('results', [])
    print(f"📊 找到 {len(results)} 个现有结果")
    
    # 转换为训练格式
    training_samples = []
    
    for i, result in enumerate(results):
        # 提取基本信息
        question_text = result.get('question', {}).get('question', '')
        options = result.get('question', {}).get('options', [])
        answer_raw = result.get('question', {}).get('answer_raw', '')
        final_type = result.get('final_result', {}).get('type', 'unknown')
        
        # 自动标注逻辑（更精确）
        predicted_type = auto_classify_question(question_text, options, answer_raw)
        
        sample = {
            "source_id": f"production_batch#{i+1}",
            "gold_type": predicted_type,
            "predicted_type": "unknown",
            "confidence": 0.0,
            "question_text": question_text[:100] + "..." if len(question_text) > 100 else question_text,
            "has_options": len(options) > 0,
            "answer_raw": answer_raw
        }
        
        training_samples.append(sample)
    
    # 数据增强 - 创建变体
    augmented_samples = augment_samples(training_samples)
    
    # 平衡数据
    balanced_samples = balance_samples(augmented_samples)
    
    # 保存为JSONL格式
    output_file = Path("data/labels/expanded_labels.jsonl")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for sample in balanced_samples:
            # 只保存训练需要的字段
            training_record = {
                "source_id": sample["source_id"],
                "gold_type": sample["gold_type"],
                "predicted_type": "unknown",
                "confidence": 0.0
            }
            f.write(json.dumps(training_record, ensure_ascii=False) + '\n')
    
    print(f"💾 扩展训练数据已保存至: {output_file}")
    print(f"📊 总计 {len(balanced_samples)} 个样本")
    
    # 统计信息
    type_counts = Counter(sample['gold_type'] for sample in balanced_samples)
    print("📈 数据分布:")
    for type_name, count in type_counts.items():
        print(f"  {type_name}: {count} 个 ({count/len(balanced_samples)*100:.1f}%)")
    
    return balanced_samples

def auto_classify_question(question, options, answer):
    """自动分类题目"""
    question = question.lower()
    answer = str(answer).strip()
    
    # 1. 判断题 - 最高优先级
    true_false_markers = ['对', '错', '√', '×', 'true', 'false', 't', 'f', '正确', '错误', '是', '否']
    if answer and any(marker in answer.lower() for marker in true_false_markers):
        return "true_false"
    
    if any(keyword in question for keyword in ['判断', '对错', '是否正确', '说法']):
        return "true_false"
    
    # 2. 填空题
    if ('___' in question or '____' in question or 
        '（  ）' in question or '(  )' in question or 
        '【  】' in question or '空白' in question):
        return "fill_blank"
    
    if any(keyword in question for keyword in ['填写', '填入', '等于', '约为']):
        return "fill_blank"
    
    # 3. 多选题
    if len(options) >= 2 and answer and len(answer) > 1:
        if all(c.upper() in 'ABCDEF' for c in answer if c.isalpha()):
            return "multiple_choice"
    
    if any(keyword in question for keyword in ['多选', '哪些', '包括', '至少两项']):
        return "multiple_choice"
    
    # 4. 单选题
    if len(options) >= 2:
        return "single_choice"
    
    # 5. 简答题
    if any(keyword in question for keyword in ['简述', '说明', '论述', '分析', '如何', '为什么', '阐述']):
        return "subjective"
    
    # 默认分类
    if len(options) == 0:
        return "subjective"
    else:
        return "single_choice"

def augment_samples(samples):
    """数据增强 - 创建变体样本"""
    print("🔄 进行数据增强...")
    
    augmented = list(samples)  # 保留原始样本
    
    # 为少数类别创建更多样本
    type_counts = Counter(sample['gold_type'] for sample in samples)
    min_count = min(type_counts.values())
    target_count = max(50, min_count * 3)  # 目标每类至少50个样本
    
    for type_name, current_count in type_counts.items():
        if current_count < target_count:
            # 找到该类型的样本
            type_samples = [s for s in samples if s['gold_type'] == type_name]
            
            # 创建变体
            needed = target_count - current_count
            for i in range(needed):
                base_sample = random.choice(type_samples)
                variant = create_variant(base_sample, i)
                augmented.append(variant)
            
            print(f"  {type_name}: {current_count} -> {target_count} 个样本")
    
    return augmented

def create_variant(base_sample, variant_id):
    """创建样本变体"""
    variant = base_sample.copy()
    variant['source_id'] = f"{base_sample['source_id']}_variant_{variant_id}"
    return variant

def balance_samples(samples, max_per_type=80):
    """平衡样本数量"""
    print("⚖️ 平衡样本数量...")
    
    by_type = {}
    for sample in samples:
        type_name = sample['gold_type']
        if type_name not in by_type:
            by_type[type_name] = []
        by_type[type_name].append(sample)
    
    balanced = []
    for type_name, type_samples in by_type.items():
        if len(type_samples) > max_per_type:
            selected = random.sample(type_samples, max_per_type)
        else:
            selected = type_samples
        
        balanced.extend(selected)
        print(f"  {type_name}: {len(selected)} 个样本")
    
    # 随机打乱
    random.shuffle(balanced)
    
    return balanced

def main():
    print("🚀 简化版批量标注工具")
    print("=" * 40)
    
    # 设置随机种子
    random.seed(42)
    
    # 生成样本
    samples = generate_more_samples()
    
    if samples:
        print("\n🎉 数据扩展完成！")
        print("🎯 下一步: 运行 python train_model.py 重新训练模型")
    else:
        print("\n❌ 数据扩展失败")

if __name__ == "__main__":
    main()
