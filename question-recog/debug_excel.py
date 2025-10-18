#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试Excel文件解析
"""

import pandas as pd
import sys
from pathlib import Path

def debug_excel():
    """调试Excel文件内容"""
    excel_path = Path("../题库/1.电力安全工作规程（发电厂和变电站电气部分）安徽分公司题库（GB 26860—2011).xlsx")
    
    if not excel_path.exists():
        print(f"❌ Excel文件不存在: {excel_path}")
        return
    
    try:
        # 读取Excel文件
        df = pd.read_excel(excel_path)
        
        print("📊 Excel文件基本信息:")
        print(f"  形状: {df.shape}")
        print(f"  列名: {df.columns.tolist()}")
        
        print("\n📈 题型分布:")
        if '题型' in df.columns:
            print(df['题型'].value_counts())
        else:
            print("  ❌ 没有找到'题型'列")
        
        print("\n📝 前5题详细信息:")
        for i in range(min(5, len(df))):
            print(f"\n第{i+1}题:")
            print(f"  题目: {df.iloc[i]['题目']}")
            
            # 检查选项
            options = []
            for opt in ['A', 'B', 'C', 'D']:
                if opt in df.columns and pd.notna(df.iloc[i][opt]):
                    options.append(f"{opt}: {df.iloc[i][opt]}")
            
            if options:
                print(f"  选项: {'; '.join(options)}")
            else:
                print("  选项: 无")
            
            print(f"  答案: {df.iloc[i]['答案']}")
            print(f"  题型: {df.iloc[i]['题型']}")
        
        # 检查有选项的题目
        print("\n🔍 选项分析:")
        has_options_count = 0
        no_options_count = 0
        
        for i in range(len(df)):
            has_any_option = False
            for opt in ['A', 'B', 'C', 'D']:
                if opt in df.columns and pd.notna(df.iloc[i][opt]) and str(df.iloc[i][opt]).strip():
                    has_any_option = True
                    break
            
            if has_any_option:
                has_options_count += 1
            else:
                no_options_count += 1
        
        print(f"  有选项的题目: {has_options_count}")
        print(f"  无选项的题目: {no_options_count}")
        
        # 找几个有选项的题目示例
        print("\n📋 有选项的题目示例:")
        count = 0
        for i in range(len(df)):
            if count >= 3:
                break
                
            has_any_option = False
            options = []
            for opt in ['A', 'B', 'C', 'D']:
                if opt in df.columns and pd.notna(df.iloc[i][opt]) and str(df.iloc[i][opt]).strip():
                    has_any_option = True
                    options.append(f"{opt}: {df.iloc[i][opt]}")
            
            if has_any_option:
                count += 1
                print(f"\n示例{count} (第{i+1}题):")
                print(f"  题目: {df.iloc[i]['题目']}")
                print(f"  选项: {'; '.join(options)}")
                print(f"  答案: {df.iloc[i]['答案']}")
                print(f"  题型: {df.iloc[i]['题型']}")
        
    except Exception as e:
        print(f"❌ 读取Excel文件失败: {e}")

if __name__ == "__main__":
    debug_excel()
