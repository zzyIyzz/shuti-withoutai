#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安规刷题程序
功能：
1. 支持Excel题库导入
2. 顺序刷题/随机刷题/错题重做
3. 自动记录错题和答题历史
4. 显示答题统计
"""

import os
import json
import random
from datetime import datetime
from 题库管理 import TikuManager
from 刷题引擎 import ShuatiEngine
from 统计分析 import StatsAnalyzer

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")

def main_menu():
    """主菜单"""
    while True:
        clear_screen()
        print_header("安规刷题系统")
        print("1. 开始刷题")
        print("2. 错题重做")
        print("3. 题库管理")
        print("4. 答题统计")
        print("5. 设置")
        print("0. 退出")
        print("\n" + "-" * 60)
        
        choice = input("请选择功能（输入数字）: ").strip()
        
        if choice == '1':
            start_practice()
        elif choice == '2':
            wrong_questions_practice()
        elif choice == '3':
            tiku_management()
        elif choice == '4':
            show_statistics()
        elif choice == '5':
            settings()
        elif choice == '0':
            print("\n感谢使用！祝考试顺利！")
            break
        else:
            print("无效选择，请重新输入")
            input("按回车键继续...")

def start_practice():
    """开始刷题"""
    clear_screen()
    print_header("开始刷题")
    
    # 加载题库
    manager = TikuManager()
    tiku_list = manager.get_tiku_list()
    
    if not tiku_list:
        print("当前没有可用题库！")
        print("\n提示：请将Excel题库文件放到 '刷题程序' 文件夹下")
        print("支持的格式：.xlsx")
        input("\n按回车键返回...")
        return
    
    # 选择题库
    print("可用题库：")
    for i, tiku in enumerate(tiku_list, 1):
        count = manager.get_question_count(tiku)
        print(f"{i}. {tiku} ({count}题)")
    
    print("0. 返回")
    choice = input("\n请选择题库（输入数字）: ").strip()
    
    if choice == '0':
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(tiku_list):
            selected_tiku = tiku_list[idx]
        else:
            print("无效选择")
            input("按回车键继续...")
            return
    except ValueError:
        print("无效输入")
        input("按回车键继续...")
        return
    
    # 选择模式
    clear_screen()
    print_header(f"题库：{selected_tiku}")
    print("刷题模式：")
    print("1. 顺序刷题")
    print("2. 随机刷题")
    print("3. 模拟考试")
    print("0. 返回")
    
    mode_choice = input("\n请选择模式: ").strip()
    
    if mode_choice == '0':
        return
    
    modes = {'1': 'sequential', '2': 'random', '3': 'exam'}
    mode = modes.get(mode_choice, 'sequential')
    
    # 开始刷题
    engine = ShuatiEngine(selected_tiku, mode)
    engine.start()

def wrong_questions_practice():
    """错题重做"""
    clear_screen()
    print_header("错题重做")
    
    engine = ShuatiEngine(source='wrong_questions', mode='random')
    if engine.has_questions():
        engine.start()
    else:
        print("当前没有错题！")
        input("\n按回车键返回...")

def tiku_management():
    """题库管理"""
    while True:
        clear_screen()
        print_header("题库管理")
        
        manager = TikuManager()
        tiku_list = manager.get_tiku_list()
        
        if tiku_list:
            print("已加载题库：")
            for i, tiku in enumerate(tiku_list, 1):
                count = manager.get_question_count(tiku)
                print(f"{i}. {tiku} ({count}题)")
        else:
            print("当前没有题库")
        
        print("\n操作：")
        print("1. 刷新题库")
        print("2. 导入题库（将Excel文件放入当前文件夹）")
        print("3. 查看题库详情")
        print("0. 返回")
        
        choice = input("\n请选择: ").strip()
        
        if choice == '1':
            manager.refresh()
            print("题库已刷新！")
            input("按回车键继续...")
        elif choice == '2':
            print("\n请将题库Excel文件复制到 '刷题程序' 文件夹")
            print("然后选择'刷新题库'即可")
            input("按回车键继续...")
        elif choice == '3':
            if tiku_list:
                idx_input = input("请输入题库编号: ").strip()
                try:
                    idx = int(idx_input) - 1
                    if 0 <= idx < len(tiku_list):
                        manager.show_tiku_detail(tiku_list[idx])
                        input("\n按回车键继续...")
                except ValueError:
                    pass
        elif choice == '0':
            break

def show_statistics():
    """显示统计"""
    clear_screen()
    print_header("答题统计")
    
    analyzer = StatsAnalyzer()
    analyzer.show_statistics()
    
    input("\n按回车键返回...")

def settings():
    """设置"""
    clear_screen()
    print_header("设置")
    print("功能开发中...")
    input("\n按回车键返回...")

if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n发生错误: {e}")
        input("按回车键退出...")

