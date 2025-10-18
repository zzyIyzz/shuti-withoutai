"""
特征提取器测试
"""

import pytest
from src.features.extractor import FeatureExtractor
from src.io.schemas import ParsedQuestion, QuestionFeatures


class TestFeatureExtractor:
    """特征提取器测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.extractor = FeatureExtractor()
    
    def test_single_choice_features(self):
        """测试单选题特征提取"""
        question = ParsedQuestion(
            question="下列关于电力安全的说法正确的是？",
            options=["安全第一", "预防为主", "综合治理", "以上都对"],
            answer_raw="D",
            layout_score=0.85
        )
        
        features = self.extractor.extract_features(question)
        
        assert features.has_options == 1
        assert features.num_options == 4
        assert features.answer_is_single_letter == 1
        assert features.answer_is_multi_letters == 0
        assert features.question_len > 0
        assert features.layout_score == 0.85
        assert features.answer_pattern_id == 1  # 单字母模式
    
    def test_multiple_choice_features(self):
        """测试多选题特征提取"""
        question = ParsedQuestion(
            question="电力系统的安全措施包括哪些？",
            options=["技术措施", "管理措施", "组织措施", "个人防护"],
            answer_raw="ABCD",
            layout_score=0.90
        )
        
        features = self.extractor.extract_features(question)
        
        assert features.has_options == 1
        assert features.num_options == 4
        assert features.answer_is_single_letter == 0
        assert features.answer_is_multi_letters == 1
        assert features.hint_keywords_multi > 0  # 应该命中"哪些"
        assert features.answer_pattern_id == 2  # 多字母模式
    
    def test_true_false_features(self):
        """测试判断题特征提取"""
        question = ParsedQuestion(
            question="电力设备运行前必须进行安全检查，这个说法是否正确？",
            options=[],
            answer_raw="√",
            layout_score=0.75
        )
        
        features = self.extractor.extract_features(question)
        
        assert features.has_options == 0
        assert features.num_options == 0
        assert features.hint_keywords_tf > 0  # 应该命中"是否正确"
        assert features.answer_pattern_id == 3  # 判断类型模式
    
    def test_fill_blank_features(self):
        """测试填空题特征提取"""
        question = ParsedQuestion(
            question="变压器的额定容量为___MVA，标准规定不超过（）。",
            options=[],
            answer_raw="100",
            layout_score=0.80
        )
        
        features = self.extractor.extract_features(question)
        
        assert features.has_options == 0
        assert features.blank_underline_count > 0  # 应该检测到下划线
        assert features.blank_parenthesis_count > 0  # 应该检测到括号
        assert features.hint_keywords_blank > 0  # 应该命中"标准"
        assert features.answer_pattern_id == 5  # 数字模式
    
    def test_subjective_features(self):
        """测试简答题特征提取"""
        question = ParsedQuestion(
            question="请简述电力系统继电保护的基本要求，并解释其重要性。",
            options=[],
            answer_raw="继电保护应满足可靠性、选择性、灵敏性、速动性四个基本要求。可靠性要求保护装置在应该动作时能正确动作。",
            layout_score=0.70
        )
        
        features = self.extractor.extract_features(question)
        
        assert features.has_options == 0
        assert features.hint_keywords_subj > 0  # 应该命中"简述"、"解释"、"基本要求"
        assert features.answer_len > 20  # 长答案
        assert features.question_mark_count > 0  # 有问号
        assert features.answer_pattern_id == 4  # 长文本模式
    
    def test_punctuation_features(self):
        """测试标点特征提取"""
        question = ParsedQuestion(
            question="这是一个测试题目，包含：标点符号！对吗？",
            options=[],
            answer_raw="是",
            layout_score=0.60
        )
        
        features = self.extractor.extract_features(question)
        
        assert features.punct_density > 0  # 标点密度
        assert features.question_mark_count == 1  # 问号数量
    
    def test_option_alignment_score(self):
        """测试选项对齐度计算"""
        # 对齐良好的选项
        good_options = ["选项A", "选项B", "选项C", "选项D"]
        alignment_score = self.extractor._calculate_option_alignment(good_options)
        assert alignment_score > 0.8
        
        # 对齐较差的选项
        bad_options = ["A", "这是一个很长的选项B", "C", "另一个长选项D内容"]
        alignment_score = self.extractor._calculate_option_alignment(bad_options)
        assert alignment_score < 0.6
    
    def test_keyword_matching(self):
        """测试关键词匹配"""
        # 多选关键词
        multi_question = ParsedQuestion(
            question="下列哪些选项是正确的？",
            options=["A", "B", "C"],
            answer_raw="AB"
        )
        features = self.extractor.extract_features(multi_question)
        assert features.hint_keywords_multi > 0
        
        # 判断关键词
        tf_question = ParsedQuestion(
            question="这个说法是否正确？",
            options=[],
            answer_raw="对"
        )
        features = self.extractor.extract_features(tf_question)
        assert features.hint_keywords_tf > 0
    
    def test_batch_feature_extraction(self):
        """测试批量特征提取"""
        questions = [
            ParsedQuestion(question="题目1", options=["A", "B"], answer_raw="A"),
            ParsedQuestion(question="题目2", options=[], answer_raw="答案2")
        ]
        
        features_list = self.extractor.extract_batch_features(questions)
        
        assert len(features_list) == 2
        assert all(isinstance(f, QuestionFeatures) for f in features_list)
    
    def test_features_to_array(self):
        """测试特征转数组"""
        question = ParsedQuestion(
            question="测试题目",
            options=["A", "B"],
            answer_raw="A"
        )
        
        features = self.extractor.extract_features(question)
        feature_array = self.extractor.features_to_array(features)
        
        assert isinstance(feature_array, list)
        assert len(feature_array) == len(self.extractor.get_feature_names())
        assert all(isinstance(x, (int, float)) for x in feature_array)
    
    def test_feature_names(self):
        """测试特征名称获取"""
        feature_names = self.extractor.get_feature_names()
        
        assert isinstance(feature_names, list)
        assert len(feature_names) > 0
        assert "has_options" in feature_names
        assert "answer_pattern_id" in feature_names


if __name__ == "__main__":
    pytest.main([__file__])
