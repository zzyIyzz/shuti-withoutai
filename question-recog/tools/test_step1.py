#!/usr/bin/env python3
"""
简单测试系统运行状态
"""

import subprocess
import sys

def test_system():
    """测试系统是否正常运行"""
    print("Step 1: 测试校准器警告是否消除...")
    
    try:
        # 运行production_test.py并捕获输出
        result = subprocess.run([
            sys.executable, "production_test.py"
        ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        output = result.stdout + result.stderr
        
        # 检查是否还有校准器警告
        calibrator_warnings = output.count("校准器未加载")
        print(f"校准器警告数量: {calibrator_warnings}")
        
        # 检查是否有题目处理
        if "题目" in output:
            print("✅ 系统正常处理题目")
        else:
            print("❌ 系统未能处理题目")
        
        # 检查是否有总结信息
        if "处理总结" in output or "完成" in output:
            print("✅ 系统正常完成处理")
        else:
            print("❌ 系统未正常完成")
            
        if calibrator_warnings == 0:
            print("✅ 第1步完成：校准器警告已消除")
            return True
        else:
            print("❌ 第1步未完成：仍有校准器警告")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_system()
