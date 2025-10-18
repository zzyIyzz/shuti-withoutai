#!/usr/bin/env python3
"""
题库识别系统 - 修复版本
正确解析Excel的列结构，识别选择题
"""

import json
import argparse
from pathlib import Path
import pandas as pd
import re
from typing import List, Dict, Any
import sys

def enhanced_question_classifier(question: str, options: List[str], answer: str, excel_type: str = None) -> tuple:
    """题目分类器，返回(类型, 置信度)"""
    
    question = question.strip()
    answer = answer.strip()
    
    # 如果Excel中已标明题型，优先参考
    if excel_type:
        excel_type = excel_type.strip()
        if excel_type == "判断题":
            return 'true_false', 0.95
        elif excel_type == "单选题":
            return 'single_choice', 0.95
        elif excel_type == "多选题":
            return 'multiple_choice', 0.95
        elif excel_type == "填空题" and not options:  # 只有真正无选项才是填空题
            return 'fill_blank', 0.95
    
    # 1. 有选项的情况 - 优先识别为选择题
    if options and len(options) >= 2:
        # 判断题识别（有两个选项且为对错类型）
        if len(options) == 2:
            option_text = ' '.join(options).lower()
            if any(keyword in option_text for keyword in ['对', '错', '√', '×', 'true', 'false', '正确', '错误']):
                return 'true_false', 0.9
        
        # 多选题识别
        multi_keywords = ['多选', '多项', '至少两项', '哪些', '哪几个', '包括']
        if any(keyword in question for keyword in multi_keywords):
            return 'multiple_choice', 0.9
        elif len(answer) > 1 and all(c.upper() in 'ABCDEFGHIJ' for c in answer):
            return 'multiple_choice', 0.85
        
        # 默认为单选题
        return 'single_choice', 0.85
    
    # 2. 判断题识别（无选项情况）
    true_false_answers = ['对', '错', '√', '×', 'T', 'F', 'TRUE', 'FALSE', '正确', '错误', '是', '否']
    if answer.upper() in [x.upper() for x in true_false_answers]:
        return 'true_false', 0.9
    
    true_false_patterns = [
        r'(对|错|√|×|正确|错误|是|否)$',
        r'[（(](对|错|√|×)[)）]$',
        r'说法.*?(对|错|正确|错误)',
        r'表述.*?(对|错|正确|错误)',
    ]
    
    for pattern in true_false_patterns:
        if re.search(pattern, question):
            return 'true_false', 0.85
    
    # 3. 填空题识别
    blank_patterns = [r'____+', r'（\s*）', r'\(\s*\)', r'【\s*】']
    for pattern in blank_patterns:
        if re.search(pattern, question):
            return 'fill_blank', 0.9
    
    # 4. 简答题识别
    subjective_patterns = [
        r'^(简述|说明|论述|分析|阐述|解释|描述)',
        r'(如何|为什么|什么是|怎样)',
        r'(请|试|谈谈)',
    ]
    
    for pattern in subjective_patterns:
        if re.search(pattern, question):
            return 'subjective', 0.85
    
    if not options and len(answer) > 20:
        return 'subjective', 0.7
    
    return 'unknown', 0.0

