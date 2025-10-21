#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进的PDF解析
"""

from 题库管理 import TikuManager

def test_improved_pdf():
    """测试改进的PDF解析"""
    print("🧪 测试改进的PDF解析")
    print("=" * 50)
    
    tm = TikuManager()
    questions = tm.load_tiku('1.电力安全工作规程（发电厂和变电站电气部分）安徽分公司题库（GB 26860—2011)')
    
    if questions:
        print(f"✅ 成功加载 {len(questions)} 道题目")
        print("\n前5道题目:")
        print("-" * 30)
        
        for i, q in enumerate(questions[:5], 1):
            print(f"\n{i}. 题目: {q['question'][:100]}...")
            print(f"   答案: {q['answer']}")
            print(f"   选项: {q['options']}")
            print(f"   题型: {q['type']}")
    else:
        print("❌ 加载失败")

if __name__ == "__main__":
    test_improved_pdf()
