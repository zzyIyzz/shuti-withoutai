#!/usr/bin/env python
"""
简化版题库质量检查工具 - 自动检查所有题库
"""

import sys
import json
from pathlib import Path
import random

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.io.readers import DocumentReader
from src.pipeline import QuestionRecognitionPipeline


def quick_validate_all():
    """快速验证所有题库质量"""
    print("🔍 自动题库质量检查")
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
    
    print(f"📚 发现 {len(supported_files)} 个题库文件，开始自动检查...")
    
    all_reports = []
    
    # 检查每个题库
    for i, file_path in enumerate(supported_files):
        print(f"\n{'='*60}")
        print(f"📄 [{i+1}/{len(supported_files)}] 检查: {file_path.name}")
        print(f"{'='*60}")
        
        try:
            # 读取文档
            print("🔄 读取文档...")
            document = reader.read_document(str(file_path))
            
            # 识别题型
            print("🤖 识别题型...")
            results = pipeline.process_document(document)
            
            if not results:
                print("❌ 未识别到任何题目")
                continue
            
            # 分析结果
            print("📊 分析结果...")
            report = analyze_and_report(results, file_path.name)
            all_reports.append(report)
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            continue
    
    # 生成总体报告
    if all_reports:
        print(f"\n{'='*80}")
        print("📋 总体质量报告")
        print(f"{'='*80}")
        generate_summary_report(all_reports)


