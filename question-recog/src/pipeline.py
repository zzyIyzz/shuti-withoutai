"""
主流程编排器 - 协调整个识别流程
parse → features → rule → model → calibrate
"""

import time
import json
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from .io.schemas import (
    DocumentInput, ParsedQuestion, QuestionFeatures, 
    RuleDecision, ModelPrediction, CalibratedResult, 
    ClassificationResult, QuestionType
)
from .parsing.layout_state_machine import LayoutStateMachine
from .features.extractor import FeatureExtractor
from .rules.engine import RuleEngine


logger = logging.getLogger(__name__)


class QuestionRecognitionPipeline:
    """题型识别流水线"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 初始化各个组件
        self.parser = LayoutStateMachine(config.get("parsing", {}))
        self.feature_extractor = FeatureExtractor(config.get("features", {}))
        self.rule_engine = RuleEngine(config.get("rules", {}))
        
        # 模型和校准器将在需要时延迟加载
        self.model = None
        self.calibrator = None
        self.label_encoder = None
        self.feature_names = None
        
        # 统计信息
        self.stats = {
            "total_processed": 0,
            "rule_hits": 0,
            "model_predictions": 0,
            "low_confidence": 0,
            "processing_times": []
        }
    
    def process_document(self, document: DocumentInput) -> List[ClassificationResult]:
        """
        处理单个文档
        
        Args:
            document: 文档输入
            
        Returns:
            分类结果列表
        """
        start_time = time.time()
        
        try:
            # 1. 解析文档为题目
            questions = self.parser.parse(document.blocks)
            logger.info(f"解析得到 {len(questions)} 个题目")
            
            # 2. 处理每个题目
            results = []
            for i, question in enumerate(questions):
                result = self.process_question(
                    question, 
                    source_id=f"{document.source_id}#q{i+1}"
                )
                results.append(result)
            
            # 3. 更新统计
            processing_time = time.time() - start_time
            self.stats["total_processed"] += len(questions)
            self.stats["processing_times"].append(processing_time)
            
            logger.info(f"文档处理完成，耗时 {processing_time:.3f}s")
            return results
            
        except Exception as e:
            logger.error(f"文档处理失败: {e}")
            raise
    
    def process_question(self, question: ParsedQuestion, source_id: str = "") -> ClassificationResult:
        """
        处理单个题目
        
        Args:
            question: 解析后的题目
            source_id: 数据源标识
            
        Returns:
            分类结果
        """
        start_time = time.time()
        explanations = []
        
        try:
            # 1. 特征提取
            features = self.feature_extractor.extract_features(question)
            explanations.append(f"提取特征: {len(self.feature_extractor.get_feature_names())} 维")
            
            # 2. 规则判定
            rule_decision = self.rule_engine.apply_rules(question, features)
            model_prediction = None
            
            if rule_decision:
                # 规则命中，直接使用规则结果
                final_type = rule_decision.type
                final_confidence = rule_decision.confidence
                final_probabilities = {rule_decision.type.value: rule_decision.confidence}
                explanations.append(rule_decision.explanation)
                self.stats["rule_hits"] += 1
                
            else:
                # 规则未命中，使用模型预测
                model_prediction = self._predict_with_model(features)
                if model_prediction:
                    # 获取最高概率的类别
                    best_type = max(model_prediction.probabilities.items(), key=lambda x: x[1])
                    final_type = QuestionType(best_type[0])
                    final_probabilities = model_prediction.probabilities
                    
                    # 校准概率
                    calibrated_probs = self._calibrate_probabilities(final_probabilities)
                    final_confidence = max(calibrated_probs.values())
                    final_probabilities = calibrated_probs
                    
                    explanations.append(f"模型预测: {final_type.value} (概率: {final_confidence:.3f})")
                    self.stats["model_predictions"] += 1
                else:
                    # 兜底：未知类型
                    final_type = QuestionType.UNKNOWN
                    final_confidence = 0.0
                    final_probabilities = {"unknown": 1.0}
                    explanations.append("兜底策略: 未知类型")
            
            # 3. 判断是否低置信度
            min_confidence = self.config.get("thresholds", {}).get("min_confidence", 0.4)
            is_low_confidence = final_confidence < min_confidence
            if is_low_confidence:
                self.stats["low_confidence"] += 1
            
            # 4. 判断是否需要复核
            review_thresholds = self.config.get("thresholds", {}).get("review", {})
            review_threshold = review_thresholds.get(final_type.value, 0.5)
            needs_review = final_confidence < review_threshold
            
            # 5. 构建最终结果
            calibrated_result = CalibratedResult(
                type=final_type,
                confidence=final_confidence,
                probabilities=final_probabilities,
                is_low_confidence=is_low_confidence,
                needs_review=needs_review
            )
            
            processing_time = time.time() - start_time
            
            result = ClassificationResult(
                source_id=source_id,
                question=question,
                features=features,
                rule_decision=rule_decision,
                model_prediction=model_prediction,
                final_result=calibrated_result,
                explanations=explanations,
                processing_time=processing_time
            )
            
            return result
            
        except Exception as e:
            logger.error(f"题目处理失败: {e}")
            # 返回错误结果
            return self._create_error_result(question, source_id, str(e))
    
    def _predict_with_model(self, features: QuestionFeatures) -> Optional[ModelPrediction]:
        """使用模型进行预测"""
        if not self.model:
            self._load_model()
        
        if not self.model:
            logger.warning("模型未加载，跳过模型预测")
            return None
        
        try:
            # 转换特征为数组
            feature_array = self.feature_extractor.features_to_array(features)
            
            # 模型预测
            probabilities = self.model.predict_proba([feature_array])[0]
            
            # 构建概率字典 - 使用实际的类别名称
            if hasattr(self, 'label_encoder') and self.label_encoder:
                class_names = self.label_encoder.classes_
            else:
                # 回退到默认类别名称
                class_names = ["single_choice", "multiple_choice", "true_false", "fill_blank", "subjective"]
            
            prob_dict = dict(zip(class_names, probabilities))
            
            return ModelPrediction(
                probabilities=prob_dict,
                features_used=self.feature_extractor.get_feature_names(),
                model_version="1.0"
            )
            
        except Exception as e:
            logger.error(f"模型预测失败: {e}")
            return None
    
    def _calibrate_probabilities(self, probabilities: Dict[str, float]) -> Dict[str, float]:
        """校准概率"""
        if not self.calibrator:
            self._load_calibrator()
        
        if not self.calibrator:
            logger.warning("校准器未加载，返回原始概率")
            return probabilities
        
        try:
            # 这里需要实际的校准实现
            return self.calibrator.calibrate(probabilities)
        except Exception as e:
            logger.error(f"概率校准失败: {e}")
            return probabilities
    
    def _load_model(self):
        """延迟加载模型"""
        try:
            model_path = self.config.get("paths", {}).get("model_path")
            if model_path and Path(model_path).exists():
                # 加载XGBoost模型
                import xgboost as xgb
                import joblib
                
                self.model = xgb.XGBClassifier()
                self.model.load_model(model_path)
                
                # 加载标签编码器
                label_encoder_path = Path(model_path).parent / "label_encoder.pkl"
                if label_encoder_path.exists():
                    self.label_encoder = joblib.load(label_encoder_path)
                
                # 加载特征名称
                feature_names_path = Path(model_path).parent / "feature_names.json"
                if feature_names_path.exists():
                    with open(feature_names_path, 'r', encoding='utf-8') as f:
                        self.feature_names = json.load(f)
                
                logger.info(f"模型加载成功: {model_path}")
            else:
                logger.warning(f"模型文件不存在: {model_path}")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            self.model = None
    
    def _load_calibrator(self):
        """延迟加载校准器"""
        try:
            cal_path = self.config.get("paths", {}).get("calibration_path")
            if cal_path and Path(cal_path).exists():
                # 加载校准数据
                with open(cal_path, 'r', encoding='utf-8') as f:
                    calibration_data = json.load(f)
                
                # 创建一个简单的校准器类
                class SimpleCalibrator:
                    def __init__(self, data):
                        self.data = data
                        self.is_fitted = data.get('is_fitted', True)
                    
                    def calibrate(self, probabilities):
                        # 简单的恒等校准（直接返回原始概率）
                        return probabilities
                
                self.calibrator = SimpleCalibrator(calibration_data)
                logger.info(f"校准器加载成功: {cal_path}")
            else:
                logger.warning(f"校准文件不存在: {cal_path}")
        except Exception as e:
            logger.error(f"校准器加载失败: {e}")
            self.calibrator = None
    
    def _create_error_result(self, question: ParsedQuestion, source_id: str, error: str) -> ClassificationResult:
        """创建错误结果"""
        # 创建默认特征
        default_features = QuestionFeatures(
            has_options=0, num_options=0, answer_is_single_letter=0,
            answer_is_multi_letters=0, question_len=0, option_len_mean=0.0,
            answer_len=0, punct_density=0.0, question_mark_count=0,
            hint_keywords_multi=0, hint_keywords_tf=0, hint_keywords_blank=0,
            hint_keywords_subj=0, blank_underline_count=0, blank_parenthesis_count=0,
            option_alignment_score=0.0, layout_score=0.0, ocr_conf_mean=1.0,
            answer_pattern_id=0
        )
        
        error_result = CalibratedResult(
            type=QuestionType.UNKNOWN,
            confidence=0.0,
            probabilities={"unknown": 1.0},
            is_low_confidence=True,
            needs_review=True
        )
        
        return ClassificationResult(
            source_id=source_id,
            question=question,
            features=default_features,
            rule_decision=None,
            model_prediction=None,
            final_result=error_result,
            explanations=[f"处理错误: {error}"],
            processing_time=0.0
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        
        if stats["processing_times"]:
            stats["avg_processing_time"] = sum(stats["processing_times"]) / len(stats["processing_times"])
            stats["total_processing_time"] = sum(stats["processing_times"])
        else:
            stats["avg_processing_time"] = 0.0
            stats["total_processing_time"] = 0.0
        
        if stats["total_processed"] > 0:
            stats["rule_hit_rate"] = stats["rule_hits"] / stats["total_processed"]
            stats["model_prediction_rate"] = stats["model_predictions"] / stats["total_processed"]
            stats["low_confidence_rate"] = stats["low_confidence"] / stats["total_processed"]
        else:
            stats["rule_hit_rate"] = 0.0
            stats["model_prediction_rate"] = 0.0
            stats["low_confidence_rate"] = 0.0
        
        return stats
    
    def reset_statistics(self):
        """重置统计信息"""
        self.stats = {
            "total_processed": 0,
            "rule_hits": 0,
            "model_predictions": 0,
            "low_confidence": 0,
            "processing_times": []
        }
        logger.info("统计信息已重置")


def create_pipeline(config: Dict[str, Any] = None) -> QuestionRecognitionPipeline:
    """
    便捷函数：创建识别流水线
    
    Args:
        config: 配置参数
        
    Returns:
        流水线实例
    """
    return QuestionRecognitionPipeline(config)
