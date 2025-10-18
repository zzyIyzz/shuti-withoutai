#!/usr/bin/env python3
"""
测试系统改进效果
"""
import subprocess
import sys

def test_system_improvements():
    """测试系统改进效果"""
    print("🧪 测试系统改进效果")
    print("=" * 40)
    
    try:
        # 运行production_test.py并捕获输出
        result = subprocess.run([
            sys.executable, "production_test.py"
        ], capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=60)
        
        output = result.stdout + result.stderr
        
        # 分析输出
        lines = output.split('\n')
        
        # 查找关键信息
        calibrator_warnings = output.count("校准器未加载")
        total_questions = 0
        high_confidence = 0
        medium_confidence = 0
        low_confidence = 0
        
        for line in lines:
            if "识别到" in line and "个题目" in line:
                try:
                    total_questions = int(line.split("识别到")[1].split("个题目")[0].strip())
                except:
                    pass
            elif "高置信度" in line:
                try:
                    high_confidence = int(line.split(":")[1].split("题")[0].strip())
                except:
                    pass
            elif "中置信度" in line:
                try:
                    medium_confidence = int(line.split(":")[1].split("题")[0].strip())
                except:
                    pass
            elif "低置信度" in line:
                try:
                    low_confidence = int(line.split(":")[1].split("题")[0].strip())
                except:
                    pass
        
        print("📊 系统改进效果分析：")
        print(f"  校准器警告数量: {calibrator_warnings}")
        print(f"  处理题目总数: {total_questions}")
        print(f"  高置信度题目: {high_confidence}")
        print(f"  中置信度题目: {medium_confidence}")
        print(f"  低置信度题目: {low_confidence}")
        
        # 评估改进效果
        improvements = []
        
        if calibrator_warnings == 0:
            improvements.append("✅ 校准器警告已消除")
        
        if total_questions > 2000:
            improvements.append("✅ 系统能处理大量题目")
        
        if result.returncode == 0:
            improvements.append("✅ 系统运行稳定")
        
        print("\n🎯 改进成果：")
        for improvement in improvements:
            print(f"  {improvement}")
        
        # 下一步建议
        print("\n💡 下一步建议：")
        if total_questions > 0:
            print("  • 系统基本功能正常，可以继续优化Word解析")
            print("  • 考虑添加更多电力专业词汇")
        else:
            print("  • 需要检查系统配置")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ 测试超时")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_system_improvements()
