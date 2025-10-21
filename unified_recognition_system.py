#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一识别系统 - 整合所有识别功能
消除重复，提供统一的识别接口
"""

import sys
import time
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from collections import defaultdict

class 统一识别系统:
    """统一识别系统 - 整合所有识别功能"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.识别历史 = []
        self.性能统计 = defaultdict(lambda: {
            '调用次数': 0,
            '成功次数': 0,
            '平均耗时': 0.0,
            '平均置信度': 0.0
        })
        
        # 题型映射
        self.题型映射 = {
            'single_choice': '单选题',
            'multiple_choice': '多选题',
            'true_false': '判断题',
            'fill_blank': '填空题',
            'subjective': '简答题',
            'unknown': '未知'
        }
        
        print("🎯 统一识别系统初始化完成")
    
    def 识别题型(self, 
                 题目内容: str, 
                 答案: str, 
                 选项: Dict = None, 
                 识别模式: str = 'auto',
                 详细输出: bool = False) -> Dict[str, Any]:
        """
        统一的题型识别接口
        
        Args:
            题目内容: 题目文本
            答案: 答案文本
            选项: 选项字典
            识别模式: 'auto'(自动), 'fast'(快速), 'accurate'(精确), 'consensus'(共识)
            详细输出: 是否输出详细信息
            
        Returns:
            识别结果字典
        """
        
        开始时间 = time.time()
        
        try:
            if 识别模式 == 'auto':
                结果 = self._自动识别(题目内容, 答案, 选项)
            elif 识别模式 == 'fast':
                结果 = self._快速识别(题目内容, 答案, 选项)
            elif 识别模式 == 'accurate':
                结果 = self._精确识别(题目内容, 答案, 选项)
            elif 识别模式 == 'consensus':
                结果 = self._共识识别(题目内容, 答案, 选项)
            else:
                结果 = self._自动识别(题目内容, 答案, 选项)
            
            结束时间 = time.time()
            耗时 = 结束时间 - 开始时间
            
            # 更新统计
            self.性能统计[识别模式]['调用次数'] += 1
            self.性能统计[识别模式]['成功次数'] += 1
            self.性能统计[识别模式]['平均耗时'] = (
                (self.性能统计[识别模式]['平均耗时'] * (self.性能统计[识别模式]['成功次数'] - 1) + 耗时) 
                / self.性能统计[识别模式]['成功次数']
            )
            self.性能统计[识别模式]['平均置信度'] = (
                (self.性能统计[识别模式]['平均置信度'] * (self.性能统计[识别模式]['成功次数'] - 1) + 结果.get('confidence', 0)) 
                / self.性能统计[识别模式]['成功次数']
            )
            
            # 记录历史
            识别记录 = {
                'timestamp': datetime.now().isoformat(),
                'mode': 识别模式,
                'question': 题目内容[:100],
                'answer': 答案,
                'options': 选项,
                'result': 结果,
                'time_cost': 耗时
            }
            self.识别历史.append(识别记录)
            
            if 详细输出:
                print(f"🎯 {识别模式}模式: {结果.get('question_type', '未知')} (置信度: {结果.get('confidence', 0):.2f}, 耗时: {耗时:.4f}s)")
            
            return 结果
            
        except Exception as e:
            结束时间 = time.time()
            耗时 = 结束时间 - 开始时间
            
            if 详细输出:
                print(f"❌ 识别失败: {e}")
            
            return {
                'success': False,
                'question_type': '未知',
                'confidence': 0.0,
                'error': str(e),
                'time_cost': 耗时
            }
    
    def _自动识别(self, 题目内容: str, 答案: str, 选项: Dict) -> Dict[str, Any]:
        """自动识别 - 根据题目特征选择最佳策略"""
        
        # 根据题目特征选择识别策略
        if len(题目内容) < 20:
            # 短题目，使用快速识别
            return self._快速识别(题目内容, 答案, 选项)
        elif 选项 and len(选项) >= 2:
            # 有选项的题目，使用精确识别
            return self._精确识别(题目内容, 答案, 选项)
        elif '判断' in 题目内容 or 答案 in ['对', '错', '√', '×', '正确', '错误']:
            # 判断题，使用精确识别
            return self._精确识别(题目内容, 答案, 选项)
        else:
            # 其他情况使用快速识别
            return self._快速识别(题目内容, 答案, 选项)
    
    def _快速识别(self, 题目内容: str, 答案: str, 选项: Dict) -> Dict[str, Any]:
        """快速识别 - 基于关键词和答案格式"""
        
        题目文本 = 题目内容.lower()
        答案文本 = 答案.upper().strip()
        
        # 1. 判断题识别（优先级最高）
        判断题答案集 = {'对', '错', '√', '×', 'T', 'F', 'TRUE', 'FALSE', '正确', '错误', '是', '否'}
        if 答案文本 in 判断题答案集:
            return {
                'success': True,
                'question_type': '判断题',
                'confidence': 0.95,
                'method': '答案格式识别'
            }
        
        # 检查判断题关键词
        判断题关键词 = ['是否正确', '对吗', '对么', '错吗', '判断', '说法', '表述', '观点']
        if any(词 in 题目文本 for 词 in 判断题关键词):
            return {
                'success': True,
                'question_type': '判断题',
                'confidence': 0.85,
                'method': '关键词识别'
            }
        
        # 2. 选择题识别
        if 选项 and len(选项) >= 2:
            # 检查是否为判断题（两个选项且为对错类型）
            if len(选项) == 2:
                选项值 = [v.strip() for v in 选项.values()]
                if ('正确' in 选项值 and '错误' in 选项值) or ('对' in 选项值 and '错' in 选项值):
                    return {
                        'success': True,
                        'question_type': '判断题',
                        'confidence': 0.90,
                        'method': '选项内容识别'
                    }
            
            # 多选题识别
            多选关键词 = ['多选', '多项', '哪些', '哪几个', '包括', '正确的有', '错误的有']
            if any(词 in 题目文本 for 词 in 多选关键词):
                return {
                    'success': True,
                    'question_type': '多选题',
                    'confidence': 0.90,
                    'method': '关键词识别'
                }
            
            # 检查答案格式
            if len(答案文本) > 1 and all(c in 'ABCDEFGHIJ' for c in 答案文本):
                return {
                    'success': True,
                    'question_type': '多选题',
                    'confidence': 0.85,
                    'method': '答案格式识别'
                }
            
            # 默认为单选题
            return {
                'success': True,
                'question_type': '单选题',
                'confidence': 0.80,
                'method': '默认识别'
            }
        
        # 3. 填空题识别
        填空标记 = ['_', '____', '（）', '()', '【】', '[]']
        if any(标记 in 题目内容 for 标记 in 填空标记):
            return {
                'success': True,
                'question_type': '填空题',
                'confidence': 0.90,
                'method': '填空标记识别'
            }
        
        # 检查填空题关键词
        填空关键词 = ['等于', '约为', '标准', '规定', '要求', '必须', '应该']
        if any(词 in 题目文本 for 词 in 填空关键词):
            return {
                'success': True,
                'question_type': '填空题',
                'confidence': 0.75,
                'method': '关键词识别'
            }
        
        # 4. 简答题识别
        简答关键词 = ['简述', '说明', '论述', '分析', '阐述', '解释', '描述', '如何', '为什么', '什么是']
        if any(词 in 题目文本 for 词 in 简答关键词):
            return {
                'success': True,
                'question_type': '简答题',
                'confidence': 0.85,
                'method': '关键词识别'
            }
        
        # 检查答案长度
        if len(答案) > 20:
            return {
                'success': True,
                'question_type': '简答题',
                'confidence': 0.70,
                'method': '答案长度识别'
            }
        
        # 5. 默认情况
        return {
            'success': True,
            'question_type': '未知',
            'confidence': 0.50,
            'method': '默认识别'
        }
    
    def _精确识别(self, 题目内容: str, 答案: str, 选项: Dict) -> Dict[str, Any]:
        """精确识别 - 使用更复杂的规则和特征"""
        
        题目文本 = 题目内容.lower()
        答案文本 = 答案.upper().strip()
        
        # 为每种题型计算得分
        题型得分 = {}
        
        # 1. 单选题得分计算
        单选得分 = 0
        if 选项 and len(选项) >= 2:
            单选得分 += 30  # 有选项基础分
        
        if len(答案文本) == 1 and 答案文本 in 'ABCDEFGHIJ':
            单选得分 += 40  # 单字母答案
        
        单选关键词 = ['单选', '单项选择', '哪个', '哪项', '最', '正确的是', '错误的是']
        if any(词 in 题目文本 for 词 in 单选关键词):
            单选得分 += 30  # 单选关键词
        
        if 选项 and 3 <= len(选项) <= 6:
            单选得分 += 20  # 选项数量合适
        
        题型得分['单选题'] = 单选得分
        
        # 2. 多选题得分计算
        多选得分 = 0
        if 选项 and len(选项) >= 2:
            多选得分 += 30  # 有选项基础分
        
        if len(答案文本) > 1 and all(c in 'ABCDEFGHIJ' for c in 答案文本):
            多选得分 += 40  # 多字母答案
        
        多选关键词 = ['多选', '多项', '哪些', '哪几个', '包括', '正确的有', '错误的有']
        if any(词 in 题目文本 for 词 in 多选关键词):
            多选得分 += 30  # 多选关键词
        
        if 选项 and len(选项) >= 4:
            多选得分 += 20  # 选项数量较多
        
        题型得分['多选题'] = 多选得分
        
        # 3. 判断题得分计算
        判断得分 = 0
        
        # 检查题目末尾的判断符号
        if re.search(r'\([√×✓✗对错]\)$', 题目内容.strip()):
            判断得分 += 50  # 判断符号
        
        # 检查二选一选项
        if 选项 and len(选项) == 2:
            选项值 = [v.strip() for v in 选项.values()]
            if ('正确' in 选项值 and '错误' in 选项值) or ('对' in 选项值 and '错' in 选项值):
                判断得分 += 40  # 二选一选项
        
        # 检查判断题答案格式
        判断题答案集 = {'对', '错', '√', '×', 'T', 'F', 'TRUE', 'FALSE', '正确', '错误', '是', '否'}
        if 答案文本 in 判断题答案集:
            判断得分 += 30  # 判断答案格式
        
        # 检查判断关键词
        判断关键词 = ['是否正确', '对吗', '对么', '判断', '说法', '表述', '观点', '是否准确', '是否', '对不对']
        if any(词 in 题目文本 for 词 in 判断关键词):
            判断得分 += 25  # 判断关键词
        
        题型得分['判断题'] = 判断得分
        
        # 4. 填空题得分计算
        填空得分 = 0
        
        # 检查填空标记
        填空模式 = [r'_{2,}', r'（\s*）', r'\(\s*\)', r'【\s*】']
        if any(re.search(模式, 题目内容) for 模式 in 填空模式):
            填空得分 += 40  # 填空标记
        
        # 检查数值答案
        if re.search(r'\d+', 答案文本):
            填空得分 += 30  # 数值答案
        
        # 检查单位答案
        单位列表 = ['MPa', 'KV', 'A', 'V', 'HZ', '年', '月', '日', '米', '克', '升', '度', '℃']
        if any(单位 in 答案文本 for 单位 in 单位列表):
            填空得分 += 25  # 单位答案
        
        # 检查填空关键词
        填空关键词 = ['填写', '填入', '应填', '等于', '约为', '标准', '规定']
        if any(词 in 题目文本 for 词 in 填空关键词):
            填空得分 += 20  # 填空关键词
        
        题型得分['填空题'] = 填空得分
        
        # 5. 简答题得分计算
        简答得分 = 0
        
        # 检查长答案
        if len(答案文本) > 15:
            简答得分 += 30  # 长答案
            if len(答案文本) > 30:
                简答得分 += 20  # 更长答案
        
        # 检查简答关键词
        简答关键词 = ['简述', '说明', '论述', '分析', '阐述', '解释', '描述', '如何', '为什么', '什么是', '怎样', '请', '试', '谈谈']
        关键词匹配数 = sum(1 for 词 in 简答关键词 if 词 in 题目文本)
        if 关键词匹配数 > 0:
            简答得分 += 25  # 简答关键词
            简答得分 += 关键词匹配数 * 5  # 匹配的关键词越多得分越高
        
        # 检查复杂内容结构
        if len(题目内容) > 30:
            简答得分 += 15  # 复杂内容
        
        # 检查无选项
        if not 选项 or len(选项) == 0:
            简答得分 += 20  # 无选项
        
        # 检查答案的复杂性
        if any(标点 in 答案文本 for 标点 in ['。', '，', '；', '：', '、']):
            简答得分 += 15  # 复杂答案
        
        题型得分['简答题'] = 简答得分
        
        # 找到得分最高的题型
        最佳题型 = max(题型得分, key=题型得分.get)
        最高得分 = 题型得分[最佳题型]
        
        # 计算置信度
        置信度 = min(最高得分 / 100.0, 1.0)
        
        return {
            'success': True,
            'question_type': 最佳题型,
            'confidence': 置信度,
            'method': '精确识别',
            'scores': 题型得分
        }
    
    def _共识识别(self, 题目内容: str, 答案: str, 选项: Dict) -> Dict[str, Any]:
        """共识识别 - 多种方法投票"""
        
        # 使用多种方法识别
        快速结果 = self._快速识别(题目内容, 答案, 选项)
        精确结果 = self._精确识别(题目内容, 答案, 选项)
        
        # 收集结果
        结果列表 = [快速结果, 精确结果]
        
        # 统计各题型的得票数
        投票统计 = defaultdict(lambda: {'votes': 0, 'confidence_sum': 0})
        
        for 结果 in 结果列表:
            if 结果.get('success', False):
                题型 = 结果.get('question_type', '未知')
                置信度 = 结果.get('confidence', 0)
                
                投票统计[题型]['votes'] += 1
                投票统计[题型]['confidence_sum'] += 置信度
        
        if 投票统计:
            # 选择得票最多的题型
            共识题型 = max(投票统计.items(), key=lambda x: x[1]['votes'])
            题型名, 统计数据 = 共识题型
            
            平均置信度 = 统计数据['confidence_sum'] / 统计数据['votes']
            
            return {
                'success': True,
                'question_type': 题型名,
                'confidence': 平均置信度,
                'method': '共识识别',
                'votes': 统计数据['votes'],
                'all_results': 结果列表
            }
        else:
            return {
                'success': False,
                'question_type': '未知',
                'confidence': 0.0,
                'method': '共识识别',
                'error': '无法达成共识'
            }
    
    def 获取性能统计(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        return {
            'performance_stats': dict(self.性能统计),
            'total_calls': sum(stat['调用次数'] for stat in self.性能统计.values()),
            'total_success': sum(stat['成功次数'] for stat in self.性能统计.values()),
            'recognition_history_count': len(self.识别历史)
        }
    
    def 重置统计(self):
        """重置性能统计"""
        self.性能统计.clear()
        self.识别历史.clear()
        print("🔄 性能统计已重置")

# 创建全局实例
统一识别器 = 统一识别系统()

def detect_question_type(question: str, answer: str, options: Dict = None) -> str:
    """
    统一题型识别接口 - 简化版本
    
    Args:
        question: 题目内容
        answer: 答案内容
        options: 选项字典
        
    Returns:
        题型名称
    """
    result = 统一识别器.识别题型(question, answer, options, 'auto', False)
    return result.get('question_type', '未知')

def detect_question_type_with_confidence(question: str, answer: str, options: Dict = None) -> Tuple[str, float]:
    """
    统一题型识别接口 - 带置信度版本
    
    Args:
        question: 题目内容
        answer: 答案内容
        options: 选项字典
        
    Returns:
        (题型名称, 置信度)
    """
    result = 统一识别器.识别题型(question, answer, options, 'auto', False)
    return result.get('question_type', '未知'), result.get('confidence', 0.0)

def detect_question_type_detailed(question: str, answer: str, options: Dict = None, mode: str = 'auto') -> Dict[str, Any]:
    """
    统一题型识别接口 - 详细版本
    
    Args:
        question: 题目内容
        answer: 答案内容
        options: 选项字典
        mode: 识别模式
        
    Returns:
        详细识别结果
    """
    return 统一识别器.识别题型(question, answer, options, mode, True)

def get_recognition_performance() -> Dict[str, Any]:
    """获取识别性能统计"""
    return 统一识别器.获取性能统计()

def reset_recognition_stats():
    """重置识别统计"""
    统一识别器.重置统计()

def main():
    """测试主函数"""
    print("🚀 统一识别系统测试")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        {
            'name': '单选题测试',
            'question': '下列哪个是正确的安全措施？',
            'answer': 'A',
            'options': {'A': '停电', 'B': '验电', 'C': '装设接地线', 'D': '以上都是'}
        },
        {
            'name': '多选题测试',
            'question': '电力安全工作的技术措施包括哪些？',
            'answer': 'ABC',
            'options': {'A': '停电', 'B': '验电', 'C': '装设接地线', 'D': '悬挂标示牌'}
        },
        {
            'name': '判断题测试',
            'question': '装设接地线可以单人进行。',
            'answer': '错',
            'options': {}
        },
        {
            'name': '填空题测试',
            'question': '电力安全工作规程规定，停电时间应不少于____分钟。',
            'answer': '30',
            'options': {}
        },
        {
            'name': '简答题测试',
            'question': '简述电力安全工作的基本要求。',
            'answer': '电力安全工作的基本要求包括：1.严格执行安全规程；2.做好安全防护；3.加强安全监护；4.及时处理安全隐患。',
            'options': {}
        }
    ]
    
    # 测试不同模式
    modes = ['auto', 'fast', 'accurate', 'consensus']
    
    for mode in modes:
        print(f"\n🔧 测试模式: {mode}")
        print("-" * 30)
        
        for case in test_cases:
            print(f"\n📝 {case['name']}")
            result = detect_question_type_detailed(
                case['question'], 
                case['answer'], 
                case['options'], 
                mode
            )
            
            if result.get('success', False):
                print(f"✅ 识别成功: {result.get('question_type', '未知')}")
                print(f"📊 置信度: {result.get('confidence', 0):.2f}")
            else:
                print(f"❌ 识别失败: {result.get('error', '未知错误')}")
    
    # 显示性能统计
    print(f"\n📊 性能统计:")
    print("-" * 30)
    stats = get_recognition_performance()
    for mode, data in stats['performance_stats'].items():
        if data['调用次数'] > 0:
            success_rate = data['成功次数'] / data['调用次数']
            print(f"{mode}: 成功率 {success_rate:.1%}, 平均耗时 {data['平均耗时']:.4f}s")

if __name__ == "__main__":
    main()