def analyze_and_report(results, filename):
    """分析并生成报告"""
    total_questions = len(results)
    
    # 统计数据
    stats = {
        "filename": filename,
        "total_questions": total_questions,
        "type_distribution": {},
        "confidence_levels": {"high": 0, "medium": 0, "low": 0, "very_low": 0},
        "rule_vs_model": {"rule": 0, "model": 0, "unknown": 0},
        "needs_review": 0,
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
    
    # 显示报告
    display_quick_report(stats)
    
    # 显示样本
    show_samples(results, filename)
    
    # 质量评分
    score = calculate_quality_score(stats)
    stats["quality_score"] = score
    
    return stats


def display_quick_report(stats):
    """显示快速报告"""
    total = stats["total_questions"]
    
    print(f"📊 基本统计:")
    print(f"  总题目数: {total}")
    
    # 题型分布（只显示前5个）
    print(f"🎯 主要题型:")
    sorted_types = sorted(stats["type_distribution"].items(), key=lambda x: x[1], reverse=True)
    for qtype, count in sorted_types[:5]:
        percentage = count / total * 100
        print(f"  {qtype:15}: {count:4} 题 ({percentage:5.1f}%)")
    
    # 置信度概览
    conf = stats["confidence_levels"]
    high_rate = conf["high"] / total * 100
    very_low_rate = conf["very_low"] / total * 100
    
    print(f"📈 置信度概览:")
    print(f"  高置信度 (≥0.8): {conf['high']:4} 题 ({high_rate:5.1f}%)")
    print(f"  极低置信度 (<0.4): {conf['very_low']:4} 题 ({very_low_rate:5.1f}%)")
    
    # 需要关注的问题
    issues = []
    if very_low_rate > 30:
        issues.append(f"⚠️  极低置信度题目过多 ({very_low_rate:.1f}%)")
    if stats["rule_vs_model"]["unknown"] / total > 0.2:
        issues.append(f"⚠️  未知题型过多 ({stats['rule_vs_model']['unknown']/total*100:.1f}%)")
    if stats["needs_review"] / total > 0.3:
        issues.append(f"⚠️  需复核题目过多 ({stats['needs_review']/total*100:.1f}%)")
    
    if issues:
        print(f"🚨 需要关注:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"✅ 未发现明显问题")


def show_samples(results, filename):
    """显示样本题目"""
    print(f"\n🔍 样本题目:")
    
    # 按题型分组
    by_type = {}
    for result in results:
        qtype = result.final_result.type.value
        if qtype not in by_type:
            by_type[qtype] = []
        by_type[qtype].append(result)
    
    # 显示每种题型的一个样本
    shown_count = 0
    for qtype, questions in list(by_type.items())[:3]:  # 只显示前3种题型
        if shown_count >= 3:  # 最多显示3个样本
            break
            
        sample = random.choice(questions)
        confidence = sample.final_result.confidence
        status = "✅" if confidence >= 0.7 else "⚠️" if confidence >= 0.5 else "❌"
        
        print(f"  {status} {qtype} (置信度: {confidence:.3f}):")
        print(f"     {sample.question.question[:60]}...")
        
        if sample.question.options:
            print(f"     选项数: {len(sample.question.options)}")
        
        if sample.question.answer_raw:
            print(f"     答案: {sample.question.answer_raw[:20]}...")
        
        shown_count += 1


def calculate_quality_score(stats):
    """计算质量评分"""
    total = stats["total_questions"]
    
    # 各项指标权重
    high_conf_rate = stats["confidence_levels"]["high"] / total
    unknown_rate = stats["type_distribution"].get("unknown", 0) / total
    review_rate = stats["needs_review"] / total
    
    # 评分逻辑
    score = 0
    
    # 高置信度比例 (40分)
    if high_conf_rate >= 0.8:
        score += 40
    elif high_conf_rate >= 0.6:
        score += 30
    elif high_conf_rate >= 0.4:
        score += 20
    else:
        score += 10
    
    # 未知题型比例 (30分)
    if unknown_rate <= 0.1:
        score += 30
    elif unknown_rate <= 0.2:
        score += 20
    elif unknown_rate <= 0.3:
        score += 10
    
    # 需复核比例 (30分)
    if review_rate <= 0.1:
        score += 30
    elif review_rate <= 0.2:
        score += 20
    elif review_rate <= 0.3:
        score += 10
    
    return score


def generate_summary_report(reports):
    """生成总体报告"""
    total_files = len(reports)
    total_questions = sum(r["total_questions"] for r in reports)
    
    print(f"📊 处理概览:")
    print(f"  题库文件数: {total_files}")
    print(f"  题目总数: {total_questions}")
    
    # 质量评分分布
    scores = [r["quality_score"] for r in reports]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    print(f"\n🎯 质量评分:")
    print(f"  平均分: {avg_score:.1f}/100")
    
    excellent = sum(1 for s in scores if s >= 80)
    good = sum(1 for s in scores if 60 <= s < 80)
    fair = sum(1 for s in scores if 40 <= s < 60)
    poor = sum(1 for s in scores if s < 40)
    
    print(f"  优秀 (≥80分): {excellent} 个")
    print(f"  良好 (60-79分): {good} 个")
    print(f"  一般 (40-59分): {fair} 个")
    print(f"  较差 (<40分): {poor} 个")
    
    # 推荐使用的题库
    print(f"\n📚 推荐题库:")
    good_files = [r for r in reports if r["quality_score"] >= 70]
    good_files.sort(key=lambda x: x["quality_score"], reverse=True)
    
    for i, report in enumerate(good_files[:3]):  # 显示前3个
        print(f"  {i+1}. {report['filename']} (评分: {report['quality_score']}/100)")
    
    if not good_files:
        print("  ⚠️  暂无高质量题库，建议优化后使用")
    
    # 总体建议
    print(f"\n💡 总体建议:")
    if avg_score >= 70:
        print("  ✅ 题库质量整体良好，可以投入使用")
    elif avg_score >= 50:
        print("  ⚠️  题库质量一般，建议选择性使用高分题库")
    else:
        print("  ❌ 题库质量偏低，建议进行优化")
        print("  📝 可考虑：")
        print("    - 标注部分数据训练XGBoost模型")
        print("    - 优化题目格式和规则引擎")
        print("    - 进行概率校准提高置信度")


if __name__ == "__main__":
    quick_validate_all()
