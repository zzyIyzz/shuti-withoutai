#!/usr/bin/env python
"""
数据标注工具 - 帮助快速标注题目类型
"""

import sys
import json
from pathlib import Path
import random

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))


def create_annotation_tool():
    """创建标注工具"""
    print("📝 题型标注工具")
    print("=" * 40)
    
    # 读取生产环境结果
    results_file = Path("production_results.json")
    if not results_file.exists():
        print("❌ 请先运行 production_test.py 生成结果文件")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data["results"]
    print(f"📚 加载了 {len(results)} 个题目")
    
    # 筛选需要标注的题目
    need_annotation = []
    
    # 1. 未知题型
    unknown_items = [r for r in results if r["final_result"]["type"] == "unknown"]
    need_annotation.extend(unknown_items[:50])  # 最多50个未知题型
    
    # 2. 低置信度题目
    low_conf_items = [r for r in results 
                      if r["final_result"]["confidence"] < 0.6 
                      and r["final_result"]["type"] != "unknown"]
    need_annotation.extend(low_conf_items[:30])  # 最多30个低置信度
    
    # 3. 随机抽样高置信度题目（用于验证）
    high_conf_items = [r for r in results if r["final_result"]["confidence"] >= 0.8]
    if high_conf_items:
        random.shuffle(high_conf_items)
        need_annotation.extend(high_conf_items[:20])  # 20个高置信度验证
    
    print(f"🎯 需要标注 {len(need_annotation)} 个题目")
    
    # 题型选项
    type_options = {
        "1": "single_choice",
        "2": "multiple_choice", 
        "3": "true_false",
        "4": "fill_blank",
        "5": "subjective"
    }
    
    annotations = []
    
    print(f"\n📋 标注说明:")
    print(f"1 - 单选题 (有选项，答案为单字母)")
    print(f"2 - 多选题 (有选项，答案为多字母)")
    print(f"3 - 判断题 (答案为对/错/√/×)")
    print(f"4 - 填空题 (题目有空白，答案为文字/数字)")
    print(f"5 - 简答题 (需要文字叙述回答)")
    print(f"s - 跳过当前题目")
    print(f"q - 退出标注")
    print(f"\n开始标注 (按Enter继续)...")
    input()
    
    for i, item in enumerate(need_annotation):
        print(f"\n{'='*60}")
        print(f"题目 {i+1}/{len(need_annotation)}")
        print(f"{'='*60}")
        
        # 显示题目信息
        question = item["question"]["question"]
        options = item["question"]["options"]
        answer = item["question"]["answer_raw"]
        
        print(f"📝 题目: {question}")
        
        if options:
            print(f"📋 选项:")
            for j, option in enumerate(options):
                print(f"   {chr(65+j)}. {option}")
        
        print(f"💡 答案: {answer}")
        
        # 显示系统预测
        predicted_type = item["final_result"]["type"]
        confidence = item["final_result"]["confidence"]
        print(f"🤖 系统预测: {predicted_type} (置信度: {confidence:.3f})")
        
        # 获取用户标注
        while True:
            user_input = input(f"\n请选择正确的题型 (1-5, s=跳过, q=退出): ").strip().lower()
            
            if user_input == 'q':
                print("标注已退出")
                break
            elif user_input == 's':
                print("跳过当前题目")
                break
            elif user_input in type_options:
                correct_type = type_options[user_input]
                
                # 保存标注
                annotation = {
                    "source_id": item["source_id"],
                    "gold_type": correct_type,
                    "predicted_type": predicted_type,
                    "confidence": confidence,
                    "question_preview": question[:100] + "..." if len(question) > 100 else question
                }
                annotations.append(annotation)
                
                print(f"✅ 已标注为: {correct_type}")
                break
            else:
                print("❌ 无效输入，请重新选择")
        
        if user_input == 'q':
            break
    
    # 保存标注结果
    if annotations:
        labels_dir = Path("data/labels")
        labels_dir.mkdir(parents=True, exist_ok=True)
        
        labels_file = labels_dir / "manual_labels.jsonl"
        with open(labels_file, 'w', encoding='utf-8') as f:
            for ann in annotations:
                f.write(json.dumps(ann, ensure_ascii=False) + '\n')
        
        print(f"\n💾 标注结果已保存至: {labels_file}")
        print(f"📊 标注统计:")
        
        type_counts = {}
        for ann in annotations:
            gt = ann["gold_type"]
            if gt not in type_counts:
                type_counts[gt] = 0
            type_counts[gt] += 1
        
        for qtype, count in type_counts.items():
            print(f"  {qtype:15}: {count:3} 题")
        
        print(f"\n🎯 下一步: 运行训练脚本")
        print(f"python train_model.py")
    else:
        print("❌ 没有标注数据")


if __name__ == "__main__":
    create_annotation_tool()
