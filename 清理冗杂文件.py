#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理冗杂文件脚本
识别并清理不必要的临时文件、备份文件和重复文件
保留核心功能文件
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Set
import json

class ProjectCleaner:
    """项目清理器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.core_files = set()
        self.redundant_files = set()
        self.backup_files = set()
        self.temp_files = set()
        
        # 定义核心文件模式
        self.core_patterns = {
            # 主程序文件
            'GUI刷题程序.py',
            'main.py', 
            '题库管理.py',
            '双系统题型识别器.py',
            '高精度题型识别.py',
            '智能题型识别.py',
            '刷题引擎.py',
            '启动器.py',
            '用户设置.py',
            '统计分析.py',
            '错题记忆.py',
            
            # 配置和数据文件
            'requirements.txt',
            'README.md',
            '.gitignore',
            
            # 题库文件
            '*.xlsx',
            '*.pdf',
            '*.docx',
            
            # 批处理文件
            '*.bat'
        }
        
        # 定义冗杂文件模式
        self.redundant_patterns = {
            # 备份文件
            '*_backup.py',
            '*_old.py',
            '*backup*.py',
            
            # 临时文件
            '分析*.py',
            '测试*.py',
            '检查*.py',
            '快速*.py',
            '临时*.py',
            '集成*.py',
            
            # 重复功能文件
            'PDF题库*.py',
            'Word题库*.py',
            '*转换*.py',
            '*解析*.py',
            
            # 缓存文件
            '__pycache__',
            '*.pyc',
            '*.pyo',
            
            # 临时数据文件
            '*_temp.json',
            '*_test.json',
            'temp_*.json'
        }
    
    def analyze_project_structure(self) -> Dict[str, List[str]]:
        """分析项目结构"""
        print("🔍 分析项目结构...")
        
        analysis = {
            'core_files': [],
            'redundant_files': [],
            'backup_files': [],
            'temp_files': [],
            'question_recog_files': [],
            'documentation_files': []
        }
        
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.project_root)
                file_name = file_path.name
                
                # 分类文件
                if self._is_core_file(file_path):
                    analysis['core_files'].append(str(relative_path))
                elif 'backup' in file_name.lower() or file_name.endswith('_backup.py'):
                    analysis['backup_files'].append(str(relative_path))
                elif any(pattern in file_name for pattern in ['测试', '临时', '分析', '检查']):
                    analysis['temp_files'].append(str(relative_path))
                elif 'question-recog' in str(relative_path):
                    analysis['question_recog_files'].append(str(relative_path))
                elif file_name.endswith('.md'):
                    analysis['documentation_files'].append(str(relative_path))
                else:
                    # 进一步判断是否冗杂
                    if self._is_redundant_file(file_path):
                        analysis['redundant_files'].append(str(relative_path))
                    else:
                        analysis['core_files'].append(str(relative_path))
        
        return analysis
    
    def _is_core_file(self, file_path: Path) -> bool:
        """判断是否是核心文件"""
        file_name = file_path.name
        
        # 检查核心文件列表
        core_files = {
            'GUI刷题程序.py', 'main.py', '题库管理.py', '双系统题型识别器.py',
            '高精度题型识别.py', '智能题型识别.py', '刷题引擎.py', '启动器.py',
            '用户设置.py', '统计分析.py', '错题记忆.py', 'requirements.txt',
            'README.md', '.gitignore'
        }
        
        if file_name in core_files:
            return True
        
        # 检查扩展名
        if file_path.suffix in ['.xlsx', '.pdf', '.docx', '.bat']:
            return True
        
        # 检查question-recog核心文件
        if 'question-recog' in str(file_path):
            qr_core_files = {
                'main.py', '智能题目重构器.py', 'train_model.py',
                'requirements.txt', 'README.md'
            }
            if file_name in qr_core_files:
                return True
            
            # 保留src目录的核心模块
            if 'src' in str(file_path) and not any(x in str(file_path) for x in ['__pycache__', 'test']):
                return True
            
            # 保留configs目录
            if 'configs' in str(file_path):
                return True
            
            # 保留model目录
            if 'model' in str(file_path):
                return True
        
        return False
    
    def _is_redundant_file(self, file_path: Path) -> bool:
        """判断是否是冗杂文件"""
        file_name = file_path.name.lower()
        
        # 临时和测试文件
        temp_keywords = ['temp', '临时', '测试', '分析', '检查', '快速', 'test_', 'debug']
        if any(keyword in file_name for keyword in temp_keywords):
            return True
        
        # 备份文件
        if 'backup' in file_name or file_name.endswith('_old.py'):
            return True
        
        # 重复功能文件
        duplicate_keywords = ['pdf题库', 'word题库', '转换', '解析器']
        if any(keyword in file_name for keyword in duplicate_keywords):
            return True
        
        # 缓存文件
        if file_path.suffix in ['.pyc', '.pyo'] or file_name == '__pycache__':
            return True
        
        return False
    
    def create_cleanup_plan(self) -> Dict[str, List[str]]:
        """创建清理计划"""
        print("📋 创建清理计划...")
        
        analysis = self.analyze_project_structure()
        
        cleanup_plan = {
            'files_to_delete': [],
            'dirs_to_delete': [],
            'files_to_keep': analysis['core_files']
        }
        
        # 标记要删除的文件
        cleanup_plan['files_to_delete'].extend(analysis['backup_files'])
        cleanup_plan['files_to_delete'].extend(analysis['temp_files'])
        cleanup_plan['files_to_delete'].extend(analysis['redundant_files'])
        
        # 标记要删除的目录
        for dir_path in self.project_root.rglob('*'):
            if dir_path.is_dir():
                dir_name = dir_path.name
                relative_path = dir_path.relative_to(self.project_root)
                
                # 删除缓存目录
                if dir_name == '__pycache__':
                    cleanup_plan['dirs_to_delete'].append(str(relative_path))
                
                # 删除临时目录
                elif '临时' in dir_name or 'temp' in dir_name.lower():
                    cleanup_plan['dirs_to_delete'].append(str(relative_path))
        
        return cleanup_plan
    
    def preview_cleanup(self, cleanup_plan: Dict[str, List[str]]):
        """预览清理计划"""
        print("\n📊 清理计划预览")
        print("=" * 50)
        
        print(f"🗑️  将删除的文件 ({len(cleanup_plan['files_to_delete'])} 个):")
        for file_path in sorted(cleanup_plan['files_to_delete'])[:10]:  # 显示前10个
            print(f"  - {file_path}")
        if len(cleanup_plan['files_to_delete']) > 10:
            print(f"  ... 还有 {len(cleanup_plan['files_to_delete']) - 10} 个文件")
        
        print(f"\n📁 将删除的目录 ({len(cleanup_plan['dirs_to_delete'])} 个):")
        for dir_path in sorted(cleanup_plan['dirs_to_delete']):
            print(f"  - {dir_path}/")
        
        print(f"\n✅ 将保留的核心文件 ({len(cleanup_plan['files_to_keep'])} 个):")
        core_by_type = {}
        for file_path in cleanup_plan['files_to_keep']:
            ext = Path(file_path).suffix or 'no_ext'
            if ext not in core_by_type:
                core_by_type[ext] = []
            core_by_type[ext].append(file_path)
        
        for ext, files in sorted(core_by_type.items()):
            print(f"  {ext}: {len(files)} 个文件")
    
    def execute_cleanup(self, cleanup_plan: Dict[str, List[str]], dry_run: bool = True):
        """执行清理"""
        if dry_run:
            print("\n🔍 干运行模式 - 不会实际删除文件")
        else:
            print("\n🗑️  开始清理文件...")
        
        deleted_files = 0
        deleted_dirs = 0
        
        # 删除文件
        for file_path in cleanup_plan['files_to_delete']:
            full_path = self.project_root / file_path
            if full_path.exists():
                if not dry_run:
                    try:
                        full_path.unlink()
                        print(f"  ✅ 删除文件: {file_path}")
                    except Exception as e:
                        print(f"  ❌ 删除失败: {file_path} - {e}")
                else:
                    print(f"  🔍 将删除: {file_path}")
                deleted_files += 1
        
        # 删除目录
        for dir_path in cleanup_plan['dirs_to_delete']:
            full_path = self.project_root / dir_path
            if full_path.exists():
                if not dry_run:
                    try:
                        shutil.rmtree(full_path)
                        print(f"  ✅ 删除目录: {dir_path}/")
                    except Exception as e:
                        print(f"  ❌ 删除失败: {dir_path}/ - {e}")
                else:
                    print(f"  🔍 将删除: {dir_path}/")
                deleted_dirs += 1
        
        print(f"\n📊 清理统计:")
        print(f"  删除文件: {deleted_files} 个")
        print(f"  删除目录: {deleted_dirs} 个")
        print(f"  保留文件: {len(cleanup_plan['files_to_keep'])} 个")
        
        if dry_run:
            print(f"\n💡 要执行实际清理，请运行: python {__file__} --execute")
    
    def create_file_inventory(self):
        """创建文件清单"""
        print("📋 创建文件清单...")
        
        inventory = {
            'core_system': {
                'description': '核心刷题系统文件',
                'files': []
            },
            'recognition_system': {
                'description': '题型识别系统文件',
                'files': []
            },
            'data_files': {
                'description': '数据和配置文件',
                'files': []
            },
            'documentation': {
                'description': '文档文件',
                'files': []
            }
        }
        
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file() and self._is_core_file(file_path):
                relative_path = str(file_path.relative_to(self.project_root))
                
                if 'question-recog' in relative_path:
                    inventory['recognition_system']['files'].append(relative_path)
                elif file_path.suffix in ['.xlsx', '.pdf', '.docx', '.json', '.yaml']:
                    inventory['data_files']['files'].append(relative_path)
                elif file_path.suffix == '.md':
                    inventory['documentation']['files'].append(relative_path)
                else:
                    inventory['core_system']['files'].append(relative_path)
        
        # 保存清单
        with open(self.project_root / '文件清单.json', 'w', encoding='utf-8') as f:
            json.dump(inventory, f, ensure_ascii=False, indent=2)
        
        print("✅ 文件清单已保存: 文件清单.json")
        return inventory

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='清理项目冗杂文件')
    parser.add_argument('--execute', action='store_true', help='执行实际清理（默认为预览模式）')
    parser.add_argument('--project-root', default='.', help='项目根目录')
    
    args = parser.parse_args()
    
    print("🧹 项目文件清理工具")
    print("=" * 50)
    
    cleaner = ProjectCleaner(args.project_root)
    
    # 创建清理计划
    cleanup_plan = cleaner.create_cleanup_plan()
    
    # 预览清理计划
    cleaner.preview_cleanup(cleanup_plan)
    
    # 创建文件清单
    inventory = cleaner.create_file_inventory()
    
    # 执行清理
    if args.execute:
        confirm = input("\n⚠️  确认执行清理？这将永久删除文件！(y/N): ")
        if confirm.lower() == 'y':
            cleaner.execute_cleanup(cleanup_plan, dry_run=False)
        else:
            print("❌ 清理已取消")
    else:
        cleaner.execute_cleanup(cleanup_plan, dry_run=True)
    
    print(f"\n🎉 清理完成！")
    print(f"📋 详细文件清单请查看: 文件清单.json")

if __name__ == "__main__":
    main()
