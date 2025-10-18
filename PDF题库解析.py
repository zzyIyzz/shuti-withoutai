#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF题库解析器 - 简化版
支持基本的PDF题库解析功能
"""

import re
from pathlib import Path
from typing import List, Dict, Any
import warnings

# 尝试导入PDF处理库
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

class PDFTikuParser:
    """PDF题库解析器"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.questions = []
        
    def parse(self) -> List[Dict[str, Any]]:
        """解析PDF文件"""
        if not self.pdf_path.exists():
            print(f"❌ PDF文件不存在: {self.pdf_path}")
            return []
        
        print(f"📄 开始解析PDF题库: {self.pdf_path.name}")
        
        # 尝试使用pdfplumber
        if PDFPLUMBER_AVAILABLE:
            return self._parse_with_pdfplumber()
        elif PYPDF2_AVAILABLE:
            return self._parse_with_pypdf2()
        else:
            print("❌ 未安装PDF处理库")
            print("请运行以下命令安装:")
            print("pip install pdfplumber")
            print("或")
            print("pip install PyPDF2")
            return []
    
    def _parse_with_pdfplumber(self) -> List[Dict[str, Any]]:
        """使用pdfplumber解析PDF"""
        try:
            questions = []
            
            with pdfplumber.open(self.pdf_path) as pdf:
                print(f"📊 PDF页数: {len(pdf.pages)}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    print(f"🔍 解析第 {page_num} 页...")
                    
                    # 提取文本
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    # 解析题目
                    page_questions = self._parse_text_to_questions(text, page_num)
                    questions.extend(page_questions)
            
            print(f"✅ PDF解析完成，共提取 {len(questions)} 道题目")
            return questions
            
        except Exception as e:
            print(f"❌ pdfplumber解析失败: {e}")
            return []
    
    def _parse_with_pypdf2(self) -> List[Dict[str, Any]]:
        """使用PyPDF2解析PDF"""
        try:
            questions = []
            
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                print(f"📊 PDF页数: {len(pdf_reader.pages)}")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    print(f"🔍 解析第 {page_num} 页...")
                    
                    # 提取文本
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    # 解析题目
                    page_questions = self._parse_text_to_questions(text, page_num)
                    questions.extend(page_questions)
            
            print(f"✅ PDF解析完成，共提取 {len(questions)} 道题目")
            return questions
            
        except Exception as e:
            print(f"❌ PyPDF2解析失败: {e}")
            return []
    
    def _parse_text_to_questions(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """将文本解析为题目"""
        questions = []
        
        # 清理文本
        text = re.sub(r'\s+', ' ', text)  # 合并多个空格
        text = text.strip()
        
        # 题目模式匹配
        question_patterns = [
            r'(\d+)[\.、]\s*([^。！？]*[。！？])',  # 数字开头
            r'(\d+)\s*[\.、]\s*([^。！？]*[。！？])',  # 数字+点
            r'第(\d+)题[：:]\s*([^。！？]*[。！？])',  # 第X题
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                question_num = match[0]
                question_text = match[1].strip()
                
                if len(question_text) > 10:  # 过滤太短的文本
                    question = {
                        'id': len(questions) + 1,
                        'question': question_text,
                        'answer': '',
                        'options': {},
                        'type': 'unknown',
                        'source': f'PDF第{page_num}页',
                        'page': page_num
                    }
                    questions.append(question)
        
        # 如果没有匹配到标准格式，尝试按段落分割
        if not questions:
            paragraphs = text.split('\n')
            for i, para in enumerate(paragraphs):
                para = para.strip()
                if len(para) > 20 and any(keyword in para for keyword in ['？', '?', '。', '：']):
                    question = {
                        'id': len(questions) + 1,
                        'question': para,
                        'answer': '',
                        'options': {},
                        'type': 'unknown',
                        'source': f'PDF第{page_num}页段落{i+1}',
                        'page': page_num
                    }
                    questions.append(question)
        
        return questions

def test_pdf_parser():
    """测试PDF解析器"""
    print("🧪 测试PDF解析器")
    print("=" * 50)
    
    # 查找PDF文件
    pdf_files = list(Path('.').glob('**/*.pdf'))
    
    if not pdf_files:
        print("❌ 未找到PDF文件")
        return
    
    for pdf_file in pdf_files:
        print(f"\n📄 测试文件: {pdf_file.name}")
        
        parser = PDFTikuParser(str(pdf_file))
        questions = parser.parse()
        
        if questions:
            print(f"✅ 成功解析 {len(questions)} 道题目")
            
            # 显示前3个题目示例
            for i, q in enumerate(questions[:3], 1):
                print(f"\n示例 {i}:")
                print(f"  题目: {q['question'][:50]}...")
                print(f"  来源: {q['source']}")
        else:
            print("❌ 解析失败或未找到题目")

if __name__ == "__main__":
    test_pdf_parser()
