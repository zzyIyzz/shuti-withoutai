"""
数据结构定义 - 输入输出接口契约
"""

from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    """题型枚举"""
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    SUBJECTIVE = "subjective"
    UNKNOWN = "unknown"


class SourceChannel(str, Enum):
    """数据来源通道"""
    EXCEL = "excel"
    WORD = "word"
    PDF = "pdf"
    OCR = "ocr"
    TEXT = "text"


class TextBlock(BaseModel):
    """文本块 - 解析器输入的基本单元"""
    type: str = Field(default="text", description="块类型")
    text: str = Field(description="文本内容")
    line_no: int = Field(description="行号")
    ocr_conf: Optional[float] = Field(default=None, description="OCR置信度")
    bbox: Optional[List[float]] = Field(default=None, description="边界框坐标")


class DocumentInput(BaseModel):
    """文档输入结构"""
    source_id: str = Field(description="数据源标识")
    blocks: List[TextBlock] = Field(description="文本块序列")
    meta: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    
    class Config:
        extra = "allow"


class ParsedQuestion(BaseModel):
    """解析后的题目结构"""
    question: str = Field(description="题干")
    options: List[str] = Field(default_factory=list, description="选项列表")
    answer_raw: str = Field(default="", description="原始答案")
    explanation_raw: str = Field(default="", description="原始解析")
    layout_score: float = Field(default=0.0, description="版面质量分数")
    parse_flags: Dict[str, bool] = Field(default_factory=dict, description="解析标志")
    
    class Config:
        extra = "allow"


class QuestionFeatures(BaseModel):
    """题目特征向量"""
    # 基础特征
    has_options: int = Field(description="是否有选项")
    num_options: int = Field(description="选项数量")
    answer_is_single_letter: int = Field(description="答案是否为单字母")
    answer_is_multi_letters: int = Field(description="答案是否为多字母")
    
    # 长度特征
    question_len: int = Field(description="题干长度")
    option_len_mean: float = Field(default=0.0, description="选项平均长度")
    answer_len: int = Field(description="答案长度")
    
    # 标点特征
    punct_density: float = Field(description="标点密度")
    question_mark_count: int = Field(description="问号数量")
    
    # 关键词特征
    hint_keywords_multi: int = Field(description="多选提示词命中")
    hint_keywords_tf: int = Field(description="判断题提示词命中")
    hint_keywords_blank: int = Field(description="填空题提示词命中")
    hint_keywords_subj: int = Field(description="简答题提示词命中")
    
    # 模式特征
    blank_underline_count: int = Field(description="下划线空白数量")
    blank_parenthesis_count: int = Field(description="括号空白数量")
    option_alignment_score: float = Field(default=0.0, description="选项对齐度")
    
    # 版面特征
    layout_score: float = Field(description="版面质量分数")
    ocr_conf_mean: float = Field(default=1.0, description="OCR平均置信度")
    
    # 答案模式特征
    answer_pattern_id: int = Field(description="答案模式ID")
    
    class Config:
        extra = "allow"


class RuleDecision(BaseModel):
    """规则判定结果"""
    rule_name: str = Field(description="规则名称")
    type: QuestionType = Field(description="题型")
    confidence: float = Field(description="置信度")
    explanation: str = Field(description="解释说明")
    priority: int = Field(description="规则优先级")


class ModelPrediction(BaseModel):
    """模型预测结果"""
    probabilities: Dict[str, float] = Field(description="各类别概率")
    features_used: List[str] = Field(description="使用的特征")
    model_version: str = Field(default="1.0", description="模型版本")


class CalibratedResult(BaseModel):
    """校准后结果"""
    type: QuestionType = Field(description="最终题型")
    confidence: float = Field(description="校准后置信度")
    probabilities: Dict[str, float] = Field(description="校准后概率分布")
    is_low_confidence: bool = Field(description="是否低置信度")
    needs_review: bool = Field(description="是否需要人工复核")


class ClassificationResult(BaseModel):
    """最终分类结果"""
    source_id: str = Field(description="数据源标识")
    question: ParsedQuestion = Field(description="解析后题目")
    features: QuestionFeatures = Field(description="特征向量")
    rule_decision: Optional[RuleDecision] = Field(default=None, description="规则判定")
    model_prediction: Optional[ModelPrediction] = Field(default=None, description="模型预测")
    final_result: CalibratedResult = Field(description="最终结果")
    explanations: List[str] = Field(default_factory=list, description="解释链")
    processing_time: float = Field(description="处理耗时")
    timestamp: datetime = Field(default_factory=datetime.now, description="处理时间")
    
    class Config:
        extra = "allow"


class EvaluationMetrics(BaseModel):
    """评估指标"""
    accuracy: float = Field(description="准确率")
    precision: Dict[str, float] = Field(description="各类精确率")
    recall: Dict[str, float] = Field(description="各类召回率")
    f1_score: Dict[str, float] = Field(description="各类F1分数")
    macro_f1: float = Field(description="宏平均F1")
    micro_f1: float = Field(description="微平均F1")
    confusion_matrix: List[List[int]] = Field(description="混淆矩阵")
    low_confidence_rate: float = Field(description="低置信度比例")
    ece_score: float = Field(description="期望校准误差")
    
    class Config:
        extra = "allow"


class CalibrationData(BaseModel):
    """校准数据结构"""
    version: str = Field(description="校准版本")
    timestamp: datetime = Field(description="生成时间")
    sample_count: int = Field(description="样本数量")
    ece_score: float = Field(description="ECE分数")
    calibration_curves: Dict[str, Dict[str, List[float]]] = Field(description="校准曲线数据")
    isotonic_mappings: Dict[str, Any] = Field(description="Isotonic映射")
    
    class Config:
        extra = "allow"


class BatchProcessRequest(BaseModel):
    """批处理请求"""
    input_path: str = Field(description="输入路径")
    output_path: str = Field(description="输出路径")
    use_ocr: bool = Field(default=False, description="是否使用OCR")
    batch_size: int = Field(default=100, description="批处理大小")
    parallel: bool = Field(default=True, description="是否并行处理")


class BatchProcessResponse(BaseModel):
    """批处理响应"""
    total_processed: int = Field(description="总处理数量")
    successful: int = Field(description="成功数量")
    failed: int = Field(description="失败数量")
    processing_time: float = Field(description="总处理时间")
    results_path: str = Field(description="结果文件路径")
    error_log: List[str] = Field(default_factory=list, description="错误日志")
