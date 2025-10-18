#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安规刷题系统启动脚本
"""

import sys
import os
from pathlib import Path

def 启动程序():
    """启动安规刷题系统"""
    print("=" * 60)
    print("安规刷题系统 v2.1 - 启动中...")
    print("=" * 60)
    
    try:
        # 检查当前目录
        当前目录 = Path.cwd()
        print(f"当前目录: {当前目录}")
        
        # 检查必要文件
        必要文件 = [
            "GUI刷题程序.py",
            "题库标准化导入.py",
            "题库管理.py",
            "智能题型识别.py"
        ]
        
        for 文件 in 必要文件:
            if Path(文件).exists():
                print(f"✅ {文件}")
            else:
                print(f"❌ {文件} - 文件不存在")
                return False
        
        print("\n正在启动GUI程序...")
        
        # 导入并启动GUI
        from GUI刷题程序 import 刷题应用
        
        print("✅ GUI模块导入成功")
        print("✅ 正在创建应用实例...")
        
        app = 刷题应用()
        print("✅ 应用实例创建成功")
        print("✅ 程序启动完成！")
        print("\n🎉 安规刷题系统 v2.1 已启动！")
        print("📝 新功能：题库强制标准化导入")
        print("📝 使用方法：文件 → 导入题库")
        
        # 启动主循环
        app.mainloop()
        
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    成功 = 启动程序()
    if not 成功:
        input("\n按回车键退出...")
