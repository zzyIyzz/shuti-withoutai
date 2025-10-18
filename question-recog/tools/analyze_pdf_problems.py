#!/usr/bin/env python
"""
问题根因分析 - 为什么PDF识别率这么低
"""

import sys
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.io.readers import DocumentReader
from src.parsing.layout_state_machine import LayoutStateMachine


def analyze_pdf_problems():
    """分析PDF识别问题的根本原因"""
    print("🔍 PDF识别问题根因分析")
    print("=" * 50)
    
    reader = DocumentReader()
    pdf_file = Path("../题库/1.电力安全工作规程（发电厂和变电站电气部分）安徽分公司题库（GB 26860—2011).pdf")
    
    if not pdf_file.exists():
        print("❌ PDF文件不存在")
        return
    
    try:
        # 读取文档
        document = reader.read_document(str(pdf_file))
        
        print(f"📊 PDF解析结果:")
        print(f"  文本块总数: {len(document.blocks)}")
        
        # 分析文本块内容
        print(f"\n🔍 文本块内容分析:")
        
        # 查找包含题目特征的块
        question_blocks = []
        for i, block in enumerate(document.blocks):
            text = block.text.strip()
            
            # 题目特征：包含数字编号 + 内容 + 选项标记
            if (len(text) > 20 and 
                any(char.isdigit() for char in text[:10]) and  # 开头有数字
                ('A、' in text or 'A.' in text or 'A）' in text)):  # 有选项
                question_blocks.append((i, text))
        
        print(f"  可能的题目块: {len(question_blocks)} 个")
        
        # 显示前5个题目块
        print(f"\n📝 题目块示例:")
        for i, (block_idx, text) in enumerate(question_blocks[:5]):
            print(f"  题目 {i+1} (块 {block_idx}):")
            print(f"    {text[:200]}...")
            print()
        
        # 分析状态机解析问题
        print(f"🤖 状态机解析测试:")
        parser = LayoutStateMachine()
        
        # 测试解析
        try:
            results = parser.parse(document.blocks)
            print(f"  解析结果: {len(results)} 个题目")
            
            # 分析解析失败的原因
            if len(results) < len(question_blocks) * 0.5:  # 解析成功率低于50%
                print(f"  ❌ 解析成功率过低!")
                print(f"  🔍 可能原因:")
                print(f"    1. PDF文本块被过度分割")
                print(f"    2. 题目跨越多个文本块")
                print(f"    3. 状态机无法正确识别题目边界")
                
                # 检查文本块分割问题
                print(f"\n📋 文本块分割分析:")
                short_blocks = [b for b in document.blocks if len(b.text.strip()) < 10]
                print(f"  短文本块 (<10字符): {len(short_blocks)} 个")
                
                single_char_blocks = [b for b in document.blocks if len(b.text.strip()) == 1]
                print(f"  单字符块: {len(single_char_blocks)} 个")
                
                # 显示一些短块内容
                print(f"  短块示例:")
                for i, block in enumerate(short_blocks[:10]):
                    print(f"    '{block.text.strip()}'")
                
        except Exception as e:
            print(f"  ❌ 状态机解析失败: {e}")
        
        # 给出解决方案
        print(f"\n💡 解决方案:")
        print(f"  1. 优化PDF文本提取 - 合并相关文本块")
        print(f"  2. 增强状态机 - 改进跨块题目识别")
        print(f"  3. 添加PDF专用规则 - 处理分割问题")
        print(f"  4. 使用OCR后处理 - 重新组织文本结构")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    analyze_pdf_problems()
