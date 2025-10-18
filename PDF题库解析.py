#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF题库解析模块
支持从PDF中提取题库内容
"""

import re
from pathlib import Path

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    pdfplumber = None

class PDFTikuParser:
    def __init__(self, pdf_file):
        self.pdf_file = Path(pdf_file)
        self.questions = []
    
    def parse(self):
        """解析PDF题库"""
        if not PDF_SUPPORT:
            print("错误：需要安装 pdfplumber 库")
            print("运行: pip install pdfplumber")
            return []
        
        try:
            # 提取PDF文本
            print(f"正在读取PDF文件: {self.pdf_file.name}")
            text = self.extract_text_from_pdf()
            
            if not text:
                print("警告：PDF文件为空或无法提取文本")
                return []
            
            print(f"成功提取文本，共 {len(text)} 字符")
            
            # 尝试提取表格
            tables = self.extract_tables_from_pdf()
            if tables:
                print(f"发现 {len(tables)} 个表格，尝试从表格解析...")
                questions_from_tables = self.parse_tables(tables)
                if questions_from_tables:
                    print(f"从表格中解析到 {len(questions_from_tables)} 道题")
                    return questions_from_tables
            
            # 从文本解析
            print("尝试从文本解析题目...")
            questions = self.parse_text(text)
            
            if questions:
                print(f"成功解析 {len(questions)} 道题目")
            else:
                print("警告：未能识别题目格式")
            
            return questions
            
        except Exception as e:
            print(f"解析PDF文件失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def extract_text_from_pdf(self):
        """从PDF提取文本"""
        text_parts = []
        
        with pdfplumber.open(self.pdf_file) as pdf:
            total_pages = len(pdf.pages)
            print(f"PDF共 {total_pages} 页，正在提取...")
            
            for i, page in enumerate(pdf.pages, 1):
                if i % 10 == 0:
                    print(f"  已处理 {i}/{total_pages} 页")
                
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return '\n'.join(text_parts)
    
    def extract_tables_from_pdf(self):
        """从PDF提取表格"""
        all_tables = []
        
        try:
            with pdfplumber.open(self.pdf_file) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        all_tables.extend(tables)
        except:
            pass
        
        return all_tables
    
    def parse_tables(self, tables):
        """解析表格数据"""
        questions = []
        
        for table in tables:
            if not table or len(table) < 2:
                continue
            
            # 第一行作为表头
            headers = [str(cell).strip() if cell else '' for cell in table[0]]
            
            # 识别列
            col_map = self.identify_columns(headers)
            
            if not col_map.get('question') or not col_map.get('answer'):
                continue
            
            # 解析数据行
            for row in table[1:]:
                if not row or not any(row):
                    continue
                
                cells = [str(cell).strip() if cell else '' for cell in row]
                
                if col_map['question'] >= len(cells):
                    continue
                
                question_text = cells[col_map['question']]
                if not question_text or question_text == 'None':
                    continue
                
                question = {
                    'id': len(questions) + 1,
                    'question': question_text,
                    'answer': '',
                    'options': {},
                    'type': 'unknown',
                    'explanation': ''
                }
                
                # 答案
                if col_map.get('answer') and col_map['answer'] < len(cells):
                    answer = cells[col_map['answer']]
                    if answer and answer != 'None':
                        question['answer'] = answer
                
                # 选项
                for opt_key, opt_idx in col_map.get('options', {}).items():
                    if opt_idx < len(cells):
                        opt_value = cells[opt_idx]
                        if opt_value and opt_value != 'None':
                            question['options'][opt_key] = opt_value
                
                # 题型
                if col_map.get('type') and col_map['type'] < len(cells):
                    qtype = cells[col_map['type']]
                    if qtype and qtype != 'None':
                        question['type'] = qtype
                
                # 解析
                if col_map.get('explanation') and col_map['explanation'] < len(cells):
                    exp = cells[col_map['explanation']]
                    if exp and exp != 'None':
                        question['explanation'] = exp
                
                # 自动判断题型
                if question['type'] == 'unknown':
                    question['type'] = self.detect_question_type(question)
                
                if question['answer']:
                    questions.append(question)
        
        return questions
    
    def parse_text(self, text):
        """从文本解析题目"""
        questions = []
        
        # 尝试多种题号格式分割
        patterns = [
            r'\n(\d+)、\s*',           # 1、（中文顿号）
            r'\n(\d+)[.．]\s*',        # 1. 或 1．
            r'\n(\d+)\)\s*',           # 1)
            r'\n\((\d+)\)\s*',         # (1)
            r'\n\[(\d+)\]\s*',         # [1]
            r'\n第(\d+)题[：:]\s*',     # 第1题：
        ]
        
        for pattern in patterns:
            parts = re.split(pattern, text)
            if len(parts) > 3:  # 找到了分割点
                print(f"使用模式 {pattern} 分割题目")
                
                for i in range(1, len(parts), 2):
                    if i + 1 < len(parts):
                        q_num = parts[i]
                        q_content = parts[i + 1].strip()
                        
                        question = self.parse_single_question(q_content, int(q_num))
                        if question:
                            questions.append(question)
                
                if questions:
                    break
        
        # 如果没有找到题号，尝试识别连续的题目
        if not questions:
            print("未找到明确题号，尝试识别连续题目...")
            questions = self.parse_continuous_questions(text)
        
        return questions
    
    def parse_single_question(self, text, q_id):
        """解析单个题目文本"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        question = {
            'id': q_id,
            'question': '',
            'answer': '',
            'options': {},
            'type': 'unknown',
            'explanation': ''
        }
        
        # 合并所有行作为完整题目文本
        full_text = ' '.join(lines)
        
        # 尝试从括号中提取答案（常见于填空题）
        # 格式：题目内容____（答案）或 题目内容（答案）
        import re
        
        # 模式1: ____（答案） 或 _____(答案)
        pattern1 = r'[_\s]*[（(]([^）)]+)[）)]'
        matches1 = list(re.finditer(pattern1, full_text))
        
        if matches1:
            # 提取答案
            答案列表 = [m.group(1).strip() for m in matches1]
            question['answer'] = '、'.join(答案列表) if len(答案列表) > 1 else 答案列表[0]
            
            # 清理题目（移除答案括号，保留下划线或用空格替代）
            cleaned_text = full_text
            for match in reversed(matches1):  # 从后往前替换，避免索引问题
                # 保留括号前的下划线或空格
                cleaned_text = cleaned_text[:match.start()] + '____' + cleaned_text[match.end():]
            
            question['question'] = cleaned_text.strip()
            question['type'] = '填空题'
        else:
            # 第一行通常是题目
            question['question'] = lines[0]
        
        # 解析其他行
        for line in lines[1:]:
            # 选项 (支持多种格式)
            opt_match = re.match(r'^([A-F])[、.．)\s:：]\s*(.+)', line)
            if opt_match:
                question['options'][opt_match.group(1)] = opt_match.group(2).strip()
                continue
            
            # 答案 (多种格式)
            ans_patterns = [
                r'^(?:答案|正确答案|参考答案|标准答案)[：:]\s*(.+)',
                r'^答[：:]\s*(.+)',
            ]
            for ans_pattern in ans_patterns:
                ans_match = re.match(ans_pattern, line, re.IGNORECASE)
                if ans_match:
                    question['answer'] = ans_match.group(1).strip()
                    break
            
            # 题型
            type_match = re.match(r'^(?:题型|类型)[：:]\s*(.+)', line)
            if type_match:
                question['type'] = type_match.group(1).strip()
                continue
            
            # 解析
            exp_patterns = [
                r'^(?:解析|解释|说明|提示)[：:]\s*(.+)',
            ]
            for exp_pattern in exp_patterns:
                exp_match = re.match(exp_pattern, line)
                if exp_match:
                    question['explanation'] = exp_match.group(1).strip()
                    break
        
        # 优先从题目文本中提取选项
        题目中的选项 = self.从题目中提取选项(question['question'])
        if 题目中的选项:
            question['options'] = 题目中的选项
            # 清理题目文本，移除选项部分
            question['question'] = self.清理题目文本(question['question'])
        elif not question['options']:
            # 如果题目中包含选项，尝试从题目中提取
            question = self.extract_options_from_question(question)
        
        # 自动判断题型
        if question['type'] == 'unknown':
            question['type'] = self.detect_question_type(question)
        
        return question if question['answer'] else None
    
    def parse_continuous_questions(self, text):
        """解析没有明确题号的连续题目"""
        questions = []
        
        # 尝试通过"答案："来分割题目
        parts = re.split(r'\n(?=.{0,200}[答答案正确答案][：:])', text)
        
        for i, part in enumerate(parts, 1):
            if len(part.strip()) < 10:
                continue
            
            question = self.parse_single_question(part, i)
            if question:
                questions.append(question)
        
        return questions
    
    def extract_options_from_question(self, question):
        """从题目文本中提取选项"""
        q_text = question['question']
        
        # 检查是否包含A. B. C. D.格式的选项
        option_pattern = r'([A-F])[.、]\s*([^A-F]+?)(?=\s*[A-F][.、]|\s*答案|$)'
        matches = re.findall(option_pattern, q_text)
        
        if matches:
            # 提取纯题干（去除选项部分）
            first_option_pos = q_text.find(matches[0][0] + '.')
            if first_option_pos == -1:
                first_option_pos = q_text.find(matches[0][0] + '、')
            
            if first_option_pos > 0:
                question['question'] = q_text[:first_option_pos].strip()
                
                # 添加选项
                for opt_key, opt_value in matches:
                    question['options'][opt_key] = opt_value.strip()
        
        return question
    
    def identify_columns(self, headers):
        """识别表格列（与Word/Excel相同）"""
        col_map = {}
        
        # 题目列
        question_keywords = ['题目', '试题', '问题', '题干', 'question', 'content', '内容']
        for i, h in enumerate(headers):
            h_lower = h.lower()
            if any(kw in h_lower for kw in question_keywords):
                col_map['question'] = i
                break
        
        # 答案列
        answer_keywords = ['答案', '正确答案', 'answer', '标准答案', '参考答案']
        for i, h in enumerate(headers):
            h_lower = h.lower()
            if any(kw in h_lower for kw in answer_keywords):
                col_map['answer'] = i
                break
        
        # 选项列
        option_map = {}
        for opt in ['A', 'B', 'C', 'D', 'E', 'F']:
            for i, h in enumerate(headers):
                h_clean = h.strip()
                if h_clean == opt or h_clean == f'选项{opt}' or '选项' in h_clean and opt in h_clean:
                    option_map[opt] = i
                    break
        if option_map:
            col_map['options'] = option_map
        
        # 题型列
        type_keywords = ['题型', '类型', 'type']
        for i, h in enumerate(headers):
            h_lower = h.lower()
            if any(kw in h_lower for kw in type_keywords):
                col_map['type'] = i
                break
        
        # 解析列
        exp_keywords = ['解析', '解释', '说明', 'explanation']
        for i, h in enumerate(headers):
            h_lower = h.lower()
            if any(kw in h_lower for kw in exp_keywords):
                col_map['explanation'] = i
                break
        
        return col_map
    
    def detect_question_type(self, question):
        """题型识别 - 使用智能识别引擎"""
        try:
            from 智能题型识别 import detect_question_type
            return detect_question_type(
                question['question'],
                question['answer'],
                question.get('options')
            )
        except:
            return self._simple_detect(question)
    
    def _simple_detect(self, question):
        """备用题型识别方法 - 详细完备版（与题库管理模块保持一致）"""
        import re
        
        q_text = question['question']
        answer = str(question['answer']).strip().upper()
        q_lower = q_text.lower()
        
        # ========== 第一优先级：判断题识别 ==========
        判断题答案集 = {'对', '错', '√', '×', 'T', 'F', 'TRUE', 'FALSE', '正确', '错误', '是', '否'}
        if answer in 判断题答案集:
            return '判断题'
        if '对错' in answer or ('对' in answer and '错' in answer):
            return '判断题'
        
        判断题关键词 = ['是否正确', '对吗', '对么', '错吗', '错么', '判断题', '判断正误', 
                    '说法正确', '说法错误', '表述正确', '表述错误',
                    '观点正确', '观点错误', '是否准确', '对不对', '错不错']
        if any(keyword in q_lower for keyword in 判断题关键词):
            return '判断题'
        
        # ========== 第二优先级：选择题识别 ==========
        选项模式列表 = [
            r'[A-F][、\.]\s*\S+',
            r'[A-F]\s*[、\.]\s*\S+',
        ]
        
        has_options = False
        for 模式 in 选项模式列表:
            if re.search(模式, q_text):
                has_options = True
                break
        
        if question.get('options'):
            has_options = True
        
        # 多选题识别
        if has_options or '多选' in q_lower or '多项' in q_lower:
            if len(answer) > 1 and all(c in 'ABCDEF' for c in answer):
                return '多选题'
            
            多选关键词 = ['多选', '多项选择', '多项', '哪些', '哪几个', '哪几项', 
                      '包括哪些', '包含哪些', '有哪些', '正确的有', '错误的有',
                      '以下正确', '以下错误', '下列正确', '下列错误']
            if any(keyword in q_lower for keyword in 多选关键词):
                return '多选题'
        
        # 单选题识别
        if has_options:
            if len(answer) == 1 and answer in 'ABCDEF':
                return '单选题'
            
            单选关键词 = ['单选', '单项选择', '单项', '哪个', '哪项', '哪一',
                      '最正确', '最合适', '最恰当', '最准确', '最合理']
            if any(keyword in q_lower for keyword in 单选关键词):
                return '单选题'
            
            return '单选题'
        
        # 无选项但答案是字母
        if len(answer) > 1 and all(c in 'ABCDEF' for c in answer):
            return '多选题'
        if len(answer) == 1 and answer in 'ABCDEF':
            return '单选题'
        
        # ========== 第三优先级：简答题识别 ==========
        if len(answer) > 20 and any(p in answer for p in ['。', '，', '；', '、']):
            return '简答题'
        
        简答题关键词 = ['简述', '简要说明', '说明', '论述', '阐述', '分析', '解释', 
                    '描述', '叙述', '介绍', '回答', '解答', '谈谈', '试述',
                    '如何', '怎样', '怎么', '为什么', '为何',
                    '什么是', '何为', '定义', '概念', '含义']
        if any(keyword in q_lower for keyword in 简答题关键词):
            if len(answer) > 5:
                return '简答题'
        
        # ========== 第四优先级：填空题识别 ==========
        填空标记 = ['_', '____', '（）', '()', '【】', '[]']
        if any(mark in q_text for mark in 填空标记):
            return '填空题'
        
        填空句式 = [
            r'是\s*[（(]?\s*[）)]?',
            r'为\s*[（(]?\s*[）)]?',
            r'应\s*[（(]?\s*[）)]?',
            r'等于\s*[（(]?\s*[）)]?',
        ]
        if any(re.search(pattern, q_text) for pattern in 填空句式):
            return '填空题'
        
        技术单位 = ['MPa', 'KPA', 'PA', 'KV', 'V', 'MV', 'A', 'MA', 'KA',
                  'W', 'KW', 'MW', 'HZ', 'KHZ', 'MHZ', 'Ω', 'KΩ', 'MΩ',
                  '米', '厘米', '毫米', '千米', '克', '千克', '吨', '升', '毫升',
                  '度', '℃', '%', '‰', '年', '月', '日', '天', '小时', '分钟', '秒']
        
        if any(char.isdigit() for char in answer):
            if any(unit in answer for unit in 技术单位):
                return '填空题'
            if re.search(r'\d+', answer):
                return '填空题'
        
        填空关键词 = ['等于', '约为', '大约', '标准', '规定', '要求',
                    '必须', '应该', '需要', '达到', '超过', '低于',
                    '称为', '叫做', '简称']
        if any(keyword in q_lower for keyword in 填空关键词):
            if not (len(answer) <= 2 and all(c in 'ABCDEF' for c in answer)):
                return '填空题'
        
        # ========== 最终兜底策略 ==========
        if len(answer) > 15:
            return '简答题'
        elif len(answer) > 0:
            return '填空题'
        
        return '未知'
    
    def 从题目中提取选项(self, 题目文本):
        """从题目文本中提取选项 - 与题库管理模块保持一致"""
        import re
        
        # 多种选项模式，按优先级排序
        选项模式列表 = [
            r'([A-D])[、\.]\s*([^A-D]*?)(?=[A-D][、\.]|$)',  # A、内容B、内容
            r'([A-D]\.\s*[^A-D]*?)(?=[A-D]\.|$)',           # A. 内容B. 内容
            r'([A-D])\s*[、\.]\s*([^A-D]*?)(?=[A-D]\s*[、\.]|$)',  # A 、内容B 、内容
            r'([A-D])\s*[、\.]\s*([^A-D]+?)(?=[A-D]\s*[、\.]|$)',  # A . 内容B . 内容
        ]
        
        选项匹配 = []
        for 模式 in 选项模式列表:
            匹配结果 = re.findall(模式, 题目文本)
            if 匹配结果:
                选项匹配 = 匹配结果
                break
        
        if not 选项匹配:
            return {}
        
        选项字典 = {}
        for 匹配项 in 选项匹配:
            if len(匹配项) == 2:
                选项字母, 选项内容 = 匹配项
            else:
                # 处理只有选项字母的情况
                选项字母 = 匹配项[0] if 匹配项 else ''
                选项内容 = ''
            
            选项内容 = 选项内容.strip()
            # 移除末尾的标点符号
            if 选项内容.endswith(('。', '，', '、', ' ')):
                选项内容 = 选项内容.rstrip('。，、 ')
            if 选项内容:  # 确保选项内容不为空
                选项字典[选项字母] = 选项内容
        
        return 选项字典
    
    def 清理题目文本(self, 题目文本):
        """清理题目文本，移除选项部分"""
        import re
        
        # 移除选项部分：A、内容B、内容C、内容D、内容 或 A. 内容B. 内容C. 内容D. 内容
        选项模式1 = r'[A-D][、\.]\s*[^A-D]*?(?=[A-D][、\.]|$)'
        选项模式2 = r'[A-D]\.\s*[^A-D]*(?=[A-D]\.|$)'
        
        清理后文本 = re.sub(选项模式1, '', 题目文本)
        清理后文本 = re.sub(选项模式2, '', 清理后文本)
        
        # 清理多余的标点和空格
        清理后文本 = re.sub(r'[。，、\s]+$', '', 清理后文本)
        
        return 清理后文本.strip()

