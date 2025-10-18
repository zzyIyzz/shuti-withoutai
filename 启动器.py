
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安规刷题系统 - 统一启动器
集成所有功能：刷题、题库管理、格式转换、依赖安装等
"""

import os
import sys
import subprocess
from pathlib import Path

class 启动器:
    """系统启动器和依赖管理"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.依赖列表 = ['openpyxl', 'python-docx', 'pdfplumber', 'PyPDF2']
    
    def 清屏(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def 显示标题(self, 标题):
        """显示标题"""
        print("\n" + "=" * 70)
        print(f"  {标题}")
        print("=" * 70 + "\n")
    
    def 检查依赖(self):
        """检查并返回缺失的依赖"""
        缺失依赖 = []
        
        for 库名 in self.依赖列表:
            try:
                if 库名 == 'python-docx':
                    __import__('docx')
                elif 库名 == 'pdfplumber':
                    __import__('pdfplumber')
                else:
                    __import__(库名)
            except ImportError:
                缺失依赖.append(库名)
        
        return 缺失依赖
    
    def 安装依赖(self, 依赖列表=None):
        """安装依赖库"""
        if 依赖列表 is None:
            依赖列表 = self.依赖列表
        
        print("正在安装依赖库...")
        print(f"需要安装: {', '.join(依赖列表)}")
        print("-" * 70)
        
        # 使用清华镜像加速下载
        镜像源 = "https://pypi.tuna.tsinghua.edu.cn/simple"
        
        try:
            for 库 in 依赖列表:
                print(f"\n安装 {库}...")
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', 库, '-i', 镜像源],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"[成功] {库} 安装成功")
                else:
                    print(f"[失败] {库} 安装失败")
                    print(result.stderr)
            
            print("\n" + "-" * 70)
            print("依赖安装完成！")
            return True
            
        except Exception as e:
            print(f"\n安装失败: {e}")
            print("\n请手动运行以下命令：")
            for 库 in 依赖列表:
                print(f"  pip install {库}")
            return False
    
    def 检查并安装依赖(self):
        """检查依赖，如有缺失则提示安装"""
        缺失 = self.检查依赖()
        
        if 缺失:
            print("[警告] 检测到缺少以下依赖库：")
            for 库 in 缺失:
                print(f"  - {库}")
            print()
            
            选择 = input("是否现在安装？(y/n): ").strip().lower()
            if 选择 == 'y':
                return self.安装依赖(缺失)
            else:
                print("\n提示：部分功能可能无法使用")
                print("稍后可以选择菜单中的'安装/检查依赖'选项")
                input("\n按回车键继续...")
                return False
        else:
            return True
    
    def 主菜单(self):
        """显示主菜单"""
        while True:
            self.清屏()
            self.显示标题("安规刷题系统 - 主菜单")
            
            print("【刷题功能】")
            print("  1. 开始刷题")
            print("  2. 错题重做")
            print("  3. 答题统计")
            print()
            
            print("【题库管理】")
            print("  4. 题库管理")
            print("  5. Word转Excel")
            print("  6. PDF转Excel")
            print("  9. 题库转换管理器")
            print()
            
            print("【系统设置】")
            print("  7. 安装/检查依赖")
            print("  8. 查看使用说明")
            print()
            
            print("  0. 退出程序")
            print("-" * 70)
            
            选择 = input("请选择功能（输入数字）: ").strip()
            
            if 选择 == '1':
                self.启动刷题程序()
            elif 选择 == '2':
                self.启动刷题程序(错题模式=True)
            elif 选择 == '3':
                self.显示统计()
            elif 选择 == '4':
                self.题库管理()
            elif 选择 == '5':
                self.Word转Excel()
            elif 选择 == '6':
                self.PDF转Excel()
            elif 选择 == '9':
                self.题库转换管理器()
            elif 选择 == '7':
                self.管理依赖()
            elif 选择 == '8':
                self.显示说明()
            elif 选择 == '0':
                print("\n感谢使用！祝考试顺利！ 💪")
                break
            else:
                print("无效选择，请重新输入")
                input("按回车键继续...")
    
    def 启动刷题程序(self, 错题模式=False):
        """启动刷题程序"""
        try:
            # 检查必要的依赖
            if not self.检查核心依赖():
                return
            
            # 导入并运行主程序
            import main
            if 错题模式:
                # 可以在main.py中添加错题模式支持
                main.main_menu()
            else:
                main.main_menu()
                
        except ImportError as e:
            print(f"\n错误: 无法导入刷题程序模块")
            print(f"详细: {e}")
            input("\n按回车键返回...")
        except Exception as e:
            print(f"\n运行出错: {e}")
            import traceback
            traceback.print_exc()
            input("\n按回车键返回...")
    
    def 显示统计(self):
        """显示答题统计"""
        try:
            from 统计分析 import StatsAnalyzer
            
            self.清屏()
            self.显示标题("答题统计")
            
            analyzer = StatsAnalyzer()
            analyzer.show_statistics()
            
            input("\n按回车键返回...")
            
        except Exception as e:
            print(f"显示统计失败: {e}")
            input("按回车键返回...")
    
    def 题库管理(self):
        """题库管理"""
        try:
            from 题库管理 import TikuManager
            
            while True:
                self.清屏()
                self.显示标题("题库管理")
                
                manager = TikuManager()
                tiku_list = manager.get_tiku_list()
                
                if tiku_list:
                    print("已加载题库：")
                    for i, tiku in enumerate(tiku_list, 1):
                        count = manager.get_question_count(tiku)
                        # 识别文件类型
                        if (self.base_dir / f"{tiku}.xlsx").exists():
                            类型 = "Excel"
                        elif (self.base_dir / f"{tiku}.docx").exists():
                            类型 = "Word"
                        elif (self.base_dir / f"{tiku}.pdf").exists():
                            类型 = "PDF"
                        else:
                            类型 = "未知"
                        
                        print(f"  {i}. [{类型}] {tiku} ({count}题)")
                else:
                    print("当前没有题库")
                    print("\n提示：请将题库文件放入'刷题程序'文件夹")
                    print("支持格式：Excel(.xlsx)、Word(.docx)、PDF(.pdf)")
                
                print("\n操作：")
                print("  1. 刷新题库")
                print("  2. 查看题库详情")
                print("  3. 清空缓存")
                print("  0. 返回")
                print("-" * 70)
                
                choice = input("请选择: ").strip()
                
                if choice == '1':
                    manager.refresh()
                    print("\n[成功] 题库已刷新！")
                    input("按回车键继续...")
                    
                elif choice == '2':
                    if tiku_list:
                        idx_input = input("\n请输入题库编号: ").strip()
                        try:
                            idx = int(idx_input) - 1
                            if 0 <= idx < len(tiku_list):
                                self.清屏()
                                manager.show_tiku_detail(tiku_list[idx])
                                input("\n按回车键继续...")
                        except ValueError:
                            print("无效输入")
                            input("按回车键继续...")
                    else:
                        print("没有题库")
                        input("按回车键继续...")
                        
                elif choice == '3':
                    确认 = input("确认清空缓存？(y/n): ").strip().lower()
                    if 确认 == 'y':
                        manager.refresh()
                        print("\n[成功] 缓存已清空！")
                        input("按回车键继续...")
                        
                elif choice == '0':
                    break
                    
        except Exception as e:
            print(f"题库管理出错: {e}")
            import traceback
            traceback.print_exc()
            input("按回车键返回...")
    
    def Word转Excel(self):
        """Word题库转Excel"""
        try:
            # 检查依赖
            try:
                import openpyxl
                from docx import Document
            except ImportError as e:
                print(f"\n缺少依赖库: {e}")
                print("请先安装依赖（选择菜单中的'安装/检查依赖'）")
                input("\n按回车键返回...")
                return
            
            from Word题库转换工具 import word_to_excel, batch_convert
            
            self.清屏()
            self.显示标题("Word题库转Excel工具")
            
            print("1. 转换单个Word文件")
            print("2. 批量转换所有Word文件")
            print("0. 返回")
            print()
            
            choice = input("请选择: ").strip()
            
            if choice == '1':
                word_file = input("\n请输入Word文件名（含.docx后缀）: ").strip()
                if word_file:
                    print()
                    word_to_excel(word_file)
                    
            elif choice == '2':
                确认 = input("\n批量转换所有Word文件，确认？(y/n): ").strip().lower()
                if 确认 == 'y':
                    print()
                    batch_convert()
            
            input("\n按回车键返回...")
            
        except Exception as e:
            print(f"转换出错: {e}")
            import traceback
            traceback.print_exc()
            input("按回车键返回...")
    
    def PDF转Excel(self):
        """PDF题库转Excel"""
        try:
            # 检查依赖
            try:
                import openpyxl
                import pdfplumber
            except ImportError as e:
                print(f"\n缺少依赖库: {e}")
                print("\n需要安装以下依赖：")
                if 'openpyxl' in str(e):
                    print("  - openpyxl")
                if 'pdfplumber' in str(e):
                    print("  - pdfplumber")
                print("\n请先安装依赖（选择菜单中的'安装/检查依赖'）")
                input("\n按回车键返回...")
                return
            
            from PDF题库转换工具 import pdf_to_excel, batch_convert
            
            self.清屏()
            self.显示标题("PDF题库转Excel工具")
            
            print("注意：")
            print("• PDF解析需要较长时间，请耐心等待")
            print("• 仅支持文本型PDF，扫描版PDF无法识别")
            print("• 建议转换后检查Excel内容")
            print()
            
            print("1. 转换单个PDF文件")
            print("2. 批量转换所有PDF文件")
            print("0. 返回")
            print()
            
            choice = input("请选择: ").strip()
            
            if choice == '1':
                pdf_file = input("\n请输入PDF文件名（含.pdf后缀）: ").strip()
                if pdf_file:
                    print("\n提示：PDF解析可能需要几分钟，请耐心等待...\n")
                    pdf_to_excel(pdf_file)
                    
            elif choice == '2':
                确认 = input("\n批量转换可能需要很长时间，确认？(y/n): ").strip().lower()
                if 确认 == 'y':
                    print()
                    batch_convert()
            
            input("\n按回车键返回...")
            
        except Exception as e:
            print(f"转换出错: {e}")
            import traceback
            traceback.print_exc()
            input("按回车键返回...")
    
    def 管理依赖(self):
        """依赖管理"""
        while True:
            self.清屏()
            self.显示标题("依赖管理")
            
            print("检查依赖状态...")
            print("-" * 70)
            
            # 检查每个依赖
            for 库名 in self.依赖列表:
                try:
                    if 库名 == 'python-docx':
                        __import__('docx')
                        版本 = __import__('docx').__version__
                    elif 库名 == 'pdfplumber':
                        模块 = __import__('pdfplumber')
                        版本 = getattr(模块, '__version__', '已安装')
                    else:
                        模块 = __import__(库名)
                        版本 = getattr(模块, '__version__', '已安装')
                    
                    print(f"  [OK] {库名:20s} {版本}")
                except ImportError:
                    print(f"  [NO] {库名:20s} 未安装")
            
            print("-" * 70)
            print()
            
            print("操作：")
            print("  1. 安装所有依赖")
            print("  2. 重新安装所有依赖")
            print("  3. 安装单个依赖")
            print("  0. 返回")
            print()
            
            choice = input("请选择: ").strip()
            
            if choice == '1':
                缺失 = self.检查依赖()
                if 缺失:
                    print()
                    self.安装依赖(缺失)
                else:
                    print("\n所有依赖已安装！")
                input("\n按回车键继续...")
                
            elif choice == '2':
                确认 = input("\n确认重新安装所有依赖？(y/n): ").strip().lower()
                if 确认 == 'y':
                    print()
                    self.安装依赖()
                input("\n按回车键继续...")
                
            elif choice == '3':
                print("\n可用依赖：")
                for i, 库 in enumerate(self.依赖列表, 1):
                    print(f"  {i}. {库}")
                
                idx = input("\n请选择: ").strip()
                try:
                    idx = int(idx) - 1
                    if 0 <= idx < len(self.依赖列表):
                        print()
                        self.安装依赖([self.依赖列表[idx]])
                except ValueError:
                    print("无效输入")
                input("\n按回车键继续...")
                
            elif choice == '0':
                break
    
    def 显示说明(self):
        """显示使用说明"""
        self.清屏()
        self.显示标题("使用说明")
        
        print("📖 快速开始")
        print("-" * 70)
        print("1. 首次使用：选择'安装/检查依赖'安装所需库")
        print("2. 准备题库：将题库文件放入'刷题程序'文件夹")
        print("3. 开始刷题：选择'开始刷题'")
        print()
        
        print("📚 支持的题库格式")
        print("-" * 70)
        print("• Excel (.xlsx)  - 推荐，识别准确率最高")
        print("• Word (.docx)   - 支持表格和结构化文本")
        print("• PDF (.pdf)     - 支持，建议转Excel后使用")
        print()
        
        print("🔧 格式转换")
        print("-" * 70)
        print("• Word转Excel：选择菜单中的'Word转Excel'")
        print("• PDF转Excel：选择菜单中的'PDF转Excel'")
        print("• 建议转换后检查内容，必要时手动调整")
        print()
        
        print("📋 详细文档")
        print("-" * 70)
        print("• 快速上手.txt - 快速入门指南")
        print("• 使用指南.txt - 详细使用说明")
        print("• README.md - 完整功能说明")
        print("• Word题库格式说明.txt - Word格式详解")
        print("• PDF题库格式说明.txt - PDF格式详解")
        print()
        
        input("按回车键返回...")
    
    def 检查核心依赖(self):
        """检查核心依赖（刷题必需）"""
        try:
            import openpyxl
            return True
        except ImportError:
            print("\n缺少核心依赖 openpyxl")
            print("请先安装依赖（选择菜单中的'安装/检查依赖'）")
            input("\n按回车键返回...")
            return False
    
    def 题库转换管理器(self):
        """题库转换管理器"""
        try:
            from 题库转换管理器 import TikuConverterManager
            
            self.清屏()
            self.显示标题("题库转换管理器")
            
            converter = TikuConverterManager()
            
            while True:
                print("【转换功能】")
                print("  1. 查看可转换文件")
                print("  2. 批量转换为Excel")
                print("  3. 转换状态统计")
                print("  4. 返回主菜单")
                print()
                
                选择 = input("请选择功能: ").strip()
                
                if 选择 == '1':
                    self.清屏()
                    self.显示标题("可转换文件列表")
                    files = converter.get_convertible_files()
                    
                    if not files:
                        print("📁 题库文件夹中没有找到可转换的文件")
                    else:
                        print(f"📋 找到 {len(files)} 个文件:")
                        for i, file_info in enumerate(files, 1):
                            size_mb = file_info['size'] / 1024 / 1024
                            print(f"  {i}. {file_info['name']} ({file_info['format']}, {size_mb:.1f}MB)")
                    
                    input("\n按回车键继续...")
                
                elif 选择 == '2':
                    self.清屏()
                    self.显示标题("批量转换")
                    
                    print("🔄 开始批量转换为Excel格式...")
                    results = converter.batch_convert('excel')
                    
                    print(f"\n📊 转换结果:")
                    print(f"  成功: {results['success']} 个")
                    print(f"  失败: {results['failed']} 个")
                    print(f"  跳过: {results['skipped']} 个")
                    
                    if results['details']:
                        print(f"\n📋 详细信息:")
                        for detail in results['details']:
                            status_icon = "✅" if detail['status'] == 'success' else "❌" if detail['status'] == 'failed' else "⏭️"
                            print(f"  {status_icon} {detail['file']}")
                            if 'reason' in detail:
                                print(f"     原因: {detail['reason']}")
                    
                    input("\n按回车键继续...")
                
                elif 选择 == '3':
                    self.清屏()
                    self.显示标题("转换状态统计")
                    
                    status = converter.get_conversion_status()
                    print(f"📊 文件统计:")
                    print(f"  总文件数: {status['total_files']}")
                    print(f"  可转换文件: {status['convertible']}")
                    print(f"  已是Excel格式: {status['already_excel']}")
                    
                    if status['formats']:
                        print(f"\n📋 格式分布:")
                        for format_type, count in status['formats'].items():
                            print(f"  {format_type}: {count} 个")
                    
                    input("\n按回车键继续...")
                
                elif 选择 == '4':
                    break
                
                else:
                    print("❌ 无效选择，请重新输入")
                    input("按回车键继续...")
        
        except Exception as e:
            print(f"❌ 转换管理器启动失败: {e}")
            input("按回车键继续...")
    
    def 运行(self):
        """启动系统"""
        self.清屏()
        self.显示标题("安规刷题系统")
        
        print("欢迎使用安规刷题系统！")
        print()
        print("系统功能：")
        print("  * 支持Excel/Word/PDF题库")
        print("  * 多种刷题模式（顺序/随机/考试/错题）")
        print("  * 智能错题管理")
        print("  * 详细答题统计")
        print("  * 题库格式转换")
        print()
        
        # 检查依赖
        print("正在检查依赖...")
        self.检查并安装依赖()
        
        # 进入主菜单
        self.主菜单()


def main():
    """主函数"""
    try:
        启动器实例 = 启动器()
        启动器实例.运行()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")


if __name__ == '__main__':
    main()

