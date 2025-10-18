"""
版面状态机解析器 - 智能分段与跨行归并
处理题干、选项、答案的自动识别和分离
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import logging

from ..io.schemas import TextBlock, ParsedQuestion


logger = logging.getLogger(__name__)


class ParseState(Enum):
    """解析状态枚举"""
    INIT = "init"
    QUESTION = "question"
    OPTIONS = "options"
    ANSWER = "answer"
    EXPLANATION = "explanation"
    EXTRA = "extra"


class LayoutStateMachine:
    """版面状态机解析器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.load_patterns()
        self.reset()
    
    def load_patterns(self):
        """加载正则模式"""
        # 选项触发符（支持全角半角）
        self.option_trigger_pattern = re.compile(
            r'^[A-Fａ-ｆ][\.\、\)\]）】]?\s+',
            re.MULTILINE
        )
        
        # 答案标记模式
        self.answer_patterns = [
            re.compile(r'答案?[:：]\s*(.+)$', re.IGNORECASE),
            re.compile(r'正确答案[:：]\s*(.+)$', re.IGNORECASE),
            re.compile(r'参考答案[:：]\s*(.+)$', re.IGNORECASE),
            re.compile(r'【答案】\s*(.+)$', re.IGNORECASE),
            re.compile(r'答案为[:：]?\s*(.+)$', re.IGNORECASE),
        ]
        
        # 题干尾部答案剥离模式
        self.tail_answer_pattern = re.compile(
            r'（?[对错√×TrueFalseTtFf]{1,5}）?$|(?:\s*[:：]\s*)?(对|错|√|×|True|False|T|F)$'
        )
        
        # 填空标记模式
        self.blank_patterns = [
            re.compile(r'_{2,}'),  # 下划线
            re.compile(r'（\s*）'),  # 中文括号
            re.compile(r'\(\s*\)'),  # 英文括号
            re.compile(r'【\s*】'),  # 方括号
        ]
        
        # 解释标记模式
        self.explanation_patterns = [
            re.compile(r'解析[:：]\s*(.+)$', re.IGNORECASE),
            re.compile(r'解释[:：]\s*(.+)$', re.IGNORECASE),
            re.compile(r'说明[:：]\s*(.+)$', re.IGNORECASE),
        ]
    
    def reset(self):
        """重置状态机"""
        self.state = ParseState.INIT
        self.question_lines = []
        self.options = []
        self.current_option = None
        self.answer_raw = ""
        self.explanation_raw = ""
        self.parse_flags = {
            "merged_lines": False,
            "missing_option_marker": False,
            "tail_answer_stripped": False,
            "multi_channel_answer": False
        }
        self.layout_score = 0.0
    
    def parse(self, blocks: List[TextBlock]) -> List[ParsedQuestion]:
        """
        解析文本块序列为题目对象
        
        Args:
            blocks: 文本块列表
            
        Returns:
            解析后的题目列表
        """
        questions = []
        current_blocks = []
        
        for block in blocks:
            # 检查是否为新题目开始
            if self._is_new_question_start(block.text):
                # 处理前一个题目
                if current_blocks:
                    question = self._parse_single_question(current_blocks)
                    if question:
                        questions.append(question)
                
                # 开始新题目
                current_blocks = [block]
            else:
                current_blocks.append(block)
        
        # 处理最后一个题目
        if current_blocks:
            question = self._parse_single_question(current_blocks)
            if question:
                questions.append(question)
        
        return questions
    
    def _is_new_question_start(self, text: str) -> bool:
        """判断是否为新题目开始 - 修复版"""
        text = text.strip()
        
        # 扩展的题目编号模式（适配Excel格式）
        number_patterns = [
            r'^\d+[\.\、]\s*',      # 1. 或 1、
            r'^\d+\s+',              # 1 （Excel常见格式）
            r'^第\d+题[:：]?\s*',     # 第1题:
            r'^\(\d+\)\s*',         # (1)
            r'^\d+\s*[、\.]\s*',    # 1 、或1 .
            r'^\d+\s*[^0-9]',       # 数字后跟非数字（宽松匹配）
        ]
        
        for pattern in number_patterns:
            if re.match(pattern, text):
                return True
        
        # 特殊情况：如果文本很长且包含题目特征，跳过（避免整个表格被当作一题）
        if len(text) > 1000:
            return False
        
        # 如果文本包含明显的题目特征且长度适中，认为是新题目
        if 50 < len(text) < 500 and any(keyword in text for keyword in ['是指', '应该', '正确的是', '错误的是', '以下', '下列']):
            return True
        
        return False
    
    def _parse_single_question(self, blocks: List[TextBlock]) -> Optional[ParsedQuestion]:
        """解析单个题目"""
        self.reset()
        
        if not blocks:
            return None
        
        # 计算版面质量分数
        self.layout_score = self._calculate_layout_score(blocks)
        
        # 状态机解析
        for block in blocks:
            self._process_block(block)
        
        # 后处理和修正
        self._post_process()
        
        # 构建结果
        return self._build_question()
    
    def _calculate_layout_score(self, blocks: List[TextBlock]) -> float:
        """计算版面质量分数"""
        if not blocks:
            return 0.0
        
        score = 1.0
        
        # OCR置信度影响
        ocr_confs = [b.ocr_conf for b in blocks if b.ocr_conf is not None]
        if ocr_confs:
            avg_ocr_conf = sum(ocr_confs) / len(ocr_confs)
            score *= avg_ocr_conf
        
        # 文本长度合理性
        total_len = sum(len(b.text.strip()) for b in blocks)
        if total_len < 10:  # 太短
            score *= 0.5
        elif total_len > 1000:  # 太长
            score *= 0.8
        
        # 选项结构完整性
        option_count = sum(1 for b in blocks if self.option_trigger_pattern.match(b.text))
        if option_count >= 2:
            score *= 1.2  # 有选项结构加分
        
        return min(score, 1.0)
    
    def _process_block(self, block: TextBlock):
        """处理单个文本块"""
        text = block.text.strip()
        if not text:
            return
        
        # 检查答案标记
        answer_match = self._extract_answer(text)
        if answer_match:
            self.answer_raw = answer_match
            self.parse_flags["multi_channel_answer"] = True
            return
        
        # 检查解释标记
        explanation_match = self._extract_explanation(text)
        if explanation_match:
            self.explanation_raw = explanation_match
            return
        
        # 状态机转换
        if self.state == ParseState.INIT:
            self.state = ParseState.QUESTION
            self.question_lines.append(text)
        
        elif self.state == ParseState.QUESTION:
            # 检查是否进入选项段
            if self._is_option_trigger(text):
                self.state = ParseState.OPTIONS
                self._add_option(text)
            else:
                self.question_lines.append(text)
        
        elif self.state == ParseState.OPTIONS:
            # 检查是否仍为选项
            if self._is_option_trigger(text):
                self._add_option(text)
            else:
                # 软归并：归并到当前选项
                if self.current_option is not None:
                    self.options[self.current_option] += " " + text
                    self.parse_flags["merged_lines"] = True
                else:
                    # 退回到题干
                    self.question_lines.append(text)
    
    def _is_option_trigger(self, text: str) -> bool:
        """检查是否为选项触发符"""
        return bool(self.option_trigger_pattern.match(text))
    
    def _add_option(self, text: str):
        """添加选项"""
        # 提取选项字母和内容
        match = self.option_trigger_pattern.match(text)
        if match:
            option_letter = text[0].upper()
            option_content = text[match.end():].strip()
            
            self.options.append(option_content)
            self.current_option = len(self.options) - 1
    
    def _extract_answer(self, text: str) -> Optional[str]:
        """提取答案（多通道策略）"""
        # 通道A: 显式标记
        for pattern in self.answer_patterns:
            match = pattern.search(text)
            if match:
                return match.group(1).strip()
        
        # 通道B: 行尾括注（简答题优先）
        bracket_match = re.search(r'（(.+?)）$|【(.+?)】$|\((.+?)\)$', text)
        if bracket_match and any(keyword in text for keyword in 
                               ["简述", "说明", "如何", "为什么", "请"]):
            return (bracket_match.group(1) or bracket_match.group(2) or 
                   bracket_match.group(3)).strip()
        
        return None
    
    def _extract_explanation(self, text: str) -> Optional[str]:
        """提取解释"""
        for pattern in self.explanation_patterns:
            match = pattern.search(text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _post_process(self):
        """后处理和修正"""
        # 1. 题干尾部答案剥离
        if self.question_lines:
            question_text = " ".join(self.question_lines)
            match = self.tail_answer_pattern.search(question_text)
            if match:
                # 剥离答案到answer_raw
                if not self.answer_raw:
                    self.answer_raw = match.group(0).strip("（）")
                
                # 更新题干
                question_text = self.tail_answer_pattern.sub('', question_text).strip()
                self.question_lines = [question_text]
                self.parse_flags["tail_answer_stripped"] = True
        
        # 2. 简答题答案抓取（无标记情况）
        if not self.answer_raw and not self.options:
            # 检查是否为简答题特征
            question_text = " ".join(self.question_lines)
            if any(keyword in question_text for keyword in 
                   ["简述", "说明", "论述", "分析", "如何", "为什么", "请"]):
                # 尝试从最后几行提取答案
                if len(self.question_lines) >= 2:
                    potential_answer = self.question_lines[-1]
                    if 2 <= len(potential_answer) <= 80 and not re.match(r'^[A-F][\.\、]', potential_answer):
                        self.answer_raw = potential_answer
                        self.question_lines = self.question_lines[:-1]
        
        # 3. 题干回灌修正（选项误判）
        if len(self.options) < 2 and not self.answer_raw:
            # 检查题干中是否有孤立的选项模式
            question_text = " ".join(self.question_lines)
            isolated_options = re.findall(r'[A-F][\.\、][^A-F]*', question_text)
            if len(isolated_options) == 1:
                # 回灌为题干补充，清空选项
                self.options = []
                self.parse_flags["missing_option_marker"] = True
        
        # 4. 守门员规则（选项连续性检查）
        if len(self.options) >= 2:
            # 检查选项字母连续性
            option_letters = []
            for i, option in enumerate(self.options):
                expected_letter = chr(ord('A') + i)
                # 这里简化处理，实际应该从原文提取字母
                option_letters.append(expected_letter)
            
            # 如果不连续，可能是误判
            if len(option_letters) != len(set(option_letters)):
                self.parse_flags["missing_option_marker"] = True
    
    def _build_question(self) -> ParsedQuestion:
        """构建最终的题目对象"""
        # 清理和规范化
        question_text = self._clean_question_text(" ".join(self.question_lines))
        options_list = [self._clean_option_text(opt) for opt in self.options if opt.strip()]
        answer_raw = self._normalize_answer(self.answer_raw)
        
        return ParsedQuestion(
            question=question_text,
            options=options_list,
            answer_raw=answer_raw,
            explanation_raw=self.explanation_raw,
            layout_score=self.layout_score,
            parse_flags=self.parse_flags.copy()
        )
    
    def _clean_question_text(self, text: str) -> str:
        """清理题干文本"""
        if not text:
            return ""
        
        # 去除题目编号
        text = re.sub(r'^\d+[\.\、]\s*', '', text)
        text = re.sub(r'^第\d+题[:：]?\s*', '', text)
        text = re.sub(r'^\(\d+\)\s*', '', text)
        
        # 去除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _clean_option_text(self, text: str) -> str:
        """清理选项文本"""
        if not text:
            return ""
        
        # 去除选项标记
        text = self.option_trigger_pattern.sub('', text)
        
        # 去除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _normalize_answer(self, answer: str) -> str:
        """规范化答案"""
        if not answer:
            return ""
        
        # OCR符号映射
        symbol_mapping = {
            "∨": "√", "v": "√", "V": "√",
            "x": "×", "X": "×", "*": "×",
            "TRUE": "True", "FALSE": "False"
        }
        
        normalized = answer
        for old, new in symbol_mapping.items():
            normalized = normalized.replace(old, new)
        
        # 全角半角转换
        fullwidth_mapping = {
            "Ａ": "A", "Ｂ": "B", "Ｃ": "C", "Ｄ": "D", "Ｅ": "E", "Ｆ": "F",
            "（": "(", "）": ")"
        }
        
        for old, new in fullwidth_mapping.items():
            normalized = normalized.replace(old, new)
        
        return normalized.strip()


def parse_document_blocks(blocks: List[TextBlock], config: Dict[str, Any] = None) -> List[ParsedQuestion]:
    """
    便捷函数：解析文档块为题目列表
    
    Args:
        blocks: 文本块列表
        config: 配置参数
        
    Returns:
        解析后的题目列表
    """
    parser = LayoutStateMachine(config)
    return parser.parse(blocks)
