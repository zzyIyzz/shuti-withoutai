#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能题目重构器 - 解决题目划分问题
自动识别和合并被错误分割的题目
"""

import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Any
import json

class QuestionRebuilder:
    """智能题目重构器"""
    
    def __init__(self):
        self.question_patterns = [
            r'^根据.*规定',  # 根据XX规定
            r'^依据.*',      # 依据XX
            r'^.*年.*月.*日', # 时间开头
            r'^\d+\.',       # 数字开头
            r'^[A-Z]',       # 大写字母开头
        ]
        
        self.ending_patterns = [
            r'[？?]$',       # 问号结尾
            r'[。.]$',       # 句号结尾
            r'[：:]$',       # 冒号结尾
            r'\)$',          # 括号结尾
            r'）$',          # 中文括号结尾
        ]
        
        self.option_patterns = [
            r'^[ABCD][.:]',  # 选项标识
            r'^[A-Z]\.',     # 大写字母点
        ]
    
    def is_question_start(self, text: str) -> bool:
        """判断是否是题目开始"""
        if not text or len(text.strip()) < 5:
            return False
        
        text = text.strip()
        
        # 检查是否匹配题目开始模式
        for pattern in self.question_patterns:
            if re.search(pattern, text):
                return True
        
        # 检查是否是选项（不是题目开始）
        for pattern in self.option_patterns:
            if re.search(pattern, text):
                return False
        
        # 如果文本较长且不是选项，可能是题目
        if len(text) > 20:
            return True
        
        return False
    
    def is_question_complete(self, text: str) -> bool:
        """判断题目是否完整"""
        if not text:
            return False
        
        text = text.strip()
        
        # 检查是否有结束标点
        for pattern in self.ending_patterns:
            if re.search(pattern, text):
                return True
        
        # 如果包含选项标识，说明题目可能完整
        if re.search(r'[ABCD][.:]', text):
            return True
        
        return False
    
    def extract_options_from_text(self, text: str) -> List[str]:
        """从文本中提取选项"""
        options = []
        
        # 查找选项模式
        option_matches = re.findall(r'([ABCD])[.:]([^ABCD]*?)(?=[ABCD][.:]|$)', text)
        
        for letter, content in option_matches:
            if content.strip():
                options.append(f"{letter}: {content.strip()}")
        
        return options
    
    def rebuild_questions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """重构题目"""
        print("🔧 开始智能重构题目...")
        
        rebuilt_questions = []
        current_question = ""
        current_options = []
        current_answer = ""
        question_start_row = -1
        
        question_col = "题目（必填）："
        answer_col = "正确答案（必填）"
        option_cols = ["选项A（必填）", "选项B（必填）", "选项C", "选项D", "选项E", "选项F"]
        
        for i, row in df.iterrows():
            question_text = str(row[question_col]) if not pd.isna(row[question_col]) else ""
            answer_text = str(row[answer_col]) if not pd.isna(row[answer_col]) else ""
            
            # 提取选项
            row_options = []
            for opt_col in option_cols:
                if opt_col in df.columns and not pd.isna(row[opt_col]):
                    opt_text = str(row[opt_col]).strip()
                    if opt_text and opt_text.lower() not in ['nan', 'none']:
                        row_options.append(opt_text)
            
            # 判断是否是新题目的开始
            if self.is_question_start(question_text):
                # 保存之前的题目（如果存在）
                if current_question.strip():
                    rebuilt_questions.append({
                        'question': current_question.strip(),
                        'options': current_options,
                        'answer': current_answer.strip(),
                        'start_row': question_start_row + 1,
                        'end_row': i
                    })
                
                # 开始新题目
                current_question = question_text
                current_options = row_options.copy()
                current_answer = answer_text
                question_start_row = i
                
            else:
                # 继续当前题目
                if question_text.strip() and question_text != "nan":
                    if current_question:
                        current_question += " " + question_text
                    else:
                        current_question = question_text
                
                # 添加选项
                current_options.extend(row_options)
                
                # 更新答案
                if answer_text.strip() and answer_text != "nan":
                    if current_answer:
                        current_answer += " " + answer_text
                    else:
                        current_answer = answer_text
        
        # 保存最后一个题目
        if current_question.strip():
            rebuilt_questions.append({
                'question': current_question.strip(),
                'options': current_options,
                'answer': current_answer.strip(),
                'start_row': question_start_row + 1,
                'end_row': len(df)
            })
        
        return rebuilt_questions
    
    def clean_question(self, question: str) -> str:
        """清理题目文本"""
        if not question:
            return ""
        
        # 移除多余空格
        question = re.sub(r'\s+', ' ', question)
        
        # 移除题目中的选项（如果误包含）
        question = re.sub(r'\s+[ABCD][.:]\s*[^ABCD]*', '', question)
        
        # 确保正确的标点
        question = question.strip()
        if not question.endswith(('？', '?', '。', '：', ':', '）', ')')):
            if '？' in question or '?' in question:
                pass  # 已有问号
            elif question.endswith('是'):
                question += '？'
            elif question.endswith(('的', '为')):
                question += '？'
            else:
                question += '。'
        
        return question
    
    def process_excel_file(self, file_path: str) -> List[Dict[str, Any]]:
        """处理Excel文件"""
        print(f"📄 处理文件: {file_path}")
        
        df = pd.read_excel(file_path)
        print(f"📊 原始数据: {df.shape[0]}行 x {df.shape[1]}列")
        
        # 重构题目
        rebuilt_questions = self.rebuild_questions(df)
        
        # 清理和验证
        cleaned_questions = []
        for i, q in enumerate(rebuilt_questions):
            cleaned_question = self.clean_question(q['question'])
            
            if len(cleaned_question) < 10:  # 过滤过短的题目
                continue
            
            cleaned_questions.append({
                'id': i + 1,
                'question': cleaned_question,
                'options': q['options'],
                'answer': q['answer'],
                'source_rows': f"{q['start_row']}-{q['end_row']}",
                'quality_score': self.calculate_quality_score(cleaned_question, q['options'], q['answer'])
            })
        
        print(f"✅ 重构完成: {len(cleaned_questions)} 个有效题目")
        return cleaned_questions
    
    def calculate_quality_score(self, question: str, options: List[str], answer: str) -> float:
        """计算题目质量分数"""
        score = 0.0
        
        # 题目长度分数
        if 20 <= len(question) <= 200:
            score += 0.3
        elif len(question) > 10:
            score += 0.1
        
        # 选项分数
        if len(options) >= 2:
            score += 0.3
        elif len(options) >= 1:
            score += 0.1
        
        # 答案分数
        if answer and answer.strip():
            score += 0.2
        
        # 格式分数
        if question.endswith(('？', '?', '。', '：', ':')):
            score += 0.1
        
        # 完整性分数
        if question and options and answer:
            score += 0.1
        
        return min(score, 1.0)

def main():
    """主函数"""
    print("🚀 智能题目重构器")
    print("=" * 50)
    
    rebuilder = QuestionRebuilder()
    
    # 处理Excel文件
    excel_file = "题库/新员工一级竞赛题库.xlsx"
    if not Path(excel_file).exists():
        print(f"❌ 文件不存在: {excel_file}")
        return
    
    try:
        questions = rebuilder.process_excel_file(excel_file)
        
        # 保存重构结果
        output_file = "question-recog/rebuilt_questions.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        
        print(f"💾 重构结果已保存: {output_file}")
        
        # 显示统计信息
        print(f"\n📊 重构统计:")
        print(f"  总题目数: {len(questions)}")
        
        # 质量分布
        high_quality = sum(1 for q in questions if q['quality_score'] >= 0.8)
        medium_quality = sum(1 for q in questions if 0.5 <= q['quality_score'] < 0.8)
        low_quality = sum(1 for q in questions if q['quality_score'] < 0.5)
        
        print(f"  高质量题目: {high_quality} ({high_quality/len(questions)*100:.1f}%)")
        print(f"  中等质量题目: {medium_quality} ({medium_quality/len(questions)*100:.1f}%)")
        print(f"  低质量题目: {low_quality} ({low_quality/len(questions)*100:.1f}%)")
        
        # 显示示例
        print(f"\n📝 重构示例:")
        for i, q in enumerate(questions[:3]):
            print(f"\n示例 {i+1} (质量分数: {q['quality_score']:.2f}):")
            print(f"  题目: {q['question'][:80]}...")
            print(f"  选项数: {len(q['options'])}")
            print(f"  答案: {q['answer']}")
            print(f"  来源行: {q['source_rows']}")
        
        print(f"\n🎉 题目重构完成！")
        print(f"📋 使用重构后的数据可以显著提高识别准确率")
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
