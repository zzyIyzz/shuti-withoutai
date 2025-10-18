#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双系统题型识别器 - 统一接口
支持原始识别系统和智能重构系统两种模式
提供最佳的题型识别体验
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import json
import time

class DualSystemRecognizer:
    """双系统题型识别器"""
    
    def __init__(self):
        """初始化双系统"""
        self.systems = {
            'original': None,    # 原始识别系统
            'rebuilder': None,   # 重构器系统
            'enhanced': None     # 增强识别系统
        }
        
        self.performance_stats = {
            'original': {'success_rate': 0.0, 'avg_confidence': 0.0, 'speed': 0.0},
            'rebuilder': {'success_rate': 0.0, 'avg_confidence': 0.0, 'speed': 0.0},
            'enhanced': {'success_rate': 0.0, 'avg_confidence': 0.0, 'speed': 0.0}
        }
        
        self._load_systems()
    
    def _load_systems(self):
        """加载各个识别系统"""
        try:
            # 加载原始识别系统
            sys.path.insert(0, str(Path(__file__).parent / "question-recog"))
            
            # 直接导入main模块
            import importlib.util
            main_spec = importlib.util.spec_from_file_location(
                "main", Path(__file__).parent / "question-recog" / "main.py"
            )
            main_module = importlib.util.module_from_spec(main_spec)
            main_spec.loader.exec_module(main_module)
            self.systems['original'] = main_module.enhanced_question_classifier
            
            # 加载重构器系统
            rebuilder_spec = importlib.util.spec_from_file_location(
                "rebuilder", Path(__file__).parent / "question-recog" / "智能题目重构器.py"
            )
            rebuilder_module = importlib.util.module_from_spec(rebuilder_spec)
            rebuilder_spec.loader.exec_module(rebuilder_module)
            self.systems['rebuilder'] = rebuilder_module.QuestionRebuilder()
            
            # 加载增强识别系统
            enhanced_spec = importlib.util.spec_from_file_location(
                "enhanced", Path(__file__).parent / "高精度题型识别.py"
            )
            enhanced_module = importlib.util.module_from_spec(enhanced_spec)
            enhanced_spec.loader.exec_module(enhanced_module)
            self.systems['enhanced'] = enhanced_module.detect_question_type_fixed
            
            print("✅ 双系统加载成功")
            
        except Exception as e:
            print(f"⚠️ 系统加载警告: {e}")
    
    def detect_question_type(self, 
                           question_text: str, 
                           answer: str, 
                           options: List[str] = None, 
                           excel_type: str = None,
                           mode: str = 'auto') -> Tuple[str, float, Dict[str, Any]]:
        """
        统一的题型识别接口
        
        Args:
            question_text: 题目文本
            answer: 答案
            options: 选项列表
            excel_type: Excel中的题型标记
            mode: 识别模式 ('auto', 'original', 'rebuilder', 'enhanced', 'consensus')
        
        Returns:
            (题型, 置信度, 详细信息)
        """
        
        if mode == 'auto':
            return self._auto_select_best_system(question_text, answer, options, excel_type)
        elif mode == 'consensus':
            return self._consensus_recognition(question_text, answer, options, excel_type)
        else:
            return self._single_system_recognition(question_text, answer, options, excel_type, mode)
    
    def _auto_select_best_system(self, question_text: str, answer: str, options: List[str], excel_type: str) -> Tuple[str, float, Dict[str, Any]]:
        """自动选择最佳系统"""
        
        # 根据题目特征选择最适合的系统
        if len(question_text) < 20:
            # 短题目，可能需要重构
            return self._use_rebuilder_system(question_text, answer, options, excel_type)
        elif options and len(options) >= 2:
            # 有选项的题目，使用增强系统
            return self._use_enhanced_system(question_text, answer, options, excel_type)
        else:
            # 其他情况使用原始系统
            return self._use_original_system(question_text, answer, options, excel_type)
    
    def _consensus_recognition(self, question_text: str, answer: str, options: List[str], excel_type: str) -> Tuple[str, float, Dict[str, Any]]:
        """共识识别 - 多系统投票"""
        
        results = {}
        
        # 获取各系统的识别结果
        try:
            results['original'] = self._use_original_system(question_text, answer, options, excel_type)
        except:
            results['original'] = ('unknown', 0.0, {})
        
        try:
            results['enhanced'] = self._use_enhanced_system(question_text, answer, options, excel_type)
        except:
            results['enhanced'] = ('unknown', 0.0, {})
        
        # 分析共识
        predictions = [r[0] for r in results.values() if r[0] != 'unknown']
        confidences = [r[1] for r in results.values() if r[0] != 'unknown']
        
        if not predictions:
            return 'unknown', 0.0, {'method': 'consensus', 'systems': results}
        
        # 投票决定
        from collections import Counter
        vote_counts = Counter(predictions)
        most_common = vote_counts.most_common(1)[0]
        
        if most_common[1] > 1:  # 有共识
            consensus_type = most_common[0]
            # 计算该类型的平均置信度
            consensus_confidence = sum(r[1] for r in results.values() if r[0] == consensus_type) / most_common[1]
        else:  # 无共识，选择置信度最高的
            best_result = max(results.values(), key=lambda x: x[1])
            consensus_type = best_result[0]
            consensus_confidence = best_result[1] * 0.8  # 降低置信度
        
        return consensus_type, consensus_confidence, {
            'method': 'consensus',
            'systems': results,
            'vote_counts': dict(vote_counts)
        }
    
    def _use_original_system(self, question_text: str, answer: str, options: List[str], excel_type: str) -> Tuple[str, float, Dict[str, Any]]:
        """使用原始系统"""
        start_time = time.time()
        
        if self.systems['original']:
            q_type, confidence = self.systems['original'](question_text, options or [], answer, excel_type)
            processing_time = time.time() - start_time
            
            return q_type, confidence, {
                'method': 'original',
                'processing_time': processing_time,
                'system': 'question-recog/main.py'
            }
        else:
            return 'unknown', 0.0, {'method': 'original', 'error': 'system_not_loaded'}
    
    def _use_enhanced_system(self, question_text: str, answer: str, options: List[str], excel_type: str) -> Tuple[str, float, Dict[str, Any]]:
        """使用增强系统"""
        start_time = time.time()
        
        if self.systems['enhanced']:
            # 转换选项格式为字典
            options_dict = {}
            if options:
                for i, opt in enumerate(options):
                    key = chr(ord('A') + i)
                    options_dict[key] = opt
            
            # 调用增强系统（返回中文类型名称）
            chinese_type = self.systems['enhanced'](question_text, answer, options_dict)
            
            # 转换为英文类型名称和置信度
            type_mapping = {
                '单选题': ('single_choice', 0.85),
                '多选题': ('multiple_choice', 0.85),
                '判断题': ('true_false', 0.90),
                '填空题': ('fill_blank', 0.80),
                '简答题': ('subjective', 0.75),
                '未知': ('unknown', 0.0)
            }
            
            q_type, confidence = type_mapping.get(chinese_type, ('unknown', 0.0))
            processing_time = time.time() - start_time
            
            return q_type, confidence, {
                'method': 'enhanced',
                'processing_time': processing_time,
                'system': '高精度题型识别.py',
                'chinese_type': chinese_type
            }
        else:
            return 'unknown', 0.0, {'method': 'enhanced', 'error': 'system_not_loaded'}
    
    def _use_rebuilder_system(self, question_text: str, answer: str, options: List[str], excel_type: str) -> Tuple[str, float, Dict[str, Any]]:
        """使用重构器系统"""
        start_time = time.time()
        
        # 对于单个题目，直接使用增强识别
        # 重构器主要用于批量处理Excel文件
        return self._use_enhanced_system(question_text, answer, options, excel_type)
    
    def _single_system_recognition(self, question_text: str, answer: str, options: List[str], excel_type: str, mode: str) -> Tuple[str, float, Dict[str, Any]]:
        """单系统识别"""
        
        if mode == 'original':
            return self._use_original_system(question_text, answer, options, excel_type)
        elif mode == 'enhanced':
            return self._use_enhanced_system(question_text, answer, options, excel_type)
        elif mode == 'rebuilder':
            return self._use_rebuilder_system(question_text, answer, options, excel_type)
        else:
            return 'unknown', 0.0, {'method': mode, 'error': 'invalid_mode'}
    
    def batch_process_excel(self, excel_path: str, mode: str = 'rebuilder', output_path: str = None) -> Dict[str, Any]:
        """批量处理Excel文件"""
        
        if mode == 'rebuilder' and self.systems['rebuilder']:
            # 使用重构器处理
            questions = self.systems['rebuilder'].process_excel_file(excel_path)
            
            # 对重构后的题目进行识别
            results = []
            for i, q in enumerate(questions):
                q_type, confidence, details = self.detect_question_type(
                    q['question'], q['answer'], q['options'], mode='enhanced'
                )
                
                results.append({
                    'id': i + 1,
                    'question': q['question'],
                    'options': q['options'],
                    'answer': q['answer'],
                    'predicted_type': q_type,
                    'confidence': confidence,
                    'quality_score': q.get('quality_score', 0.0),
                    'details': details
                })
            
            # 保存结果
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            
            return {
                'total_questions': len(results),
                'results': results,
                'method': 'rebuilder_batch',
                'source_file': excel_path
            }
        
        else:
            # 使用原始方法处理
            import pandas as pd
            df = pd.read_excel(excel_path)
            
            results = []
            for i, row in df.iterrows():
                question = str(row.get('题目（必填）：', ''))
                answer = str(row.get('正确答案（必填）', ''))
                
                # 提取选项
                options = []
                for opt_col in ['选项A（必填）', '选项B（必填）', '选项C', '选项D']:
                    if opt_col in df.columns and not pd.isna(row[opt_col]):
                        options.append(str(row[opt_col]))
                
                q_type, confidence, details = self.detect_question_type(
                    question, answer, options, mode=mode
                )
                
                results.append({
                    'id': i + 1,
                    'question': question,
                    'options': options,
                    'answer': answer,
                    'predicted_type': q_type,
                    'confidence': confidence,
                    'details': details
                })
            
            # 保存结果
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            
            return {
                'total_questions': len(results),
                'results': results,
                'method': f'{mode}_batch',
                'source_file': excel_path
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'loaded_systems': {k: v is not None for k, v in self.systems.items()},
            'performance_stats': self.performance_stats,
            'available_modes': ['auto', 'original', 'enhanced', 'rebuilder', 'consensus']
        }
    
    def benchmark_systems(self, test_questions: List[Dict]) -> Dict[str, Any]:
        """基准测试各系统性能"""
        
        benchmark_results = {}
        
        for system_name in ['original', 'enhanced']:
            if self.systems.get(system_name.split('_')[0]):
                results = []
                total_time = 0
                
                for q in test_questions:
                    start_time = time.time()
                    q_type, confidence, details = self.detect_question_type(
                        q['question'], q['answer'], q.get('options', []), mode=system_name
                    )
                    processing_time = time.time() - start_time
                    total_time += processing_time
                    
                    results.append({
                        'predicted': q_type,
                        'confidence': confidence,
                        'time': processing_time,
                        'correct': q_type == q.get('expected_type', 'unknown')
                    })
                
                accuracy = sum(1 for r in results if r['correct']) / len(results) if results else 0
                avg_confidence = sum(r['confidence'] for r in results) / len(results) if results else 0
                avg_time = total_time / len(results) if results else 0
                
                benchmark_results[system_name] = {
                    'accuracy': accuracy,
                    'avg_confidence': avg_confidence,
                    'avg_processing_time': avg_time,
                    'total_questions': len(results),
                    'results': results
                }
        
        return benchmark_results

