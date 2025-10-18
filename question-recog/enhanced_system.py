#!/usr/bin/env python3
"""
增强版题目分类器 - 支持更多题型识别
"""

import json
from pathlib import Path
import pandas as pd
import re
from typing import List, Dict, Any

def enhanced_question_classifier(question: str, options: List[str], answer: str) -> tuple:
    """增强版题目分类器，返回(类型, 置信度)"""
    
    # 清理输入
    question = question.strip()
    answer = answer.strip()
    
    # 1. 判断题识别（高优先级）
    true_false_patterns = [
        r'(对|错|√|×|正确|错误|是|否)$',
        r'[（(](对|错|√|×)[)）]$',
        r'说法.*?(对|错|正确|错误)',
        r'表述.*?(对|错|正确|错误)',
        r'判断.*?(对|错)',
    ]
    
    for pattern in true_false_patterns:
        if re.search(pattern, question):
            return 'true_false', 0.9
    
    if len(options) == 2:
        option_text = ' '.join(options).lower()
        if any(keyword in option_text for keyword in ['对', '错', '√', '×', 'true', 'false', 'a. 对', 'b. 错']):
            return 'true_false', 0.85
    
    # 2. 填空题识别
    blank_patterns = [
        r'____+',
        r'（\s*）',
        r'\(\s*\)',
        r'【\s*】',
        r'等于\s*$',
        r'约为\s*$',
        r'是\s*$',
        r'为\s*$',
    ]
    
    for pattern in blank_patterns:
        if re.search(pattern, question):
            return 'fill_blank', 0.9
    
    # 3. 选择题识别
    if len(options) >= 3:
        # 多选题关键词
        multi_keywords = ['多选', '多项', '至少两项', '两个以上', '不止一个', '哪些', '哪几个', '包括']
        if any(keyword in question for keyword in multi_keywords):
            return 'multiple_choice', 0.9
        
        # 根据答案长度判断
        if len(answer) > 1 and all(c.isalpha() for c in answer):
            return 'multiple_choice', 0.8
        else:
            return 'single_choice', 0.85
    
    # 4. 简答题识别
    subjective_patterns = [
        r'^(简述|说明|论述|分析|阐述|解释|描述)',
        r'(如何|为什么|什么是|怎样)',
        r'(请|试|谈谈)',
        r'(基本要求|工作原理|主要特点|注意事项)',
        r'(操作步骤|检修方法|故障处理|安全要求)',
    ]
    
    for pattern in subjective_patterns:
        if re.search(pattern, question):
            return 'subjective', 0.85
    
    # 如果没有选项且答案很长，也认为是简答题
    if not options and len(answer) > 20:
        return 'subjective', 0.7
    
    # 5. 根据题目内容进一步判断
    question_lower = question.lower()
    
    # 电力专业判断题特征
    power_tf_keywords = ['符合规程', '违反规定', '安全规范', '技术标准', '允许', '禁止', '必须', '应当', '不得']
    if any(keyword in question for keyword in power_tf_keywords):
        return 'true_false', 0.75
    
    # 电力专业填空题特征  
    power_blank_keywords = ['额定', '容量', '电压等级', '频率', '功率', '电流', '电压', '阻抗', '参数', '数值', '范围', '限值']
    if any(keyword in question for keyword in power_blank_keywords):
        return 'fill_blank', 0.7
    
    return 'unknown', 0.0

