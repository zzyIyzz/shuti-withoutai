#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Excel题库加载
"""

def test_excel_tiku():
    """测试Excel题库加载"""
    print("📖 测试Excel题库加载")
    print("=" * 50)
    
    try:
        from 题库管理 import TikuManager
        
        tiku_manager = TikuManager()
        
        # 加载Excel题库 - 使用完整的题库名称
        questions = tiku_manager.load_tiku('1.电力安全工作规程（发电厂和变电站电气部分）安徽分公司题库（GB 26860—2011)')
        
        if questions:
            print(f"✅ 成功加载 {len(questions)} 道题目")
            
            # 显示前5道题目
            print("\n前5道题目:")
            for i, q in enumerate(questions[:5], 1):
                print(f"\n{i}. 题目: {q['question'][:80]}...")
                print(f"   答案: {q['answer']}")
                print(f"   题型: {q['type']}")
                print(f"   选项: {q['options']}")
        else:
            print("❌ 加载题目失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_excel_tiku()
