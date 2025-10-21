#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超级PDF解析器 - 专门处理复杂PDF格式
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

class SuperPDFTikuParser:
    """超级PDF解析器 - 专门处理复杂PDF格式"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        
    def parse(self) -> List[Dict[str, Any]]:
        """解析PDF题库"""
        try:
            import pdfplumber
            return self._parse_with_pdfplumber()
        except ImportError:
            try:
                import PyPDF2
                return self._parse_with_pypdf2()
            except ImportError:
                print("❌ 需要安装PDF解析库:")
                print("pip install pdfplumber")
                print("或")
                print("pip install PyPDF2")
                return []
    
    def _parse_with_pdfplumber(self) -> List[Dict[str, Any]]:
        """使用pdfplumber解析PDF"""
        try:
            import pdfplumber
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
    
    def _parse_text_to_questions(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """超级文本解析为题目"""
        questions = []
        
        # 清理文本
        text = re.sub(r'\s+', ' ', text)  # 合并多个空格
        text = text.strip()
        
        # 按行分割文本
        lines = text.split('\n')
        
        # 使用更智能的解析策略
        questions = self._smart_parse_lines(lines, page_num)
        
        return questions
    
    def _smart_parse_lines(self, lines: List[str], page_num: int) -> List[Dict[str, Any]]:
        """智能解析行"""
        questions = []
        current_question = None
        current_options = {}
        current_answer = ""
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            # 检查是否是题目开始
            question_info = self._detect_question_start(line)
            if question_info:
                # 保存之前的题目
                if current_question:
                    questions.append(self._create_question(current_question, current_options, current_answer, page_num))
                
                # 开始新题目
                current_question = question_info['text']
                current_options = {}
                current_answer = ""
                
                # 检查下一行是否是选项
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if self._is_option_line(next_line):
                        # 提取选项
                        options = self._extract_options_from_line(next_line)
                        current_options.update(options)
                        i += 1  # 跳过选项行
                
                i += 1
                continue
            
            # 检查是否是选项行
            if self._is_option_line(line) and current_question:
                options = self._extract_options_from_line(line)
                current_options.update(options)
                i += 1
                continue
            
            # 检查是否是答案行
            answer_match = self._is_answer_line(line)
            if answer_match and current_question:
                current_answer = answer_match
                i += 1
                continue
            
            # 如果当前有题目，可能是题目内容的延续
            if current_question and not self._is_option_line(line):
                # 检查是否包含选项内容
                if self._contains_options(line):
                    # 从题目文本中提取选项
                    extracted_options = self._extract_options_from_text(line)
                    current_options.update(extracted_options)
                    # 移除选项内容，保留题目内容
                    line = self._remove_options_from_text(line)
                
                current_question += " " + line
            
            i += 1
        
        # 保存最后一个题目
        if current_question:
            questions.append(self._create_question(current_question, current_options, current_answer, page_num))
        
        return questions
    
    def _detect_question_start(self, line: str) -> Dict[str, str]:
        """检测题目开始"""
        # 题目开始模式
        patterns = [
            r'^(\d+)[\.、]\s*(.+)$',  # 数字开头
            r'^第(\d+)题[：:]\s*(.+)$',  # 第X题
            r'^(\d+)\s*[\.、]\s*(.+)$',  # 数字+点
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                return {
                    'text': match.group(2).strip(),
                    'number': match.group(1)
                }
        
        return None
    
    def _is_option_line(self, line: str) -> bool:
        """判断是否是选项行"""
        # 选项模式
        patterns = [
            r'^[A-Z]、.+$',  # A、选项内容
            r'^[A-Z]\.\s*.+$',  # A. 选项内容
            r'^[A-Z]\s+.+$',  # A 选项内容
        ]
        
        for pattern in patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _extract_options_from_line(self, line: str) -> Dict[str, str]:
        """从行中提取选项"""
        options = {}
        
        # 选项模式
        patterns = [
            r'([A-Z])、([^A-Z]+?)(?=[A-Z]、|$)',  # A、选项内容
            r'([A-Z])\.([^A-Z]+?)(?=[A-Z]\.|$)',  # A.选项内容
            r'([A-Z])\s+([^A-Z]+?)(?=[A-Z]\s+|$)',  # A 选项内容
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                key = match[0]
                value = match[1].strip()
                if len(value) > 0:
                    options[key] = value
        
        return options
    
    def _is_answer_line(self, line: str) -> str:
        """判断是否是答案行"""
        # 答案模式
        patterns = [
            r'^答案[：:]\s*([A-Z]+)$',  # 答案：A
            r'^正确答案[：:]\s*([A-Z]+)$',  # 正确答案：A
            r'^答案\s*([A-Z]+)$',  # 答案A
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _contains_options(self, text: str) -> bool:
        """检查文本是否包含选项"""
        # 检查是否包含选项模式
        patterns = [
            r'[A-Z]、[^A-Z]',  # A、选项内容
            r'[A-Z]\.[^A-Z]',  # A.选项内容
            r'[A-Z]\s+[^A-Z]',  # A 选项内容
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _extract_options_from_text(self, text: str) -> Dict[str, str]:
        """从文本中提取选项"""
        options = {}
        
        # 选项模式
        patterns = [
            r'([A-Z])、([^A-Z]+?)(?=[A-Z]、|$)',  # A、选项内容
            r'([A-Z])\.([^A-Z]+?)(?=[A-Z]\.|$)',  # A.选项内容
            r'([A-Z])\s+([^A-Z]+?)(?=[A-Z]\s+|$)',  # A 选项内容
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                key = match[0]
                value = match[1].strip()
                if len(value) > 0:
                    options[key] = value
        
        return options
    
    def _remove_options_from_text(self, text: str) -> str:
        """从文本中移除选项内容"""
        # 移除选项模式
        patterns = [
            r'[A-Z]、[^A-Z]+?(?=[A-Z]、|$)',  # A、选项内容
            r'[A-Z]\.[^A-Z]+?(?=[A-Z]\.|$)',  # A.选项内容
            r'[A-Z]\s+[^A-Z]+?(?=[A-Z]\s+|$)',  # A 选项内容
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text)
        
        return text.strip()
    
    def _create_question(self, question_text: str, options: Dict[str, str], answer: str, page_num: int) -> Dict[str, Any]:
        """创建题目对象"""
        # 清理题目文本
        question_text = self._clean_question_text(question_text)
        
        # 从题目文本中提取答案（如果存在）
        extracted_answer = self._extract_answer_from_text(question_text)
        if extracted_answer:
            answer = extracted_answer
            question_text = self._remove_answer_from_text(question_text)
        
        # 从题目文本中提取选项（如果存在）
        if not options:
            extracted_options = self._extract_options_from_text(question_text)
            if extracted_options:
                options = extracted_options
                question_text = self._remove_options_from_text(question_text)
        
        return {
            'id': 0,  # 将在外部设置
            'question': question_text,
            'answer': answer,
            'options': options,
            'type': 'unknown',
            'source': f'PDF第{page_num}页',
            'page': page_num
        }
    
    def _clean_question_text(self, text: str) -> str:
        """清理题目文本"""
        # 移除多余的标点符号
        text = re.sub(r'[。！？]+$', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _extract_answer_from_text(self, text: str) -> str:
        """从题目文本中提取答案"""
        # 查找括号中的答案
        patterns = [
            r'\(([A-Z]+)\)',  # (A)
            r'（([A-Z]+)）',  # （A）
            r'答案[：:]\s*([A-Z]+)',  # 答案：A
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return ""
    
    def _remove_answer_from_text(self, text: str) -> str:
        """从题目文本中移除答案"""
        # 移除括号中的答案
        text = re.sub(r'\([A-Z]+\)', '', text)
        text = re.sub(r'（[A-Z]+）', '', text)
        text = re.sub(r'答案[：:]\s*[A-Z]+', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

def test_super_pdf_parser():
    """测试超级PDF解析器"""
    print("🧪 测试超级PDF解析器")
    print("=" * 50)
    
    # 查找PDF文件
    pdf_files = list(Path('题库').glob('*.pdf'))
    
    if not pdf_files:
        print("❌ 未找到PDF文件")
        return
    
    for pdf_file in pdf_files:
        print(f"\n📄 测试文件: {pdf_file.name}")
        
        parser = SuperPDFTikuParser(str(pdf_file))
        questions = parser.parse()
        
        if questions:
            print(f"✅ 成功解析 {len(questions)} 道题目")
            
            # 显示前5个题目示例
            for i, q in enumerate(questions[:5], 1):
                print(f"\n示例 {i}:")
                print(f"  题目: {q['question'][:100]}...")
                print(f"  答案: {q['answer']}")
                print(f"  选项: {q['options']}")
                print(f"  来源: {q['source']}")
        else:
            print("❌ 解析失败或未找到题目")

if __name__ == "__main__":
    test_super_pdf_parser()
