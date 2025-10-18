#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
刷题引擎模块
负责刷题逻辑、答题判断和记录
"""

import os
import random
import json
from datetime import datetime
from pathlib import Path
from 题库管理 import TikuManager

class ShuatiEngine:
    def __init__(self, source, mode='sequential'):
        """
        初始化刷题引擎
        :param source: 题库名称或'wrong_questions'
        :param mode: sequential(顺序)/random(随机)/exam(考试)
        """
        self.source = source
        self.mode = mode
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / '.data'
        self.data_dir.mkdir(exist_ok=True)
        
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.total_answered = 0
        
        self.load_questions()
    
    def load_questions(self):
        """加载题目"""
        if self.source == 'wrong_questions':
            self.questions = self.load_wrong_questions()
        else:
            manager = TikuManager()
            all_questions = manager.load_tiku(self.source)
            if all_questions:
                self.questions = all_questions.copy()
        
        if self.mode == 'random':
            random.shuffle(self.questions)
    
    def has_questions(self):
        """是否有题目"""
        return len(self.questions) > 0
    
    def start(self):
        """开始刷题"""
        if not self.questions:
            print("没有可用题目！")
            input("按回车键返回...")
            return
        
        print(f"\n共 {len(self.questions)} 道题目")
        
        if self.mode == 'exam':
            print("模拟考试模式：答题完成后统一显示成绩")
        
        input("\n按回车键开始...")
        
        for i, question in enumerate(self.questions):
            self.current_index = i
            result = self.ask_question(question, i + 1)
            
            if result == 'quit':
                break
            elif result == 'correct':
                self.score += 1
            
            self.total_answered += 1
        
        self.show_result()
    
    def ask_question(self, question, number):
        """提问"""
        self.clear_screen()
        
        print("=" * 60)
        print(f"题目 {number}/{len(self.questions)}")
        if self.mode != 'exam':
            print(f"当前正确率: {self.score}/{self.total_answered} ({self.get_accuracy():.1f}%)" if self.total_answered > 0 else "")
        print("=" * 60)
        
        print(f"\n【{question.get('type', '未知')}】{question['question']}\n")
        
        # 显示选项
        if question.get('options'):
            for opt_key in sorted(question['options'].keys()):
                print(f"{opt_key}. {question['options'][opt_key]}")
            print()
        
        # 获取答案
        user_answer = input("你的答案（输入'q'退出，'s'跳过）: ").strip().upper()
        
        if user_answer == 'Q':
            return 'quit'
        
        if user_answer == 'S':
            return 'skip'
        
        # 判断答案
        correct_answer = question['answer'].upper()
        is_correct = self.check_answer(user_answer, correct_answer, question.get('type', ''))
        
        # 立即反馈（非考试模式）
        if self.mode != 'exam':
            print("\n" + "-" * 60)
            if is_correct:
                print("✓ 回答正确！")
            else:
                print("✗ 回答错误！")
                print(f"正确答案: {correct_answer}")
                
                if question.get('options') and correct_answer in question['options']:
                    print(f"正确选项: {question['options'][correct_answer]}")
            
            if question.get('explanation'):
                print(f"\n解析: {question['explanation']}")
            
            print("-" * 60)
            
            input("\n按回车键继续...")
        
        # 记录答题
        self.record_answer(question, user_answer, is_correct)
        
        return 'correct' if is_correct else 'wrong'
    
    def check_answer(self, user_answer, correct_answer, question_type):
        """检查答案"""
        # 判断题特殊处理
        if question_type == '判断题':
            # 标准化答案
            user_answer = self.normalize_judge_answer(user_answer)
            correct_answer = self.normalize_judge_answer(correct_answer)
        
        # 多选题：顺序无关
        if question_type == '多选题':
            return set(user_answer) == set(correct_answer)
        
        return user_answer == correct_answer
    
    def normalize_judge_answer(self, answer):
        """标准化判断题答案"""
        answer = answer.upper()
        if answer in ['对', '√', 'T', 'TRUE', '正确', 'Y', 'YES']:
            return '对'
        if answer in ['错', '×', 'X', 'F', 'FALSE', '错误', 'N', 'NO']:
            return '错'
        return answer
    
    def record_answer(self, question, user_answer, is_correct):
        """记录答题"""
        record = {
            'question_id': question.get('id', 0),
            'question': question['question'],
            'answer': question['answer'],
            'user_answer': user_answer,
            'is_correct': is_correct,
            'timestamp': datetime.now().isoformat(),
            'source': self.source
        }
        
        # 保存到历史
        history_file = self.data_dir / 'history.jsonl'
        with open(history_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        # 如果答错，加入错题本
        if not is_correct:
            self.add_to_wrong_questions(question)
        else:
            # 如果答对，从错题本移除
            self.remove_from_wrong_questions(question)
    
    def add_to_wrong_questions(self, question):
        """添加到错题本"""
        wrong_file = self.data_dir / 'wrong_questions.json'
        
        wrong_questions = []
        if wrong_file.exists():
            try:
                with open(wrong_file, 'r', encoding='utf-8') as f:
                    wrong_questions = json.load(f)
            except:
                wrong_questions = []
        
        # 避免重复
        question_ids = [q.get('id') for q in wrong_questions]
        if question.get('id') not in question_ids:
            wrong_questions.append(question)
        
        with open(wrong_file, 'w', encoding='utf-8') as f:
            json.dump(wrong_questions, f, ensure_ascii=False, indent=2)
    
    def remove_from_wrong_questions(self, question):
        """从错题本移除"""
        wrong_file = self.data_dir / 'wrong_questions.json'
        
        if not wrong_file.exists():
            return
        
        try:
            with open(wrong_file, 'r', encoding='utf-8') as f:
                wrong_questions = json.load(f)
            
            wrong_questions = [q for q in wrong_questions if q.get('id') != question.get('id')]
            
            with open(wrong_file, 'w', encoding='utf-8') as f:
                json.dump(wrong_questions, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def load_wrong_questions(self):
        """加载错题"""
        wrong_file = self.data_dir / 'wrong_questions.json'
        
        if not wrong_file.exists():
            return []
        
        try:
            with open(wrong_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def get_accuracy(self):
        """获取正确率"""
        if self.total_answered == 0:
            return 0
        return (self.score / self.total_answered) * 100
    
    def show_result(self):
        """显示结果"""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("  答题完成！")
        print("=" * 60)
        print(f"\n总题数: {self.total_answered}")
        print(f"正确数: {self.score}")
        print(f"错误数: {self.total_answered - self.score}")
        print(f"正确率: {self.get_accuracy():.1f}%")
        
        if self.get_accuracy() >= 90:
            print("\n评价: 优秀！继续保持！")
        elif self.get_accuracy() >= 80:
            print("\n评价: 良好！再接再厉！")
        elif self.get_accuracy() >= 60:
            print("\n评价: 及格，还需努力！")
        else:
            print("\n评价: 需要加强练习！")
        
        input("\n按回车键返回...")
    
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')

