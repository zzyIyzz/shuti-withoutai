"""
强规则引擎 - 基于规则的题型判定
实现高置信度短路判定，避免进入机器学习模型
"""

import re
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass

from ..io.schemas import ParsedQuestion, QuestionFeatures, RuleDecision, QuestionType


logger = logging.getLogger(__name__)


@dataclass
class RuleCondition:
    """规则条件"""
    name: str
    check_func: callable
    weight: float = 1.0


class RuleEngine:
    """强规则引擎"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.rules = {}
        self.load_rules()
    
    def load_rules(self):
        """加载规则定义"""
        # 规则1: 判断题答案强规则
        self.rules["true_false_answer"] = {
            "priority": 1,
            "enabled": True,
            "description": "答案为判断类型时强制识别为判断题",
            "conditions": [
                RuleCondition("answer_is_tf", self._check_answer_is_tf, 2.0),
            ],
            "action": {
                "type": QuestionType.TRUE_FALSE,
                "confidence": 0.95,
                "explanation": "强规则命中：答案为判断类型"
            }
        }
        
        # 规则2: 填空题标记强规则
        self.rules["fill_blank_markers"] = {
            "priority": 2,
            "enabled": True,
            "description": "题干含填空标记时识别为填空题",
            "conditions": [
                RuleCondition("has_blank_markers", self._check_blank_markers, 1.5),
                RuleCondition("answer_not_letter", self._check_answer_not_letter, 1.0),
                RuleCondition("no_options", self._check_no_options, 0.5),
            ],
            "action": {
                "type": QuestionType.FILL_BLANK,
                "confidence": 0.90,
                "explanation": "强规则命中：题干含填空标记"
            }
        }
        
        # 规则3: 多选题提示强规则
        self.rules["multiple_choice_hints"] = {
            "priority": 3,
            "enabled": True,
            "description": "题干含多选提示词时识别为多选题",
            "conditions": [
                RuleCondition("has_multi_hints", self._check_multi_choice_hints, 2.0),
                RuleCondition("has_options", self._check_has_options, 1.0),
                RuleCondition("min_options", self._check_min_options, 0.5),
            ],
            "action": {
                "type": QuestionType.MULTIPLE_CHOICE,
                "confidence": 0.88,
                "explanation": "强规则命中：题干含多选提示"
            }
        }
        
        # 规则4: 单选题默认规则
        self.rules["single_choice_default"] = {
            "priority": 4,
            "enabled": True,
            "description": "有选项且答案为单字母时默认为单选题",
            "conditions": [
                RuleCondition("has_options", self._check_has_options, 1.0),
                RuleCondition("valid_option_count", self._check_valid_option_count, 1.0),
                RuleCondition("single_letter_answer", self._check_single_letter_answer, 1.5),
            ],
            "action": {
                "type": QuestionType.SINGLE_CHOICE,
                "confidence": 0.85,
                "explanation": "强规则命中：标准单选题格式"
            }
        }
        
        # 规则5: 简答题兜底规则
        self.rules["subjective_fallback"] = {
            "priority": 5,
            "enabled": True,
            "description": "无选项且答案为长文本时识别为简答题",
            "conditions": [
                RuleCondition("no_options", self._check_no_options, 1.0),
                RuleCondition("long_answer", self._check_long_answer, 1.5),
                RuleCondition("subjective_hints", self._check_subjective_hints, 1.0),
            ],
            "action": {
                "type": QuestionType.SUBJECTIVE,
                "confidence": 0.80,
                "explanation": "强规则命中：简答题特征"
            }
        }
    
    def apply_rules(self, question: ParsedQuestion, features: QuestionFeatures) -> Optional[RuleDecision]:
        """
        应用规则进行判定
        
        Args:
            question: 解析后的题目
            features: 特征向量
            
        Returns:
            规则判定结果（如果命中）
        """
        # 按优先级排序规则
        sorted_rules = sorted(
            self.rules.items(),
            key=lambda x: x[1]["priority"]
        )
        
        for rule_name, rule_config in sorted_rules:
            if not rule_config["enabled"]:
                continue
            
            # 检查规则条件
            decision = self._evaluate_rule(rule_name, rule_config, question, features)
            if decision:
                logger.info(f"规则命中: {rule_name} -> {decision.type}")
                return decision
        
        logger.debug("无规则命中，将使用模型预测")
        return None
    
    def _evaluate_rule(
        self, 
        rule_name: str, 
        rule_config: Dict[str, Any], 
        question: ParsedQuestion, 
        features: QuestionFeatures
    ) -> Optional[RuleDecision]:
        """评估单个规则"""
        conditions = rule_config["conditions"]
        total_score = 0.0
        max_score = 0.0
        
        for condition in conditions:
            max_score += condition.weight
            if condition.check_func(question, features):
                total_score += condition.weight
        
        # 计算条件满足度
        if max_score > 0:
            satisfaction_rate = total_score / max_score
        else:
            satisfaction_rate = 0.0
        
        # 判断是否满足阈值（默认0.6）
        threshold = rule_config.get("threshold", 0.6)
        if satisfaction_rate >= threshold:
            action = rule_config["action"]
            return RuleDecision(
                rule_name=rule_name,
                type=action["type"],
                confidence=action["confidence"] * satisfaction_rate,  # 调整置信度
                explanation=action["explanation"],
                priority=rule_config["priority"]
            )
        
        return None
    
    # 条件检查函数
    def _check_answer_is_tf(self, question: ParsedQuestion, features: QuestionFeatures) -> bool:
        """检查答案是否为判断类型"""
        answer = question.answer_raw.strip()
        tf_answers = {"对", "错", "√", "×", "True", "False", "T", "F", "正确", "错误", "是", "否"}
        return answer in tf_answers
    
    def _check_blank_markers(self, question: ParsedQuestion, features: QuestionFeatures) -> bool:
        """检查是否有填空标记"""
        question_text = question.question
        blank_patterns = [
            r'_{2,}',  # 下划线
            r'（\s*）',  # 中文括号
            r'\(\s*\)',  # 英文括号
            r'【\s*】',  # 方括号
        ]
        
        for pattern in blank_patterns:
            if re.search(pattern, question_text):
                return True
        
        return False
    
    def _check_answer_not_letter(self, question: ParsedQuestion, features: QuestionFeatures) -> bool:
        """检查答案不是单字母"""
        answer = question.answer_raw.strip()
        return not re.match(r'^[A-F]$', answer)
    
    def _check_no_options(self, question: ParsedQuestion, features: QuestionFeatures) -> bool:
        """检查是否无选项"""
        return len(question.options) == 0
    
    def _check_multi_choice_hints(self, question: ParsedQuestion, features: QuestionFeatures) -> bool:
        """检查多选题提示词"""
        question_text = question.question.lower()
        multi_keywords = [
            "多选", "多项", "至少两项", "两个以上", "不止一个", 
            "哪些", "哪几个", "包括"
        ]
        
        return any(keyword in question_text for keyword in multi_keywords)
    
    def _check_has_options(self, question: ParsedQuestion, features: QuestionFeatures) -> bool:
        """检查是否有选项"""
        return len(question.options) > 0
    
    def _check_min_options(self, question: ParsedQuestion, features: QuestionFeatures) -> bool:
        """检查最小选项数量"""
        return len(question.options) >= 3
    
    def _check_valid_option_count(self, question: ParsedQuestion, features: QuestionFeatures) -> bool:
        """检查选项数量是否合理"""
        option_count = len(question.options)
        return 2 <= option_count <= 6
    
    def _check_single_letter_answer(self, question: ParsedQuestion, features: QuestionFeatures) -> bool:
        """检查答案是否为单字母"""
        answer = question.answer_raw.strip()
        return bool(re.match(r'^[A-F]$', answer))
    
    def _check_long_answer(self, question: ParsedQuestion, features: QuestionFeatures) -> bool:
        """检查答案是否为长文本"""
        return len(question.answer_raw) > 15
    
    def _check_subjective_hints(self, question: ParsedQuestion, features: QuestionFeatures) -> bool:
        """检查简答题提示词"""
        question_text = question.question.lower()
        subj_keywords = [
            "简述", "说明", "论述", "分析", "阐述", "解释", "描述",
            "如何", "为什么", "什么是", "请", "试"
        ]
        
        return any(keyword in question_text for keyword in subj_keywords)
    
    def get_rule_stats(self) -> Dict[str, Any]:
        """获取规则统计信息"""
        stats = {
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for rule in self.rules.values() if rule["enabled"]),
            "rule_priorities": {name: rule["priority"] for name, rule in self.rules.items()},
        }
        return stats
    
    def enable_rule(self, rule_name: str) -> bool:
        """启用规则"""
        if rule_name in self.rules:
            self.rules[rule_name]["enabled"] = True
            logger.info(f"规则已启用: {rule_name}")
            return True
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """禁用规则"""
        if rule_name in self.rules:
            self.rules[rule_name]["enabled"] = False
            logger.info(f"规则已禁用: {rule_name}")
            return True
        return False
    
    def update_rule_threshold(self, rule_name: str, threshold: float) -> bool:
        """更新规则阈值"""
        if rule_name in self.rules and 0.0 <= threshold <= 1.0:
            self.rules[rule_name]["threshold"] = threshold
            logger.info(f"规则阈值已更新: {rule_name} -> {threshold}")
            return True
        return False
    
    def resolve_conflicts(self, decisions: List[RuleDecision]) -> RuleDecision:
        """
        解决规则冲突
        
        Args:
            decisions: 冲突的规则决策列表
            
        Returns:
            最终决策
        """
        if not decisions:
            raise ValueError("决策列表不能为空")
        
        if len(decisions) == 1:
            return decisions[0]
        
        # 按优先级排序，优先级数字越小越优先
        decisions.sort(key=lambda x: x.priority)
        
        # 记录冲突
        rule_names = [d.rule_name for d in decisions]
        logger.warning(f"规则冲突: {rule_names}, 选择最高优先级: {decisions[0].rule_name}")
        
        return decisions[0]


def apply_rule_engine(
    question: ParsedQuestion, 
    features: QuestionFeatures, 
    config: Dict[str, Any] = None
) -> Optional[RuleDecision]:
    """
    便捷函数：应用规则引擎
    
    Args:
        question: 解析后的题目
        features: 特征向量
        config: 配置参数
        
    Returns:
        规则判定结果
    """
    engine = RuleEngine(config)
    return engine.apply_rules(question, features)