def enhanced_parse_excel(file_path: str) -> List[Dict[str, Any]]:
    """增强版Excel解析"""
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
            
            # 题目编号识别（更准确）
            question_start_patterns = [
                r'^\d+\s+[^0-9]',  # "1 运用中..."
                r'^\d+[.\、]\s*',   # "1. " 或 "1、"
                r'^第\d+题',        # "第1题"
                r'^\(\d+\)',        # "(1)"
            ]
            
            is_new_question = any(re.match(pattern, row_text.strip()) for pattern in question_start_patterns)
            
            if is_new_question:
                # 处理前一个题目
                if current_question and question_buffer:
                    full_question = " ".join(question_buffer)
                    
                    # 提取答案
                    answer_patterns = [
                        r'答案[:：]\s*([^\s\n]+)',
                        r'正确答案[:：]\s*([^\s\n]+)',
                        r'参考答案[:：]\s*([^\s\n]+)',
                    ]
                    
                    answer = ""
                    for pattern in answer_patterns:
                        match = re.search(pattern, full_question)
                        if match:
                            answer = match.group(1)
                            break
                    
                    # 清理题目（移除答案、题型标记等）
                    clean_question = full_question
                    clean_question = re.sub(r'\s*答案[:：].*$', '', clean_question)
                    clean_question = re.sub(r'\s*(填空题|选择题|判断题|简答题|多选题).*$', '', clean_question)
                    clean_question = re.sub(r'^\d+[.\、]?\s*', '', clean_question)  # 移除题号
                    
                    # 分类
                    question_type, confidence = enhanced_question_classifier(clean_question, current_options, answer)
                    
                    if clean_question.strip():  # 确保题目不为空
                        questions.append({
                            'question': clean_question.strip(),
                            'options': current_options.copy(),
                            'answer': answer.strip(),
                            'type': question_type,
                            'confidence': confidence
                        })
                
                # 开始新题目
                current_question = row_text.strip()
                current_options = []
                question_buffer = [current_question]
            
            # 选项识别
            elif re.match(r'^[A-F][.\)]\s+', row_text.strip()):
                current_options.append(row_text.strip())
                question_buffer.append(row_text.strip())
            
            # 否则追加到题目缓冲区
            else:
                question_buffer.append(row_text.strip())
        
        # 处理最后一个题目
        if current_question and question_buffer:
            full_question = " ".join(question_buffer)
            
            answer_patterns = [
                r'答案[:：]\s*([^\s\n]+)',
                r'正确答案[:：]\s*([^\s\n]+)',
                r'参考答案[:：]\s*([^\s\n]+)',
            ]
            
            answer = ""
            for pattern in answer_patterns:
                match = re.search(pattern, full_question)
                if match:
                    answer = match.group(1)
                    break
            
            clean_question = full_question
            clean_question = re.sub(r'\s*答案[:：].*$', '', clean_question)
            clean_question = re.sub(r'\s*(填空题|选择题|判断题|简答题|多选题).*$', '', clean_question)
            clean_question = re.sub(r'^\d+[.\、]?\s*', '', clean_question)
            
            question_type, confidence = enhanced_question_classifier(clean_question, current_options, answer)
            
            if clean_question.strip():
                questions.append({
                    'question': clean_question.strip(),
                    'options': current_options.copy(),
                    'answer': answer.strip(),
                    'type': question_type,
                    'confidence': confidence
                })
    
    except Exception as e:
        print(f"Excel解析失败: {e}")
    
    return questions

def test_enhanced_system():
    """测试增强版系统"""
    print("🚀 测试增强版题目识别系统")
    print("=" * 50)
    
    # 查找题库文件
    tiku_dir = Path("../题库")
    if not tiku_dir.exists():
        tiku_dir = Path(__file__).parent.parent / "题库"
        if not tiku_dir.exists():
            print("❌ 题库目录不存在")
            return
    
    excel_files = list(tiku_dir.glob("*.xlsx"))
    if not excel_files:
        print("❌ 未找到Excel文件")
        return
    
    all_results = []
    
    for excel_file in excel_files:
        print(f"📄 处理文件: {excel_file.name}")
        
        questions = enhanced_parse_excel(str(excel_file))
        
        for i, q in enumerate(questions):
            result = {
                "source_id": f"file://{excel_file.name}#q{i+1}",
                "question": q['question'],
                "options": q['options'],
                "answer_raw": q['answer'],
                "predicted_type": q['type'],
                "confidence": q['confidence'],
                "method": "enhanced_rule_based"
            }
            all_results.append(result)
        
        print(f"  📊 识别到 {len(questions)} 个题目")
    
    # 统计结果
    type_counts = {}
    confidence_levels = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
    
    for result in all_results:
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
    print(f"题目总数: {len(all_results)}")
    
    print(f"\n📈 题型分布:")
    for q_type, count in sorted(type_counts.items()):
        percentage = count / len(all_results) * 100 if all_results else 0
        print(f"  {q_type:<15}: {count:>4} 题 ({percentage:>5.1f}%)")
    
    print(f"\n🎯 置信度分布:")
    for level, count in confidence_levels.items():
        percentage = count / len(all_results) * 100 if all_results else 0
        print(f"  {level:<10}: {count:>4} 题 ({percentage:>5.1f}%)")
    
    # 保存结果
    output_file = "enhanced_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存至: {output_file}")
    
    # 显示各类型题目示例
    print(f"\n📝 各题型示例:")
    shown_types = set()
    for result in all_results:
        if result['predicted_type'] not in shown_types and len(shown_types) < 5:
            shown_types.add(result['predicted_type'])
            print(f"  【{result['predicted_type']}】(置信度: {result['confidence']:.1f})")
            print(f"    题干: {result['question'][:100]}...")
            if result['options']:
                print(f"    选项: {', '.join(result['options'][:2])}...")
            print(f"    答案: {result['answer_raw'][:50]}...")
            print()
    
    return len(all_results), type_counts, confidence_levels

if __name__ == "__main__":
    total, types, confidence = test_enhanced_system()
    
    if total > 0:
        print("🎉 增强版系统运行成功！")
        print(f"📊 成功识别 {total} 个题目")
        print(f"📈 识别了 {len(types)} 种题型")
        high_conf_ratio = confidence['high'] / total * 100 if total > 0 else 0
        print(f"🎯 高置信度题目占比: {high_conf_ratio:.1f}%")
    else:
        print("❌ 仍有问题需要进一步调试")
