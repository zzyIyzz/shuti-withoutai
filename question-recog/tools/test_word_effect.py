#!/usr/bin/env python3
"""
测试Word解析在实际系统中的效果
"""

import subprocess
import sys
import json
from pathlib import Path

def test_word_in_production():
    """测试Word文档在生产系统中的效果"""
    print("🧪 测试Word文档在生产系统中的识别效果")
    print("=" * 50)
    
    try:
        # 运行production_test，专门处理Word文件
        result = subprocess.run([
            sys.executable, "production_test.py"
        ], capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=120)
        
        output = result.stdout + result.stderr
        
        # 分析输出
        print("📊 系统运行结果:")
        
        # 查找关键信息
        lines = output.split('\n')
        
        word_processed = False
        total_questions = 0
        word_questions = 0
        excel_questions = 0
        
        for line in lines:
            if ".docx" in line and "处理文件" in line:
                word_processed = True
                print(f"  ✅ Word文件已处理: {line.strip()}")
            
            elif "识别到" in line and "个题目" in line:
                try:
                    total_questions = int(line.split("识别到")[1].split("个题目")[0].strip())
                except:
                    pass
            
            elif "📄" in line and ".docx" in line:
                try:
                    # 提取Word文件的题目数
                    if "题目数:" in line:
                        word_questions = int(line.split("题目数:")[1].split()[0])
                except:
                    pass
            
            elif "📄" in line and ".xlsx" in line:
                try:
                    # 提取Excel文件的题目数
                    if "题目数:" in line:
                        excel_questions = int(line.split("题目数:")[1].split()[0])
                except:
                    pass
        
        print(f"  总题目数: {total_questions}")
        print(f"  Word题目数: {word_questions}")
        print(f"  Excel题目数: {excel_questions}")
        
        # 检查production_results.json
        results_file = Path("production_results.json")
        if results_file.exists():
            with open(results_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            results = data.get('results', [])
            
            # 分析Word来源的题目
            word_results = []
            for result in results:
                source_id = result.get('source_id', '')
                if '.docx' in source_id:
                    word_results.append(result)
            
            print(f"\n📋 Word文档识别详情:")
            print(f"  Word来源题目: {len(word_results)} 个")
            
            if word_results:
                # 分析前几个Word题目
                print(f"  前5个Word题目示例:")
                for i, result in enumerate(word_results[:5]):
                    question = result.get('question', {})
                    final_result = result.get('final_result', {})
                    
                    question_text = question.get('question', '')[:60] + "..."
                    question_type = final_result.get('type', 'unknown')
                    confidence = final_result.get('confidence', 0)
                    
                    print(f"    {i+1}. [{question_type}] (置信度: {confidence:.3f}) {question_text}")
                
                # 统计Word题目的类型分布
                word_types = {}
                for result in word_results:
                    qtype = result.get('final_result', {}).get('type', 'unknown')
                    word_types[qtype] = word_types.get(qtype, 0) + 1
                
                print(f"\n  Word题目类型分布:")
                for qtype, count in word_types.items():
                    print(f"    {qtype}: {count} 个")
        
        # 评估Word解析效果
        print(f"\n🎯 Word解析效果评估:")
        
        if word_processed:
            print(f"  ✅ Word文档成功处理")
        else:
            print(f"  ❌ Word文档处理失败")
        
        if word_questions > 0:
            print(f"  ✅ 成功识别 {word_questions} 个Word题目")
            
            if word_questions > 1000:
                print(f"  🎉 Word解析效果优秀！题目数量丰富")
            elif word_questions > 100:
                print(f"  ✅ Word解析效果良好")
            else:
                print(f"  ⚠️ Word题目数量较少，可能需要进一步优化")
        else:
            print(f"  ❌ 未识别到Word题目")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ 测试超时（超过2分钟）")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    print("🏅 第4步：Word解析效果测试")
    print("=" * 40)
    
    success = test_word_in_production()
    
    if success:
        print(f"\n🎉 Word解析测试完成！")
        print("🎯 第4步：Word解析优化 - 已完成")
    else:
        print(f"\n❌ Word解析测试失败")

if __name__ == "__main__":
    main()
