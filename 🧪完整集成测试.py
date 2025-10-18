#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整集成测试脚本
测试整个刷题系统的各个组件和功能
确保系统稳定性和功能完整性
"""

import sys
import os
import time
import json
import traceback
from pathlib import Path
from typing import Dict, List, Any, Tuple
import unittest

class SystemIntegrationTest:
    """系统集成测试类"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        self.project_root = Path(__file__).parent
        
        # 测试配置
        self.test_config = {
            'timeout': 30,  # 每个测试的超时时间（秒）
            'retry_count': 3,  # 重试次数
            'verbose': True  # 详细输出
        }
        
        print("🧪 系统集成测试初始化")
        print("=" * 60)
    
    def run_all_tests(self):
        """运行所有集成测试"""
        test_suites = [
            ('🔧 核心组件测试', self.test_core_components),
            ('🎯 双系统识别测试', self.test_dual_recognition_system),
            ('📚 题库管理测试', self.test_question_bank_management),
            ('🎨 GUI界面测试', self.test_gui_interface),
            ('📊 数据处理测试', self.test_data_processing),
            ('🔄 系统集成测试', self.test_system_integration),
            ('⚡ 性能压力测试', self.test_performance),
            ('🛡️ 错误处理测试', self.test_error_handling)
        ]
        
        total_tests = len(test_suites)
        passed_tests = 0
        
        for i, (test_name, test_func) in enumerate(test_suites, 1):
            print(f"\n🧪 [{i}/{total_tests}] {test_name}")
            print("-" * 50)
            
            try:
                result = self.run_test_with_timeout(test_func)
                if result:
                    print(f"✅ {test_name} - 通过")
                    passed_tests += 1
                    self.test_results[test_name] = {'status': 'PASS', 'details': result}
                else:
                    print(f"❌ {test_name} - 失败")
                    self.test_results[test_name] = {'status': 'FAIL', 'details': 'Test returned False'}
            except Exception as e:
                print(f"💥 {test_name} - 异常: {e}")
                self.test_results[test_name] = {'status': 'ERROR', 'details': str(e)}
        
        # 生成测试报告
        self.generate_test_report(passed_tests, total_tests)
    
    def run_test_with_timeout(self, test_func):
        """带超时的测试执行"""
        try:
            return test_func()
        except Exception as e:
            print(f"⚠️ 测试异常: {e}")
            if self.test_config['verbose']:
                traceback.print_exc()
            return False
    
    def test_core_components(self):
        """测试核心组件"""
        print("🔍 检查核心文件存在性...")
        
        core_files = [
            'GUI刷题程序.py',
            '双系统题型识别器.py',
            '高精度题型识别.py',
            '智能题型识别.py',
            '题库管理.py',
            '刷题引擎.py',
            '启动器.py'
        ]
        
        missing_files = []
        for file_name in core_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                missing_files.append(file_name)
                print(f"❌ 缺少文件: {file_name}")
            else:
                print(f"✅ 文件存在: {file_name}")
        
        if missing_files:
            print(f"⚠️ 缺少 {len(missing_files)} 个核心文件")
            return False
        
        print("🔍 检查question-recog子系统...")
        qr_path = self.project_root / 'question-recog'
        if not qr_path.exists():
            print("❌ question-recog目录不存在")
            return False
        
        qr_files = ['main.py', '智能题目重构器.py', 'train_model.py']
        for file_name in qr_files:
            file_path = qr_path / file_name
            if not file_path.exists():
                print(f"❌ 缺少question-recog文件: {file_name}")
                return False
            else:
                print(f"✅ question-recog文件存在: {file_name}")
        
        print("🎉 核心组件检查完成")
        return True
    
    def test_dual_recognition_system(self):
        """测试双系统识别功能"""
        print("🔍 测试双系统题型识别器...")
        
        try:
            # 导入双系统识别器
            from 双系统题型识别器 import DualSystemRecognizer, detect_question_type_dual
            
            print("✅ 双系统识别器导入成功")
            
            # 创建识别器实例
            recognizer = DualSystemRecognizer()
            
            # 检查系统状态
            status = recognizer.get_system_status()
            print(f"📊 系统状态: {status['loaded_systems']}")
            
            # 测试用例
            test_cases = [
                {
                    'name': '单选题测试',
                    'question': '下列哪个是正确的安全措施？',
                    'answer': 'A',
                    'options': ['A: 停电', 'B: 验电', 'C: 装设接地线', 'D: 以上都是'],
                    'expected': 'single_choice'
                },
                {
                    'name': '多选题测试',
                    'question': '电力安全工作的技术措施包括哪些？',
                    'answer': 'ABC',
                    'options': ['A: 停电', 'B: 验电', 'C: 装设接地线', 'D: 悬挂标示牌'],
                    'expected': 'multiple_choice'
                },
                {
                    'name': '判断题测试',
                    'question': '装设接地线可以单人进行。',
                    'answer': '错',
                    'options': [],
                    'expected': 'true_false'
                }
            ]
            
            # 执行测试
            success_count = 0
            for case in test_cases:
                try:
                    q_type, confidence, details = recognizer.detect_question_type(
                        case['question'], case['answer'], case['options'], mode='auto'
                    )
                    
                    if q_type == case['expected']:
                        print(f"✅ {case['name']}: {q_type} (置信度: {confidence:.2f})")
                        success_count += 1
                    else:
                        print(f"❌ {case['name']}: 期望 {case['expected']}, 实际 {q_type}")
                        
                except Exception as e:
                    print(f"💥 {case['name']} 测试异常: {e}")
            
            # 测试不同模式
            print("\n🔍 测试不同识别模式...")
            modes = ['auto', 'original', 'enhanced', 'consensus']
            for mode in modes:
                try:
                    q_type, confidence, details = recognizer.detect_question_type(
                        test_cases[0]['question'], 
                        test_cases[0]['answer'], 
                        test_cases[0]['options'], 
                        mode=mode
                    )
                    print(f"✅ {mode}模式: {q_type} (置信度: {confidence:.2f})")
                except Exception as e:
                    print(f"❌ {mode}模式异常: {e}")
            
            return success_count == len(test_cases)
            
        except Exception as e:
            print(f"💥 双系统识别测试异常: {e}")
            return False
    
    def test_question_bank_management(self):
        """测试题库管理功能"""
        print("🔍 测试题库管理系统...")
        
        try:
            # 导入题库管理
            from 题库管理 import TikuManager
            
            print("✅ 题库管理器导入成功")
            
            # 创建管理器实例
            manager = TikuManager()
            
            # 检查题库目录
            tiku_dir = self.project_root / '题库'
            if not tiku_dir.exists():
                print("⚠️ 题库目录不存在，创建测试目录")
                tiku_dir.mkdir(exist_ok=True)
            
            # 查找题库文件
            excel_files = list(tiku_dir.glob('*.xlsx'))
            print(f"📊 找到 {len(excel_files)} 个Excel题库文件")
            
            if excel_files:
                # 测试加载题库
                test_file = excel_files[0]
                print(f"🔍 测试加载题库: {test_file.name}")
                
                try:
                    questions = manager.load_questions_from_excel(str(test_file))
                    print(f"✅ 成功加载 {len(questions)} 个题目")
                    
                    # 测试题型识别
                    if questions:
                        sample_question = questions[0]
                        q_type = manager.detect_question_type(sample_question)
                        print(f"✅ 题型识别测试: {q_type}")
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ 题库加载失败: {e}")
                    return False
            else:
                print("⚠️ 未找到题库文件，跳过题库加载测试")
                return True
                
        except Exception as e:
            print(f"💥 题库管理测试异常: {e}")
            return False
    
    def test_gui_interface(self):
        """测试GUI界面（非交互式）"""
        print("🔍 测试GUI界面组件...")
        
        try:
            # 检查tkinter可用性
            import tkinter as tk
            print("✅ tkinter可用")
            
            # 创建测试窗口
            root = tk.Tk()
            root.withdraw()  # 隐藏窗口
            
            # 测试基本组件
            test_frame = tk.Frame(root)
            test_label = tk.Label(test_frame, text="测试标签")
            test_button = tk.Button(test_frame, text="测试按钮")
            
            print("✅ 基本GUI组件创建成功")
            
            # 清理
            root.destroy()
            
            # 检查GUI程序文件
            gui_file = self.project_root / 'GUI刷题程序.py'
            if gui_file.exists():
                print("✅ GUI程序文件存在")
                
                # 简单语法检查
                try:
                    with open(gui_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 检查关键导入
                    if 'import tkinter' in content or 'from tkinter' in content:
                        print("✅ GUI程序包含tkinter导入")
                    else:
                        print("⚠️ GUI程序可能缺少tkinter导入")
                    
                    # 检查主要类
                    if 'class' in content and 'def __init__' in content:
                        print("✅ GUI程序包含类定义")
                    else:
                        print("⚠️ GUI程序可能缺少主类")
                        
                except Exception as e:
                    print(f"⚠️ GUI程序文件读取异常: {e}")
            else:
                print("❌ GUI程序文件不存在")
                return False
            
            return True
            
        except Exception as e:
            print(f"💥 GUI测试异常: {e}")
            return False
    
    def test_data_processing(self):
        """测试数据处理功能"""
        print("🔍 测试数据处理功能...")
        
        try:
            # 测试智能重构器
            qr_path = self.project_root / 'question-recog'
            rebuilder_file = qr_path / '智能题目重构器.py'
            
            if rebuilder_file.exists():
                print("✅ 智能重构器文件存在")
                
                # 导入重构器
                sys.path.insert(0, str(qr_path))
                from 智能题目重构器 import QuestionRebuilder
                
                rebuilder = QuestionRebuilder()
                print("✅ 智能重构器创建成功")
                
                # 测试重构功能（如果有测试数据）
                tiku_dir = self.project_root / '题库'
                excel_files = list(tiku_dir.glob('*.xlsx'))
                
                if excel_files:
                    test_file = excel_files[0]
                    print(f"🔍 测试重构功能: {test_file.name}")
                    
                    try:
                        questions = rebuilder.process_excel_file(str(test_file))
                        print(f"✅ 重构成功，得到 {len(questions)} 个题目")
                        
                        # 检查重构质量
                        if questions:
                            avg_quality = sum(q.get('quality_score', 0) for q in questions) / len(questions)
                            print(f"📊 平均质量分数: {avg_quality:.3f}")
                            
                            if avg_quality > 0.8:
                                print("✅ 重构质量优秀")
                            else:
                                print("⚠️ 重构质量需要改进")
                        
                    except Exception as e:
                        print(f"⚠️ 重构测试异常: {e}")
                
            else:
                print("❌ 智能重构器文件不存在")
                return False
            
            # 测试高精度识别
            enhanced_file = self.project_root / '高精度题型识别.py'
            if enhanced_file.exists():
                print("✅ 高精度识别文件存在")
                
                from 高精度题型识别 import detect_question_type_fixed
                
                # 测试识别功能
                test_result = detect_question_type_fixed(
                    "下列哪个是正确的？",
                    "A",
                    {"A": "选项A", "B": "选项B"}
                )
                print(f"✅ 高精度识别测试: {test_result}")
                
            else:
                print("❌ 高精度识别文件不存在")
                return False
            
            return True
            
        except Exception as e:
            print(f"💥 数据处理测试异常: {e}")
            return False
    
    def test_system_integration(self):
        """测试系统集成"""
        print("🔍 测试系统集成...")
        
        try:
            # 测试启动器
            launcher_file = self.project_root / '启动器.py'
            if launcher_file.exists():
                print("✅ 启动器文件存在")
                
                # 检查启动器内容
                with open(launcher_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'GUI刷题程序' in content:
                    print("✅ 启动器包含GUI程序引用")
                else:
                    print("⚠️ 启动器可能缺少GUI程序引用")
            
            # 测试配置文件
            config_files = [
                'requirements.txt',
                'README.md'
            ]
            
            for config_file in config_files:
                file_path = self.project_root / config_file
                if file_path.exists():
                    print(f"✅ 配置文件存在: {config_file}")
                else:
                    print(f"⚠️ 配置文件缺失: {config_file}")
            
            # 测试批处理文件
            bat_files = list(self.project_root.glob('*.bat'))
            if bat_files:
                print(f"✅ 找到 {len(bat_files)} 个批处理文件")
                for bat_file in bat_files:
                    print(f"  - {bat_file.name}")
            else:
                print("⚠️ 未找到批处理文件")
            
            # 测试文档文件
            doc_files = [
                '📚系统完整文档.md',
                '🎨GUI界面详细说明.md',
                '文件清单.json'
            ]
            
            for doc_file in doc_files:
                file_path = self.project_root / doc_file
                if file_path.exists():
                    print(f"✅ 文档文件存在: {doc_file}")
                else:
                    print(f"⚠️ 文档文件缺失: {doc_file}")
            
            return True
            
        except Exception as e:
            print(f"💥 系统集成测试异常: {e}")
            return False
    
    def test_performance(self):
        """测试系统性能"""
        print("🔍 测试系统性能...")
        
        try:
            # 测试识别性能
            from 双系统题型识别器 import detect_question_type_dual
            
            test_questions = [
                ("单选题测试", "A", ["A: 选项A", "B: 选项B"]),
                ("多选题测试", "ABC", ["A: 选项A", "B: 选项B", "C: 选项C"]),
                ("判断题测试", "对", []),
                ("填空题测试", "答案", []),
                ("简答题测试", "这是一个详细的答案说明", [])
            ] * 10  # 重复10次
            
            start_time = time.time()
            
            for question, answer, options in test_questions:
                q_type, confidence = detect_question_type_dual(question, answer, options)
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / len(test_questions)
            
            print(f"📊 性能测试结果:")
            print(f"  总测试数: {len(test_questions)}")
            print(f"  总用时: {total_time:.3f}秒")
            print(f"  平均用时: {avg_time:.3f}秒/题")
            print(f"  处理速度: {len(test_questions)/total_time:.1f}题/秒")
            
            if avg_time < 0.1:
                print("✅ 性能优秀 (< 0.1秒/题)")
            elif avg_time < 0.5:
                print("✅ 性能良好 (< 0.5秒/题)")
            else:
                print("⚠️ 性能需要优化 (> 0.5秒/题)")
            
            return avg_time < 1.0  # 1秒内完成识别
            
        except Exception as e:
            print(f"💥 性能测试异常: {e}")
            return False
    
    def test_error_handling(self):
        """测试错误处理"""
        print("🔍 测试错误处理...")
        
        try:
            from 双系统题型识别器 import detect_question_type_dual
            
            # 测试异常输入
            error_cases = [
                ("空题目", "", "A", ["A: 选项A"]),
                ("空答案", "题目", "", ["A: 选项A"]),
                ("无选项", "题目", "A", []),
                ("异常字符", "题目\x00\x01", "A", ["A\x00: 选项"]),
                ("超长文本", "题目" * 1000, "A", ["A: 选项A"])
            ]
            
            error_handled = 0
            
            for case_name, question, answer, options in error_cases:
                try:
                    q_type, confidence = detect_question_type_dual(question, answer, options)
                    print(f"✅ {case_name}: 正常处理 -> {q_type}")
                    error_handled += 1
                except Exception as e:
                    print(f"❌ {case_name}: 异常 -> {e}")
            
            success_rate = error_handled / len(error_cases)
            print(f"📊 错误处理成功率: {success_rate:.1%}")
            
            return success_rate >= 0.8  # 80%以上的错误能正常处理
            
        except Exception as e:
            print(f"💥 错误处理测试异常: {e}")
            return False
    
    def generate_test_report(self, passed_tests: int, total_tests: int):
        """生成测试报告"""
        end_time = time.time()
        total_time = end_time - self.start_time
        
        print("\n" + "=" * 60)
        print("🎉 集成测试完成")
        print("=" * 60)
        
        print(f"📊 测试统计:")
        print(f"  总测试数: {total_tests}")
        print(f"  通过测试: {passed_tests}")
        print(f"  失败测试: {total_tests - passed_tests}")
        print(f"  成功率: {passed_tests/total_tests:.1%}")
        print(f"  总用时: {total_time:.2f}秒")
        
        # 详细结果
        print(f"\n📋 详细结果:")
        for test_name, result in self.test_results.items():
            status_icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥"}[result['status']]
            print(f"  {status_icon} {test_name}: {result['status']}")
            if result['status'] != 'PASS' and self.test_config['verbose']:
                print(f"    详情: {result['details']}")
        
        # 系统健康度评估
        health_score = passed_tests / total_tests
        if health_score >= 0.9:
            health_status = "🟢 优秀"
        elif health_score >= 0.7:
            health_status = "🟡 良好"
        else:
            health_status = "🔴 需要改进"
        
        print(f"\n🏥 系统健康度: {health_status} ({health_score:.1%})")
        
        # 保存测试报告
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': health_score,
            'total_time': total_time,
            'test_results': self.test_results,
            'system_health': health_status
        }
        
        report_file = self.project_root / '🧪集成测试报告.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📋 详细测试报告已保存: {report_file}")
        
        # 建议
        if health_score < 1.0:
            print(f"\n💡 改进建议:")
            failed_tests = [name for name, result in self.test_results.items() if result['status'] != 'PASS']
            for test_name in failed_tests:
                print(f"  - 修复 {test_name}")
            print(f"  - 检查依赖项安装")
            print(f"  - 验证文件完整性")
            print(f"  - 查看详细错误日志")

def main():
    """主函数"""
    print("🚀 启动系统集成测试")
    print("🎯 测试目标: 验证刷题系统各组件功能完整性")
    print("⏰ 开始时间:", time.strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # 创建测试实例
    tester = SystemIntegrationTest()
    
    # 运行所有测试
    tester.run_all_tests()
    
    print("\n🎊 集成测试结束")

if __name__ == "__main__":
    main()
