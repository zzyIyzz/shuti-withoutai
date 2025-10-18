#!/usr/bin/env python
"""
题库质量检查工具 - 在选择题库时进行题型识别验证
"""

import sys
import json
from pathlib import Path
import random

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.io.readers import DocumentReader
from src.pipeline import QuestionRecognitionPipeline


def validate_question_bank():
    """验证题库质量和题型识别准确性"""
    print("🔍 题库质量检查工具")
    print("=" * 50)
    
    # 配置系统
    config = {
        "thresholds": {
            "min_confidence": 0.4,
            "accept": {
                "single_choice": 0.75,
                "multiple_choice": 0.75,
                "true_false": 0.70,
                "fill_blank": 0.65,
                "subjective": 0.60,
            }
        }
    }
    
    pipeline = QuestionRecognitionPipeline(config)
    reader = DocumentReader()
    
    # 检查题库目录
    tiku_dir = Path("../题库")
    if not tiku_dir.exists():
        print("❌ 题库目录不存在")
        return
    
    # 查找所有题库文件
    supported_files = []
    for pattern in ["*.xlsx", "*.docx", "*.pdf"]:
        supported_files.extend(tiku_dir.glob(pattern))
    
    if not supported_files:
        print("❌ 未找到支持的题库文件")
        return
    
    print(f"📚 发现 {len(supported_files)} 个题库文件:")
    for i, file_path in enumerate(supported_files):
        print(f"  {i+1}. {file_path.name}")
    
    # 让用户选择要检查的题库
    while True:
        try:
            choice = input(f"\n请选择要检查的题库 (1-{len(supported_files)}, 或输入 'all' 检查全部): ").strip()
            
            if choice.lower() == 'all':
                selected_files = supported_files
                break
            else:
                idx = int(choice) - 1
                if 0 <= idx < len(supported_files):
                    selected_files = [supported_files[idx]]
                    break
                else:
                    print("❌ 无效选择，请重新输入")
        except ValueError:
            print("❌ 请输入有效数字")
    
    # 检查每个选中的题库
    for file_path in selected_files:
        print(f"\n{'='*60}")
        print(f"📄 检查题库: {file_path.name}")
        print(f"{'='*60}")
        
        try:
            # 读取文档
            document = reader.read_document(str(file_path))
            
            # 识别题型
            results = pipeline.process_document(document)
            
            if not results:
                print("❌ 未识别到任何题目")
                continue
            
            # 统计分析
            stats = analyze_results(results)
            
            # 显示统计信息
            display_statistics(stats, len(results))
            
            # 显示样本题目
            display_samples(results, file_path.name)
            
            # 质量评估
            quality_assessment(stats, len(results))
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")


def analyze_results(results):
    """分析识别结果"""
    stats = {
        "type_distribution": {},
        "confidence_levels": {"high": 0, "medium": 0, "low": 0, "very_low": 0},
        "rule_vs_model": {"rule": 0, "model": 0, "unknown": 0},
        "needs_review": 0,
        "confidence_by_type": {}
    }
    
    for result in results:
        qtype = result.final_result.type.value
        confidence = result.final_result.confidence
        
        # 题型分布
        if qtype not in stats["type_distribution"]:
            stats["type_distribution"][qtype] = 0
        stats["type_distribution"][qtype] += 1
        
        # 置信度分级
        if confidence >= 0.8:
            stats["confidence_levels"]["high"] += 1
        elif confidence >= 0.6:
            stats["confidence_levels"]["medium"] += 1
        elif confidence >= 0.4:
            stats["confidence_levels"]["low"] += 1
        else:
            stats["confidence_levels"]["very_low"] += 1
        
        # 规则vs模型
        if result.rule_decision:
            stats["rule_vs_model"]["rule"] += 1
        elif qtype == "unknown":
            stats["rule_vs_model"]["unknown"] += 1
        else:
            stats["rule_vs_model"]["model"] += 1
        
        # 需要复核
        if result.final_result.needs_review:
            stats["needs_review"] += 1
        
        # 按题型统计置信度
        if qtype not in stats["confidence_by_type"]:
            stats["confidence_by_type"][qtype] = []
        stats["confidence_by_type"][qtype].append(confidence)
    
    return stats


def display_statistics(stats, total_questions):
    """显示统计信息"""
    print(f"📊 识别统计 (总题目: {total_questions})")
    print("-" * 40)
    
    # 题型分布
    print("🎯 题型分布:")
    for qtype, count in sorted(stats["type_distribution"].items(), key=lambda x: x[1], reverse=True):
        percentage = count / total_questions * 100
        print(f"  {qtype:15}: {count:4} 题 ({percentage:5.1f}%)")
    
    # 置信度分布
    print(f"\n📈 置信度分布:")
    conf_levels = stats["confidence_levels"]
    print(f"  高置信度 (≥0.8): {conf_levels['high']:4} 题 ({conf_levels['high']/total_questions*100:5.1f}%)")
    print(f"  中置信度 (0.6-0.8): {conf_levels['medium']:4} 题 ({conf_levels['medium']/total_questions*100:5.1f}%)")
    print(f"  低置信度 (0.4-0.6): {conf_levels['low']:4} 题 ({conf_levels['low']/total_questions*100:5.1f}%)")
    print(f"  极低置信度 (<0.4): {conf_levels['very_low']:4} 题 ({conf_levels['very_low']/total_questions*100:5.1f}%)")
    
    # 识别方式
    print(f"\n🔧 识别方式:")
    rule_model = stats["rule_vs_model"]
    print(f"  规则识别: {rule_model['rule']:4} 题 ({rule_model['rule']/total_questions*100:5.1f}%)")
    print(f"  模型识别: {rule_model['model']:4} 题 ({rule_model['model']/total_questions*100:5.1f}%)")
    print(f"  未知题型: {rule_model['unknown']:4} 题 ({rule_model['unknown']/total_questions*100:5.1f}%)")
    
    # 需要复核
    print(f"\n⚠️  需要复核: {stats['needs_review']:4} 题 ({stats['needs_review']/total_questions*100:5.1f}%)")


