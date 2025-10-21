#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全集成启动器 - 统一所有系统接口
将所有识别系统和功能完全接入刷题程序
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class 完全集成启动器:
    """完全集成启动器 - 统一所有系统接口"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.系统状态 = {}
        self.集成配置 = {
            '识别系统': {
                '主系统': '完全集成识别系统',
                '备用系统': ['高精度题型识别', '智能题型识别', '双系统题型识别器'],
                '自动切换': True,
                '性能监控': True
            },
            '题库管理': {
                '主解析器': '题库管理',
                '备用解析器': ['PDF题库解析', 'Word题库智能解析器'],
                '缓存启用': True
            },
            '刷题引擎': {
                '主引擎': '刷题引擎',
                '统计系统': '统计分析',
                '错题管理': '错题记忆'
            },
            '用户界面': {
                'GUI程序': 'GUI刷题程序',
                '命令行': 'main',
                '启动器': '启动器'
            }
        }
        
        print("🚀 完全集成启动器初始化")
        self._初始化所有系统()
    
    def _初始化所有系统(self):
        """初始化所有系统"""
        print("🔧 正在初始化所有系统...")
        
        # 1. 初始化识别系统
        self._初始化识别系统()
        
        # 2. 初始化题库管理
        self._初始化题库管理()
        
        # 3. 初始化刷题引擎
        self._初始化刷题引擎()
        
        # 4. 初始化用户界面
        self._初始化用户界面()
        
        print("✅ 所有系统初始化完成")
    
    def _初始化识别系统(self):
        """初始化识别系统"""
        try:
            from 完全集成识别系统 import 完全集成识别器, get_recognition_performance
            
            self.识别系统 = 完全集成识别器
            self.识别性能 = get_recognition_performance
            
            self.系统状态['识别系统'] = {
                '状态': '已加载',
                '主系统': '完全集成识别系统',
                '可用系统': list(self.识别系统.识别系统列表.keys()),
                '初始化时间': datetime.now().isoformat()
            }
            
            print(f"✅ 识别系统已加载: {len(self.识别系统.识别系统列表)} 个子系统")
            
        except Exception as e:
            print(f"❌ 识别系统加载失败: {e}")
            self.系统状态['识别系统'] = {
                '状态': '加载失败',
                '错误': str(e),
                '初始化时间': datetime.now().isoformat()
            }
    
    def _初始化题库管理(self):
        """初始化题库管理"""
        try:
            from 题库管理 import TikuManager
            
            self.题库管理器 = TikuManager()
            self.题库列表 = self.题库管理器.get_tiku_list()
            
            self.系统状态['题库管理'] = {
                '状态': '已加载',
                '题库数量': len(self.题库列表),
                '题库列表': [name for name, path in self.题库列表],
                '初始化时间': datetime.now().isoformat()
            }
            
            print(f"✅ 题库管理已加载: {len(self.题库列表)} 个题库")
            
        except Exception as e:
            print(f"❌ 题库管理加载失败: {e}")
            self.系统状态['题库管理'] = {
                '状态': '加载失败',
                '错误': str(e),
                '初始化时间': datetime.now().isoformat()
            }
    
    def _初始化刷题引擎(self):
        """初始化刷题引擎"""
        try:
            from 刷题引擎 import ShuatiEngine
            from 统计分析 import StatsAnalyzer
            from 错题记忆 import 错题记忆管理器
            
            self.刷题引擎 = ShuatiEngine
            self.统计分析器 = StatsAnalyzer
            self.错题管理器 = 错题记忆管理器
            
            self.系统状态['刷题引擎'] = {
                '状态': '已加载',
                '组件': ['刷题引擎', '统计分析', '错题记忆'],
                '初始化时间': datetime.now().isoformat()
            }
            
            print("✅ 刷题引擎已加载")
            
        except Exception as e:
            print(f"❌ 刷题引擎加载失败: {e}")
            self.系统状态['刷题引擎'] = {
                '状态': '加载失败',
                '错误': str(e),
                '初始化时间': datetime.now().isoformat()
            }
    
    def _初始化用户界面(self):
        """初始化用户界面"""
        try:
            # 检查GUI组件
            gui_file = self.project_root / 'GUI刷题程序.py'
            main_file = self.project_root / 'main.py'
            
            gui_available = gui_file.exists()
            cli_available = main_file.exists()
            
            self.系统状态['用户界面'] = {
                '状态': '已检查',
                'GUI可用': gui_available,
                '命令行可用': cli_available,
                '初始化时间': datetime.now().isoformat()
            }
            
            if gui_available:
                print("✅ GUI界面可用")
            if cli_available:
                print("✅ 命令行界面可用")
                
        except Exception as e:
            print(f"❌ 用户界面检查失败: {e}")
            self.系统状态['用户界面'] = {
                '状态': '检查失败',
                '错误': str(e),
                '初始化时间': datetime.now().isoformat()
            }
    
    def 启动GUI界面(self):
        """启动GUI界面"""
        try:
            print("🖥️ 启动GUI界面...")
            
            # 导入并启动GUI
            from GUI刷题程序 import 刷题应用
            
            app = 刷题应用()
            app.mainloop()
            
        except Exception as e:
            print(f"❌ GUI启动失败: {e}")
            print("💡 尝试启动命令行界面...")
            self.启动命令行界面()
    
    def 启动命令行界面(self):
        """启动命令行界面"""
        try:
            print("💻 启动命令行界面...")
            
            # 导入并启动命令行
            from main import main_menu
            
            main_menu()
            
        except Exception as e:
            print(f"❌ 命令行启动失败: {e}")
            print("💡 启动简化界面...")
            self.启动简化界面()
    
    def 启动简化界面(self):
        """启动简化界面"""
        print("🔧 启动简化界面...")
        
        while True:
            print("\n" + "=" * 50)
            print("🚀 完全集成刷题系统")
            print("=" * 50)
            print("1. 开始刷题")
            print("2. 查看题库")
            print("3. 测试识别系统")
            print("4. 查看系统状态")
            print("5. 性能统计")
            print("0. 退出")
            print("=" * 50)
            
            choice = input("请选择功能 (0-5): ").strip()
            
            if choice == '1':
                self.开始刷题()
            elif choice == '2':
                self.查看题库()
            elif choice == '3':
                self.测试识别系统()
            elif choice == '4':
                self.查看系统状态()
            elif choice == '5':
                self.查看性能统计()
            elif choice == '0':
                print("👋 退出系统")
                break
            else:
                print("❌ 无效选择")
    
    def 开始刷题(self):
        """开始刷题"""
        try:
            if '题库管理' not in self.系统状态 or self.系统状态['题库管理']['状态'] != '已加载':
                print("❌ 题库管理系统未加载")
                return
            
            if not self.题库列表:
                print("❌ 没有可用题库")
                return
            
            print("\n📚 可用题库:")
            for i, (name, path) in enumerate(self.题库列表, 1):
                print(f"{i}. {name}")
            
            choice = input("\n请选择题库 (输入数字): ").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.题库列表):
                    selected_tiku = self.题库列表[idx][0]
                    print(f"\n🎯 开始刷题: {selected_tiku}")
                    
                    # 创建刷题引擎
                    engine = self.刷题引擎(selected_tiku, 'sequential')
                    engine.start()
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入有效数字")
                
        except Exception as e:
            print(f"❌ 刷题启动失败: {e}")
    
    def 查看题库(self):
        """查看题库"""
        try:
            if '题库管理' not in self.系统状态 or self.系统状态['题库管理']['状态'] != '已加载':
                print("❌ 题库管理系统未加载")
                return
            
            print("\n📚 题库信息:")
            print("-" * 50)
            
            for name, path in self.题库列表:
                try:
                    count = self.题库管理器.get_question_count(name)
                    print(f"📖 {name}")
                    print(f"   文件: {path.name}")
                    print(f"   题目数: {count}")
                    print()
                except Exception as e:
                    print(f"❌ {name}: 加载失败 - {e}")
            
        except Exception as e:
            print(f"❌ 查看题库失败: {e}")
    
    def 测试识别系统(self):
        """测试识别系统"""
        try:
            if '识别系统' not in self.系统状态 or self.系统状态['识别系统']['状态'] != '已加载':
                print("❌ 识别系统未加载")
                return
            
            print("\n🧪 识别系统测试")
            print("-" * 50)
            
            # 测试用例
            test_cases = [
                {
                    'name': '单选题',
                    'question': '下列哪个是正确的安全措施？',
                    'answer': 'A',
                    'options': {'A': '停电', 'B': '验电', 'C': '装设接地线', 'D': '以上都是'}
                },
                {
                    'name': '多选题',
                    'question': '电力安全工作的技术措施包括哪些？',
                    'answer': 'ABC',
                    'options': {'A': '停电', 'B': '验电', 'C': '装设接地线', 'D': '悬挂标示牌'}
                },
                {
                    'name': '判断题',
                    'question': '装设接地线可以单人进行。',
                    'answer': '错',
                    'options': {}
                }
            ]
            
            for case in test_cases:
                print(f"\n📝 测试 {case['name']}:")
                print(f"题目: {case['question']}")
                print(f"答案: {case['answer']}")
                
                # 使用完全集成识别系统
                result = self.识别系统.识别题型(
                    case['question'], 
                    case['answer'], 
                    case['options'], 
                    'auto', 
                    False
                )
                
                if result.get('success', False):
                    print(f"✅ 识别结果: {result.get('question_type', '未知')}")
                    print(f"📊 置信度: {result.get('confidence', 0):.2f}")
                    print(f"⏱️ 耗时: {result.get('time_cost', 0):.4f}s")
                else:
                    print(f"❌ 识别失败: {result.get('error', '未知错误')}")
            
        except Exception as e:
            print(f"❌ 识别系统测试失败: {e}")
    
    def 查看系统状态(self):
        """查看系统状态"""
        print("\n📊 系统状态")
        print("=" * 50)
        
        for 系统名, 状态信息 in self.系统状态.items():
            print(f"\n🔧 {系统名}:")
            for 键, 值 in 状态信息.items():
                if isinstance(值, list):
                    print(f"  {键}: {', '.join(map(str, 值))}")
                else:
                    print(f"  {键}: {值}")
    
    def 查看性能统计(self):
        """查看性能统计"""
        try:
            if '识别系统' not in self.系统状态 or self.系统状态['识别系统']['状态'] != '已加载':
                print("❌ 识别系统未加载")
                return
            
            print("\n📈 性能统计")
            print("-" * 50)
            
            stats = self.识别性能()
            
            print(f"总调用次数: {stats['total_calls']}")
            print(f"总成功次数: {stats['total_success']}")
            print(f"整体成功率: {stats['overall_success_rate']:.1%}")
            print(f"识别历史数量: {stats['recognition_history_count']}")
            
            print(f"\n各系统性能:")
            for 系统名, 数据 in stats['systems'].items():
                if 数据['调用次数'] > 0:
                    成功率 = 数据['成功次数'] / 数据['调用次数']
                    print(f"  {系统名}:")
                    print(f"    成功率: {成功率:.1%}")
                    print(f"    平均耗时: {数据['平均耗时']:.4f}s")
                    print(f"    平均置信度: {数据['平均置信度']:.2f}")
            
        except Exception as e:
            print(f"❌ 性能统计查看失败: {e}")
    
    def 保存系统报告(self):
        """保存系统报告"""
        try:
            报告目录 = self.project_root / '.integration_reports'
            报告目录.mkdir(exist_ok=True)
            
            报告文件 = 报告目录 / f'system_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            
            报告数据 = {
                'timestamp': datetime.now().isoformat(),
                'system_status': self.系统状态,
                'integration_config': self.集成配置,
                'recognition_performance': self.识别性能() if '识别系统' in self.系统状态 else None
            }
            
            with open(报告文件, 'w', encoding='utf-8') as f:
                json.dump(报告数据, f, ensure_ascii=False, indent=2)
            
            print(f"📊 系统报告已保存: {报告文件}")
            return 报告文件
            
        except Exception as e:
            print(f"❌ 保存系统报告失败: {e}")
            return None

def main():
    """主函数"""
    print("🚀 启动完全集成刷题系统")
    print("⏰ 开始时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # 创建完全集成启动器
    启动器 = 完全集成启动器()
    
    # 检查系统状态
    if all(状态['状态'] in ['已加载', '已检查'] for 状态 in 启动器.系统状态.values()):
        print("✅ 所有系统加载成功")
        
        # 尝试启动GUI
        try:
            启动器.启动GUI界面()
        except Exception as e:
            print(f"⚠️ GUI启动失败: {e}")
            print("💡 切换到命令行模式...")
            启动器.启动命令行界面()
    else:
        print("⚠️ 部分系统加载失败，启动简化模式...")
        启动器.启动简化界面()
    
    # 保存系统报告
    启动器.保存系统报告()
    
    print("\n🎊 完全集成刷题系统运行完成")

if __name__ == "__main__":
    main()
