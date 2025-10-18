#!/usr/bin/env python
"""
简化版标注工具 - 批量展示题目供人工判断
"""

import sys
import json
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))


def show_annotation_examples():
    """展示标注示例"""
    print("🏷️ 数据标注示例和规则")
    print("=" * 50)
    
    # 读取生产环境结果
    results_file = Path("production_results.json")
    if not results_file.exists():
        print("❌ 请先运行 production_test.py")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data["results"]
    
    # 标注规则说明
    print("📋 标注规则:")
    print("1️⃣  单选题: 有A、B、C、D选项，答案为单个字母(如A)")
    print("2️⃣  多选题: 有选项，答案为多个字母(如ABC)或包含'多选'提示")
    print("3️⃣  判断题: 答案为 对/错/√/×/True/False")
    print("4️⃣  填空题: 题目中有空白处(___)或括号()，答案为文字/数字")
    print("5️⃣  简答题: 需要文字叙述回答，通常以'简述'、'说明'开头")
    
    print(f"\n🔍 让我们看几个具体例子:")
    
    # 找一些典型例子
    examples = []
    
    # 查找不同类型的题目
    for result in results[:50]:  # 只看前50个
        question_text = result["question"]["question"]
        answer = result["question"]["answer_raw"]
        options = result["question"]["options"]
        
        # 跳过明显的非题目内容
        if len(question_text) < 10 or "目录" in question_text or "前言" in question_text:
            continue
            
        examples.append({
            "question": question_text,
            "options": options,
            "answer": answer,
            "predicted": result["final_result"]["type"]
        })
        
        if len(examples) >= 10:  # 收集10个例子
            break
    
    # 显示例子
    for i, example in enumerate(examples):
        print(f"\n📝 例子 {i+1}:")
        print(f"题目: {example['question'][:100]}...")
        
        if example['options']:
            print(f"选项: {len(example['options'])} 个")
            for j, option in enumerate(example['options'][:3]):  # 只显示前3个选项
                print(f"  {chr(65+j)}. {option[:50]}...")
        else:
            print("选项: 无")
            
        print(f"答案: {example['answer']}")
        print(f"系统预测: {example['predicted']}")
        
        # 给出建议标注
        suggested_type = suggest_annotation(example)
        print(f"💡 建议标注: {suggested_type}")
        print("-" * 40)


def suggest_annotation(example):
    """根据题目特征建议标注类型"""
    question = example['question'].lower()
    answer = example['answer'].strip()
    options = example['options']
    
    # 判断题特征
    if answer in ['对', '错', '√', '×', 'True', 'False', 'T', 'F', '正确', '错误']:
        return "3️⃣ 判断题"
    
    # 填空题特征
    if ('___' in example['question'] or 
        '（）' in example['question'] or 
        '()' in example['question'] or
        '【】' in example['question']):
        return "4️⃣ 填空题"
    
    # 简答题特征
    if any(keyword in question for keyword in ['简述', '说明', '论述', '分析', '阐述', '解释']):
        return "5️⃣ 简答题"
    
    # 多选题特征
    if (any(keyword in question for keyword in ['多选', '哪些', '包括']) or
        len(answer) > 1 and all(c in 'ABCDEF' for c in answer)):
        return "2️⃣ 多选题"
    
    # 单选题特征
    if options and len(options) >= 2 and len(answer) == 1 and answer in 'ABCDEF':
        return "1️⃣ 单选题"
    
    return "❓ 需要仔细判断"


def create_simple_annotation_file():
    """创建简化的标注文件"""
    print(f"\n💡 创建简化标注方案...")
    
    # 读取结果
    results_file = Path("production_results.json")
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data["results"]
    
    # 选择需要标注的题目
    to_annotate = []
    
    # 优先选择有明显特征的题目
    for result in results:
        question_text = result["question"]["question"]
        answer = result["question"]["answer_raw"]
        
        # 跳过明显的非题目
        if (len(question_text) < 10 or 
            "目录" in question_text or 
            "前言" in question_text or
            "章" in question_text[:10]):
            continue
        
        # 选择有明确特征的题目
        if (answer in ['对', '错', '√', '×'] or  # 判断题
            len(result["question"]["options"]) >= 3 or  # 有选项的题目
            any(keyword in question_text for keyword in ['简述', '说明', '填写'])):  # 简答/填空题
            
            to_annotate.append({
                "source_id": result["source_id"],
                "question": question_text[:200],  # 截断长题目
                "options_count": len(result["question"]["options"]),
                "answer": answer,
                "suggested_type": suggest_annotation({
                    "question": question_text,
                    "answer": answer,
                    "options": result["question"]["options"]
                })
            })
        
        if len(to_annotate) >= 50:  # 收集50个样本
            break
    
    # 保存到文件供手动编辑
    annotation_file = Path("data/labels/annotation_batch.json")
    annotation_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(annotation_file, 'w', encoding='utf-8') as f:
        json.dump(to_annotate, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已生成 {len(to_annotate)} 个待标注样本")
    print(f"📁 保存位置: {annotation_file}")
    
    print(f"\n📋 下一步操作:")
    print(f"1. 打开文件: {annotation_file}")
    print(f"2. 在每个题目的 'suggested_type' 字段中确认或修改标注")
    print(f"3. 标注格式: 1=单选题, 2=多选题, 3=判断题, 4=填空题, 5=简答题")
    print(f"4. 完成后运行: python process_annotations.py")
    
    return annotation_file


if __name__ == "__main__":
    show_annotation_examples()
    create_simple_annotation_file()
