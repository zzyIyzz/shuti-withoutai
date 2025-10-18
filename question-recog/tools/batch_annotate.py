#!/usr/bin/env python3
"""
批量数据标注工具 - 从所有题库文件中提取更多样本
"""

import sys
import os
from pathlib import Path
import json
import random
from collections import Counter

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 直接导入，不使用相对导入
try:
    from readers import DocumentReader
    from layout_state_machine import LayoutStateMachine
except ImportError:
    # 备用导入方式
    sys.path.append(str(Path(__file__).parent / "src" / "io"))
    sys.path.append(str(Path(__file__).parent / "src" / "parsing"))
    from readers import DocumentReader
    from layout_state_machine import LayoutStateMachine

def extract_more_samples():
    """从所有题库文件中提取更多样本"""
    print("🔍 批量提取题库样本...")
    
    # 查找所有题库文件
    tiku_dir = Path("../题库")
    if not tiku_dir.exists():
        tiku_dir = Path(__file__).parent.parent / "题库"
    
    if not tiku_dir.exists():
        print("❌ 题库目录不存在")
        return
    
    # 支持的文件格式
    supported_files = []
    for pattern in ["*.xlsx", "*.docx"]:  # 暂时跳过PDF
        supported_files.extend(tiku_dir.glob(pattern))
    
    print(f"📁 找到 {len(supported_files)} 个题库文件")
    
    # 读取器和解析器
    reader = DocumentReader()
    parser = LayoutStateMachine()
    
    all_samples = []
    
    for file_path in supported_files:
        print(f"📖 处理文件: {file_path.name}")
        
        try:
            # 读取文档
            doc_input = reader.read_document(str(file_path))
            
            # 解析题目
            questions = parser.parse(doc_input.blocks)
            
            print(f"  📊 解析到 {len(questions)} 个题目")
            
            # 随机采样（避免数据过多）
            if len(questions) > 100:
                questions = random.sample(questions, 100)
                print(f"  🎲 随机采样 100 个题目")
            
            # 添加到样本集
            for i, question in enumerate(questions):
                sample = {
                    "source_id": f"file://{file_path}#q{i+1}",
                    "question": question.question,
                    "options": question.options,
                    "answer_raw": question.answer_raw,
                    "explanation_raw": question.explanation_raw,
                    "predicted_type": "unknown",  # 待标注
                    "confidence": 0.0,
                    "layout_score": question.layout_score
                }
                all_samples.append(sample)
                
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            continue
    
    print(f"📊 总共提取 {len(all_samples)} 个样本")
    
    # 自动标注
    auto_labeled = auto_label_samples(all_samples)
    
    # 保存样本
    output_file = Path("data/labels/batch_samples.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(auto_labeled, f, indent=2, ensure_ascii=False)
    
    print(f"💾 样本已保存至: {output_file}")
    
    # 统计信息
    type_counts = Counter(sample['predicted_type'] for sample in auto_labeled)
    print("📈 标注结果统计:")
    for type_name, count in type_counts.items():
        print(f"  {type_name}: {count} 个")
    
    return auto_labeled

def auto_label_samples(samples):
    """自动标注样本"""
    print("🤖 开始自动标注...")
    
    labeled_samples = []
    
    for sample in samples:
        question = sample['question']
        answer = sample['answer_raw']
        options = sample['options']
        
        # 自动标注逻辑
        predicted_type = "unknown"
        confidence = 0.5
        
        # 1. 判断题 - 最高优先级
        if answer and any(marker in answer for marker in ['对', '错', '√', '×', 'True', 'False', 'T', 'F', '正确', '错误']):
            predicted_type = "true_false"
            confidence = 0.9
        
        # 2. 填空题 - 检测空白标记
        elif ('___' in question or '____' in question or 
              '（  ）' in question or '(  )' in question or 
              '【  】' in question):
            predicted_type = "fill_blank"
            confidence = 0.85
        
        # 3. 选择题 - 有选项
        elif len(options) >= 2:
            if answer and len(answer) > 1 and all(c in 'ABCDEF' for c in answer):
                predicted_type = "multiple_choice"
                confidence = 0.8
            elif answer and len(answer) == 1 and answer in 'ABCDEF':
                predicted_type = "single_choice"
                confidence = 0.8
            else:
                predicted_type = "single_choice"  # 默认单选
                confidence = 0.6
        
        # 4. 简答题 - 其他情况
        else:
            if any(keyword in question for keyword in ['简述', '说明', '论述', '分析', '如何', '为什么']):
                predicted_type = "subjective"
                confidence = 0.7
            else:
                predicted_type = "subjective"  # 兜底
                confidence = 0.4
        
        sample['predicted_type'] = predicted_type
        sample['confidence'] = confidence
        labeled_samples.append(sample)
    
    return labeled_samples

def convert_to_training_format(samples, target_count=200):
    """转换为训练格式并平衡数据"""
    print(f"🔄 转换为训练格式，目标样本数: {target_count}")
    
    # 按类型分组
    by_type = {}
    for sample in samples:
        type_name = sample['predicted_type']
        if type_name not in by_type:
            by_type[type_name] = []
        by_type[type_name].append(sample)
    
    # 计算每个类型的目标数量（尽量平衡）
    num_types = len(by_type)
    target_per_type = target_count // num_types
    
    balanced_samples = []
    
    for type_name, type_samples in by_type.items():
        # 如果样本不足，全部使用
        if len(type_samples) <= target_per_type:
            selected = type_samples
        else:
            # 随机采样
            selected = random.sample(type_samples, target_per_type)
        
        print(f"  {type_name}: {len(selected)} 个样本")
        balanced_samples.extend(selected)
    
    # 转换为JSONL格式
    training_samples = []
    for sample in balanced_samples:
        training_sample = {
            "source_id": sample['source_id'],
            "gold_type": sample['predicted_type'],
            "predicted_type": "unknown",
            "confidence": 0.0
        }
        training_samples.append(training_sample)
    
    # 保存训练文件
    output_file = Path("data/labels/expanded_labels.jsonl")
    with open(output_file, 'w', encoding='utf-8') as f:
        for sample in training_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    print(f"💾 训练数据已保存至: {output_file}")
    print(f"📊 总计 {len(training_samples)} 个平衡样本")
    
    return training_samples

def main():
    print("🚀 批量数据标注工具")
    print("=" * 40)
    
    # 设置随机种子
    random.seed(42)
    
    # 提取样本
    samples = extract_more_samples()
    
    if not samples:
        print("❌ 没有提取到样本")
        return
    
    # 转换为训练格式
    training_samples = convert_to_training_format(samples, target_count=200)
    
    print("\n🎉 批量标注完成！")
    print(f"📊 可用于训练的样本: {len(training_samples)} 个")
    print("🎯 下一步: 运行 python train_model.py 重新训练模型")

if __name__ == "__main__":
    main()
