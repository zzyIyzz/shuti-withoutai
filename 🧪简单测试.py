#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本 - 验证原始系统
"""

def test_original_system():
    """测试原始系统"""
    print("🧪 测试原始系统")
    print("=" * 50)
    
    try:
        # 测试题库管理
        print("📚 测试题库管理...")
        from 题库管理 import TikuManager
        
        tiku_manager = TikuManager()
        tiku_list = tiku_manager.get_tiku_list()
        
        print(f"✅ 找到 {len(tiku_list)} 个题库:")
        for tiku in tiku_list:
            print(f"  - {tiku}")
        
        # 测试Excel题库加载
        if tiku_list:
            print(f"\n📖 测试加载Excel题库: {tiku_list[0]}")
            questions = tiku_manager.load_tiku(tiku_list[0])
            
            if questions:
                print(f"✅ 成功加载 {len(questions)} 道题目")
                
                # 显示前3道题目
                for i, q in enumerate(questions[:3], 1):
                    print(f"\n题目 {i}:")
                    print(f"  题目: {q['question'][:50]}...")
                    print(f"  答案: {q['answer']}")
                    print(f"  题型: {q['type']}")
                    print(f"  选项: {q['options']}")
            else:
                print("❌ 加载题目失败")
        
        # 测试题型识别
        print(f"\n🧠 测试题型识别...")
        from 智能题型识别 import detect_question_type
        
        test_questions = [
            "下列哪个选项是正确的？A、选项1 B、选项2 C、选项3 D、选项4",
            "以下哪些是正确的？A、选项1 B、选项2 C、选项3 D、选项4",
            "这个说法是否正确？",
            "请填写空白处：_____是重要的。",
            "请简述你的观点。"
        ]
        
        for i, question in enumerate(test_questions, 1):
            result = detect_question_type(question, "A", {})
            print(f"  测试 {i}: {result}")
        
        print("\n✅ 原始系统测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_original_system()
