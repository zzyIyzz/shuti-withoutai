"""
端到端测试 - 完整流程测试
"""

import pytest
import tempfile
import json
from pathlib import Path

from src.pipeline import QuestionRecognitionPipeline
from src.io.schemas import DocumentInput, TextBlock, QuestionType


class TestEndToEnd:
    """端到端测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.config = {
            "thresholds": {
                "min_confidence": 0.4,
                "accept": {
                    "single_choice": 0.8,
                    "multiple_choice": 0.8,
                    "true_false": 0.8,
                    "fill_blank": 0.75,
                    "subjective": 0.75
                },
                "review": {
                    "single_choice": 0.55,
                    "multiple_choice": 0.55,
                    "true_false": 0.55,
                    "fill_blank": 0.50,
                    "subjective": 0.50
                }
            }
        }
        self.pipeline = QuestionRecognitionPipeline(self.config)
    
    def test_single_choice_pipeline(self):
        """测试单选题完整流程"""
        # 构建文档输入
        blocks = [
            TextBlock(type="text", text="1. 下列关于电力安全的说法正确的是？", line_no=1),
            TextBlock(type="text", text="A. 安全第一", line_no=2),
            TextBlock(type="text", text="B. 预防为主", line_no=3),
            TextBlock(type="text", text="C. 综合治理", line_no=4),
            TextBlock(type="text", text="D. 以上都对", line_no=5)
        ]
        
        document = DocumentInput(
            source_id="test://single_choice",
            blocks=blocks,
            meta={"channel": "test"}
        )
        
        # 处理文档
        results = self.pipeline.process_document(document)
        
        assert len(results) == 1
        result = results[0]
        
        # 验证解析结果
        assert "下列关于电力安全的说法正确的是" in result.question.question
        assert len(result.question.options) == 4
        assert result.question.options[0] == "安全第一"
        
        # 验证特征提取
        assert result.features.has_options == 1
        assert result.features.num_options == 4
        
        # 验证规则判定（应该命中单选题规则）
        assert result.rule_decision is not None
        assert result.rule_decision.type == QuestionType.SINGLE_CHOICE
        
        # 验证最终结果
        assert result.final_result.type == QuestionType.SINGLE_CHOICE
        assert result.final_result.confidence > 0.8
        assert not result.final_result.is_low_confidence
    
    def test_true_false_pipeline(self):
        """测试判断题完整流程"""
        blocks = [
            TextBlock(type="text", text="2. 电力设备运行前必须进行安全检查。(√)", line_no=1)
        ]
        
        document = DocumentInput(
            source_id="test://true_false",
            blocks=blocks,
            meta={"channel": "test"}
        )
        
        results = self.pipeline.process_document(document)
        
        assert len(results) == 1
        result = results[0]
        
        # 验证答案剥离
        assert "√" not in result.question.question
        assert result.question.answer_raw == "√"
        assert result.question.parse_flags["tail_answer_stripped"] == True
        
        # 验证规则命中
        assert result.rule_decision is not None
        assert result.rule_decision.type == QuestionType.TRUE_FALSE
        
        # 验证最终结果
        assert result.final_result.type == QuestionType.TRUE_FALSE
    
    def test_subjective_pipeline(self):
        """测试简答题完整流程"""
        blocks = [
            TextBlock(type="text", text="3. 请简述电力系统继电保护的基本要求。", line_no=1),
            TextBlock(type="text", text="答案：继电保护应满足可靠性、选择性、灵敏性、速动性四个基本要求。", line_no=2)
        ]
        
        document = DocumentInput(
            source_id="test://subjective",
            blocks=blocks,
            meta={"channel": "test"}
        )
        
        results = self.pipeline.process_document(document)
        
        assert len(results) == 1
        result = results[0]
        
        # 验证答案提取
        assert "继电保护应满足" in result.question.answer_raw
        assert len(result.question.options) == 0
        
        # 验证特征
        assert result.features.has_options == 0
        assert result.features.hint_keywords_subj > 0
        
        # 验证规则或模型判定
        assert result.final_result.type == QuestionType.SUBJECTIVE
    
    def test_multiple_questions_pipeline(self):
        """测试多题目文档流程"""
        blocks = [
            # 第一题：单选题
            TextBlock(type="text", text="1. 第一题内容", line_no=1),
            TextBlock(type="text", text="A. 选项A", line_no=2),
            TextBlock(type="text", text="B. 选项B", line_no=3),
            
            # 第二题：判断题
            TextBlock(type="text", text="2. 第二题是判断题。(×)", line_no=4),
            
            # 第三题：填空题
            TextBlock(type="text", text="3. 填空题内容___。", line_no=5),
            TextBlock(type="text", text="答案：填空答案", line_no=6)
        ]
        
        document = DocumentInput(
            source_id="test://multiple",
            blocks=blocks,
            meta={"channel": "test"}
        )
        
        results = self.pipeline.process_document(document)
        
        assert len(results) == 3
        
        # 验证第一题
        assert results[0].final_result.type == QuestionType.SINGLE_CHOICE
        assert len(results[0].question.options) == 2
        
        # 验证第二题
        assert results[1].final_result.type == QuestionType.TRUE_FALSE
        assert results[1].question.answer_raw == "×"
        
        # 验证第三题
        assert results[2].final_result.type == QuestionType.FILL_BLANK
        assert "___" in results[2].question.question
        assert results[2].question.answer_raw == "填空答案"
    
    def test_low_confidence_handling(self):
        """测试低置信度处理"""
        # 构建一个模糊的题目
        blocks = [
            TextBlock(type="text", text="模糊题目", line_no=1),
            TextBlock(type="text", text="模糊答案", line_no=2)
        ]
        
        document = DocumentInput(
            source_id="test://low_confidence",
            blocks=blocks,
            meta={"channel": "test"}
        )
        
        results = self.pipeline.process_document(document)
        
        assert len(results) == 1
        result = results[0]
        
        # 应该被标记为低置信度或需要复核
        assert (result.final_result.is_low_confidence or 
                result.final_result.needs_review)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 空文档
        empty_document = DocumentInput(
            source_id="test://empty",
            blocks=[],
            meta={"channel": "test"}
        )
        
        results = self.pipeline.process_document(empty_document)
        assert len(results) == 0
        
        # 无效文本块
        invalid_blocks = [
            TextBlock(type="text", text="", line_no=1),  # 空文本
            TextBlock(type="text", text="   ", line_no=2)  # 空白文本
        ]
        
        invalid_document = DocumentInput(
            source_id="test://invalid",
            blocks=invalid_blocks,
            meta={"channel": "test"}
        )
        
        results = self.pipeline.process_document(invalid_document)
        # 应该能处理但可能结果为空或错误
        assert isinstance(results, list)
    
    def test_pipeline_statistics(self):
        """测试流水线统计"""
        # 处理多个文档
        documents = []
        
        # 单选题文档
        documents.append(DocumentInput(
            source_id="test://stats1",
            blocks=[
                TextBlock(type="text", text="单选题", line_no=1),
                TextBlock(type="text", text="A. 选项A", line_no=2),
                TextBlock(type="text", text="B. 选项B", line_no=3)
            ]
        ))
        
        # 判断题文档
        documents.append(DocumentInput(
            source_id="test://stats2",
            blocks=[
                TextBlock(type="text", text="判断题。(√)", line_no=1)
            ]
        ))
        
        # 处理所有文档
        for doc in documents:
            self.pipeline.process_document(doc)
        
        # 获取统计信息
        stats = self.pipeline.get_statistics()
        
        assert stats["total_processed"] == 2
        assert stats["rule_hits"] >= 0
        assert stats["avg_processing_time"] >= 0
        assert 0 <= stats["rule_hit_rate"] <= 1
    
    def test_config_impact(self):
        """测试配置参数影响"""
        # 使用严格阈值的配置
        strict_config = {
            "thresholds": {
                "min_confidence": 0.9,  # 很高的最小置信度
                "review": {
                    "single_choice": 0.95,  # 很高的复核阈值
                }
            }
        }
        
        strict_pipeline = QuestionRecognitionPipeline(strict_config)
        
        blocks = [
            TextBlock(type="text", text="普通单选题", line_no=1),
            TextBlock(type="text", text="A. 选项A", line_no=2),
            TextBlock(type="text", text="B. 选项B", line_no=3)
        ]
        
        document = DocumentInput(
            source_id="test://strict",
            blocks=blocks
        )
        
        results = strict_pipeline.process_document(document)
        
        # 在严格配置下，更可能需要复核
        assert len(results) == 1
        result = results[0]
        
        # 根据严格配置，可能会被标记为需要复核
        # 具体行为取决于规则命中情况


if __name__ == "__main__":
    pytest.main([__file__])
