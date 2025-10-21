#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试启动器 - 一键运行所有测试
"""

import os
import sys
from pathlib import Path

def main():
    """主函数"""
    print("🚀 刷题系统测试启动器")
    print("=" * 50)
    print("1. 智能测试与优化系统")
    print("2. 测试执行器与可视化分析")
    print("3. 闭环反馈优化系统")
    print("4. 完整集成测试")
    print("5. 运行所有测试")
    print("6. 简化测试系统 (推荐)")
    print("7. 统一识别系统测试")
    print("0. 退出")
    print("=" * 50)
    
    choice = input("请选择测试类型 (0-7): ").strip()
    
    if choice == '1':
        print("\n🧪 启动智能测试与优化系统...")
        run_single_test("🧪智能测试与优化系统.py")
    
    elif choice == '2':
        print("\n📊 启动测试执行器与可视化分析...")
        run_single_test("🧪测试执行器与可视化分析.py")
    
    elif choice == '3':
        print("\n🔄 启动闭环反馈优化系统...")
        run_single_test("🔄闭环反馈优化系统.py")
    
    elif choice == '4':
        print("\n🧪 启动完整集成测试...")
        run_single_test("🧪完整集成测试.py")
    
    elif choice == '5':
        print("\n🎯 运行所有测试...")
        run_all_tests()
    
    elif choice == '6':
        print("\n🧪 启动简化测试系统...")
        run_single_test("🧪简化测试系统.py")
    
    elif choice == '7':
        print("\n🎯 启动统一识别系统测试...")
        run_single_test("🎯统一识别系统.py")
    
    elif choice == '0':
        print("👋 退出测试启动器")
        return
    
    else:
        print("❌ 无效选择")

def run_single_test(file_name):
    """运行单个测试文件"""
    import subprocess
    import sys
    
    try:
        print(f"正在运行 {file_name}...")
        result = subprocess.run([sys.executable, file_name], 
                              timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {file_name} 运行完成")
        else:
            print(f"❌ {file_name} 运行失败")
            
    except subprocess.TimeoutExpired:
        print(f"❌ {file_name} 运行超时")
    except Exception as e:
        print(f"❌ {file_name} 运行异常: {e}")

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行所有测试...")
    
    # 使用subprocess运行测试文件
    import subprocess
    import sys
    
    test_files = [
        ("智能测试与优化系统", "🧪智能测试与优化系统.py"),
        ("测试执行器与可视化分析", "🧪测试执行器与可视化分析.py"),
        ("闭环反馈优化系统", "🔄闭环反馈优化系统.py"),
        ("完整集成测试", "🧪完整集成测试.py")
    ]
    
    results = {}
    
    for test_name, file_name in test_files:
        print(f"\n🧪 运行 {test_name}...")
        try:
            # 使用subprocess运行Python文件
            result = subprocess.run([sys.executable, file_name], 
                                  capture_output=True, text=True, 
                                  encoding='utf-8', errors='ignore', timeout=300)
            
            if result.returncode == 0:
                results[test_name] = "✅ 成功"
                print(f"✅ {test_name} 完成")
                if result.stdout:
                    print("输出:", result.stdout[-200:])  # 显示最后200个字符
            else:
                results[test_name] = f"❌ 失败: {result.stderr}"
                print(f"❌ {test_name} 失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            results[test_name] = "❌ 超时"
            print(f"❌ {test_name} 超时")
        except Exception as e:
            results[test_name] = f"❌ 失败: {e}"
            print(f"❌ {test_name} 失败: {e}")
    
    # 显示总结
    print("\n" + "=" * 50)
    print("🎉 所有测试完成")
    print("=" * 50)
    
    for test_name, result in results.items():
        print(f"{result} {test_name}")

if __name__ == "__main__":
    main()
