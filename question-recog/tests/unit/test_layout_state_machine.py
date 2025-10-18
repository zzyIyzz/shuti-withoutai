"""
版面状态机解析器测试
"""

import pytest
from src.parsing.layout_state_machine import LayoutStateMachine, ParseState
from src.io.schemas import TextBlock, ParsedQuestion


class TestLayoutStateMachine:
    """版面状态机测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.parser = LayoutStateMachine()
    
    def test_single_choice_question(self):
        """测试单选题解析"""
        blocks = [
            TextBlock(type="text", text="1. 下列关于电力安全的说法正确的是？", line_no=1),
            TextBlock(type="text", text="A. 安全第一", line_no=2),
            TextBlock(type="text", text="B. 预防为主", line_no=3),
            TextBlock(type="text", text="C. 综合治理", line_no=4),
            TextBlock(type="text", text="D. 以上都对", line_no=5),
            TextBlock(type="text", text="答案：D", line_no=6)
        ]
        
        questions = self.parser.parse(blocks)
        
        assert len(questions) == 1
        question = questions[0]
        
        assert "下列关于电力安全的说法正确的是" in question.question
        assert len(question.options) == 4
        assert question.options[0] == "安全第一"
        assert question.answer_raw == "D"
    
    def test_true_false_question_with_symbol(self):
        """测试带符号的判断题"""
        blocks = [
            TextBlock(type="text", text="2. 电力设备运行前必须进行安全检查。(√)", line_no=1)
        ]
        
        questions = self.parser.parse(blocks)
        
        assert len(questions) == 1
        question = questions[0]
        
        assert "电力设备运行前必须进行安全检查" in question.question
        assert "√" not in question.question  # 答案符号应该被剥离
        assert question.answer_raw == "√"
        assert question.parse_flags["tail_answer_stripped"] == True
    
    def test_fill_blank_question(self):
        """测试填空题解析"""
        blocks = [
            TextBlock(type="text", text="3. 变压器的额定容量为___MVA。", line_no=1),
            TextBlock(type="text", text="答案：100", line_no=2)
        ]
        
        questions = self.parser.parse(blocks)
        
        assert len(questions) == 1
        question = questions[0]
        
        assert "变压器的额定容量为" in question.question
        assert "___" in question.question
        assert question.answer_raw == "100"
        assert len(question.options) == 0
    
    def test_subjective_question(self):
        """测试简答题解析"""
        blocks = [
            TextBlock(type="text", text="4. 请简述电力系统继电保护的基本要求。", line_no=1),
            TextBlock(type="text", text="答案：继电保护应满足可靠性、选择性、灵敏性、速动性四个基本要求。", line_no=2)
        ]
        
        questions = self.parser.parse(blocks)
        
        assert len(questions) == 1
        question = questions[0]
        
        assert "请简述电力系统继电保护的基本要求" in question.question
        assert "继电保护应满足" in question.answer_raw
        assert len(question.options) == 0
    
    def test_option_line_merging(self):
        """测试选项跨行归并"""
        blocks = [
            TextBlock(type="text", text="5. 下列选项正确的是？", line_no=1),
            TextBlock(type="text", text="A. 这是一个很长的选项", line_no=2),
            TextBlock(type="text", text="内容跨越了多行", line_no=3),
            TextBlock(type="text", text="B. 这是选项B", line_no=4)
        ]
        
        questions = self.parser.parse(blocks)
        
        assert len(questions) == 1
        question = questions[0]
        
        assert len(question.options) == 2
        assert "这是一个很长的选项 内容跨越了多行" in question.options[0]
        assert question.parse_flags["merged_lines"] == True
    
    def test_multiple_questions(self):
        """测试多题目解析"""
        blocks = [
            TextBlock(type="text", text="1. 第一题内容", line_no=1),
            TextBlock(type="text", text="A. 选项A", line_no=2),
            TextBlock(type="text", text="B. 选项B", line_no=3),
            TextBlock(type="text", text="2. 第二题内容", line_no=4),
            TextBlock(type="text", text="答案：正确答案", line_no=5)
        ]
        
        questions = self.parser.parse(blocks)
        
        assert len(questions) == 2
        assert "第一题内容" in questions[0].question
        assert "第二题内容" in questions[1].question
        assert len(questions[0].options) == 2
        assert questions[1].answer_raw == "正确答案"
    
    def test_layout_score_calculation(self):
        """测试版面质量分数计算"""
        # 高质量版面
        high_quality_blocks = [
            TextBlock(type="text", text="1. 清晰的题目内容", line_no=1, ocr_conf=0.95),
            TextBlock(type="text", text="A. 选项A", line_no=2, ocr_conf=0.98),
            TextBlock(type="text", text="B. 选项B", line_no=3, ocr_conf=0.97)
        ]
        
        questions = self.parser.parse(high_quality_blocks)
        assert questions[0].layout_score > 0.9
        
        # 低质量版面
        low_quality_blocks = [
            TextBlock(type="text", text="题", line_no=1, ocr_conf=0.3),
        ]
        
        questions = self.parser.parse(low_quality_blocks)
        assert questions[0].layout_score < 0.5
    
    def test_answer_extraction_channels(self):
        """测试多通道答案抓取"""
        # 通道A: 显式标记
        blocks_a = [
            TextBlock(type="text", text="题目内容", line_no=1),
            TextBlock(type="text", text="参考答案：这是答案", line_no=2)
        ]
        
        questions = self.parser.parse(blocks_a)
        assert questions[0].answer_raw == "这是答案"
        
        # 通道B: 行尾括注
        blocks_b = [
            TextBlock(type="text", text="请简述工作原理（基本原理说明）", line_no=1)
        ]
        
        questions = self.parser.parse(blocks_b)
        assert questions[0].answer_raw == "基本原理说明"
    
    def test_question_cleaning(self):
        """测试题目清理"""
        blocks = [
            TextBlock(type="text", text="1. 这是题目内容", line_no=1)
        ]
        
        questions = self.parser.parse(blocks)
        
        # 题目编号应该被清理
        assert "1." not in questions[0].question
        assert "这是题目内容" in questions[0].question
    
    def test_normalization(self):
        """测试答案规范化"""
        blocks = [
            TextBlock(type="text", text="题目", line_no=1),
            TextBlock(type="text", text="答案：Ａ", line_no=2)  # 全角A
        ]
        
        questions = self.parser.parse(blocks)
        assert questions[0].answer_raw == "A"  # 应该转换为半角


if __name__ == "__main__":
    pytest.main([__file__])
