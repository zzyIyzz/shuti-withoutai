#!/usr/bin/env python3
"""
清理冗余文件和文档
"""

import os
from pathlib import Path
import shutil

def clean_redundant_files():
    """清理冗余文件"""
    print("🧹 清理冗余文件和文档")
    print("=" * 40)
    
    # 要删除的冗余文件
    redundant_files = [
        # 测试和诊断脚本
        "diagnose_issue.py",
        "test_rules.py", 
        "fix_system.py",
        "test_fixed_system.py",
        "fix_model.py",
        "🔧问题诊断报告.md",
        
        # 旧版本文件
        "demo.py",
        "quick_calibrate.py",
        "test_calibrator.py",
        "🎯简单使用指南.md",
        
        # 结果文件
        "fixed_results.json",
        "production_results.json",
        
        # 重复的工具脚本
        "organize_files.py",
    ]
    
    # 删除文件
    deleted_count = 0
    for file_name in redundant_files:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"  ✅ 删除: {file_name}")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ 删除失败: {file_name} ({e})")
    
    print(f"\n📊 清理完成，删除了 {deleted_count} 个冗余文件")
    
    # 整理目录结构
    organize_directory_structure()
    
    return deleted_count

def organize_directory_structure():
    """整理目录结构"""
    print("\n📁 整理目录结构...")
    
    # 确保关键目录存在
    key_dirs = [
        "src/model",
        "calibration", 
        "data/labels",
        "docs",
        "tools"
    ]
    
    for dir_path in key_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # 移动文档到docs目录（如果还没移动）
    doc_files = [
        "🎓新手教程.md",
        "📋使用手册.md"
    ]
    
    docs_dir = Path("docs")
    for doc_file in doc_files:
        if Path(doc_file).exists():
            try:
                shutil.move(doc_file, docs_dir / doc_file)
                print(f"  ✅ 移动文档: {doc_file} -> docs/")
            except Exception as e:
                print(f"  ⚠️ 跳过: {doc_file} ({e})")
    
    print("  ✅ 目录结构整理完成")

def create_file_structure_summary():
    """创建文件结构总结"""
    structure = """
# 📁 项目文件结构

## 🎯 核心文件（必需）
```
question-recog/
├── 📋 README.md                    # 项目说明
├── 🚀 enhanced_system.py           # 主程序（推荐使用）
├── ⚙️ requirements.txt             # 依赖包
├── 📊 src/                         # 核心代码
│   ├── io/                         # 文档读取
│   ├── parsing/                    # 题目解析
│   ├── features/                   # 特征提取
│   ├── rules/                      # 规则引擎
│   ├── calibrator/                 # 概率校准
│   └── model/                      # 训练好的模型
├── ⚙️ configs/                     # 配置文件
├── 📊 data/labels/                 # 标注数据
├── 🔧 calibration/                 # 校准文件
└── 📚 docs/                        # 文档目录
```

## 🔧 工具文件（可选）
```
tools/
├── expand_data.py                  # 数据扩展
├── train_model.py                  # 模型训练
├── test_trained_model.py           # 模型测试
└── 其他工具...
```

## 📋 结果文件
```
enhanced_results.json              # 识别结果
```
"""
    
    with open("📁文件结构说明.md", 'w', encoding='utf-8') as f:
        f.write(structure)
    
    print("  ✅ 创建文件结构说明")

if __name__ == "__main__":
    deleted = clean_redundant_files()
    create_file_structure_summary()
    
    print(f"\n🎉 清理完成！")
    print(f"📊 删除了 {deleted} 个冗余文件")
    print(f"📁 目录结构已整理")
    print(f"📋 文件结构说明已创建")
