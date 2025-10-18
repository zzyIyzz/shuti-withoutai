#!/usr/bin/env python
"""
系统全面审核工具 - 识别需要人工配置的问题
"""

import sys
import json
from pathlib import Path

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.io.readers import DocumentReader
from src.pipeline import QuestionRecognitionPipeline
from src.rules.engine import RuleEngine
from src.features.extractor import FeatureExtractor


def comprehensive_system_audit():
    """全面系统审核"""
    print("🔍 题型识别系统全面审核")
    print("=" * 60)
    
    issues = []
    config_needed = []
    
    # 1. 检查配置文件
    print("📋 1. 配置文件检查")
    print("-" * 30)
    
    config_files = [
        "configs/app.yaml",
        "configs/features.yaml", 
        "configs/rules.yaml",
        "configs/logging.yaml"
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"  ✅ {config_file}")
        else:
            print(f"  ❌ {config_file} - 缺失")
            issues.append(f"配置文件缺失: {config_file}")
    
    # 2. 检查规则引擎覆盖率
    print(f"\n🔧 2. 规则引擎分析")
    print("-" * 30)
    
    engine = RuleEngine()
    rule_stats = engine.get_rule_stats()
    
    print(f"  规则总数: {rule_stats['total_rules']}")
    print(f"  启用规则: {rule_stats['enabled_rules']}")
    
    if rule_stats['enabled_rules'] < rule_stats['total_rules']:
        issues.append("部分规则被禁用，可能影响识别效果")
    
    # 检查规则优先级
    priorities = rule_stats['rule_priorities']
    print(f"  规则优先级:")
    for rule_name, priority in sorted(priorities.items(), key=lambda x: x[1]):
        print(f"    {priority}. {rule_name}")
    
    # 3. 检查特征工程
    print(f"\n🎯 3. 特征工程分析")
    print("-" * 30)
    
    extractor = FeatureExtractor()
    feature_names = extractor.get_feature_names()
    
    print(f"  特征总数: {len(feature_names)}")
    print(f"  特征类别:")
    
    feature_categories = {
        "基础特征": ["has_options", "num_options", "answer_is_single_letter", "answer_is_multi_letters"],
        "长度特征": ["question_len", "option_len_mean", "answer_len"],
        "标点特征": ["punct_density", "question_mark_count"],
        "关键词特征": ["hint_keywords_multi", "hint_keywords_tf", "hint_keywords_blank", "hint_keywords_subj"],
        "模式特征": ["blank_underline_count", "blank_parenthesis_count", "option_alignment_score"],
        "版面特征": ["layout_score", "ocr_conf_mean"],
        "答案特征": ["answer_pattern_id"]
    }
    
    for category, features in feature_categories.items():
        available = sum(1 for f in features if f in feature_names)
        print(f"    {category}: {available}/{len(features)}")
        if available < len(features):
            missing = [f for f in features if f not in feature_names]
            issues.append(f"{category}缺失特征: {missing}")
    
    # 4. 检查模型文件
    print(f"\n🤖 4. 模型文件检查")
    print("-" * 30)
    
    model_files = [
        "src/model/xgb_model.json",
        "src/model/feature_names.json",
        "src/model/training_info.json",
        "calibration/calibration.json",
        "calibration/version.meta"
    ]
    
    model_status = {"trained": False, "calibrated": False}
    
    for model_file in model_files:
        if Path(model_file).exists():
            print(f"  ✅ {model_file}")
            if "xgb_model" in model_file:
                model_status["trained"] = True
            elif "calibration.json" in model_file:
                model_status["calibrated"] = True
        else:
            print(f"  ❌ {model_file} - 缺失")
    
    if not model_status["trained"]:
        config_needed.append("需要训练XGBoost模型以提高未知题目识别率")
    
    if not model_status["calibrated"]:
        config_needed.append("需要进行概率校准以提高置信度准确性")
    
    # 5. 检查数据目录结构
    print(f"\n📁 5. 数据目录检查")
    print("-" * 30)
    
    data_dirs = [
        "data/raw",
        "data/interim", 
        "data/processed",
        "data/labels"
    ]
    
    for data_dir in data_dirs:
        if Path(data_dir).exists():
            file_count = len(list(Path(data_dir).glob("*")))
            print(f"  ✅ {data_dir} ({file_count} 文件)")
        else:
            print(f"  ❌ {data_dir} - 缺失")
            issues.append(f"数据目录缺失: {data_dir}")
    
    # 6. 题库质量问题分析
    print(f"\n📚 6. 题库质量问题")
    print("-" * 30)
    
    # 基于之前的验证结果
    quality_issues = [
        "PDF题库识别率过低 (83.1%未知)",
        "Word题库可能存在格式问题",
        "缺少标注数据用于模型训练",
        "规则引擎覆盖率不足"
    ]
    
    for issue in quality_issues:
        print(f"  ⚠️  {issue}")
        issues.append(issue)
    
    # 7. 生成配置建议
    print(f"\n💡 7. 需要人工配置的项目")
    print("-" * 30)
    
    manual_config_items = [
        {
            "项目": "规则引擎优化",
            "描述": "根据实际题库调整规则优先级和阈值",
            "配置文件": "configs/rules.yaml",
            "紧急程度": "高"
        },
        {
            "项目": "特征工程调优",
            "描述": "添加领域特定的关键词和模式",
            "配置文件": "configs/features.yaml", 
            "紧急程度": "中"
        },
        {
            "项目": "PDF解析优化",
            "描述": "调整PDF文本块合并策略",
            "配置文件": "configs/app.yaml",
            "紧急程度": "高"
        },
        {
            "项目": "置信度阈值调整",
            "描述": "根据实际使用调整各题型的接受/复核阈值",
            "配置文件": "configs/app.yaml",
            "紧急程度": "中"
        },
        {
            "项目": "数据标注",
            "描述": "标注100-200个样本用于模型训练",
            "配置文件": "data/labels/manual_labels.jsonl",
            "紧急程度": "高"
        }
    ]
    
    for item in manual_config_items:
        priority = "🔴" if item["紧急程度"] == "高" else "🟡" if item["紧急程度"] == "中" else "🟢"
        print(f"  {priority} {item['项目']}")
        print(f"     描述: {item['描述']}")
        print(f"     配置: {item['配置文件']}")
        print()
    
    # 8. 生成问题报告
    print(f"\n📋 8. 问题汇总")
    print("-" * 30)
    
    print(f"发现问题: {len(issues)} 个")
    print(f"需要配置: {len(manual_config_items)} 项")
    
    # 保存详细报告
    report = {
        "audit_timestamp": "2025-01-12T15:00:00",
        "issues_found": issues,
        "configuration_needed": manual_config_items,
        "model_status": model_status,
        "recommendations": [
            "优先处理PDF解析问题，这是当前最大的瓶颈",
            "标注50-100个样本进行模型训练",
            "调整规则引擎以提高覆盖率",
            "优化置信度阈值以减少误判"
        ]
    }
    
    with open("system_audit_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 详细报告已保存至: system_audit_report.json")
    
    # 9. 给出立即行动建议
    print(f"\n🚀 立即行动建议")
    print("-" * 30)
    
    immediate_actions = [
        "1. 运行 annotation_tool.py 标注50个样本",
        "2. 运行 train_model.py 训练XGBoost模型", 
        "3. 运行 calibrate_model.py 进行概率校准",
        "4. 调整 configs/rules.yaml 中的规则参数",
        "5. 优化PDF解析的文本块合并逻辑"
    ]
    
    for action in immediate_actions:
        print(f"  {action}")
    
    return report


if __name__ == "__main__":
    comprehensive_system_audit()
