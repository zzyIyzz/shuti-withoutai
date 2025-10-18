#!/usr/bin/env python3
"""
测试校准器是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 现在可以直接导入
from pipeline import QuestionRecognitionPipeline

def test_calibrator():
    """测试校准器"""
    print("测试校准器加载...")
    
    config = {
        "paths": {
            "model_path": "src/model/xgb_model.json",
            "calibration_path": "calibration/calibration.json"
        }
    }
    
    pipeline = QuestionRecognitionPipeline(config)
    
    # 测试校准器是否加载
    test_probs = {"true_false": 0.7, "fill_blank": 0.2, "subjective": 0.1}
    calibrated = pipeline._calibrate_probabilities(test_probs)
    
    print(f"原始概率: {test_probs}")
    print(f"校准概率: {calibrated}")
    print("校准器测试完成!")

if __name__ == "__main__":
    test_calibrator()
