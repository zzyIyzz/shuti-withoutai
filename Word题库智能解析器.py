#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Word题库智能解析器
专门解决Word题库解析问题
"""

import re
from docx import Document
from pathlib import Path

class Word题库智能解析器:
    """Word题库智能解析器"""
    
    def __init__(self, word_file):
        self.word_file = Path(word_file)
        self.questions = []
        
    def parse(self):
        """智能解析Word题库"""
        try:
            print(f"正在智能解析Word题库: {self.word_file.name}")
            
            # 读取Word文档
            doc = Document(self.word_file)
            
            # 获取所有段落
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            
            print(f"找到 {len(paragraphs)} 个段落")
            
            # 智能识别题目模式
            题目列表 = self._智能识别题目(paragraphs)
            
            print(f"智能识别到 {len(题目列表)} 道题目")
            
            # 智能补全题目信息
            完整题目列表 = self._智能补全题目(题目列表)
            
            self.questions = 完整题目列表
            return self.questions
            
        except Exception as e:
            print(f"Word解析失败: {e}")
            return []
    
    def _智能识别题目(self, paragraphs):
        """智能识别题目（增强过滤）"""
        题目列表 = []
        当前题目 = None
        
        # 过滤规则：排除微题目和无关内容
        def _是有效题目(文本):
            """判断是否为有效题目"""
            if not 文本 or len(文本.strip()) < 10:
                return False
            
            # 排除微题目（太短的题目）
            if len(文本.strip()) < 20:
                return False
            
            # 排除无关内容
            无关关键词 = ['目录', '前言', '说明', '注意事项', '参考文献', '附录', '页眉', '页脚']
            for 关键词 in 无关关键词:
                if 关键词 in 文本:
                    return False
            
            # 排除纯数字或符号
            if 文本.strip().isdigit() or len(文本.strip()) < 5:
                return False
            
            # 排除明显的标题
            if 文本.startswith('第') and ('章' in 文本 or '节' in 文本):
                return False
            
            return True
        
        for i, paragraph in enumerate(paragraphs):
            # 首先检查是否为有效题目
            if not _是有效题目(paragraph):
                continue
                
            # 检查是否是题目开始
            if self._是题目开始(paragraph):
                if 当前题目:
                    题目列表.append(当前题目)
                
                当前题目 = {
                    'id': len(题目列表) + 1,
                    'question': paragraph,
                    'answer': '',
                    'options': {},
                    'type': 'unknown',
                    'explanation': ''
                }
            
            # 检查是否是选项
            elif 当前题目 and self._是选项(paragraph):
                选项字母 = self._提取选项字母(paragraph)
                if 选项字母:
                    当前题目['options'][选项字母] = self._清理选项内容(paragraph)
            
            # 检查是否是答案
            elif 当前题目 and self._是答案(paragraph):
                当前题目['answer'] = self._提取答案(paragraph)
            
            # 检查是否是解析
            elif 当前题目 and self._是解析(paragraph):
                当前题目['explanation'] = paragraph
        
        # 添加最后一个题目
        if 当前题目:
            题目列表.append(当前题目)
        
        return 题目列表
    
    def _是题目开始(self, text):
        """判断是否是题目开始（增强版）"""
        # 题目通常以数字开头
        if re.match(r'^\d+[、\.]\s*', text):
            return True
        
        # 或者包含问号
        if '？' in text or '?' in text:
            return True
        
        # 或者包含"下列"、"哪个"等关键词
        question_keywords = ['下列', '哪个', '哪项', '哪些', '哪几', '正确的是', '错误的是', '判断', '简述', '说明', '分析', '解释']
        if any(keyword in text for keyword in question_keywords):
            return True
        
        # 或者包含选项格式
        if re.search(r'[A-D][、\.]\s*\S+', text):
            return True
        
        return False
    
    def _是选项(self, text):
        """判断是否是选项"""
        # 选项通常以字母开头
        if re.match(r'^[A-L][、\.]\s*', text):
            return True
        
        # 或者包含选项模式
        if re.match(r'^[①②③④⑤⑥⑦⑧⑨⑩]', text):
            return True
        
        return False
    
    def _是答案(self, text):
        """判断是否是答案"""
        答案关键词 = ['答案', '正确答案', '标准答案', '答案：', '答案：']
        return any(keyword in text for keyword in 答案关键词)
    
    def _是解析(self, text):
        """判断是否是解析"""
        解析关键词 = ['解析', '解释', '说明', '原因', '依据']
        return any(keyword in text for keyword in 解析关键词)
    
    def _提取选项字母(self, text):
        """提取选项字母"""
        # 匹配 A. 格式
        match = re.match(r'^([A-L])[、\.]\s*', text)
        if match:
            return match.group(1)
        
        # 匹配 ①②③④ 格式
        if re.match(r'^[①②③④⑤⑥⑦⑧⑨⑩]', text):
            return chr(ord('A') + int(text[0]) - 0x2460)
        
        return None
    
    def _清理选项内容(self, text):
        """清理选项内容"""
        # 移除选项字母前缀
        text = re.sub(r'^[A-L][、\.]\s*', '', text)
        text = re.sub(r'^[①②③④⑤⑥⑦⑧⑨⑩]\s*', '', text)
        
        return text.strip()
    
    def _提取答案(self, text):
        """提取答案"""
        # 提取答案字母
        match = re.search(r'[A-L]', text)
        if match:
            return match.group()
        
        # 提取数字答案
        match = re.search(r'\d+', text)
        if match:
            return match.group()
        
        return text.strip()
    
    def _智能补全题目(self, 题目列表):
        """智能补全题目信息"""
        完整题目列表 = []
        
        for 题目 in 题目列表:
            # 智能识别题型
            题目['type'] = self._智能识别题型(题目)
            
            # 如果没有答案，智能补全
            if not 题目['answer']:
                题目['answer'] = self._智能补全答案(题目)
            
            # 如果没有选项，智能生成
            if not 题目['options']:
                题目['options'] = self._智能生成选项(题目)
            
            完整题目列表.append(题目)
        
        return 完整题目列表
    
    def _智能识别题型(self, 题目):
        """智能识别题型"""
        题目文本 = 题目['question'].lower()
        答案 = 题目['answer']
        选项 = 题目['options']
        
        # 判断题识别
        if self._是判断题(题目文本, 答案):
            return '判断题'
        
        # 选择题识别
        if 选项 and len(选项) > 0:
            if len(答案) > 1:
                return '多选题'
            else:
                return '单选题'
        
        # 简答题识别
        if self._是简答题(题目文本, 答案):
            return '简答题'
        
        # 填空题识别
        if self._是填空题(题目文本):
            return '填空题'
        
        return '判断题'  # 默认判断题
    
    def _是判断题(self, 题目文本, 答案):
        """判断是否为判断题"""
        # 答案特征
        if 答案 in ['A', 'B', '对', '错', '正确', '错误']:
            return True
        
        # 题目特征
        判断关键词 = ['是否正确', '是否', '对错', '正误', '判断']
        if any(keyword in 题目文本 for keyword in 判断关键词):
            return True
        
        return False
    
    def _是简答题(self, 题目文本, 答案):
        """判断是否为简答题"""
        简答关键词 = ['简述', '说明', '论述', '分析', '解释', '如何', '为什么', '什么是']
        if any(keyword in 题目文本 for keyword in 简答关键词):
            return True
        
        if len(答案) > 20:
            return True
        
        return False
    
    def _是填空题(self, 题目文本):
        """判断是否为填空题"""
        填空标记 = ['_', '____', '（）', '()', '【】', '[]']
        if any(mark in 题目文本 for mark in 填空标记):
            return True
        
        return False
    
    def _智能补全答案(self, 题目):
        """智能补全答案"""
        题目文本 = 题目['question'].lower()
        
        # 判断题答案补全
        if '正确' in 题目文本 or '对' in 题目文本:
            return 'A'
        elif '错误' in 题目文本 or '错' in 题目文本:
            return 'B'
        
        # 技术性描述通常是正确的
        技术词 = ['用于', '作用', '功能', '特点', '性质', '原理']
        if any(词 in 题目文本 for 词 in 技术词):
            return 'A'
        
        return 'A'  # 默认正确
    
    def _智能生成选项(self, 题目):
        """智能生成选项"""
        题目文本 = 题目['question']
        
        # 如果是判断题，生成标准选项
        if 题目['type'] == '判断题':
            return {
                'A': '正确',
                'B': '错误'
            }
        
        # 如果是选择题但没有选项，生成通用选项
        if 题目['type'] in ['单选题', '多选题']:
            return {
                'A': '选项A',
                'B': '选项B',
                'C': '选项C',
                'D': '选项D'
            }
        
        return {}


def 测试Word智能解析():
    """测试Word智能解析"""
    解析器 = Word题库智能解析器('题库/附件：安徽分公司电力生产培训题库(1).docx')
    结果 = 解析器.parse()
    
    print("解析结果:")
    for i, 题目 in enumerate(结果[:5], 1):
        print(f"第{i}题:")
        print(f"  题目: {题目['question'][:50]}...")
        print(f"  答案: {题目['answer']}")
        print(f"  题型: {题目['type']}")
        print(f"  选项: {题目['options']}")
        print()


if __name__ == '__main__':
    测试Word智能解析()
