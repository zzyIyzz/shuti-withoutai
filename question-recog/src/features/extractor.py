"""
特征工程模块 - 提取可解释的非语义特征
避免重模型依赖，专注于结构化和统计特征
"""

import re
from typing import Dict, List, Any
import logging
from collections import Counter

from ..io.schemas import ParsedQuestion, QuestionFeatures


logger = logging.getLogger(__name__)


class FeatureExtractor:
    """特征提取器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.load_dictionaries()
        self.load_patterns()
    
    def load_dictionaries(self):
        """加载词典和关键词"""
        # 多选题提示词
        self.multi_choice_keywords = [
            "多选", "多项", "至少两项", "两个以上", "不止一个", 
            "哪些", "哪几个", "包括", "多个", "几个"
        ]
        
        # 判断题提示词
        self.true_false_keywords = [
            "判断对错", "是否正确", "对吗", "对么", "是非题", 
            "判断题", "说法", "表述", "观点", "是否准确"
        ]
        
        # 填空题提示词
        self.fill_blank_keywords = [
            "填写", "填入", "应填", "等于", "约为", "标准", 
            "规定", "数值", "参数", "单位"
        ]
        
        # 简答题提示词
        self.subjective_keywords = [
            "简述", "说明", "论述", "分析", "阐述", "解释", "描述",
            "如何", "为什么", "什么是", "怎样", "请", "试", "谈谈",
            "基本要求", "工作原理", "主要特点", "注意事项", "定义",
            "比较", "列举", "举例"
        ]
        
        # 停用词
        self.stopwords = set([
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
            "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
            "你", "会", "着", "没有", "看", "好", "自己", "这", "那"
        ])
    
    def load_patterns(self):
        """加载正则模式"""
        # 答案模式
        self.single_letter_pattern = re.compile(r'^[A-F]$')
        self.multi_letter_pattern = re.compile(r'^[A-F]{2,6}$')
        self.true_false_pattern = re.compile(
            r'^(对|错|√|×|True|False|T|F|正确|错误|是|否)$'
        )
        
        # 填空标记模式
        self.blank_patterns = [
            re.compile(r'_{2,}'),  # 下划线
            re.compile(r'（\s*）'),  # 中文括号
            re.compile(r'\(\s*\)'),  # 英文括号
            re.compile(r'【\s*】'),  # 方括号
        ]
        
        # 标点符号模式
        self.punct_pattern = re.compile(r'[。，！？；：、""''（）【】《》〈〉.,!?;:()\\[\\]<>"]')
        
        # 问号模式
        self.question_mark_pattern = re.compile(r'[？?]')
    
    def extract_features(self, question: ParsedQuestion) -> QuestionFeatures:
        """
        提取题目特征
        
        Args:
            question: 解析后的题目
            
        Returns:
            特征向量
        """
        features = {}
        
        # 基础特征
        features.update(self._extract_basic_features(question))
        
        # 长度特征
        features.update(self._extract_length_features(question))
        
        # 标点特征
        features.update(self._extract_punctuation_features(question))
        
        # 关键词特征
        features.update(self._extract_keyword_features(question))
        
        # 模式特征
        features.update(self._extract_pattern_features(question))
        
        # 版面特征
        features.update(self._extract_layout_features(question))
        
        # 答案模式特征
        features.update(self._extract_answer_pattern_features(question))
        
        return QuestionFeatures(**features)
    
    def _extract_basic_features(self, question: ParsedQuestion) -> Dict[str, Any]:
        """提取基础特征"""
        return {
            "has_options": 1 if question.options else 0,
            "num_options": len(question.options),
            "answer_is_single_letter": 1 if self.single_letter_pattern.match(question.answer_raw) else 0,
            "answer_is_multi_letters": 1 if self.multi_letter_pattern.match(question.answer_raw) else 0,
        }
    
    def _extract_length_features(self, question: ParsedQuestion) -> Dict[str, Any]:
        """提取长度特征"""
        option_lengths = [len(opt) for opt in question.options] if question.options else [0]
        
        return {
            "question_len": len(question.question),
            "option_len_mean": sum(option_lengths) / len(option_lengths) if option_lengths else 0.0,
            "answer_len": len(question.answer_raw),
        }
    
    def _extract_punctuation_features(self, question: ParsedQuestion) -> Dict[str, Any]:
        """提取标点特征"""
        question_text = question.question
        punct_count = len(self.punct_pattern.findall(question_text))
        total_chars = len(question_text)
        
        return {
            "punct_density": punct_count / total_chars if total_chars > 0 else 0.0,
            "question_mark_count": len(self.question_mark_pattern.findall(question_text)),
        }
    
    def _extract_keyword_features(self, question: ParsedQuestion) -> Dict[str, Any]:
        """提取关键词特征"""
        question_text = question.question.lower()
        
        # 计算各类关键词命中数
        multi_hits = sum(1 for kw in self.multi_choice_keywords if kw in question_text)
        tf_hits = sum(1 for kw in self.true_false_keywords if kw in question_text)
        blank_hits = sum(1 for kw in self.fill_blank_keywords if kw in question_text)
        subj_hits = sum(1 for kw in self.subjective_keywords if kw in question_text)
        
        return {
            "hint_keywords_multi": min(multi_hits, 3),  # 截断到3避免过拟合
            "hint_keywords_tf": min(tf_hits, 3),
            "hint_keywords_blank": min(blank_hits, 3),
            "hint_keywords_subj": min(subj_hits, 3),
        }
    
    def _extract_pattern_features(self, question: ParsedQuestion) -> Dict[str, Any]:
        """提取模式特征"""
        question_text = question.question
        
        # 填空标记计数
        blank_underline_count = len(self.blank_patterns[0].findall(question_text))
        blank_parenthesis_count = sum(
            len(pattern.findall(question_text)) 
            for pattern in self.blank_patterns[1:]
        )
        
        # 选项对齐度评分
        option_alignment_score = self._calculate_option_alignment(question.options)
        
        return {
            "blank_underline_count": blank_underline_count,
            "blank_parenthesis_count": blank_parenthesis_count,
            "option_alignment_score": option_alignment_score,
        }
    
    def _extract_layout_features(self, question: ParsedQuestion) -> Dict[str, Any]:
        """提取版面特征"""
        return {
            "layout_score": question.layout_score,
            "ocr_conf_mean": 1.0,  # 默认值，实际应从parse_flags中获取
        }
    
    def _extract_answer_pattern_features(self, question: ParsedQuestion) -> Dict[str, Any]:
        """提取答案模式特征"""
        answer = question.answer_raw
        
        # 答案模式ID编码
        if self.single_letter_pattern.match(answer):
            pattern_id = 1  # 单字母
        elif self.multi_letter_pattern.match(answer):
            pattern_id = 2  # 多字母
        elif self.true_false_pattern.match(answer):
            pattern_id = 3  # 判断类型
        elif len(answer) > 20:
            pattern_id = 4  # 长文本
        elif answer.isdigit():
            pattern_id = 5  # 数字
        else:
            pattern_id = 0  # 其他
        
        return {
            "answer_pattern_id": pattern_id,
        }
    
    def _calculate_option_alignment(self, options: List[str]) -> float:
        """计算选项对齐度"""
        if len(options) < 2:
            return 0.0
        
        # 计算选项长度的变异系数
        lengths = [len(opt) for opt in options]
        if not lengths:
            return 0.0
        
        mean_len = sum(lengths) / len(lengths)
        if mean_len == 0:
            return 0.0
        
        variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        cv = (variance ** 0.5) / mean_len  # 变异系数
        
        # 转换为对齐度分数（变异系数越小，对齐度越高）
        alignment_score = max(0.0, 1.0 - cv)
        
        return alignment_score
    
    def extract_batch_features(self, questions: List[ParsedQuestion]) -> List[QuestionFeatures]:
        """
        批量提取特征
        
        Args:
            questions: 题目列表
            
        Returns:
            特征向量列表
        """
        return [self.extract_features(q) for q in questions]
    
    def get_feature_names(self) -> List[str]:
        """获取特征名称列表"""
        # 创建一个虚拟的特征对象来获取所有字段名
        dummy_features = QuestionFeatures(
            has_options=0, num_options=0, answer_is_single_letter=0,
            answer_is_multi_letters=0, question_len=0, option_len_mean=0.0,
            answer_len=0, punct_density=0.0, question_mark_count=0,
            hint_keywords_multi=0, hint_keywords_tf=0, hint_keywords_blank=0,
            hint_keywords_subj=0, blank_underline_count=0, blank_parenthesis_count=0,
            option_alignment_score=0.0, layout_score=0.0, ocr_conf_mean=1.0,
            answer_pattern_id=0
        )
        
        return list(dummy_features.dict().keys())
    
    def features_to_array(self, features: QuestionFeatures) -> List[float]:
        """将特征对象转换为数组"""
        feature_dict = features.dict()
        feature_names = self.get_feature_names()
        return [float(feature_dict[name]) for name in feature_names]


def extract_question_features(question: ParsedQuestion, config: Dict[str, Any] = None) -> QuestionFeatures:
    """
    便捷函数：提取单个题目的特征
    
    Args:
        question: 解析后的题目
        config: 配置参数
        
    Returns:
        特征向量
    """
    extractor = FeatureExtractor(config)
    return extractor.extract_features(question)