# 全局实例
dual_recognizer = DualSystemRecognizer()

def detect_question_type_dual(question_text: str, 
                             answer: str, 
                             options: List[str] = None, 
                             excel_type: str = None,
                             mode: str = 'auto') -> Tuple[str, float]:
    """
    双系统题型识别的简化接口
    
    Args:
        question_text: 题目文本
        answer: 答案
        options: 选项列表
        excel_type: Excel中的题型标记
        mode: 识别模式
    
    Returns:
        (题型, 置信度)
    """
    q_type, confidence, _ = dual_recognizer.detect_question_type(
        question_text, answer, options, excel_type, mode
    )
    return q_type, confidence

def test_dual_system():
    """测试双系统"""
    print("🧪 双系统测试")
    print("=" * 50)
    
    test_cases = [
        {
            'question': '下列哪个是正确的？',
            'answer': 'A',
            'options': ['A: 选项A', 'B: 选项B', 'C: 选项C', 'D: 选项D'],
            'expected': 'single_choice'
        },
        {
            'question': '以下说法正确的是？',
            'answer': 'ABC',
            'options': ['A: 选项A', 'B: 选项B', 'C: 选项C', 'D: 选项D'],
            'expected': 'multiple_choice'
        },
        {
            'question': '地球是圆的。',
            'answer': '对',
            'options': [],
            'expected': 'true_false'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"  题目: {case['question']}")
        print(f"  答案: {case['answer']}")
        print(f"  选项: {len(case['options'])}个")
        
        # 测试不同模式
        for mode in ['auto', 'original', 'enhanced', 'consensus']:
            try:
                q_type, confidence, details = dual_recognizer.detect_question_type(
                    case['question'], case['answer'], case['options'], mode=mode
                )
                
                correct = "✅" if q_type == case['expected'] else "❌"
                print(f"  {mode:10}: {q_type:15} ({confidence:.2f}) {correct}")
                
            except Exception as e:
                print(f"  {mode:10}: 错误 - {e}")
    
    # 显示系统状态
    status = dual_recognizer.get_system_status()
    print(f"\n📊 系统状态:")
    for system, loaded in status['loaded_systems'].items():
        status_icon = "✅" if loaded else "❌"
        print(f"  {system:10}: {status_icon}")

if __name__ == "__main__":
    test_dual_system()
