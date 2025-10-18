"""
评估指标模块 - 计算各种分类指标
支持宏/微F1、召回、精度、ECE、PSI等指标
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report
)
import logging


logger = logging.getLogger(__name__)


class MetricsCalculator:
    """指标计算器"""
    
    def __init__(self):
        self.classes = []
    
    def calculate_classification_metrics(
        self, 
        y_true: List[str], 
        y_pred: List[str], 
        classes: List[str] = None
    ) -> Dict[str, Any]:
        """
        计算分类指标
        
        Args:
            y_true: 真实标签
            y_pred: 预测标签
            classes: 类别列表
            
        Returns:
            指标字典
        """
        if classes is None:
            classes = sorted(list(set(y_true + y_pred)))
        
        self.classes = classes
        
        # 基础指标
        accuracy = accuracy_score(y_true, y_pred)
        
        # 每类别指标
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, labels=classes, zero_division=0
        )
        
        # 宏平均和微平均
        macro_precision = np.mean(precision)
        macro_recall = np.mean(recall)
        macro_f1 = np.mean(f1)
        
        weighted_precision = np.average(precision, weights=support)
        weighted_recall = np.average(recall, weights=support)
        weighted_f1 = np.average(f1, weights=support)
        
        # 混淆矩阵
        cm = confusion_matrix(y_true, y_pred, labels=classes)
        
        # 构建结果
        metrics = {
            "accuracy": float(accuracy),
            "macro_precision": float(macro_precision),
            "macro_recall": float(macro_recall),
            "macro_f1": float(macro_f1),
            "weighted_precision": float(weighted_precision),
            "weighted_recall": float(weighted_recall),
            "weighted_f1": float(weighted_f1),
            "confusion_matrix": cm.tolist(),
            "classes": classes,
            "per_class_metrics": {}
        }
        
        # 每个类别的详细指标
        for i, class_name in enumerate(classes):
            metrics["per_class_metrics"][class_name] = {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1_score": float(f1[i]),
                "support": int(support[i])
            }
        
        return metrics
    
    def calculate_confidence_metrics(
        self, 
        confidences: List[float], 
        predictions: List[str], 
        y_true: List[str],
        threshold_low: float = 0.5
    ) -> Dict[str, Any]:
        """
        计算置信度相关指标
        
        Args:
            confidences: 置信度列表
            predictions: 预测标签
            y_true: 真实标签
            threshold_low: 低置信度阈值
            
        Returns:
            置信度指标
        """
        confidences = np.array(confidences)
        is_correct = np.array(predictions) == np.array(y_true)
        
        # 低置信度样本比例
        low_confidence_mask = confidences < threshold_low
        low_confidence_rate = low_confidence_mask.mean()
        
        # 低置信度样本的准确率
        if low_confidence_mask.sum() > 0:
            low_confidence_accuracy = is_correct[low_confidence_mask].mean()
        else:
            low_confidence_accuracy = 0.0
        
        # 高置信度样本的准确率
        high_confidence_mask = ~low_confidence_mask
        if high_confidence_mask.sum() > 0:
            high_confidence_accuracy = is_correct[high_confidence_mask].mean()
        else:
            high_confidence_accuracy = 0.0
        
        # 置信度分布统计
        confidence_stats = {
            "mean": float(confidences.mean()),
            "std": float(confidences.std()),
            "min": float(confidences.min()),
            "max": float(confidences.max()),
            "median": float(np.median(confidences)),
            "q25": float(np.percentile(confidences, 25)),
            "q75": float(np.percentile(confidences, 75))
        }
        
        return {
            "low_confidence_rate": float(low_confidence_rate),
            "low_confidence_accuracy": float(low_confidence_accuracy),
            "high_confidence_accuracy": float(high_confidence_accuracy),
            "confidence_stats": confidence_stats,
            "threshold_low": threshold_low
        }
    
    def calculate_ece(
        self, 
        confidences: List[float], 
        predictions: List[str], 
        y_true: List[str],
        n_bins: int = 10
    ) -> Dict[str, Any]:
        """
        计算期望校准误差 (Expected Calibration Error)
        
        Args:
            confidences: 置信度列表
            predictions: 预测标签
            y_true: 真实标签
            n_bins: 分箱数量
            
        Returns:
            ECE相关指标
        """
        confidences = np.array(confidences)
        is_correct = np.array(predictions) == np.array(y_true)
        
        # 分箱
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        ece = 0
        bin_data = []
        
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            # 找到在当前箱中的样本
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            prop_in_bin = in_bin.mean()
            
            if prop_in_bin > 0:
                # 计算箱内的平均置信度和准确率
                accuracy_in_bin = is_correct[in_bin].mean()
                avg_confidence_in_bin = confidences[in_bin].mean()
                
                # 累加ECE
                calibration_error = abs(avg_confidence_in_bin - accuracy_in_bin)
                ece += calibration_error * prop_in_bin
                
                bin_data.append({
                    "bin_lower": float(bin_lower),
                    "bin_upper": float(bin_upper),
                    "avg_confidence": float(avg_confidence_in_bin),
                    "accuracy": float(accuracy_in_bin),
                    "count": int(in_bin.sum()),
                    "proportion": float(prop_in_bin),
                    "calibration_error": float(calibration_error)
                })
            else:
                bin_data.append({
                    "bin_lower": float(bin_lower),
                    "bin_upper": float(bin_upper),
                    "avg_confidence": float((bin_lower + bin_upper) / 2),
                    "accuracy": 0.0,
                    "count": 0,
                    "proportion": 0.0,
                    "calibration_error": 0.0
                })
        
        return {
            "ece": float(ece),
            "n_bins": n_bins,
            "bin_data": bin_data
        }
    
    def calculate_psi(
        self, 
        baseline_dist: Dict[str, float], 
        current_dist: Dict[str, float]
    ) -> float:
        """
        计算人口稳定性指数 (Population Stability Index)
        
        Args:
            baseline_dist: 基线分布
            current_dist: 当前分布
            
        Returns:
            PSI值
        """
        psi = 0.0
        
        all_classes = set(baseline_dist.keys()) | set(current_dist.keys())
        
        for class_name in all_classes:
            baseline_prop = baseline_dist.get(class_name, 0.001)  # 避免0
            current_prop = current_dist.get(class_name, 0.001)
            
            # PSI公式
            psi += (current_prop - baseline_prop) * np.log(current_prop / baseline_prop)
        
        return float(psi)
    
    def calculate_layout_score_metrics(self, layout_scores: List[float]) -> Dict[str, Any]:
        """
        计算版面质量分数指标
        
        Args:
            layout_scores: 版面分数列表
            
        Returns:
            版面指标
        """
        scores = np.array(layout_scores)
        
        return {
            "mean_layout_score": float(scores.mean()),
            "std_layout_score": float(scores.std()),
            "min_layout_score": float(scores.min()),
            "max_layout_score": float(scores.max()),
            "low_quality_rate": float((scores < 0.5).mean()),  # 低质量版面比例
            "high_quality_rate": float((scores > 0.8).mean())  # 高质量版面比例
        }


class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.metrics_calculator = MetricsCalculator()
    
    def analyze_by_source_channel(
        self, 
        results: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        按数据来源通道分析性能
        
        Args:
            results: 分类结果列表
            
        Returns:
            各通道的性能指标
        """
        # 按通道分组
        channel_groups = {}
        for result in results:
            channel = result.get("meta", {}).get("channel", "unknown")
            if channel not in channel_groups:
                channel_groups[channel] = []
            channel_groups[channel].append(result)
        
        # 计算各通道指标
        channel_metrics = {}
        for channel, channel_results in channel_groups.items():
            y_true = [r["true_label"] for r in channel_results]
            y_pred = [r["predicted_label"] for r in channel_results]
            confidences = [r["confidence"] for r in channel_results]
            
            metrics = self.metrics_calculator.calculate_classification_metrics(y_true, y_pred)
            confidence_metrics = self.metrics_calculator.calculate_confidence_metrics(
                confidences, y_pred, y_true
            )
            
            channel_metrics[channel] = {
                **metrics,
                **confidence_metrics,
                "sample_count": len(channel_results)
            }
        
        return channel_metrics
    
    def analyze_by_layout_quality(
        self, 
        results: List[Dict[str, Any]],
        quality_bins: List[Tuple[float, float]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        按版面质量分析性能
        
        Args:
            results: 分类结果列表
            quality_bins: 质量分箱 [(low, high), ...]
            
        Returns:
            各质量段的性能指标
        """
        if quality_bins is None:
            quality_bins = [(0.0, 0.4), (0.4, 0.7), (0.7, 1.0)]
        
        # 按质量分组
        quality_groups = {f"{low}-{high}": [] for low, high in quality_bins}
        
        for result in results:
            layout_score = result.get("layout_score", 0.0)
            
            for low, high in quality_bins:
                if low <= layout_score < high:
                    quality_groups[f"{low}-{high}"].append(result)
                    break
        
        # 计算各质量段指标
        quality_metrics = {}
        for quality_range, quality_results in quality_groups.items():
            if not quality_results:
                continue
            
            y_true = [r["true_label"] for r in quality_results]
            y_pred = [r["predicted_label"] for r in quality_results]
            confidences = [r["confidence"] for r in quality_results]
            
            metrics = self.metrics_calculator.calculate_classification_metrics(y_true, y_pred)
            confidence_metrics = self.metrics_calculator.calculate_confidence_metrics(
                confidences, y_pred, y_true
            )
            
            quality_metrics[quality_range] = {
                **metrics,
                **confidence_metrics,
                "sample_count": len(quality_results)
            }
        
        return quality_metrics


def calculate_comprehensive_metrics(
    y_true: List[str],
    y_pred: List[str],
    confidences: List[float],
    layout_scores: List[float] = None,
    classes: List[str] = None
) -> Dict[str, Any]:
    """
    便捷函数：计算综合指标
    
    Args:
        y_true: 真实标签
        y_pred: 预测标签
        confidences: 置信度
        layout_scores: 版面分数
        classes: 类别列表
        
    Returns:
        综合指标
    """
    calculator = MetricsCalculator()
    
    # 基础分类指标
    classification_metrics = calculator.calculate_classification_metrics(y_true, y_pred, classes)
    
    # 置信度指标
    confidence_metrics = calculator.calculate_confidence_metrics(confidences, y_pred, y_true)
    
    # ECE指标
    ece_metrics = calculator.calculate_ece(confidences, y_pred, y_true)
    
    # 版面指标
    layout_metrics = {}
    if layout_scores:
        layout_metrics = calculator.calculate_layout_score_metrics(layout_scores)
    
    return {
        "classification": classification_metrics,
        "confidence": confidence_metrics,
        "calibration": ece_metrics,
        "layout": layout_metrics
    }
