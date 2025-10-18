#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库转换管理器
统一管理PDF、Word、Excel格式之间的转换
集成到主刷题系统中
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

class TikuConverterManager:
    """题库转换管理器"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.tiku_dir = self.base_dir / '题库'
        self.output_dir = self.base_dir / '题库' / '转换输出'
        self.output_dir.mkdir(exist_ok=True)
        
        # 支持的格式
        self.supported_formats = {
            'pdf': ['.pdf'],
            'word': ['.docx', '.doc'],
            'excel': ['.xlsx', '.xls']
        }
    
    def get_convertible_files(self) -> List[Dict[str, Any]]:
        """获取可转换的文件列表"""
        files = []
        
        if not self.tiku_dir.exists():
            return files
        
        for file_path in self.tiku_dir.rglob('*'):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                
                # 跳过临时文件和输出文件
                if file_path.name.startswith('~$') or '转换输出' in str(file_path):
                    continue
                
                file_info = {
                    'name': file_path.name,
                    'path': str(file_path),
                    'size': file_path.stat().st_size,
                    'format': self._get_format_type(suffix),
                    'suffix': suffix
                }
                files.append(file_info)
        
        return files
    
    def _get_format_type(self, suffix: str) -> str:
        """获取文件格式类型"""
        for format_type, extensions in self.supported_formats.items():
            if suffix in extensions:
                return format_type
        return 'unknown'
    
    def convert_pdf_to_excel(self, pdf_path: str, output_path: Optional[str] = None) -> bool:
        """PDF转Excel"""
        try:
            from PDF题库转换工具 import pdf_to_excel
            
            if not output_path:
                pdf_file = Path(pdf_path)
                output_path = self.output_dir / f"{pdf_file.stem}_转换.xlsx"
            
            print(f"🔄 开始转换: {Path(pdf_path).name} -> {Path(output_path).name}")
            result = pdf_to_excel(pdf_path, str(output_path))
            
            if result:
                print(f"✅ 转换成功: {output_path}")
                return True
            else:
                print(f"❌ 转换失败: {pdf_path}")
                return False
                
        except Exception as e:
            print(f"❌ PDF转换异常: {e}")
            return False
    
    def convert_word_to_excel(self, word_path: str, output_path: Optional[str] = None) -> bool:
        """Word转Excel"""
        try:
            from Word题库转换工具 import word_to_excel
            
            if not output_path:
                word_file = Path(word_path)
                output_path = self.output_dir / f"{word_file.stem}_转换.xlsx"
            
            print(f"🔄 开始转换: {Path(word_path).name} -> {Path(output_path).name}")
            result = word_to_excel(word_path, str(output_path))
            
            if result:
                print(f"✅ 转换成功: {output_path}")
                return True
            else:
                print(f"❌ 转换失败: {word_path}")
                return False
                
        except Exception as e:
            print(f"❌ Word转换异常: {e}")
            return False
    
    def batch_convert(self, target_format: str = 'excel') -> Dict[str, Any]:
        """批量转换"""
        print(f"🚀 开始批量转换为 {target_format} 格式")
        
        files = self.get_convertible_files()
        results = {
            'total': len(files),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
        
        for file_info in files:
            file_path = file_info['path']
            file_format = file_info['format']
            
            print(f"\n📄 处理文件: {file_info['name']}")
            
            if file_format == target_format:
                print("⏭️ 跳过：已经是目标格式")
                results['skipped'] += 1
                results['details'].append({
                    'file': file_info['name'],
                    'status': 'skipped',
                    'reason': '已经是目标格式'
                })
                continue
            
            success = False
            if file_format == 'pdf' and target_format == 'excel':
                success = self.convert_pdf_to_excel(file_path)
            elif file_format == 'word' and target_format == 'excel':
                success = self.convert_word_to_excel(file_path)
            else:
                print(f"⚠️ 不支持的转换: {file_format} -> {target_format}")
                results['skipped'] += 1
                results['details'].append({
                    'file': file_info['name'],
                    'status': 'skipped',
                    'reason': f'不支持的转换: {file_format} -> {target_format}'
                })
                continue
            
            if success:
                results['success'] += 1
                results['details'].append({
                    'file': file_info['name'],
                    'status': 'success'
                })
            else:
                results['failed'] += 1
                results['details'].append({
                    'file': file_info['name'],
                    'status': 'failed'
                })
        
        # 显示结果统计
        print(f"\n📊 批量转换完成:")
        print(f"  总文件数: {results['total']}")
        print(f"  转换成功: {results['success']}")
        print(f"  转换失败: {results['failed']}")
        print(f"  跳过文件: {results['skipped']}")
        
        return results
    
    def get_conversion_status(self) -> Dict[str, Any]:
        """获取转换状态"""
        files = self.get_convertible_files()
        
        status = {
            'total_files': len(files),
            'formats': {},
            'convertible': 0,
            'already_excel': 0
        }
        
        for file_info in files:
            format_type = file_info['format']
            if format_type not in status['formats']:
                status['formats'][format_type] = 0
            status['formats'][format_type] += 1
            
            if format_type in ['pdf', 'word']:
                status['convertible'] += 1
            elif format_type == 'excel':
                status['already_excel'] += 1
        
        return status

def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='题库转换管理器')
    parser.add_argument('--list', action='store_true', help='列出可转换的文件')
    parser.add_argument('--convert', choices=['pdf', 'word'], help='转换指定格式的文件')
    parser.add_argument('--batch', action='store_true', help='批量转换为Excel格式')
    parser.add_argument('--status', action='store_true', help='显示转换状态')
    
    args = parser.parse_args()
    
    converter = TikuConverterManager()
    
    if args.list:
        print("📋 可转换的文件列表:")
        files = converter.get_convertible_files()
        for file_info in files:
            print(f"  {file_info['name']} ({file_info['format']})")
    
    elif args.convert:
        print(f"🔄 转换所有 {args.convert} 文件为Excel格式")
        if args.convert == 'pdf':
            files = [f for f in converter.get_convertible_files() if f['format'] == 'pdf']
            for file_info in files:
                converter.convert_pdf_to_excel(file_info['path'])
        elif args.convert == 'word':
            files = [f for f in converter.get_convertible_files() if f['format'] == 'word']
            for file_info in files:
                converter.convert_word_to_excel(file_info['path'])
    
    elif args.batch:
        converter.batch_convert('excel')
    
    elif args.status:
        status = converter.get_conversion_status()
        print("📊 转换状态:")
        print(f"  总文件数: {status['total_files']}")
        print(f"  可转换文件: {status['convertible']}")
        print(f"  已是Excel格式: {status['already_excel']}")
        print("  格式分布:")
        for format_type, count in status['formats'].items():
            print(f"    {format_type}: {count} 个")
    
    else:
        print("🎯 题库转换管理器")
        print("使用 --help 查看可用选项")

if __name__ == "__main__":
    main()
