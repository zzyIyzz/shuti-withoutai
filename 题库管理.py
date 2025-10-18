#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
题库管理模块
负责题库的加载、解析和管理
"""

import os
import json
import openpyxl
from pathlib import Path
from Word题库解析 import WordTikuParser
from PDF题库解析 import PDFTikuParser

class TikuManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.tiku_dir = self.base_dir / '题库'  # 题库文件夹
        self.cache_dir = self.base_dir / '.cache'
        self.cache_dir.mkdir(exist_ok=True)
        self.tiku_cache = {}
        self.内存缓存 = {}  # 内存缓存，避免重复加载
        
        # 确保题库文件夹存在
        self.tiku_dir.mkdir(exist_ok=True)
        self.load_cache()
    
    def get_tiku_list(self):
        """获取题库列表（只搜索题库文件夹）"""
        all_files = []
        
        # 只搜索题库文件夹
        if not self.tiku_dir.exists():
            return []
            
        for root, dirs, files in os.walk(self.tiku_dir):
            # 跳过缓存目录和隐藏目录
            if '.cache' in root or '.data' in root or '__pycache__' in root:
                continue
                
            for file in files:
                file_path = Path(root) / file
                
                # Excel文件
                if file.endswith('.xlsx') and not file.startswith('~$'):
                    all_files.append(file_path)
                
                # Word文件
                elif file.endswith('.docx') and not file.startswith('~$'):
                    all_files.append(file_path)
                
                # PDF文件
                elif file.endswith('.pdf'):
                    all_files.append(file_path)
        
        # 生成题库名称（包含文件夹路径）
        tiku_list = []
        for file_path in all_files:
            # 计算相对路径（相对于题库文件夹）
            relative_path = file_path.relative_to(self.tiku_dir)
            
            # 如果文件在子文件夹中，使用文件夹名+文件名
            if len(relative_path.parts) > 1:
                folder_name = relative_path.parts[0]
                file_name = relative_path.stem
                tiku_name = f"[{folder_name}] {file_name}"
            else:
                tiku_name = relative_path.stem
            
            tiku_list.append((tiku_name, file_path))
        
        return tiku_list
    
    def get_question_count(self, tiku_name):
        """获取题目数量"""
        questions = self.load_tiku(tiku_name)
        return len(questions) if questions else 0
    
    def load_tiku(self, tiku_name):
        """加载题库（支持子文件夹，带缓存）"""
        # 检查内存缓存
        if tiku_name in self.内存缓存:
            print(f"从内存缓存加载题库: {tiku_name}")
            return self.内存缓存[tiku_name]
        
        # 从题库列表中查找对应的文件路径
        tiku_list = self.get_tiku_list()
        file_path = None
        
        for name, path in tiku_list:
            if name == tiku_name:
                file_path = path
                break
        
        if not file_path or not file_path.exists():
            print(f"题库文件不存在: {tiku_name}")
            return None
        
        questions = None
        
        # 根据文件扩展名选择解析方法
        if file_path.suffix.lower() == '.xlsx':
            questions = self.parse_excel(file_path)
        elif file_path.suffix.lower() == '.docx':
            questions = self.parse_word(file_path)
        elif file_path.suffix.lower() == '.pdf':
            questions = self.parse_pdf(file_path)
        
        if not questions:
            return None
        
        # 保存到缓存
        self.tiku_cache[tiku_name] = questions
        self.内存缓存[tiku_name] = questions  # 添加到内存缓存
        self.save_cache()
        
        return questions
    
    def 从题目中提取选项(self, 题目文本):
        """从题目文本中提取选项 - 全面完善版本"""
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
    
    def parse_excel(self, excel_file):
        """解析Excel题库（使用pandas）"""
        try:
            import pandas as pd
            
            # 使用pandas读取Excel
            df = pd.read_excel(excel_file)
            
            if df.empty:
                print("Excel文件为空")
                return []
            
            print(f"Excel列名: {list(df.columns)}")
            
            # 智能识别列
            col_map = self.identify_columns(list(df.columns))
            
            if 'question' not in col_map or 'answer' not in col_map:
                print(f"警告: 无法识别题库格式，请确保包含'题目'和'答案'列")
                print(f"可用列: {list(df.columns)}")
                return []
            
            questions = []
            
            # 解析每一行
            for index, row in df.iterrows():
                # 跳过空行
                if pd.isna(row.iloc[col_map['question']]) or str(row.iloc[col_map['question']]).strip() == '':
                    continue
                
                question = {
                    'id': index + 1,
                    'question': str(row.iloc[col_map['question']]).strip(),
                    'answer': str(row.iloc[col_map['answer']]).strip() if not pd.isna(row.iloc[col_map['answer']]) else '',
                    'options': {},
                    'type': 'unknown',
                    'explanation': ''
                }
                
                # 解析选项
                for opt_key, opt_idx in col_map.get('options', {}).items():
                    if opt_idx < len(row) and not pd.isna(row.iloc[opt_idx]) and str(row.iloc[opt_idx]).strip():
                        question['options'][opt_key] = str(row.iloc[opt_idx]).strip()
                
                # 解析题型
                if col_map.get('type') is not None and col_map['type'] < len(row):
                    qtype = row.iloc[col_map['type']]
                    question['type'] = str(qtype).strip() if not pd.isna(qtype) else 'unknown'
                else:
                    # 自动判断题型
                    question['type'] = self.detect_question_type(question)
                
                # 解析解析
                if col_map.get('explanation') is not None and col_map['explanation'] < len(row):
                    explanation = row.iloc[col_map['explanation']]
                    question['explanation'] = str(explanation).strip() if not pd.isna(explanation) else ''
                
                questions.append(question)
            
            print(f"成功加载 {len(questions)} 道题目")
            return questions
            
        except Exception as e:
            print(f"解析Excel文件失败: {e}")
            return []
    
    def parse_word(self, word_file):
        """解析Word题库"""
        try:
            print(f"正在智能解析Word题库: {word_file.name}")
            
            # 使用智能解析器
            from Word题库智能解析器 import Word题库智能解析器
            智能解析器 = Word题库智能解析器(word_file)
            questions = 智能解析器.parse()
            
            if questions:
                print(f"成功加载 {len(questions)} 道题目")
            else:
                print("未能从Word文档中解析到题目")
            
            return questions
        except Exception as e:
            print(f"解析Word文件失败: {e}")
            print("提示: 请确保已安装 python-docx 库")
            print("运行: pip install python-docx")
            return []
    
    def parse_pdf(self, pdf_file):
        """解析PDF题库"""
        try:
            print(f"正在解析PDF题库: {pdf_file.name}")
            parser = PDFTikuParser(pdf_file)
            questions = parser.parse()
            
            if questions:
                print(f"成功加载 {len(questions)} 道题目")
            else:
                print("未能从PDF文档中解析到题目")
                print("提示: PDF格式复杂，建议使用'PDF转Excel.bat'转换后使用")
            
            return questions
        except Exception as e:
            print(f"解析PDF文件失败: {e}")
            print("提示: 请确保已安装 pdfplumber 库")
            print("运行: pip install pdfplumber")
            return []
    
    def identify_columns(self, headers):
        """智能识别列（支持多种格式）"""
        col_map = {}
        
        # 题目列（支持更多格式）
        question_keywords = ['题目', '试题', '问题', '题干', 'question', 'content']
        for i, h in enumerate(headers):
            h_lower = h.lower()
            # 支持"题目（必填）："这种格式
            if any(kw in h_lower for kw in question_keywords):
                col_map['question'] = i
                print(f"识别到题目列: {h} (索引: {i})")
                break
        
        # 答案列（精确匹配）
        for i, h in enumerate(headers):
            # 精确匹配"正确答案（必填）"
            if h == '正确答案（必填）':
                col_map['answer'] = i
                print(f"识别到答案列: {h} (索引: {i})")
                break
        
        # 如果没有找到"正确答案"，再找其他答案列
        if 'answer' not in col_map:
            answer_keywords = ['标准答案', '答案', 'answer']
            for i, h in enumerate(headers):
                h_lower = h.lower()
                if any(kw in h_lower for kw in answer_keywords):
                    # 排除选项列
                    if not any(opt in h for opt in ['选项', 'option', 'A', 'B', 'C', 'D']):
                        col_map['answer'] = i
                        print(f"识别到答案列: {h} (索引: {i})")
                        break
        
        # 选项列（支持更多格式）
        option_map = {}
        for opt in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
            for i, h in enumerate(headers):
                h_clean = h.strip()
                # 支持"选项A（必填）"这种格式
                if (h_clean == opt or 
                    h_clean == f'选项{opt}' or 
                    h_clean.lower() == f'option{opt.lower()}' or
                    f'选项{opt}' in h_clean):
                    option_map[opt] = i
                    print(f"识别到选项列: {h} (索引: {i})")
                    break
        
        if option_map:
            col_map['options'] = option_map
        
        # 题型列
        type_keywords = ['题型', '类型', 'type', '题目类型']
        for i, h in enumerate(headers):
            h_lower = h.lower()
            if any(kw in h_lower for kw in type_keywords):
                col_map['type'] = i
                print(f"识别到题型列: {h} (索引: {i})")
                break
        
        # 解析列
        explanation_keywords = ['解析', '解释', '说明', 'explanation', '试题解析']
        for i, h in enumerate(headers):
            h_lower = h.lower()
            if any(kw in h_lower for kw in explanation_keywords):
                col_map['explanation'] = i
                print(f"识别到解析列: {h} (索引: {i})")
                break
        
        print(f"列映射结果: {col_map}")
        return col_map
        
        # 题型列
        type_keywords = ['题型', '类型', 'type', '题目类型']
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
    
    def 分割合并选项(self, 选项内容, 当前选项):
        """分割合并的选项内容"""
        try:
            # 如果选项内容包含多个选项（如"A. 五年B、三年C、一年D、两年"）
            # 需要提取当前选项对应的内容
            
            # 查找当前选项的位置
            选项模式 = f"{当前选项}\\."
            import re
            
            # 查找当前选项开始位置
            当前选项开始 = re.search(选项模式, 选项内容)
            if not 当前选项开始:
                return 选项内容
            
            开始位置 = 当前选项开始.start()
            
            # 查找下一个选项的位置
            下一个选项 = chr(ord(当前选项) + 1)  # A->B, B->C, etc.
            下一个选项模式 = f"{下一个选项}\\."
            下一个选项开始 = re.search(下一个选项模式, 选项内容)
            
            if 下一个选项开始:
                结束位置 = 下一个选项开始.start()
                提取内容 = 选项内容[开始位置:结束位置].strip()
            else:
                # 如果没有下一个选项，取到末尾
                提取内容 = 选项内容[开始位置:].strip()
            
            # 移除选项字母和点号
            提取内容 = re.sub(f"^{当前选项}\\.", "", 提取内容).strip()
            
            return 提取内容 if 提取内容 else 选项内容
            
        except Exception as e:
            print(f"分割选项失败: {e}")
            return 选项内容
    
    def detect_question_type(self, question):
        """自动检测题型 - 使用高精度识别引擎"""
        try:
            # 优先使用修复后的高精度识别
            from 高精度题型识别 import detect_question_type_fixed
            return detect_question_type_fixed(
                question['question'],
                question['answer'],
                question.get('options')
            )
        except Exception as e:
            print(f"高精度识别失败，使用智能识别: {e}")
            try:
                # 备用方案1: 使用原有智能识别
                from 智能题型识别 import detect_question_type
                return detect_question_type(
                    question['question'],
                    question['answer'],
                    question.get('options')
                )
            except Exception as e2:
                print(f"智能识别失败，使用备用方法: {e2}")
                # 备用方案2: 使用内置识别方法
                return self._fallback_detect(question)
    
    def _fallback_detect(self, question):
        """备用题型识别方法 - 详细完备版"""
        import re
        
        q_text = question['question']
        answer = str(question['answer']).strip().upper()
        q_lower = q_text.lower()
        
        # ========== 第一优先级：明确的题型标识 ==========
        
        # 1. 判断题 - 最容易识别
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
        
        # 2.1 检查题目中是否有选项（兼容题干前后有大量无关文字）
        # “单选”和“多选”通常都表现为有选项(A~F)，区别如下：
        #   - 多选题的答案可能是多个，比如"AB"、"BCD"
        #   - 单选题的答案仅为一个，比如"A"，“D"
        #   - 题干中“多选”“多项”“哪些”等字眼多为多选题指示
        #   - 题干中“下列哪项”“哪一个”“最合适”或出现“单选题”等多为单选题指示

        选项模式列表 = [
            r'(?:^|[\n\r])[A-F][、\.．]\s*.+?(?=(?:[\n\r][A-F][、\.．])|$)',  # 行首A、内容，防止干扰
            r'(?:^|[\n\r])[A-F][)）]\s*.+?(?=(?:[\n\r][A-F][)）])|$)',      # A) 内容 或 A）内容
            r'(?:^|[\n\r])[A-F]、?\s*.+?(?=(?:[\n\r][A-F]、?)|$)',           # A 内容 (带/不带 逗号)
        ]
        has_options = False

        # 多选识别关键词 — 只要题干有这些词大概率是多选
        多选提示词 = [
            '多选', '多项选择', '多项', '哪些', '哪几个', '哪几项',
            '包括哪些', '包含哪些', '有哪些', '正确的有', '错误的有',
            '以下正确', '以下错误', '下列正确', '下列错误'
        ]
        # 单选识别关键词 — 对应单选常见表达
        单选提示词 = [
            '单选', '单项选择', '单项', '哪个', '哪项', '哪一',
            '最正确', '最合适', '最恰当', '最准确', '最合理',
            '下列哪项', '下列哪个', '下列正确的是', '以下哪项', '以下哪个', '符合', '属于', '应选择'
        ]

        # 检查题干是否带选项（无关文本有容忍），匹配多行后接A.B.C.D等样式即判有选项
        for 模式 in 选项模式列表:
            if re.search(模式, q_text, re.MULTILINE):
                has_options = True
                break

        # 进一步加强题型提示词辅助识别
        if not has_options:
            if any(tip in q_lower for tip in 多选提示词 + 单选提示词):
                has_options = True

        # 如果有options字段，也算有选项
        if question.get('options'):
            has_options = True
        
        # 2.2 多选题识别
        if has_options or '多选' in q_lower or '多项' in q_lower:
            # 答案是多个字母
            if len(answer) > 1 and all(c in 'ABCDEF' for c in answer):
                return '多选题'
            
            多选关键词 = ['多选', '多项选择', '多项', '哪些', '哪几个', '哪几项', 
                      '包括哪些', '包含哪些', '有哪些', '正确的有', '错误的有',
                      '以下正确', '以下错误', '下列正确', '下列错误']
            if any(keyword in q_lower for keyword in 多选关键词):
                return '多选题'
        
        # 2.3 单选题识别
        if has_options:
            # 答案是单个字母
            if len(answer) == 1 and answer in 'ABCDEF':
                return '单选题'
            
            单选关键词 = ['单选', '单项选择', '单项', '哪个', '哪项', '哪一',
                      '最正确', '最合适', '最恰当', '最准确', '最合理']
            if any(keyword in q_lower for keyword in 单选关键词):
                return '单选题'
            
            # 默认有选项就是单选题
            return '单选题'
        
        # 2.4 无选项但答案是字母（可能是选择题）
        # --- 问题追踪说明 ---
        # 有时选项被识别成题目，原因是：题目中并没有通过前面的选项匹配模式/关键词判断出“has_options”为True，
        # 但答案却是A/B/C等单个或多个字母，导致程序仅仅通过答案形式错误推断为单/多选题。
        # 这可能发生在OCR/PDF等采集导致选项和题目文本部分没有被正确识别/合并，错过正确的选项匹配。
        # 因此：这里额外以q_text内容二次尝试判断“实际上有没有选项文本”，如果没有，则不直接判为单/多选题，防止误判。
        candidate_is_choice = all(c in 'ABCDEF' for c in answer)
        if candidate_is_choice:
            # 再用正则检测题目文本是否有选项字母
            # 比如是否有“A.”、“A、”这样的序号
            option_pattern = r'\b[ABCDEF][\.、)]'
            if re.search(option_pattern, q_text):
                # 题干实际是有选项的，只是之前没统计出来
                if len(answer) > 1:
                    return '多选题'
                elif len(answer) == 1:
                    return '单选题'
            else:
                # 没有检测到选项序号，不直接按选择题处理
                # 可以记录日志或者debug提示
                pass
        
        # ========== 第三优先级：简答题识别 ==========
        
        # 3. 简答题识别优化
        # 3.1 答案够长、且有标点符号（易为简答）
        if len(answer) > 20 and sum(p in answer for p in ['。', '，', '；', '、', '\n']) >= 2:
            return '简答题'

        # 3.2 答案虽然较短，但题干明显问法是主观题
        简答题关键词 = [
            '简述', '简要说明', '说明', '论述', '阐述', '分析', '解释', 
            '描述', '叙述', '介绍', '回答', '解答', '谈谈', '试述',
            '如何', '怎样', '怎么', '为什么', '为何',
            '什么是', '何为', '定义', '概念', '含义',
            '谈谈你的理解', '谈谈你的看法', '谈谈你的认识', '试分析', '举例说明', '简答', '举例'
        ]
        if any(keyword in q_lower for keyword in 简答题关键词):
            # 如果答案为空（常因采集出错），依然认定为简答题
            if not answer or len(answer.strip()) == 0:
                return '简答题'
            # 如果答案太短且只有单词、短语、数字，很可能采集错误/误判，不当简答题
            # 但如果有较多的中文、标点，可认定为简答
            # 判断答案是否类似“是”“否”“1”“A”等，排除
            if len(answer) <= 5 and re.fullmatch(r'[A-Za-z0-9一二三四五六七八九十是正确错误对错好坏]', answer.strip()):
                pass  # 可能是采集问题，不直接当做简答
            else:
                # 答案含较多中文/标点，或者答案长度正常
                return '简答题'
        
        # ========== 第四优先级：填空题识别 ==========
        
        # 4.1 明确的填空标记
        填空标记 = ['_', '____', '（）', '()', '【】', '[]']
        if any(mark in q_text for mark in 填空标记):
            return '填空题'
        
        # 4.2 填空题常见句式
        填空句式 = [
            r'是\s*[（(]?\s*[）)]?',  # "是()"
            r'为\s*[（(]?\s*[）)]?',  # "为()"
            r'应\s*[（(]?\s*[）)]?',  # "应()"
            r'等于\s*[（(]?\s*[）)]?',  # "等于()"
            r'约\s*[（(]?\s*[）)]?',  # "约()"
        ]
        if any(re.search(pattern, q_text) for pattern in 填空句式):
            return '填空题'
        
        # 4.3 技术参数类填空题（答案包含数字和单位）
        技术单位 = ['MPa', 'KPA', 'PA', 'KV', 'V', 'MV', 'A', 'MA', 'KA',
                  'W', 'KW', 'MW', 'HZ', 'KHZ', 'MHZ', 'Ω', 'KΩ', 'MΩ',
                  'F', 'UF', 'PF', 'H', 'MH', 'UH', 
                  'M', 'CM', 'MM', 'KM', 'MM²', 'CM²', 'M²', 'MM³', 'CM³', 'M³',
                  'KG', 'G', 'MG', 'T', 'L', 'ML',
                  '米', '厘米', '毫米', '千米', '公里',
                  '克', '千克', '吨', '升', '毫升',
                  '度', '℃', '°C', '%', '‰',
                  '年', '月', '日', '天', '小时', '分钟', '秒']
        
        if any(char.isdigit() for char in answer):
            # 答案包含数字
            if any(unit in answer for unit in 技术单位):
                return '填空题'
            
            # 纯数字或数字+中文
            if re.search(r'\d+', answer):
                return '填空题'
        
        # 4.4 填空题常见关键词
        填空关键词 = ['等于', '约为', '大约', '标准', '规定', '要求',
                    '必须', '应该', '需要', '达到', '超过', '低于', '不少于', '不超过',
                    '范围', '限度', '时间', '距离', '长度', '高度', '宽度',
                    '面积', '体积', '重量', '质量', '温度', '压力', '速度',
                    '电压', '电流', '功率', '频率', '称为', '叫做', '简称']
        if any(keyword in q_lower for keyword in 填空关键词):
            # 且答案不是字母选项
            if not (len(answer) <= 2 and all(c in 'ABCDEF' for c in answer)):
                return '填空题'
        
        # ========== 最终兜底策略 ==========
        
        # 根据答案长度判断
        if len(answer) > 15:
            return '简答题'
        elif len(answer) > 0:
            return '填空题'
        
        return '未知'
    
    def show_tiku_detail(self, tiku_name):
        """显示题库详情"""
        questions = self.load_tiku(tiku_name)
        if not questions:
            print("题库为空或加载失败")
            return
        
        print(f"\n题库名称: {tiku_name}")
        print(f"题目总数: {len(questions)}")
        
        # 统计题型
        type_stats = {}
        for q in questions:
            qtype = q.get('type', '未知')
            type_stats[qtype] = type_stats.get(qtype, 0) + 1
        
        print("\n题型分布:")
        for qtype, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {qtype}: {count}题")
    
    def refresh(self):
        """刷新题库"""
        self.tiku_cache.clear()
        self.save_cache()
    
    def load_cache(self):
        """加载缓存"""
        cache_file = self.cache_dir / 'tiku_cache.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.tiku_cache = json.load(f)
            except:
                self.tiku_cache = {}
    
    def save_cache(self):
        """保存缓存"""
        cache_file = self.cache_dir / 'tiku_cache.json'
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.tiku_cache, f, ensure_ascii=False, indent=2)
        except:
            pass

