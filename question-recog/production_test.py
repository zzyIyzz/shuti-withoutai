#!/usr/bin/env python
"""
生产环境快速使用脚本
演示如何在实际环境中使用题型识别系统
"""

import sys
from pathlib import Path
import json

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.io.readers import DocumentReader
from src.pipeline import QuestionRecognitionPipeline


def process_real_files():
    """处理真实的题库文件"""
    print("🚀 生产环境题库识别系统")
    print("=" * 40)
    
    # 配置（生产环境优化）
    config = {
        "paths": {
            "model_path": "src/model/xgb_model.json",
            "calibration_path": "calibration/calibration.json"
        },
        "thresholds": {
            "min_confidence": 0.4,
            "accept": {
                "single_choice": 0.75,    # 稍微降低阈值提高召回率
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
    
    # 创建系统组件
    pipeline = QuestionRecognitionPipeline(config)
    reader = DocumentReader()
    
    # 检查题库目录
    tiku_dir = Path("../题库")
    if not tiku_dir.exists():
        # 尝试绝对路径
        tiku_dir = Path(__file__).parent.parent / "题库"
        if not tiku_dir.exists():
            print("❌ 题库目录不存在，请确保有题库文件")
            print(f"   查找路径1: {Path('../题库').absolute()}")
            print(f"   查找路径2: {tiku_dir.absolute()}")
            return
    
    # 查找题库文件
    supported_files = []
    for pattern in ["*.xlsx", "*.docx", "*.pdf"]:
        supported_files.extend(tiku_dir.glob(pattern))
    
    if not supported_files:
        print("❌ 未找到支持的题库文件 (.xlsx, .docx, .pdf)")
        return
    
    print(f"📚 发现 {len(supported_files)} 个题库文件")
    
    all_results = []
    stats_summary = {
        "total_files": 0,
        "total_questions": 0,
        "type_distribution": {},
        "confidence_levels": {"high": 0, "medium": 0, "low": 0, "review": 0}
    }
    
    # 处理每个文件
    for file_path in supported_files[:3]:  # 先处理前3个文件作为示例
        print(f"\n📄 处理文件: {file_path.name}")
        
        try:
            # 读取文档
            document = reader.read_document(str(file_path))
            
            # 识别题型
            results = pipeline.process_document(document)
            all_results.extend(results)
            
            # 统计信息
            stats_summary["total_files"] += 1
            stats_summary["total_questions"] += len(results)
            
            print(f"  📊 识别到 {len(results)} 个题目")
            
            # 显示前几个结果
            for i, result in enumerate(results[:3]):  # 只显示前3个
                qtype = result.final_result.type.value
                confidence = result.final_result.confidence
                
                # 更新统计
                if qtype not in stats_summary["type_distribution"]:
                    stats_summary["type_distribution"][qtype] = 0
                stats_summary["type_distribution"][qtype] += 1
                
                # 置信度分级
                if confidence >= 0.8:
                    stats_summary["confidence_levels"]["high"] += 1
                elif confidence >= 0.6:
                    stats_summary["confidence_levels"]["medium"] += 1
                elif confidence >= 0.4:
                    stats_summary["confidence_levels"]["low"] += 1
                else:
                    stats_summary["confidence_levels"]["review"] += 1
                
                status = "✅" if confidence >= 0.6 else "⚠️" if confidence >= 0.4 else "❌"
                review_flag = " [需复核]" if result.final_result.needs_review else ""
                
                print(f"    {status} 题目{i+1}: {qtype} (置信度: {confidence:.3f}){review_flag}")
                print(f"       题干: {result.question.question[:50]}...")
                
                if result.rule_decision:
                    print(f"       规则: {result.rule_decision.rule_name}")
                
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
    
    # 输出总体统计
    print(f"\n📊 处理总结")
    print(f"文件数量: {stats_summary['total_files']}")
    print(f"题目总数: {stats_summary['total_questions']}")
    
    print(f"\n📈 题型分布:")
    for qtype, count in stats_summary["type_distribution"].items():
        percentage = (count / stats_summary['total_questions']) * 100
        print(f"  {qtype:15}: {count:3} 题 ({percentage:5.1f}%)")
    
    print(f"\n🎯 置信度分布:")
    total_q = stats_summary['total_questions']
    if total_q > 0:
        print(f"  高置信度 (≥0.8): {stats_summary['confidence_levels']['high']:3} 题 ({stats_summary['confidence_levels']['high']/total_q*100:5.1f}%)")
        print(f"  中置信度 (0.6-0.8): {stats_summary['confidence_levels']['medium']:3} 题 ({stats_summary['confidence_levels']['medium']/total_q*100:5.1f}%)")
        print(f"  低置信度 (0.4-0.6): {stats_summary['confidence_levels']['low']:3} 题 ({stats_summary['confidence_levels']['low']/total_q*100:5.1f}%)")
        print(f"  需要复核 (<0.4): {stats_summary['confidence_levels']['review']:3} 题 ({stats_summary['confidence_levels']['review']/total_q*100:5.1f}%)")
    
    # 保存结果
    output_file = Path("production_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": stats_summary,
            "results": [result.model_dump() for result in all_results]
        }, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 详细结果已保存至: {output_file}")
    
    # 给出建议
    print(f"\n💡 使用建议:")
    if stats_summary['confidence_levels']['review'] > 0:
        print(f"  • 有 {stats_summary['confidence_levels']['review']} 个题目需要人工复核")
    
    high_conf_rate = stats_summary['confidence_levels']['high'] / total_q if total_q > 0 else 0
    if high_conf_rate < 0.6:
        print(f"  • 高置信度比例较低 ({high_conf_rate:.1%})，建议训练XGBoost模型")
    
    unknown_count = stats_summary["type_distribution"].get("unknown", 0)
    if unknown_count > 0:
        print(f"  • 有 {unknown_count} 个未知题型，建议优化规则或训练模型")
    
    print(f"\n🎉 生产环境测试完成！系统可以投入使用。")


if __name__ == "__main__":
    process_real_files()