def parse_excel_file_structured(file_path: str) -> List[Dict[str, Any]]:
    """解析结构化Excel文件（有列名的）"""
    questions = []
    
    try:
        df = pd.read_excel(file_path)
        print(f"  📋 Excel结构: {df.shape[0]}行 x {df.shape[1]}列")
        print(f"  📋 列名: {df.columns.tolist()}")
        
        # 检查是否有标准列结构
        has_structured_format = all(col in df.columns for col in ['题目', '答案'])
        
        if has_structured_format:
            print("  ✅ 检测到结构化格式，使用列解析")
            
            for idx, row in df.iterrows():
                try:
                    # 提取基本信息
                    question_text = str(row['题目']).strip() if pd.notna(row['题目']) else ""
                    answer_text = str(row['答案']).strip() if pd.notna(row['答案']) else ""
                    excel_type = str(row['题型']).strip() if '题型' in df.columns and pd.notna(row['题型']) else None
                    
                    if not question_text or question_text == 'nan':
                        continue
                    
                    # 提取选项
                    options = []
                    for opt_col in ['A', 'B', 'C', 'D', 'E', 'F']:
                        if opt_col in df.columns and pd.notna(row[opt_col]):
                            opt_text = str(row[opt_col]).strip()
                            if opt_text and opt_text != 'nan':
                                options.append(f"{opt_col}: {opt_text}")
                    
                    # 分类
                    question_type, confidence = enhanced_question_classifier(
                        question_text, options, answer_text, excel_type
                    )
                    
                    questions.append({
                        'question': question_text,
                        'options': options,
                        'answer': answer_text,
                        'type': question_type,
                        'confidence': confidence,
                        'excel_type': excel_type,
                        'row_index': idx + 1
                    })
                    
                except Exception as e:
                    print(f"    ⚠️ 第{idx+1}行解析失败: {e}")
                    continue
        else:
            print("  ⚠️ 非结构化格式，使用文本解析")
            questions = parse_excel_file_text(file_path)
    
    except Exception as e:
        print(f"❌ Excel解析失败: {e}")
    
    return questions

def parse_excel_file_text(file_path: str) -> List[Dict[str, Any]]:
    """解析文本格式Excel文件（原有逻辑）"""
    questions = []
    
    try:
        df = pd.read_excel(file_path)
        current_question = None
        current_options = []
        question_buffer = []
        
        for idx, row in df.iterrows():
            row_text = " ".join(str(cell) for cell in row.values if pd.notna(cell) and str(cell).strip())
            
            if not row_text.strip():
                continue
            
            # 题目开始识别
            question_start_patterns = [
                r'^\d+\s+[^0-9]',  # "1 运用中..."
                r'^\d+[.\、]\s*',   # "1. " 或 "1、"
                r'^第\d+题',        # "第1题"
                r'^\(\d+\)',        # "(1)"
            ]
            
            is_new_question = any(re.match(pattern, row_text.strip()) for pattern in question_start_patterns)
            
            if is_new_question:
                # 处理前一题
                if current_question and question_buffer:
                    question = process_question_buffer(question_buffer, current_options)
                    if question:
                        questions.append(question)
                
                # 开始新题
                current_question = row_text.strip()
                current_options = []
                question_buffer = [current_question]
            
            elif re.match(r'^[A-F][.\)]\s+', row_text.strip()):
                # 选项识别
                current_options.append(row_text.strip())
                question_buffer.append(row_text.strip())
            else:
                # 追加到题目
                question_buffer.append(row_text.strip())
        
        # 处理最后一题
        if current_question and question_buffer:
            question = process_question_buffer(question_buffer, current_options)
            if question:
                questions.append(question)
    
    except Exception as e:
        print(f"❌ Excel文本解析失败: {e}")
    
    return questions

def process_question_buffer(buffer: List[str], options: List[str]) -> Dict[str, Any]:
    """处理题目缓冲区"""
    full_text = " ".join(buffer)
    
    # 提取答案
    answer_patterns = [
        r'答案[:：]\s*([^\s\n]+)',
        r'正确答案[:：]\s*([^\s\n]+)',
        r'参考答案[:：]\s*([^\s\n]+)',
    ]
    
    answer = ""
    for pattern in answer_patterns:
        match = re.search(pattern, full_text)
        if match:
            answer = match.group(1)
            break
    
    # 清理题目
    clean_question = full_text
    clean_question = re.sub(r'\s*答案[:：].*$', '', clean_question)
    clean_question = re.sub(r'\s*(填空题|选择题|判断题|简答题|多选题).*$', '', clean_question)
    clean_question = re.sub(r'^\d+[.\、]?\s*', '', clean_question)
    
    # 分类
    question_type, confidence = enhanced_question_classifier(clean_question, options, answer)
    
    if clean_question.strip():
        return {
            'question': clean_question.strip(),
            'options': options.copy(),
            'answer': answer.strip(),
            'type': question_type,
            'confidence': confidence
        }
    
    return None

