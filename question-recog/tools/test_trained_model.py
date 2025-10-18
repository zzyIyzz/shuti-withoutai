#!/usr/bin/env python
"""
测试训练后的模型效果
"""

import sys
import json
from pathlib import Path
import numpy as np
import xgboost as xgb

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.pipeline import QuestionRecognitionPipeline
from src.io.readers import DocumentReader


def test_trained_model():
    """测试训练后的模型"""
    print("🧪 测试训练后的模型效果")
    print("=" * 40)
    
    # 检查模型文件
    model_path = Path("src/model/xgb_model.json")
    if not model_path.exists():
        print("❌ 模型文件不存在，请先运行 train_model.py")
        return
    
    # 检查训练信息
    info_path = Path("src/model/training_info.json")
    if info_path.exists():
        with open(info_path, 'r', encoding='utf-8') as f:
            training_info = json.load(f)
        
        print(f"📊 模型信息:")
        print(f"  训练样本: {training_info['training_samples']}")
        print(f"  测试样本: {training_info['test_samples']}")
        print(f"  F1分数 (宏平均): {training_info['f1_macro']:.4f}")
        print(f"  F1分数 (加权): {training_info['f1_weighted']:.4f}")
        print(f"  支持类别: {', '.join(training_info['classes'])}")
    
    # 配置流水线（指定模型路径）
    config = {
        "paths": {
            "model_path": str(model_path),
            "calibration_path": "calibration/calibration.json"
        },
        "thresholds": {
            "min_confidence": 0.4,
            "accept": {
                "single_choice": 0.75,
                "multiple_choice": 0.75,
                "true_false": 0.70,
                "fill_blank": 0.65,
                "subjective": 0.60,
            },
            "review": {
                "single_choice": 0.50,
                "multiple_choice": 0.50,
                "true_false": 0.45,
                "fill_blank": 0.40,
                "subjective": 0.35,
            }
        }
    }
    
    # 创建带模型的流水线
    pipeline = QuestionRecognitionPipeline(config)
    reader = DocumentReader()
    
    # 测试一些题目
    print(f"\n🔍 测试模型效果...")
    
    # 检查题库目录
    tiku_dir = Path("../题库")
    if not tiku_dir.exists():
        print("❌ 题库目录不存在")
        return
    
    # 查找一个题库文件进行测试
    test_files = list(tiku_dir.glob("*.xlsx"))[:1]  # 只测试一个文件
    
    if not test_files:
        print("❌ 未找到测试文件")
        return
    
    test_file = test_files[0]
    print(f"📄 测试文件: {test_file.name}")
    
    try:
        # 读取并处理文档
        document = reader.read_document(str(test_file))
        results = pipeline.process_document(document)
        
        # 统计结果
        stats = {
            "total": len(results),
            "rule_hits": 0,
            "model_predictions": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "needs_review": 0,
            "type_distribution": {}
        }
        
        print(f"\n📊 测试结果:")
        print(f"总题目数: {stats['total']}")
        
        # 分析每个结果
        for result in results[:20]:  # 只显示前20个结果
            qtype = result.final_result.type.value
            confidence = result.final_result.confidence
            
            # 更新统计
            if result.rule_decision:
                stats["rule_hits"] += 1
            else:
                stats["model_predictions"] += 1
            
            if confidence >= 0.8:
                stats["high_confidence"] += 1
            elif confidence >= 0.6:
                stats["medium_confidence"] += 1
            elif confidence >= 0.4:
                stats["low_confidence"] += 1
            
            if result.final_result.needs_review:
                stats["needs_review"] += 1
            
            if qtype not in stats["type_distribution"]:
                stats["type_distribution"][qtype] = 0
            stats["type_distribution"][qtype] += 1
            
            # 显示结果
            status = "✅" if confidence >= 0.7 else "⚠️" if confidence >= 0.5 else "❌"
            source = "规则" if result.rule_decision else "模型"
            review_flag = " [需复核]" if result.final_result.needs_review else ""
            
            print(f"  {status} {qtype:15} (置信度: {confidence:.3f}) [{source}]{review_flag}")
            print(f"     题干: {result.question.question[:60]}...")
        
        # 显示总体统计
        print(f"\n📈 统计摘要:")
        print(f"规则命中: {stats['rule_hits']:3} ({stats['rule_hits']/stats['total']*100:5.1f}%)")
        print(f"模型预测: {stats['model_predictions']:3} ({stats['model_predictions']/stats['total']*100:5.1f}%)")
        print(f"高置信度: {stats['high_confidence']:3} ({stats['high_confidence']/stats['total']*100:5.1f}%)")
        print(f"中置信度: {stats['medium_confidence']:3} ({stats['medium_confidence']/stats['total']*100:5.1f}%)")
        print(f"低置信度: {stats['low_confidence']:3} ({stats['low_confidence']/stats['total']*100:5.1f}%)")
        print(f"需要复核: {stats['needs_review']:3} ({stats['needs_review']/stats['total']*100:5.1f}%)")
        
        print(f"\n🎯 题型分布:")
        for qtype, count in stats["type_distribution"].items():
            percentage = count / stats['total'] * 100
            print(f"  {qtype:15}: {count:3} 题 ({percentage:5.1f}%)")
        
        # 性能对比
        print(f"\n📊 模型效果评估:")
        model_accuracy = (stats['high_confidence'] + stats['medium_confidence']) / stats['total']
        print(f"整体准确率: {model_accuracy:.1%}")
        
        if stats['model_predictions'] > 0:
            model_contribution = stats['model_predictions'] / stats['total']
            print(f"模型贡献度: {model_contribution:.1%}")
        
        if stats['needs_review'] / stats['total'] < 0.2:
            print("✅ 需复核比例较低，模型效果良好")
        else:
            print("⚠️ 需复核比例较高，建议增加训练数据")
        
        print(f"\n🎉 模型测试完成！")
        
        # 给出下一步建议
        print(f"\n💡 下一步建议:")
        if model_accuracy < 0.7:
            print("  • 模型准确率较低，建议增加更多标注数据重新训练")
        if stats['needs_review'] / stats['total'] > 0.3:
            print("  • 需复核比例过高，建议优化规则或增加训练数据")
        if stats['model_predictions'] / stats['total'] < 0.3:
            print("  • 模型使用率较低，大部分由规则处理，可以考虑优化规则覆盖")
        
        print("  • 运行 calibrate_model.py 进行概率校准")
        print("  • 运行 evaluate_model.py 进行全面评估")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    test_trained_model()
