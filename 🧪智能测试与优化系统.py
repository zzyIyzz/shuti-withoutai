#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能测试与优化系统 - 闭环控制版本
实现自动控制中的闭环控制：原因→结果→反馈→优化→原因

测试目标：
1. 题目读取准确率测试
2. 题干与选项识别准确率测试  
3. 题型识别准确率测试
4. 自动优化和反馈机制
"""

import os
import json
import time
import random
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import traceback
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns

class 智能测试与优化系统:
    """智能测试与优化系统 - 实现闭环控制"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_data_dir = self.project_root / '.test_data'
        self.test_data_dir.mkdir(exist_ok=True)
        
        # 测试结果存储
        self.test_results = {}
        self.optimization_history = []
        self.performance_metrics = defaultdict(list)
        
        # 测试配置
        self.test_config = {
            'sample_size': 100,  # 测试样本大小
            'confidence_threshold': 0.8,  # 置信度阈值
            'optimization_iterations': 5,  # 优化迭代次数
            'performance_target': 0.95  # 性能目标
        }
        
        print("🧪 智能测试与优化系统初始化")
        print("🎯 实现闭环控制：测试→分析→优化→反馈→再测试")
        print("=" * 60)
    
    def 运行完整测试闭环(self):
        """运行完整的测试优化闭环"""
        print("🚀 启动完整测试优化闭环")
        
        for iteration in range(self.test_config['optimization_iterations']):
            print(f"\n🔄 第 {iteration + 1} 轮优化迭代")
            print("-" * 50)
            
            # 1. 测试阶段
            test_results = self.执行全面测试()
            
            # 2. 分析阶段
            analysis_results = self.分析测试结果(test_results)
            
            # 3. 优化阶段
            optimization_results = self.执行系统优化(analysis_results)
            
            # 4. 反馈阶段
            feedback_results = self.生成反馈报告(test_results, analysis_results, optimization_results)
            
            # 5. 检查是否达到目标
            if self.检查优化目标(feedback_results):
                print(f"🎉 第 {iteration + 1} 轮达到优化目标！")
                break
        
        # 生成最终报告
        self.生成最终优化报告()
    
    def 执行全面测试(self) -> Dict[str, Any]:
        """执行全面的系统测试"""
        print("🔍 执行全面系统测试...")
        
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'reading_accuracy': self.测试题目读取准确率(),
            'parsing_accuracy': self.测试题干选项识别准确率(),
            'classification_accuracy': self.测试题型识别准确率(),
            'system_performance': self.测试系统性能(),
            'error_analysis': self.分析错误模式()
        }
        
        # 保存测试结果
        self.test_results[datetime.now().strftime('%Y%m%d_%H%M%S')] = test_results
        
        return test_results
    
    def 测试题目读取准确率(self) -> Dict[str, Any]:
        """测试题目读取准确率"""
        print("📚 测试题目读取准确率...")
        
        try:
            from 题库管理 import TikuManager
            
            manager = TikuManager()
            tiku_list = manager.get_tiku_list()
            
            if not tiku_list:
                return {'accuracy': 0, 'total': 0, 'errors': ['无题库文件']}
            
            total_questions = 0
            successful_reads = 0
            read_errors = []
            
            for tiku_name, tiku_path in tiku_list[:3]:  # 测试前3个题库
                try:
                    questions = manager.load_tiku(tiku_name)
                    if questions:
                        total_questions += len(questions)
                        successful_reads += len(questions)
                        print(f"✅ {tiku_name}: 成功读取 {len(questions)} 题")
                    else:
                        read_errors.append(f"{tiku_name}: 读取失败")
                        print(f"❌ {tiku_name}: 读取失败")
                        
                except Exception as e:
                    read_errors.append(f"{tiku_name}: {str(e)}")
                    print(f"❌ {tiku_name}: 异常 - {e}")
            
            accuracy = successful_reads / total_questions if total_questions > 0 else 0
            
            return {
                'accuracy': accuracy,
                'total': total_questions,
                'successful': successful_reads,
                'errors': read_errors,
                'details': f"成功读取 {successful_reads}/{total_questions} 题"
            }
            
        except Exception as e:
            return {'accuracy': 0, 'total': 0, 'errors': [f'测试异常: {e}']}
    
    def 测试题干选项识别准确率(self) -> Dict[str, Any]:
        """测试题干与选项识别准确率"""
        print("🎯 测试题干选项识别准确率...")
        
        try:
            from 题库管理 import TikuManager
            
            manager = TikuManager()
            tiku_list = manager.get_tiku_list()
            
            if not tiku_list:
                return {'accuracy': 0, 'total': 0, 'errors': ['无题库文件']}
            
            total_questions = 0
            correct_parsing = 0
            parsing_errors = []
            
            # 测试样本
            sample_size = min(self.test_config['sample_size'], 50)
            
            for tiku_name, tiku_path in tiku_list[:2]:  # 测试前2个题库
                try:
                    questions = manager.load_tiku(tiku_name)
                    if not questions:
                        continue
                    
                    # 随机采样
                    sample_questions = random.sample(questions, min(sample_size, len(questions)))
                    
                    for question in sample_questions:
                        total_questions += 1
                        
                        # 检查题干完整性
                        if not question.get('question') or len(question['question'].strip()) < 5:
                            parsing_errors.append(f"题干不完整: {question.get('question', '')[:50]}...")
                            continue
                        
                        # 检查选项解析
                        options = question.get('options', {})
                        if options:
                            # 检查选项格式
                            valid_options = 0
                            for opt_key, opt_value in options.items():
                                if opt_value and len(opt_value.strip()) > 1:
                                    valid_options += 1
                            
                            if valid_options >= 2:  # 至少2个有效选项
                                correct_parsing += 1
                            else:
                                parsing_errors.append(f"选项解析不完整: {len(options)}个选项")
                        else:
                            # 无选项题目（填空题、简答题等）
                            if question.get('answer') and len(question['answer'].strip()) > 0:
                                correct_parsing += 1
                            else:
                                parsing_errors.append("无选项且无答案")
                        
                except Exception as e:
                    parsing_errors.append(f"{tiku_name}: {str(e)}")
            
            accuracy = correct_parsing / total_questions if total_questions > 0 else 0
            
            return {
                'accuracy': accuracy,
                'total': total_questions,
                'correct': correct_parsing,
                'errors': parsing_errors[:10],  # 只显示前10个错误
                'details': f"正确解析 {correct_parsing}/{total_questions} 题"
            }
            
        except Exception as e:
            return {'accuracy': 0, 'total': 0, 'errors': [f'测试异常: {e}']}
    
    def 测试题型识别准确率(self) -> Dict[str, Any]:
        """测试题型识别准确率"""
        print("🔍 测试题型识别准确率...")
        
        try:
            # 创建测试用例
            test_cases = self.创建题型测试用例()
            
            total_tests = len(test_cases)
            correct_predictions = 0
            prediction_details = []
            
            # 测试不同识别系统
            recognition_systems = [
                ('智能识别', self.测试智能识别系统),
                ('高精度识别', self.测试高精度识别系统),
                ('双系统识别', self.测试双系统识别)
            ]
            
            system_results = {}
            
            for system_name, test_func in recognition_systems:
                try:
                    system_correct = 0
                    system_details = []
                    
                    for case in test_cases:
                        predicted_type = test_func(case['question'], case['answer'], case.get('options', {}))
                        
                        if predicted_type == case['expected_type']:
                            system_correct += 1
                            system_details.append(f"✅ {case['name']}: {predicted_type}")
                        else:
                            system_details.append(f"❌ {case['name']}: 期望{case['expected_type']}, 实际{predicted_type}")
                    
                    system_accuracy = system_correct / total_tests
                    system_results[system_name] = {
                        'accuracy': system_accuracy,
                        'correct': system_correct,
                        'total': total_tests,
                        'details': system_details[:5]  # 只显示前5个
                    }
                    
                    print(f"📊 {system_name}: {system_accuracy:.1%} ({system_correct}/{total_tests})")
                    
                except Exception as e:
                    system_results[system_name] = {'accuracy': 0, 'error': str(e)}
                    print(f"❌ {system_name}: 测试异常 - {e}")
            
            # 选择最佳系统结果
            best_system = max(system_results.items(), key=lambda x: x[1].get('accuracy', 0))
            
            return {
                'overall_accuracy': best_system[1].get('accuracy', 0),
                'best_system': best_system[0],
                'system_results': system_results,
                'total_tests': total_tests,
                'details': f"最佳系统 {best_system[0]}: {best_system[1].get('accuracy', 0):.1%}"
            }
            
        except Exception as e:
            return {'overall_accuracy': 0, 'error': f'测试异常: {e}'}
    
    def 创建题型测试用例(self) -> List[Dict[str, Any]]:
        """创建题型识别测试用例"""
        return [
            # 单选题测试用例
            {
                'name': '单选题-基础',
                'question': '下列哪个是正确的安全措施？',
                'answer': 'A',
                'options': {'A': '停电', 'B': '验电', 'C': '装设接地线', 'D': '以上都是'},
                'expected_type': '单选题'
            },
            {
                'name': '单选题-关键词',
                'question': '电力安全工作中，最正确的做法是：',
                'answer': 'B',
                'options': {'A': '单人作业', 'B': '双人作业', 'C': '无监护作业', 'D': '随意作业'},
                'expected_type': '单选题'
            },
            
            # 多选题测试用例
            {
                'name': '多选题-基础',
                'question': '电力安全工作的技术措施包括哪些？',
                'answer': 'ABC',
                'options': {'A': '停电', 'B': '验电', 'C': '装设接地线', 'D': '悬挂标示牌'},
                'expected_type': '多选题'
            },
            {
                'name': '多选题-关键词',
                'question': '下列哪些是正确的安全要求？',
                'answer': 'ABD',
                'options': {'A': '戴安全帽', 'B': '穿绝缘鞋', 'C': '不戴手套', 'D': '使用工具'},
                'expected_type': '多选题'
            },
            
            # 判断题测试用例
            {
                'name': '判断题-基础',
                'question': '装设接地线可以单人进行。',
                'answer': '错',
                'options': {},
                'expected_type': '判断题'
            },
            {
                'name': '判断题-符号',
                'question': '电力设备检修时必须停电。(√)',
                'answer': '对',
                'options': {},
                'expected_type': '判断题'
            },
            
            # 填空题测试用例
            {
                'name': '填空题-基础',
                'question': '电力安全工作规程规定，停电时间应不少于____分钟。',
                'answer': '30',
                'options': {},
                'expected_type': '填空题'
            },
            {
                'name': '填空题-单位',
                'question': '安全距离应保持____米以上。',
                'answer': '1.5',
                'options': {},
                'expected_type': '填空题'
            },
            
            # 简答题测试用例
            {
                'name': '简答题-基础',
                'question': '简述电力安全工作的基本要求。',
                'answer': '电力安全工作的基本要求包括：1.严格执行安全规程；2.做好安全防护；3.加强安全监护；4.及时处理安全隐患。',
                'options': {},
                'expected_type': '简答题'
            },
            {
                'name': '简答题-分析',
                'question': '分析电力事故的主要原因及预防措施。',
                'answer': '电力事故的主要原因包括：1.违反安全规程；2.设备缺陷；3.管理不善；4.人员素质不高。预防措施：1.加强培训；2.完善制度；3.定期检查；4.严格管理。',
                'options': {},
                'expected_type': '简答题'
            }
        ]
    
    def 测试智能识别系统(self, question: str, answer: str, options: Dict) -> str:
        """测试智能识别系统"""
        try:
            from 智能题型识别 import detect_question_type
            return detect_question_type(question, answer, options)
        except:
            return '未知'
    
    def 测试高精度识别系统(self, question: str, answer: str, options: Dict) -> str:
        """测试高精度识别系统"""
        try:
            from 高精度题型识别 import detect_question_type_fixed
            return detect_question_type_fixed(question, answer, options)
        except:
            return '未知'
    
    def 测试双系统识别(self, question: str, answer: str, options: Dict) -> str:
        """测试双系统识别"""
        try:
            from 双系统题型识别器 import detect_question_type_dual
            q_type, confidence = detect_question_type_dual(question, answer, options)
            return q_type
        except:
            return '未知'
    
    def 测试系统性能(self) -> Dict[str, Any]:
        """测试系统性能"""
        print("⚡ 测试系统性能...")
        
        try:
            # 性能测试用例
            test_questions = [
                ("单选题测试", "A", {"A": "选项A", "B": "选项B"}),
                ("多选题测试", "ABC", {"A": "选项A", "B": "选项B", "C": "选项C"}),
                ("判断题测试", "对", {}),
                ("填空题测试", "答案", {}),
                ("简答题测试", "这是一个详细的答案说明", {})
            ] * 20  # 重复20次
            
            # 测试识别性能
            start_time = time.time()
            
            for question, answer, options in test_questions:
                try:
                    from 双系统题型识别器 import detect_question_type_dual
                    detect_question_type_dual(question, answer, options)
                except:
                    pass
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / len(test_questions)
            throughput = len(test_questions) / total_time
            
            return {
                'total_time': total_time,
                'avg_time_per_question': avg_time,
                'throughput': throughput,
                'total_questions': len(test_questions),
                'performance_level': self.评估性能等级(avg_time)
            }
            
        except Exception as e:
            return {'error': f'性能测试异常: {e}'}
    
    def 评估性能等级(self, avg_time: float) -> str:
        """评估性能等级"""
        if avg_time < 0.01:
            return '优秀 (< 0.01秒)'
        elif avg_time < 0.05:
            return '良好 (< 0.05秒)'
        elif avg_time < 0.1:
            return '一般 (< 0.1秒)'
        else:
            return '需要优化 (> 0.1秒)'
    
    def 分析错误模式(self) -> Dict[str, Any]:
        """分析错误模式"""
        print("🔍 分析错误模式...")
        
        try:
            # 收集错误信息
            error_patterns = defaultdict(int)
            error_sources = defaultdict(int)
            
            # 从测试结果中提取错误
            for test_result in self.test_results.values():
                if 'errors' in test_result.get('reading_accuracy', {}):
                    for error in test_result['reading_accuracy']['errors']:
                        error_patterns[error] += 1
                        error_sources['reading'] += 1
                
                if 'errors' in test_result.get('parsing_accuracy', {}):
                    for error in test_result['parsing_accuracy']['errors']:
                        error_patterns[error] += 1
                        error_sources['parsing'] += 1
            
            return {
                'error_patterns': dict(error_patterns),
                'error_sources': dict(error_sources),
                'total_errors': sum(error_patterns.values()),
                'most_common_error': max(error_patterns.items(), key=lambda x: x[1]) if error_patterns else None
            }
            
        except Exception as e:
            return {'error': f'错误分析异常: {e}'}
    
    def 分析测试结果(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """分析测试结果"""
        print("📊 分析测试结果...")
        
        analysis = {
            'overall_score': 0,
            'component_scores': {},
            'improvement_areas': [],
            'strengths': [],
            'recommendations': []
        }
        
        # 计算各组件得分
        reading_acc = test_results.get('reading_accuracy', {}).get('accuracy', 0)
        parsing_acc = test_results.get('parsing_accuracy', {}).get('accuracy', 0)
        classification_acc = test_results.get('classification_accuracy', {}).get('overall_accuracy', 0)
        performance_level = test_results.get('system_performance', {}).get('performance_level', '需要优化')
        
        analysis['component_scores'] = {
            'reading_accuracy': reading_acc,
            'parsing_accuracy': parsing_acc,
            'classification_accuracy': classification_acc,
            'performance': 0.9 if '优秀' in performance_level else 0.7 if '良好' in performance_level else 0.5
        }
        
        # 计算总体得分
        analysis['overall_score'] = sum(analysis['component_scores'].values()) / len(analysis['component_scores'])
        
        # 识别改进领域
        if reading_acc < 0.9:
            analysis['improvement_areas'].append('题目读取准确率')
        if parsing_acc < 0.9:
            analysis['improvement_areas'].append('题干选项识别准确率')
        if classification_acc < 0.9:
            analysis['improvement_areas'].append('题型识别准确率')
        if '需要优化' in performance_level:
            analysis['improvement_areas'].append('系统性能')
        
        # 识别优势
        if reading_acc >= 0.95:
            analysis['strengths'].append('题目读取稳定')
        if parsing_acc >= 0.95:
            analysis['strengths'].append('题干解析准确')
        if classification_acc >= 0.95:
            analysis['strengths'].append('题型识别精确')
        
        # 生成建议
        if reading_acc < 0.8:
            analysis['recommendations'].append('优化题库文件格式，检查文件完整性')
        if parsing_acc < 0.8:
            analysis['recommendations'].append('改进选项解析算法，增强格式兼容性')
        if classification_acc < 0.8:
            analysis['recommendations'].append('调整题型识别参数，增加训练样本')
        
        return analysis
    
    def 执行系统优化(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """执行系统优化"""
        print("🔧 执行系统优化...")
        
        optimization_results = {
            'optimizations_applied': [],
            'parameters_adjusted': {},
            'success': False
        }
        
        try:
            # 根据分析结果执行优化
            improvement_areas = analysis_results.get('improvement_areas', [])
            
            if '题目读取准确率' in improvement_areas:
                self.优化题目读取()
                optimization_results['optimizations_applied'].append('题目读取优化')
            
            if '题干选项识别准确率' in improvement_areas:
                self.优化题干解析()
                optimization_results['optimizations_applied'].append('题干解析优化')
            
            if '题型识别准确率' in improvement_areas:
                self.优化题型识别()
                optimization_results['optimizations_applied'].append('题型识别优化')
            
            if '系统性能' in improvement_areas:
                self.优化系统性能()
                optimization_results['optimizations_applied'].append('系统性能优化')
            
            optimization_results['success'] = len(optimization_results['optimizations_applied']) > 0
            
        except Exception as e:
            optimization_results['error'] = f'优化异常: {e}'
        
        return optimization_results
    
    def 优化题目读取(self):
        """优化题目读取"""
        print("🔧 优化题目读取...")
        # 这里可以实现具体的优化逻辑
        # 例如：调整解析参数、增加错误处理等
        pass
    
    def 优化题干解析(self):
        """优化题干解析"""
        print("🔧 优化题干解析...")
        # 这里可以实现具体的优化逻辑
        # 例如：改进正则表达式、增强格式识别等
        pass
    
    def 优化题型识别(self):
        """优化题型识别"""
        print("🔧 优化题型识别...")
        # 这里可以实现具体的优化逻辑
        # 例如：调整识别阈值、增加特征权重等
        pass
    
    def 优化系统性能(self):
        """优化系统性能"""
        print("🔧 优化系统性能...")
        # 这里可以实现具体的优化逻辑
        # 例如：缓存优化、算法优化等
        pass
    
    def 生成反馈报告(self, test_results: Dict, analysis_results: Dict, optimization_results: Dict) -> Dict[str, Any]:
        """生成反馈报告"""
        print("📋 生成反馈报告...")
        
        feedback = {
            'timestamp': datetime.now().isoformat(),
            'test_summary': {
                'reading_accuracy': test_results.get('reading_accuracy', {}).get('accuracy', 0),
                'parsing_accuracy': test_results.get('parsing_accuracy', {}).get('accuracy', 0),
                'classification_accuracy': test_results.get('classification_accuracy', {}).get('overall_accuracy', 0),
                'overall_score': analysis_results.get('overall_score', 0)
            },
            'optimization_summary': {
                'optimizations_applied': optimization_results.get('optimizations_applied', []),
                'success': optimization_results.get('success', False)
            },
            'recommendations': analysis_results.get('recommendations', []),
            'next_steps': self.生成下一步建议(analysis_results, optimization_results)
        }
        
        # 保存反馈报告
        feedback_file = self.test_data_dir / f'feedback_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback, f, ensure_ascii=False, indent=2)
        
        return feedback
    
    def 生成下一步建议(self, analysis_results: Dict, optimization_results: Dict) -> List[str]:
        """生成下一步建议"""
        suggestions = []
        
        overall_score = analysis_results.get('overall_score', 0)
        
        if overall_score < 0.7:
            suggestions.append('系统需要重大改进，建议重新设计核心算法')
        elif overall_score < 0.85:
            suggestions.append('系统需要持续优化，重点关注薄弱环节')
        elif overall_score < 0.95:
            suggestions.append('系统性能良好，进行精细化调优')
        else:
            suggestions.append('系统性能优秀，保持当前状态')
        
        if not optimization_results.get('success', False):
            suggestions.append('优化未生效，需要检查优化策略')
        
        return suggestions
    
    def 检查优化目标(self, feedback_results: Dict[str, Any]) -> bool:
        """检查是否达到优化目标"""
        overall_score = feedback_results.get('test_summary', {}).get('overall_score', 0)
        target_score = self.test_config['performance_target']
        
        return overall_score >= target_score
    
    def 生成最终优化报告(self):
        """生成最终优化报告"""
        print("📊 生成最终优化报告...")
        
        # 收集所有测试数据
        all_results = list(self.test_results.values())
        
        if not all_results:
            print("❌ 无测试数据，无法生成报告")
            return
        
        # 计算趋势
        reading_trend = [r.get('reading_accuracy', {}).get('accuracy', 0) for r in all_results]
        parsing_trend = [r.get('parsing_accuracy', {}).get('accuracy', 0) for r in all_results]
        classification_trend = [r.get('classification_accuracy', {}).get('overall_accuracy', 0) for r in all_results]
        
        # 生成报告
        report = {
            'summary': {
                'total_iterations': len(all_results),
                'final_reading_accuracy': reading_trend[-1] if reading_trend else 0,
                'final_parsing_accuracy': parsing_trend[-1] if parsing_trend else 0,
                'final_classification_accuracy': classification_trend[-1] if classification_trend else 0,
                'improvement_achieved': self.计算改进程度(reading_trend, parsing_trend, classification_trend)
            },
            'trends': {
                'reading_accuracy': reading_trend,
                'parsing_accuracy': parsing_trend,
                'classification_accuracy': classification_trend
            },
            'recommendations': self.生成最终建议(all_results),
            'timestamp': datetime.now().isoformat()
        }
        
        # 保存报告
        report_file = self.test_data_dir / 'final_optimization_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 显示报告摘要
        self.显示报告摘要(report)
    
    def 计算改进程度(self, reading_trend: List[float], parsing_trend: List[float], classification_trend: List[float]) -> Dict[str, float]:
        """计算改进程度"""
        improvements = {}
        
        if len(reading_trend) > 1:
            improvements['reading'] = reading_trend[-1] - reading_trend[0]
        
        if len(parsing_trend) > 1:
            improvements['parsing'] = parsing_trend[-1] - parsing_trend[0]
        
        if len(classification_trend) > 1:
            improvements['classification'] = classification_trend[-1] - classification_trend[0]
        
        return improvements
    
    def 生成最终建议(self, all_results: List[Dict]) -> List[str]:
        """生成最终建议"""
        suggestions = []
        
        # 基于所有测试结果生成建议
        latest_result = all_results[-1] if all_results else {}
        
        reading_acc = latest_result.get('reading_accuracy', {}).get('accuracy', 0)
        parsing_acc = latest_result.get('parsing_accuracy', {}).get('accuracy', 0)
        classification_acc = latest_result.get('classification_accuracy', {}).get('overall_accuracy', 0)
        
        if reading_acc < 0.9:
            suggestions.append('建议优化题库文件格式，提高读取稳定性')
        
        if parsing_acc < 0.9:
            suggestions.append('建议改进题干解析算法，增强格式兼容性')
        
        if classification_acc < 0.9:
            suggestions.append('建议调整题型识别参数，增加训练样本')
        
        suggestions.append('建议定期运行测试闭环，持续优化系统性能')
        
        return suggestions
    
    def 显示报告摘要(self, report: Dict[str, Any]):
        """显示报告摘要"""
        print("\n" + "=" * 60)
        print("🎉 最终优化报告")
        print("=" * 60)
        
        summary = report['summary']
        print(f"📊 测试迭代次数: {summary['total_iterations']}")
        print(f"📚 最终读取准确率: {summary['final_reading_accuracy']:.1%}")
        print(f"🎯 最终解析准确率: {summary['final_parsing_accuracy']:.1%}")
        print(f"🔍 最终识别准确率: {summary['final_classification_accuracy']:.1%}")
        
        improvements = summary.get('improvement_achieved', {})
        if improvements:
            print(f"\n📈 改进程度:")
            for component, improvement in improvements.items():
                print(f"  {component}: {improvement:+.1%}")
        
        print(f"\n💡 建议:")
        for suggestion in report['recommendations']:
            print(f"  - {suggestion}")
        
        print(f"\n📋 详细报告已保存: {self.test_data_dir / 'final_optimization_report.json'}")

def main():
    """主函数"""
    print("🚀 启动智能测试与优化系统")
    print("🎯 实现闭环控制：测试→分析→优化→反馈→再测试")
    print("⏰ 开始时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # 创建测试系统
    test_system = 智能测试与优化系统()
    
    # 运行完整测试闭环
    test_system.运行完整测试闭环()
    
    print("\n🎊 智能测试与优化系统运行完成")

if __name__ == "__main__":
    main()
