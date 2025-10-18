#!/usr/bin/env python3
"""
代码和文档整理工具
"""

import os
from pathlib import Path
import shutil

def organize_files():
    """整理文件结构"""
    print("🗂️ 整理文件和代码")
    print("=" * 40)
    
    # 创建文档目录
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # 创建工具目录
    tools_dir = Path("tools")
    tools_dir.mkdir(exist_ok=True)
    
    # 移动文档文件
    doc_files = [
        "📋使用手册.md",
        "🎉最终优化完成报告.md", 
        "🎉5步优化完成报告.md",
        "🎉系统使用总结报告.md",
        "📋人工配置指南.md",
        "📋项目交付报告.md",
        "📋标注操作指南.md",
        "🎯您还需要做什么.md"
    ]
    
    print("📚 整理文档文件...")
    for doc_file in doc_files:
        if Path(doc_file).exists():
            try:
                shutil.move(doc_file, docs_dir / doc_file)
                print(f"  ✅ 移动: {doc_file} -> docs/")
            except Exception as e:
                print(f"  ⚠️ 跳过: {doc_file} ({e})")
    
    # 移动工具脚本
    tool_files = [
        "expand_data.py",
        "quick_train.py", 
        "train_improved_model.py",
        "batch_annotate.py",
        "auto_annotate.py",
        "annotation_tool.py",
        "test_trained_model.py",
        "calibrate_model.py",
        "validate_question_bank.py",
        "quick_validate.py",
        "diagnose_pdf.py",
        "analyze_pdf_problems.py",
        "system_audit.py",
        "simple_annotation.py",
        "test_step1.py",
        "test_improvements.py",
        "test_calibrator.py",
        "optimize_word.py",
        "test_word_effect.py",
        "evaluate_pdf.py",
        "organize_files.py"
    ]
    
    print("🔧 整理工具脚本...")
    for tool_file in tool_files:
        if Path(tool_file).exists():
            try:
                shutil.move(tool_file, tools_dir / tool_file)
                print(f"  ✅ 移动: {tool_file} -> tools/")
            except Exception as e:
                print(f"  ⚠️ 跳过: {tool_file} ({e})")
    
    # 清理临时文件
    temp_files = [
        "temp_output.txt",
        "annotation_batch.json",
        "auto_labeled.json"
    ]
    
    print("🧹 清理临时文件...")
    for temp_file in temp_files:
        if Path(temp_file).exists():
            try:
                Path(temp_file).unlink()
                print(f"  ✅ 删除: {temp_file}")
            except Exception as e:
                print(f"  ⚠️ 跳过: {temp_file} ({e})")
    
    print("\n📁 最终目录结构:")
    print_directory_structure()

def print_directory_structure():
    """打印目录结构"""
    structure = """
question-recog/
├── 📖 README.md                   # 项目说明
├── 🚀 production_test.py          # 主程序（推荐使用）
├── 🔧 train_model.py              # 模型训练
├── 📊 src/                        # 核心代码
│   ├── model/                     # 训练好的模型
│   ├── io/                        # 输入输出处理
│   ├── parsing/                   # 解析模块
│   ├── features/                  # 特征提取
│   ├── rules/                     # 规则引擎
│   └── calibrator/                # 概率校准
├── ⚙️ configs/                    # 配置文件
│   ├── app.yaml                   # 主配置
│   ├── features.yaml              # 特征配置
│   └── rules.yaml                 # 规则配置
├── 📊 data/                       # 数据目录
│   └── labels/                    # 标注数据
├── 📚 docs/                       # 文档目录
│   ├── 📋使用手册.md              # 使用说明
│   └── 其他文档...
├── 🔧 tools/                      # 工具脚本
│   ├── expand_data.py             # 数据扩展
│   ├── test_trained_model.py      # 模型测试
│   └── 其他工具...
└── 📋 production_results.json     # 识别结果
    """
    print(structure)

if __name__ == "__main__":
    organize_files()
    print("\n🎉 文件整理完成！")
