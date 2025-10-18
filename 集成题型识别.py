#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成题型识别系统 - 统一接口
整合原有的智能题型识别.py和修复后的question-recog系统
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

# 添加question-recog到路径
sys.path.insert(0, str(Path(__file__).parent / "question-recog"))

def detect_question_type_enhanced(question: str, answer: str, options: Dict = None) -> str:
    """
    增强版题型识别 - 优先使用修复后的高精度系统
    
    Args:
        question: 题目内容
        answer: 答案内容  
        options: 选项字典
        
    Returns:
        题型名称
    """
    try:
        # 方法1: 尝试使用修复后的高精度系统
        from question_recog.main import enhanced_question_classifier
        
        # 转换选项格式
        option_list = []
        if options:
            for key, value in options.items():
                option_list.append(f"{key}: {value}")
        
        result_type, confidence = enhanced_question_classifier(question, option_list, answer)
        
        # 转换题型名称到中文
        type_mapping = {
            'single_choice': '单选题',
            'multiple_choice': '多选题', 
            'true_false': '判断题',
            'fill_blank': '填空题',
            'subjective': '简答题',
            'unknown': '未知'
        }
        
        chinese_type = type_mapping.get(result_type, result_type)
        print(f"🎯 高精度识别: {chinese_type} (置信度: {confidence:.2f})")
        return chinese_type
        
    except Exception as e:
        print(f"⚠️ 高精度识别失败，使用备用方法: {e}")
        
        # 方法2: 使用原有的智能题型识别系统
        try:
            from 智能题型识别 import detect_question_type
            result = detect_question_type(question, answer, options)
            print(f"📊 备用识别: {result}")
            return result
        except Exception as e2:
            print(f"❌ 备用识别也失败: {e2}")
            return "未知"

def get_question_type_with_confidence_enhanced(question: str, answer: str, options: Dict = None) -> Tuple[str, float]:
    """
    增强版题型识别（带置信度）
    
    Returns:
        (题型名称, 置信度)
    """
    try:
        # 尝试使用修复后的系统
        from question_recog.main import enhanced_question_classifier
        
        option_list = []
        if options:
            for key, value in options.items():
                option_list.append(f"{key}: {value}")
        
        result_type, confidence = enhanced_question_classifier(question, option_list, answer)
        
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
        # 使用原有系统
        try:
            from 智能题型识别 import get_question_type_with_confidence
            return get_question_type_with_confidence(question, answer, options)
        except Exception as e2:
            return "未知", 0.0

def batch_classify_questions(questions: List[Dict]) -> List[Dict]:
    """
    批量题型识别
    
    Args:
        questions: 题目列表，每个题目包含question、answer、options字段
        
    Returns:
        添加了type和confidence字段的题目列表
    """
    results = []
    
    print(f"🚀 开始批量识别 {len(questions)} 个题目...")
    
    for i, q in enumerate(questions):
        try:
            question_type, confidence = get_question_type_with_confidence_enhanced(
                q.get('question', ''),
                q.get('answer', ''),
                q.get('options', {})
            )
            
            result = q.copy()
            result['type'] = question_type
            result['confidence'] = confidence
            results.append(result)
            
            if (i + 1) % 10 == 0:
                print(f"📊 已处理 {i + 1}/{len(questions)} 个题目")
                
        except Exception as e:
            print(f"❌ 第{i+1}题识别失败: {e}")
            result = q.copy()
            result['type'] = '未知'
            result['confidence'] = 0.0
            results.append(result)
    
    # 统计结果
    type_stats = {}
    total_confidence = 0
    
    for r in results:
        q_type = r['type']
        type_stats[q_type] = type_stats.get(q_type, 0) + 1
        total_confidence += r['confidence']
    
    print(f"\n📈 识别结果统计:")
    for q_type, count in sorted(type_stats.items()):
        percentage = count / len(results) * 100
        print(f"  {q_type}: {count} 题 ({percentage:.1f}%)")
    
    avg_confidence = total_confidence / len(results) if results else 0
    print(f"\n🎯 平均置信度: {avg_confidence:.3f}")
    
    return results

def test_integration():
    """测试集成功能"""
    print("🧪 测试集成题型识别系统")
    print("=" * 50)
    
    # 测试用例
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
        }
    ]
    
    print("🎯 单题识别测试:")
    for i, case in enumerate(test_cases):
        print(f"\n测试 {i+1}: {case['question'][:30]}...")
        result = detect_question_type_enhanced(
            case['question'], 
            case['answer'], 
            case['options']
        )
        status = "✅" if result == case['expected'] else "❌"
        print(f"  预期: {case['expected']}, 实际: {result} {status}")
    
    print(f"\n🚀 批量识别测试:")
    batch_results = batch_classify_questions(test_cases)
    
    print(f"\n✅ 集成测试完成！")

if __name__ == "__main__":
    test_integration()