def display_samples(results, filename):
    """显示样本题目"""
    print(f"\n🔍 样本题目检查:")
    print("-" * 40)
    
    # 按题型分组
    by_type = {}
    for result in results:
        qtype = result.final_result.type.value
        if qtype not in by_type:
            by_type[qtype] = []
        by_type[qtype].append(result)
    
    # 每种题型显示1-2个样本
    for qtype, questions in by_type.items():
        print(f"\n📝 {qtype} 样本:")
        
        # 选择样本：一个高置信度，一个低置信度
        samples = []
        high_conf = [q for q in questions if q.final_result.confidence >= 0.8]
        low_conf = [q for q in questions if q.final_result.confidence < 0.6]
        
        if high_conf:
            samples.append(random.choice(high_conf))
        if low_conf and len(samples) < 2:
            samples.append(random.choice(low_conf))
        if not samples and questions:
            samples.append(random.choice(questions))
        
        for i, sample in enumerate(samples[:2]):
            confidence = sample.final_result.confidence
            status = "✅" if confidence >= 0.7 else "⚠️" if confidence >= 0.5 else "❌"
            
            print(f"  {status} 样本 {i+1} (置信度: {confidence:.3f}):")
            print(f"     题干: {sample.question.question[:80]}...")
            
            if sample.question.options:
                print(f"     选项: {len(sample.question.options)} 个")
                for j, option in enumerate(sample.question.options[:2]):  # 只显示前2个选项
                    print(f"       {chr(65+j)}. {option[:40]}...")
            
            if sample.question.answer_raw:
                print(f"     答案: {sample.question.answer_raw[:30]}...")
            
            if sample.rule_decision:
                print(f"     规则: {sample.rule_decision.rule_name}")
            
            print()


def quality_assessment(stats, total_questions):
    """质量评估"""
    print(f"\n📋 质量评估报告:")
    print("-" * 40)
    
    # 计算质量指标
    high_conf_rate = stats["confidence_levels"]["high"] / total_questions
    unknown_rate = stats["type_distribution"].get("unknown", 0) / total_questions
    review_rate = stats["needs_review"] / total_questions
    rule_coverage = stats["rule_vs_model"]["rule"] / total_questions
    
    # 总体评分
    score = 0
    max_score = 100
    
    # 高置信度比例 (30分)
    if high_conf_rate >= 0.8:
        score += 30
        print("✅ 高置信度比例: 优秀 (≥80%)")
    elif high_conf_rate >= 0.6:
        score += 20
        print("⚠️  高置信度比例: 良好 (60-80%)")
    elif high_conf_rate >= 0.4:
        score += 10
        print("❌ 高置信度比例: 一般 (40-60%)")
    else:
        print("❌ 高置信度比例: 较差 (<40%)")
    
    # 未知题型比例 (25分)
    if unknown_rate <= 0.1:
        score += 25
        print("✅ 未知题型比例: 优秀 (≤10%)")
    elif unknown_rate <= 0.2:
        score += 15
        print("⚠️  未知题型比例: 良好 (10-20%)")
    elif unknown_rate <= 0.3:
        score += 5
        print("❌ 未知题型比例: 一般 (20-30%)")
    else:
        print("❌ 未知题型比例: 较差 (>30%)")
    
    # 需复核比例 (25分)
    if review_rate <= 0.1:
        score += 25
        print("✅ 需复核比例: 优秀 (≤10%)")
    elif review_rate <= 0.2:
        score += 15
        print("⚠️  需复核比例: 良好 (10-20%)")
    elif review_rate <= 0.3:
        score += 5
        print("❌ 需复核比例: 一般 (20-30%)")
    else:
        print("❌ 需复核比例: 较差 (>30%)")
    
    # 规则覆盖率 (20分)
    if rule_coverage >= 0.7:
        score += 20
        print("✅ 规则覆盖率: 优秀 (≥70%)")
    elif rule_coverage >= 0.5:
        score += 15
        print("⚠️  规则覆盖率: 良好 (50-70%)")
    elif rule_coverage >= 0.3:
        score += 10
        print("❌ 规则覆盖率: 一般 (30-50%)")
    else:
        print("❌ 规则覆盖率: 较差 (<30%)")
    
    # 总分和建议
    print(f"\n🎯 总体质量评分: {score}/{max_score} 分")
    
    if score >= 80:
        print("🎉 题库质量优秀，可以直接使用！")
    elif score >= 60:
        print("👍 题库质量良好，建议少量优化后使用")
    elif score >= 40:
        print("⚠️  题库质量一般，建议优化后使用")
    else:
        print("❌ 题库质量较差，强烈建议优化或重新整理")
    
    # 具体建议
    print(f"\n💡 改进建议:")
    if unknown_rate > 0.2:
        print("  • 未知题型过多，建议优化题目格式或增强规则")
    if review_rate > 0.2:
        print("  • 需复核题目过多，建议人工检查并优化")
    if high_conf_rate < 0.6:
        print("  • 高置信度比例偏低，建议训练XGBoost模型")
    if rule_coverage < 0.5:
        print("  • 规则覆盖率偏低，建议优化规则引擎")


if __name__ == "__main__":
    validate_question_bank()
