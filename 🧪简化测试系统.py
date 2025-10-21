#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试系统 - 确保基本功能正常
"""

import os
import sys
import time
from pathlib import Path

def test_basic_functionality():
    """测试基本功能"""
    print("🧪 简化测试系统")
    print("=" * 50)
    
    # 测试1: 检查核心文件
    print("📁 检查核心文件...")
    core_files = [
        'GUI刷题程序.py',
        'main.py',
        '刷题引擎.py',
        '题库管理.py',
        '智能题型识别.py',
        '双系统题型识别器.py'
    ]
    
    missing_files = []
    for file_name in core_files:
        if Path(file_name).exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name}")
            missing_files.append(file_name)
    
    if missing_files:
        print(f"⚠️ 缺少 {len(missing_files)} 个核心文件")
    else:
        print("✅ 所有核心文件存在")
    
    # 测试2: 检查题库文件
    print("\n📚 检查题库文件...")
    tiku_dir = Path('题库')
    if tiku_dir.exists():
        excel_files = list(tiku_dir.glob('*.xlsx'))
        pdf_files = list(tiku_dir.glob('*.pdf'))
        word_files = list(tiku_dir.glob('*.docx'))
        
        print(f"📊 Excel文件: {len(excel_files)} 个")
        print(f"📄 PDF文件: {len(pdf_files)} 个")
        print(f"📝 Word文件: {len(word_files)} 个")
        
        if excel_files or pdf_files or word_files:
            print("✅ 题库文件存在")
        else:
            print("⚠️ 未找到题库文件")
    else:
        print("❌ 题库目录不存在")
    
    # 测试3: 测试基本导入
    print("\n🔍 测试基本导入...")
    try:
        import pandas as pd
        print("✅ pandas 导入成功")
    except ImportError:
        print("❌ pandas 导入失败")
    
    try:
        import openpyxl
        print("✅ openpyxl 导入成功")
    except ImportError:
        print("❌ openpyxl 导入失败")
    
    try:
        import tkinter as tk
        print("✅ tkinter 导入成功")
    except ImportError:
        print("❌ tkinter 导入失败")
    
    # 测试4: 测试题型识别
    print("\n🎯 测试题型识别...")
    try:
        from 智能题型识别 import detect_question_type
        
        test_cases = [
            ("下列哪个正确？", "A", {"A": "选项A", "B": "选项B"}),
            ("哪些正确？", "AB", {"A": "选项A", "B": "选项B"}),
            ("这是对的吗？", "对", {})
        ]
        
        for i, (question, answer, options) in enumerate(test_cases, 1):
            try:
                result = detect_question_type(question, answer, options)
                print(f"✅ 测试用例{i}: {result}")
            except Exception as e:
                print(f"❌ 测试用例{i}: {e}")
                
    except Exception as e:
        print(f"❌ 题型识别测试失败: {e}")
    
    # 测试5: 测试题库管理
    print("\n📚 测试题库管理...")
    try:
        from 题库管理 import TikuManager
        
        manager = TikuManager()
        tiku_list = manager.get_tiku_list()
        
        if tiku_list:
            print(f"✅ 找到 {len(tiku_list)} 个题库")
            for name, path in tiku_list[:3]:  # 显示前3个
                print(f"  - {name}")
        else:
            print("⚠️ 未找到题库")
            
    except Exception as e:
        print(f"❌ 题库管理测试失败: {e}")
    
    print("\n🎉 简化测试完成")
    print("=" * 50)

def test_performance():
    """测试性能"""
    print("\n⚡ 性能测试...")
    
    try:
        from 双系统题型识别器 import detect_question_type_dual
        
        test_cases = [
            ("单选题测试", "A", {"A": "选项A", "B": "选项B"}),
            ("多选题测试", "AB", {"A": "选项A", "B": "选项B"}),
            ("判断题测试", "对", {}),
            ("填空题测试", "答案", {}),
            ("简答题测试", "详细答案", {})
        ]
        
        start_time = time.time()
        
        for question, answer, options in test_cases:
            try:
                q_type, confidence = detect_question_type_dual(question, answer, options)
            except:
                pass
        
        end_time = time.time()
        avg_time = (end_time - start_time) / len(test_cases)
        
        print(f"📊 平均响应时间: {avg_time:.4f}秒")
        print(f"📊 处理速度: {len(test_cases)/avg_time:.1f}题/秒")
        
        if avg_time < 0.1:
            print("✅ 性能优秀")
        elif avg_time < 0.5:
            print("✅ 性能良好")
        else:
            print("⚠️ 性能需要优化")
            
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")

def main():
    """主函数"""
    print("🚀 启动简化测试系统")
    print("⏰ 开始时间:", time.strftime('%Y-%m-%d %H:%M:%S'))
    print()
    
    # 运行基本功能测试
    test_basic_functionality()
    
    # 运行性能测试
    test_performance()
    
    print("\n🎊 简化测试系统运行完成")

if __name__ == "__main__":
    main()
