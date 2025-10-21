#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF题目切割测试 - 专门测试PDF识别和切割功能
"""

import sys
from pathlib import Path

def test_pdf_recognition():
    """测试PDF识别和切割功能"""
    print("🔍 PDF题目切割测试")
    print("=" * 50)
    
    try:
        # 导入题库管理模块
        from 题库管理 import TikuManager
        
        # 创建题库管理器
        tiku_manager = TikuManager()
        
        # 测试PDF题库路径
        pdf_path = Path("题库") / "1.电力安全工作规程（发电厂和变电站电气部分）安徽分公司题库（GB 26860—2011).pdf"
        
        if pdf_path.exists():
            print(f"📄 找到PDF题库: {pdf_path.name}")
            
            # 尝试加载PDF题库
            print("🔄 正在加载PDF题库...")
            questions = tiku_manager.load_tiku(pdf_path.name)
            
            if questions:
                print(f"✅ PDF题库加载成功，共 {len(questions)} 道题")
                
                # 测试前5道题的识别
                print("\n🧪 测试题目识别:")
                print("-" * 30)
                
                for i, question in enumerate(questions[:5]):
                    print(f"\n📝 第 {i+1} 题:")
                    print(f"题目: {question.get('question', '')[:100]}...")
                    print(f"答案: {question.get('answer', '')}")
                    print(f"选项: {question.get('options', {})}")
                    
                    # 测试题型识别
                    question_type = tiku_manager.detect_question_type(question)
                    print(f"识别题型: {question_type}")
                    
            else:
                print("❌ PDF题库加载失败")
        else:
            print(f"❌ PDF文件不存在: {pdf_path}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_word_recognition():
    """测试Word识别和切割功能"""
    print("\n🔍 Word题目切割测试")
    print("=" * 50)
    
    try:
        # 导入题库管理模块
        from 题库管理 import TikuManager
        
        # 创建题库管理器
        tiku_manager = TikuManager()
        
        # 测试Word题库路径
        word_path = Path("题库") / "附件：安徽分公司电力生产培训题库(1).docx"
        
        if word_path.exists():
            print(f"📄 找到Word题库: {word_path.name}")
            
            # 尝试加载Word题库
            print("🔄 正在加载Word题库...")
            questions = tiku_manager.load_tiku(word_path.name)
            
            if questions:
                print(f"✅ Word题库加载成功，共 {len(questions)} 道题")
                
                # 测试前5道题的识别
                print("\n🧪 测试题目识别:")
                print("-" * 30)
                
                for i, question in enumerate(questions[:5]):
                    print(f"\n📝 第 {i+1} 题:")
                    print(f"题目: {question.get('question', '')[:100]}...")
                    print(f"答案: {question.get('answer', '')}")
                    print(f"选项: {question.get('options', {})}")
                    
                    # 测试题型识别
                    question_type = tiku_manager.detect_question_type(question)
                    print(f"识别题型: {question_type}")
                    
            else:
                print("❌ Word题库加载失败")
        else:
            print(f"❌ Word文件不存在: {word_path}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_excel_recognition():
    """测试Excel识别和切割功能"""
    print("\n🔍 Excel题目切割测试")
    print("=" * 50)
    
    try:
        # 导入题库管理模块
        from 题库管理 import TikuManager
        
        # 创建题库管理器
        tiku_manager = TikuManager()
        
        # 测试Excel题库路径
        excel_path = Path("题库") / "1.电力安全工作规程（发电厂和变电站电气部分）安徽分公司题库（GB 26860—2011).xlsx"
        
        if excel_path.exists():
            print(f"📄 找到Excel题库: {excel_path.name}")
            
            # 尝试加载Excel题库
            print("🔄 正在加载Excel题库...")
            questions = tiku_manager.load_tiku(excel_path.name)
            
            if questions:
                print(f"✅ Excel题库加载成功，共 {len(questions)} 道题")
                
                # 测试前5道题的识别
                print("\n🧪 测试题目识别:")
                print("-" * 30)
                
                for i, question in enumerate(questions[:5]):
                    print(f"\n📝 第 {i+1} 题:")
                    print(f"题目: {question.get('question', '')[:100]}...")
                    print(f"答案: {question.get('answer', '')}")
                    print(f"选项: {question.get('options', {})}")
                    
                    # 测试题型识别
                    question_type = tiku_manager.detect_question_type(question)
                    print(f"识别题型: {question_type}")
                    
            else:
                print("❌ Excel题库加载失败")
        else:
            print(f"❌ Excel文件不存在: {excel_path}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("🚀 题目切割测试系统")
    print("=" * 50)
    
    # 测试PDF识别
    test_pdf_recognition()
    
    # 测试Word识别
    test_word_recognition()
    
    # 测试Excel识别
    test_excel_recognition()
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main()