def process_files(input_dir: str, output_file: str = "fixed_results.json"):
    """处理题库文件"""
    print("🚀 题库识别系统 - 修复版")
    print("=" * 50)
    
    # 查找题库文件
    tiku_dir = Path(input_dir)
    if not tiku_dir.exists():
        print(f"❌ 题库目录不存在: {input_dir}")
        return
    
    excel_files = list(tiku_dir.glob("*.xlsx"))
    if not excel_files:
        print("❌ 未找到Excel文件")
        return
    
    all_results = []
    
    for excel_file in excel_files:
        print(f"📄 处理文件: {excel_file.name}")
        
        questions = parse_excel_file_structured(str(excel_file))
        
        for i, q in enumerate(questions):
            result = {
                "source_id": f"file://{excel_file.name}#q{i+1}",
                "question": q['question'],
                "options": q['options'],
                "answer_raw": q['answer'],
                "predicted_type": q['type'],
                "confidence": q['confidence'],
                "method": "fixed_structured_parser",
                "excel_type": q.get('excel_type', ''),
                "row_index": q.get('row_index', i+1)
            }
            all_results.append(result)
        
        print(f"  📊 识别到 {len(questions)} 个题目")
    
    # 统计结果
    print_statistics(all_results)
    
    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存至: {output_file}")
    
    # 显示示例
    show_examples(all_results)
    
    return len(all_results)

def print_statistics(results: List[Dict]):
    """打印统计信息"""
    if not results:
        return
    
    # 题型统计
    type_counts = {}
    confidence_levels = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
    
    for result in results:
        q_type = result["predicted_type"]
        confidence = result["confidence"]
        
        type_counts[q_type] = type_counts.get(q_type, 0) + 1
        
        if confidence >= 0.8:
            confidence_levels["high"] += 1
        elif confidence >= 0.6:
            confidence_levels["medium"] += 1
        elif confidence >= 0.4:
            confidence_levels["low"] += 1
        else:
            confidence_levels["unknown"] += 1
    
    print(f"\n📊 处理总结")
    print(f"题目总数: {len(results)}")
    
    print(f"\n📈 题型分布:")
    for q_type, count in sorted(type_counts.items()):
        percentage = count / len(results) * 100
        print(f"  {q_type:<15}: {count:>4} 题 ({percentage:>5.1f}%)")
    
    print(f"\n🎯 置信度分布:")
    for level, count in confidence_levels.items():
        percentage = count / len(results) * 100
        print(f"  {level:<10}: {count:>4} 题 ({percentage:>5.1f}%)")

def show_examples(results: List[Dict], max_examples: int = 5):
    """显示题目示例"""
    print(f"\n📝 题目示例:")
    
    # 按题型分组显示
    type_examples = {}
    for result in results:
        q_type = result['predicted_type']
        if q_type not in type_examples:
            type_examples[q_type] = []
        if len(type_examples[q_type]) < 2:  # 每种题型最多显示2个
            type_examples[q_type].append(result)
    
    for q_type, examples in type_examples.items():
        print(f"\n  🎯 {q_type} 示例:")
        for i, result in enumerate(examples):
            print(f"    示例{i+1} (置信度: {result['confidence']:.2f}):")
            print(f"      题干: {result['question'][:60]}...")
            if result['options']:
                print(f"      选项: {'; '.join(result['options'][:2])}...")
            print(f"      答案: {result['answer_raw']}")
            if result.get('excel_type'):
                print(f"      Excel标记: {result['excel_type']}")
            print()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='题库识别系统 - 修复版')
    parser.add_argument('--input', '-i', default='../题库', help='题库目录路径')
    parser.add_argument('--output', '-o', default='fixed_results.json', help='输出文件路径')
    parser.add_argument('--version', '-v', action='version', version='题库识别系统 v2.1-fixed')
    
    args = parser.parse_args()
    
    try:
        total = process_files(args.input, args.output)
        
        if total > 0:
            print("\n🎉 处理完成！")
            print(f"📊 成功识别 {total} 个题目")
            print(f"📋 详细结果请查看: {args.output}")
        else:
            print("\n❌ 未处理任何题目，请检查输入目录和文件格式")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 系统错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
