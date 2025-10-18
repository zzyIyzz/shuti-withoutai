"""
Isotonic校准器 - 概率校准与可靠性评估
实现Isotonic回归校准和ECE计算
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import logging
from datetime import datetime

from sklearn.isotonic import IsotonicRegression
from sklearn.calibration import calibration_curve


logger = logging.getLogger(__name__)


class IsotonicCalibrator:
    """Isotonic校准器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.calibrators = {}  # 每个类别一个校准器
        self.is_fitted = False
        self.classes = []
        self.calibration_data = {}
    
    def fit(self, y_true: np.ndarray, y_proba: np.ndarray, classes: List[str]) -> 'IsotonicCalibrator':
        """
        拟合校准器
        
        Args:
            y_true: 真实标签
            y_proba: 预测概率矩阵 (n_samples, n_classes)
            classes: 类别名称列表
            
        Returns:
            自身实例
        """
        self.classes = classes
        n_classes = len(classes)
        
        if y_proba.shape[1] != n_classes:
            raise ValueError(f"概率矩阵维度 {y_proba.shape[1]} 与类别数 {n_classes} 不匹配")
        
        # 为每个类别训练校准器
        for i, class_name in enumerate(classes):
            # 创建二分类标签
            y_binary = (y_true == class_name).astype(int)
            y_prob_class = y_proba[:, i]
            
            # 训练Isotonic回归
            calibrator = IsotonicRegression(out_of_bounds='clip')
            calibrator.fit(y_prob_class, y_binary)
            
            self.calibrators[class_name] = calibrator
            
            logger.info(f"类别 {class_name} 校准器训练完成")
        
        self.is_fitted = True
        return self
    
    def predict_proba(self, y_proba: np.ndarray) -> np.ndarray:
        """
        校准概率预测
        
        Args:
            y_proba: 原始概率矩阵
            
        Returns:
            校准后概率矩阵
        """
        if not self.is_fitted:
            raise ValueError("校准器未训练，请先调用fit方法")
        
        n_samples, n_classes = y_proba.shape
        calibrated_proba = np.zeros_like(y_proba)
        
        # 对每个类别进行校准
        for i, class_name in enumerate(self.classes):
            calibrator = self.calibrators[class_name]
            calibrated_proba[:, i] = calibrator.predict(y_proba[:, i])
        
        # 归一化概率（确保每行和为1）
        row_sums = calibrated_proba.sum(axis=1)
        calibrated_proba = calibrated_proba / row_sums[:, np.newaxis]
        
        return calibrated_proba
    
    def calibrate(self, probabilities: Dict[str, float]) -> Dict[str, float]:
        """
        校准单个样本的概率
        
        Args:
            probabilities: 原始概率字典
            
        Returns:
            校准后概率字典
        """
        if not self.is_fitted:
            logger.warning("校准器未训练，返回原始概率")
            return probabilities
        
        # 转换为数组格式
        prob_array = np.array([[probabilities.get(cls, 0.0) for cls in self.classes]])
        
        # 校准
        calibrated_array = self.predict_proba(prob_array)
        
        # 转换回字典格式
        calibrated_dict = {}
        for i, class_name in enumerate(self.classes):
            calibrated_dict[class_name] = float(calibrated_array[0, i])
        
        return calibrated_dict
    
    def calculate_ece(self, y_true: np.ndarray, y_proba: np.ndarray, n_bins: int = 10) -> float:
        """
        计算期望校准误差 (Expected Calibration Error)
        
        Args:
            y_true: 真实标签
            y_proba: 预测概率
            n_bins: 分箱数量
            
        Returns:
            ECE分数
        """
        # 获取最大概率和预测类别
        max_probs = np.max(y_proba, axis=1)
        predictions = np.argmax(y_proba, axis=1)
        
        # 转换真实标签为数值
        if len(y_true) > 0 and isinstance(y_true[0], str):
            # 字符串标签，需要转换
            try:
                true_labels = np.array([self.classes.index(label) for label in y_true])
            except ValueError as e:
                # 如果标签不在classes中，尝试创建映射
                unique_labels = list(set(y_true))
                if not self.classes:
                    self.classes = unique_labels
                true_labels = np.array([self.classes.index(label) for label in y_true])
        else:
            # 数值标签
            true_labels = np.array(y_true)
        
        # 计算准确性
        accuracies = (predictions == true_labels).astype(float)
        
        # 分箱
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        ece = 0
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            # 找到在当前箱中的样本
            in_bin = (max_probs > bin_lower) & (max_probs <= bin_upper)
            prop_in_bin = in_bin.mean()
            
            if prop_in_bin > 0:
                # 计算箱内的平均置信度和准确率
                accuracy_in_bin = accuracies[in_bin].mean()
                avg_confidence_in_bin = max_probs[in_bin].mean()
                
                # 累加ECE
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
        
        return ece
    
    def get_reliability_diagram_data(self, y_true: np.ndarray, y_proba: np.ndarray, n_bins: int = 10) -> Dict[str, Any]:
        """
        获取可靠性图数据
        
        Args:
            y_true: 真实标签
            y_proba: 预测概率
            n_bins: 分箱数量
            
        Returns:
            可靠性图数据
        """
        max_probs = np.max(y_proba, axis=1)
        predictions = np.argmax(y_proba, axis=1)
        true_labels = np.array([self.classes.index(label) for label in y_true])
        accuracies = (predictions == true_labels).astype(float)
        
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_centers = (bin_boundaries[:-1] + bin_boundaries[1:]) / 2
        
        bin_accuracies = []
        bin_confidences = []
        bin_counts = []
        
        for i in range(n_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i + 1]
            
            in_bin = (max_probs > bin_lower) & (max_probs <= bin_upper)
            
            if in_bin.sum() > 0:
                bin_accuracy = accuracies[in_bin].mean()
                bin_confidence = max_probs[in_bin].mean()
                bin_count = in_bin.sum()
            else:
                bin_accuracy = 0
                bin_confidence = bin_centers[i]
                bin_count = 0
            
            bin_accuracies.append(bin_accuracy)
            bin_confidences.append(bin_confidence)
            bin_counts.append(bin_count)
        
        return {
            "bin_centers": bin_centers.tolist(),
            "bin_accuracies": bin_accuracies,
            "bin_confidences": bin_confidences,
            "bin_counts": bin_counts,
            "ece": self.calculate_ece(y_true, y_proba, n_bins)
        }
    
    def save_calibration_data(self, output_path: str, metadata: Dict[str, Any] = None):
        """
        保存校准数据
        
        Args:
            output_path: 输出路径
            metadata: 元数据
        """
        if not self.is_fitted:
            raise ValueError("校准器未训练，无法保存")
        
        # 准备校准数据
        calibration_data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "classes": self.classes,
            "is_fitted": self.is_fitted,
            "isotonic_mappings": {},
            "metadata": metadata or {}
        }
        
        # 保存每个类别的校准映射
        for class_name, calibrator in self.calibrators.items():
            # 获取校准函数的关键点
            x_points = calibrator.X_thresholds_
            y_points = calibrator.y_thresholds_
            
            calibration_data["isotonic_mappings"][class_name] = {
                "x_thresholds": x_points.tolist(),
                "y_thresholds": y_points.tolist()
            }
        
        # 保存到文件
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(calibration_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"校准数据已保存至: {output_path}")
    
    def load_calibration_data(self, input_path: str) -> 'IsotonicCalibrator':
        """
        加载校准数据
        
        Args:
            input_path: 输入路径
            
        Returns:
            自身实例
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"校准文件不存在: {input_path}")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            calibration_data = json.load(f)
        
        self.classes = calibration_data["classes"]
        self.is_fitted = calibration_data["is_fitted"]
        self.calibration_data = calibration_data
        
        # 重建校准器
        self.calibrators = {}
        for class_name, mapping in calibration_data["isotonic_mappings"].items():
            calibrator = IsotonicRegression(out_of_bounds='clip')
            
            # 手动设置校准器的阈值
            calibrator.X_thresholds_ = np.array(mapping["x_thresholds"])
            calibrator.y_thresholds_ = np.array(mapping["y_thresholds"])
            calibrator.increasing_ = True  # Isotonic默认单调递增
            
            self.calibrators[class_name] = calibrator
        
        logger.info(f"校准数据已加载: {input_path}")
        return self
    
    def get_calibration_info(self) -> Dict[str, Any]:
        """获取校准器信息"""
        if not self.is_fitted:
            return {"status": "not_fitted"}
        
        info = {
            "status": "fitted",
            "classes": self.classes,
            "n_classes": len(self.classes),
            "calibrators": list(self.calibrators.keys())
        }
        
        if self.calibration_data:
            info.update({
                "version": self.calibration_data.get("version"),
                "timestamp": self.calibration_data.get("timestamp"),
                "metadata": self.calibration_data.get("metadata", {})
            })
        
        return info


class CalibrationManager:
    """校准管理器 - 支持热更新"""
    
    def __init__(self, calibration_path: str):
        self.calibration_path = Path(calibration_path)
        self.calibrator = IsotonicCalibrator()
        self.last_modified = None
        
        # 初始加载
        self.reload_if_needed()
    
    def reload_if_needed(self) -> bool:
        """如果需要则重新加载校准数据"""
        if not self.calibration_path.exists():
            return False
        
        current_modified = self.calibration_path.stat().st_mtime
        
        if self.last_modified is None or current_modified > self.last_modified:
            try:
                self.calibrator.load_calibration_data(str(self.calibration_path))
                self.last_modified = current_modified
                logger.info("校准数据已热更新")
                return True
            except Exception as e:
                logger.error(f"校准数据热更新失败: {e}")
                return False
        
        return False
    
    def calibrate(self, probabilities: Dict[str, float]) -> Dict[str, float]:
        """校准概率（支持热更新）"""
        self.reload_if_needed()
        return self.calibrator.calibrate(probabilities)


def create_calibrator(config: Dict[str, Any] = None) -> IsotonicCalibrator:
    """
    便捷函数：创建校准器
    
    Args:
        config: 配置参数
        
    Returns:
        校准器实例
    """
    return IsotonicCalibrator(config)
