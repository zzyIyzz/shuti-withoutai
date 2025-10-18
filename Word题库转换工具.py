#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Word题库转Excel工具
用于将Word格式的题库转换为Excel格式
"""

import sys
from pathlib import Path
from Word题库解析 import WordTikuParser

try:
    import openpyxl
except ImportError:
    print("错误：需要安装 openpyxl 库")
    print("运行: pip install openpyxl")
    sys.exit(1)

def word_to_excel(word_file, excel_file=None):
    """将Word题库转换为Excel格式"""
    word_path = Path(word_file)
    
    if not word_path.exists():
        print(f"错误：文件不存在 - {word_file}")
        return False
    
    # 解析Word文件
    print(f"正在解析Word文件: {word_path.name}")
    parser = WordTikuParser(word_path)
    questions = parser.parse()
    
    if not questions:
        print("错误：未能从Word文档中解析到题目")
        return False
    
    print(f"成功解析 {len(questions)} 道题目")
    
    # 创建Excel文件
    if excel_file is None:
        excel_file = word_path.with_suffix('.xlsx')
    else:
        excel_file = Path(excel_file)
    
    print(f"正在创建Excel文件: {excel_file.name}")
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "题库"
    
    # 写入表头
    headers = ['序号', '题目', 'A', 'B', 'C', 'D', '答案', '题型', '解析']
    ws.append(headers)
    
    # 写入题目
    for i, q in enumerate(questions, 1):
        row = [
            i,
            q.get('question', ''),
            q.get('options', {}).get('A', ''),
            q.get('options', {}).get('B', ''),
            q.get('options', {}).get('C', ''),
            q.get('options', {}).get('D', ''),
            q.get('answer', ''),
            q.get('type', ''),
            q.get('explanation', '')
        ]
        ws.append(row)
    
    # 调整列宽
    ws.column_dimensions['A'].width = 6
    ws.column_dimensions['B'].width = 50
    ws.column_dimensions['C'].width = 30
    ws.column_dimensions['D'].width = 30
    ws.column_dimensions['E'].width = 30
    ws.column_dimensions['F'].width = 30
    ws.column_dimensions['G'].width = 10
    ws.column_dimensions['H'].width = 10
    ws.column_dimensions['I'].width = 50
    
    # 保存
    wb.save(excel_file)
    print(f"✓ 转换完成！Excel文件已保存到: {excel_file}")
    print(f"  共 {len(questions)} 道题目")
    
    return True

def batch_convert():
    """批量转换当前目录下的所有Word文件"""
    current_dir = Path(__file__).parent
    word_files = list(current_dir.glob('*.docx'))
    word_files = [f for f in word_files if not f.name.startswith('~$')]
    
    if not word_files:
        print("当前目录没有Word文件（.docx）")
        return
    
    print(f"找到 {len(word_files)} 个Word文件")
    print("-" * 60)
    
    success_count = 0
    for word_file in word_files:
        print(f"\n处理: {word_file.name}")
        if word_to_excel(word_file):
            success_count += 1
        print("-" * 60)
    
    print(f"\n批量转换完成！")
    print(f"成功: {success_count}/{len(word_files)}")

def main():
    """主函数"""
    print("=" * 60)
    print("  Word题库转Excel工具")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        # 命令行模式
        word_file = sys.argv[1]
        excel_file = sys.argv[2] if len(sys.argv) > 2 else None
        word_to_excel(word_file, excel_file)
    else:
        # 交互模式
        print("1. 转换单个Word文件")
        print("2. 批量转换当前目录所有Word文件")
        print("0. 退出")
        print()
        
        choice = input("请选择: ").strip()
        
        if choice == '1':
            word_file = input("\n请输入Word文件名（含.docx后缀）: ").strip()
            excel_file = input("请输入Excel文件名（直接回车则自动命名）: ").strip()
            excel_file = excel_file if excel_file else None
            word_to_excel(word_file, excel_file)
        elif choice == '2':
            batch_convert()
        
        print()
        input("按回车键退出...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n发生错误: {e}")
        input("按回车键退出...")

