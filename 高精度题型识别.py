#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高精度题型识别系统 - 刷题系统专用接口
集成修复后的Excel解析和题型识别功能
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

def enhanced_question_classifier(question: str, options: List[str], answer: str, excel_type: str = None) -> tuple:
    """
    修复后的题目分类器 - 来自question-recog/main.py
    返回(类型, 置信度)
    """
    
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

def detect_question_type_fixed(question: str, answer: str, options: Dict = None) -> str:
    """
    修复后的题型识别函数 - 刷题系统专用接口
    
    Args:
        question: 题目内容
        answer: 答案内容
        options: 选项字典
        
    Returns:
        题型名称（中文）
    """
    try:
        # 转换选项格式
        option_list = []
        if options:
            for key, value in options.items():
                option_list.append(f"{key}: {value}")
        
        # 使用修复后的分类器
        result_type, confidence = enhanced_question_classifier(question, option_list, answer)
        
        # 转换为中文题型名称
        type_mapping = {
            'single_choice': '单选题',
            'multiple_choice': '多选题',
            'true_false': '判断题',
            'fill_blank': '填空题', 
            'subjective': '简答题',
            'unknown': '未知'
        }
        
        chinese_type = type_mapping.get(result_type, result_type)
        
        # 输出识别信息
        print(f"🎯 高精度识别: {chinese_type} (置信度: {confidence:.2f})")
        
        return chinese_type
        
    except Exception as e:
        print(f"❌ 高精度识别失败: {e}")
        return "未知"

def get_question_type_with_confidence_fixed(question: str, answer: str, options: Dict = None) -> Tuple[str, float]:
    """
    修复后的题型识别（带置信度）
    
    Returns:
        (题型名称, 置信度)
    """
    try:
        # 转换选项格式
        option_list = []
        if options:
            for key, value in options.items():
                option_list.append(f"{key}: {value}")
        
        # 使用修复后的分类器
        result_type, confidence = enhanced_question_classifier(question, option_list, answer)
        
        # 转换为中文题型名称
        type_mapping = {
            'single_choice': '单选题',
            'multiple_choice': '多选题',
            'true_false': '判断题',
            'fill_blank': '填空题',
            'subjective': '简答题', 
            'unknown': '未知'
        }
        
        chinese_type = type_mapping.get(result_type, result_type)
        return chinese_type, confidence
        
    except Exception as e:
        print(f"❌ 高精度识别失败: {e}")
        return "未知", 0.0

def test_fixed_recognition():
    """测试修复后的识别功能"""
    print("🧪 测试修复后的高精度题型识别")
    print("=" * 50)
    
    test_cases = [
        {
            'question': '装设接地线____单人进行',
            'answer': 'C',
            'options': {'A': '严禁', 'B': '必须', 'C': '不宜', 'D': '不宜'},
            'expected': '单选题'
        },
        {
            'question': '安全组织措施包括哪些？',
            'answer': 'ABC',
            'options': {'A': '工作票', 'B': '工作许可', 'C': '工作监护', 'D': '工作间断'},
            'expected': '多选题'
        },
        {
            'question': '运用中的电气设备是指：____或____及____的电气设备。',
            'answer': '全部带有电压、一部分带有电压、一经操作即带有电压',
            'options': {},
            'expected': '填空题'
        },
        {
            'question': '装设接地线可以单人进行。',
            'answer': '×',
            'options': {},
            'expected': '判断题'
        }
    ]
    
    correct_count = 0
    
    for i, case in enumerate(test_cases):
        print(f"\n测试 {i+1}: {case['question'][:40]}...")
        result_type, confidence = get_question_type_with_confidence_fixed(
            case['question'],
            case['answer'], 
            case['options']
        )
        
        is_correct = result_type == case['expected']
        status = "✅" if is_correct else "❌"
        
        if is_correct:
            correct_count += 1
            
        print(f"  预期: {case['expected']}")
        print(f"  实际: {result_type} (置信度: {confidence:.2f}) {status}")
    
    accuracy = correct_count / len(test_cases) * 100
    print(f"\n📊 识别准确率: {accuracy:.1f}% ({correct_count}/{len(test_cases)})")
    
    if accuracy >= 75:
        print("🎉 高精度识别系统工作正常！")
    else:
        print("⚠️ 识别准确率需要进一步优化")

if __name__ == "__main__":
    test_fixed_recognition()
