#!/usr/bin/env python
"""
PDF解析诊断工具 - 分析PDF解析问题
"""

import sys
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.io.readers import DocumentReader


def diagnose_pdf_parsing():
    """诊断PDF解析问题"""
    print("🔍 PDF解析诊断")
    print("=" * 40)
    
    reader = DocumentReader()
    
    # 检查PDF文件
    pdf_file = Path("../题库/1.电力安全工作规程（发电厂和变电站电气部分）安徽分公司题库（GB 26860—2011).pdf")
    
    if not pdf_file.exists():
        print("❌ PDF文件不存在")
        return
    
    try:
        print("🔄 读取PDF文档...")
        document = reader.read_document(str(pdf_file))
        
        print(f"📊 文档信息:")
        print(f"  文本块数量: {len(document.blocks)}")
        print(f"  总字符数: {sum(len(block.text) for block in document.blocks)}")
        
        # 显示前10个文本块
        print(f"\n📝 前10个文本块内容:")
        for i, block in enumerate(document.blocks[:10]):
            print(f"  块 {i+1}: {repr(block.text[:100])}")
            print(f"    长度: {len(block.text)}")
            print()
        
        # 分析文本块特征
        print(f"📈 文本块特征分析:")
        lengths = [len(block.text) for block in document.blocks]
        print(f"  平均长度: {sum(lengths)/len(lengths):.1f}")
        print(f"  最短长度: {min(lengths)}")
        print(f"  最长长度: {max(lengths)}")
        
        # 查找可能的题目标记
        print(f"\n🔍 题目标记分析:")
        question_patterns = [
            r'\d+[\.\、\)]',  # 数字编号
            r'[A-F][\.\、\)]',  # 选项标记
            r'答案[:：]',  # 答案标记
            r'[？?]',  # 问号
        ]
        
        for pattern_name, pattern in [
            ("数字编号", r'\d+[\.\、\)]'),
            ("选项标记", r'[A-F][\.\、\)]'),
            ("答案标记", r'答案[:：]'),
            ("问号", r'[？?]'),
        ]:
            import re
            count = 0
            for block in document.blocks:
                count += len(re.findall(pattern, block.text))
            print(f"  {pattern_name}: {count} 个")
        
        # 查找包含完整题目的文本块
        print(f"\n🎯 可能的题目块:")
        for i, block in enumerate(document.blocks):
            text = block.text.strip()
            if len(text) > 50 and ('A、' in text or 'A.' in text) and '?' in text:
                print(f"  块 {i+1}: {text[:150]}...")
                print()
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    diagnose_pdf_parsing()
