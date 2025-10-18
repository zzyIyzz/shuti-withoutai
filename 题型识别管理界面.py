#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工业化商用级题型识别管理界面
提供可视化的配置管理、性能监控、统计分析等功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from 智能题型识别 import get_performance_report, adjust_confidence_threshold, reset_statistics
from 确定度配置管理 import 配置管理器

class 题型识别管理界面:
    """题型识别系统管理界面"""
    
    def __init__(self, parent=None):
        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("🧠 智能题型识别系统 - 管理控制台")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        self.配置管理器 = 配置管理器
        
        self.创建界面()
        self.刷新数据()
    
    def 创建界面(self):
        """创建管理界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建笔记本控件（选项卡）
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 1. 性能监控选项卡
        self.创建性能监控选项卡(notebook)
        
        # 2. 配置管理选项卡
        self.创建配置管理选项卡(notebook)
        
        # 3. 统计分析选项卡
        self.创建统计分析选项卡(notebook)
        
        # 4. 系统日志选项卡
        self.创建系统日志选项卡(notebook)
        
        # 底部操作按钮
        self.创建底部按钮(main_frame)
    
    def 创建性能监控选项卡(self, notebook):
        """创建性能监控选项卡"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📊 性能监控")
        
        # 性能指标显示区域
        指标框架 = ttk.LabelFrame(frame, text="实时性能指标")
        指标框架.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建性能指标标签
        self.性能指标 = {}
        指标列表 = [
            ("总识别次数", "total_count"),
            ("成功率", "success_rate"),
            ("平均确定度", "avg_confidence"),
            ("平均耗时", "avg_time"),
            ("低确定度比例", "low_confidence_rate")
        ]
        
        for i, (标签, 键) in enumerate(指标列表):
            row = i // 2
            col = i % 2
            
            ttk.Label(指标框架, text=f"{标签}:").grid(row=row, column=col*2, sticky=tk.W, padx=5, pady=2)
            
            self.性能指标[键] = ttk.Label(指标框架, text="加载中...", foreground="blue")
            self.性能指标[键].grid(row=row, column=col*2+1, sticky=tk.W, padx=5, pady=2)
        
        # 题型分布图表区域
        分布框架 = ttk.LabelFrame(frame, text="题型识别分布")
        分布框架.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建分布显示的文本框
        self.分布文本 = tk.Text(分布框架, height=10, wrap=tk.WORD)
        分布滚动条 = ttk.Scrollbar(分布框架, orient=tk.VERTICAL, command=self.分布文本.yview)
        self.分布文本.configure(yscrollcommand=分布滚动条.set)
        
        self.分布文本.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        分布滚动条.pack(side=tk.RIGHT, fill=tk.Y)
    
    def 创建配置管理选项卡(self, notebook):
        """创建配置管理选项卡"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="⚙️ 配置管理")
        
        # 确定度阈值配置
        阈值框架 = ttk.LabelFrame(frame, text="确定度阈值配置")
        阈值框架.pack(fill=tk.X, padx=5, pady=5)
        
        # 题型阈值配置
        self.阈值控件 = {}
        题型列表 = ['单选题', '多选题', '判断题', '填空题', '简答题']
        
        for i, 题型 in enumerate(题型列表):
            ttk.Label(阈值框架, text=f"{题型}确定度阈值:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            
            阈值变量 = tk.IntVar()
            阈值变量.set(self.配置管理器.配置["题型特征"][题型]["确定度阈值"])
            
            阈值滑块 = ttk.Scale(阈值框架, from_=30, to=95, orient=tk.HORIZONTAL, variable=阈值变量)
            阈值滑块.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
            
            阈值标签 = ttk.Label(阈值框架, text=str(阈值变量.get()))
            阈值标签.grid(row=i, column=2, padx=5, pady=2)
            
            # 绑定变化事件
            阈值变量.trace('w', lambda *args, 题型=题型, 标签=阈值标签, 变量=阈值变量: self.更新阈值显示(题型, 标签, 变量))
            
            self.阈值控件[题型] = {
                'variable': 阈值变量,
                'label': 阈值标签,
                'scale': 阈值滑块
            }
        
        # 配置阈值框架的列权重
        阈值框架.columnconfigure(1, weight=1)
        
        # 系统设置
        系统框架 = ttk.LabelFrame(frame, text="系统设置")
        系统框架.pack(fill=tk.X, padx=5, pady=5)
        
        # 性能监控开关
        self.性能监控开关 = tk.BooleanVar()
        self.性能监控开关.set(self.配置管理器.配置["系统设置"]["启用性能监控"])
        ttk.Checkbutton(系统框架, text="启用性能监控", variable=self.性能监控开关).pack(anchor=tk.W, padx=5, pady=2)
        
        # 详细日志开关
        self.详细日志开关 = tk.BooleanVar()
        self.详细日志开关.set(self.配置管理器.配置["系统设置"]["启用详细日志"])
        ttk.Checkbutton(系统框架, text="启用详细日志", variable=self.详细日志开关).pack(anchor=tk.W, padx=5, pady=2)
        
        # 最小确定度阈值
        最小阈值框架 = ttk.Frame(系统框架)
        最小阈值框架.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(最小阈值框架, text="最小确定度阈值:").pack(side=tk.LEFT)
        
        self.最小阈值变量 = tk.IntVar()
        self.最小阈值变量.set(self.配置管理器.配置["系统设置"]["最小确定度阈值"])
        
        最小阈值滑块 = ttk.Scale(最小阈值框架, from_=20, to=80, orient=tk.HORIZONTAL, variable=self.最小阈值变量)
        最小阈值滑块.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.最小阈值标签 = ttk.Label(最小阈值框架, text=str(self.最小阈值变量.get()))
        self.最小阈值标签.pack(side=tk.RIGHT)
        
        self.最小阈值变量.trace('w', lambda *args: self.最小阈值标签.config(text=str(self.最小阈值变量.get())))
    
    def 创建统计分析选项卡(self, notebook):
        """创建统计分析选项卡"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📈 统计分析")
        
        # 统计数据显示
        统计文本 = tk.Text(frame, wrap=tk.WORD, font=("Consolas", 10))
        统计滚动条 = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=统计文本.yview)
        统计文本.configure(yscrollcommand=统计滚动条.set)
        
        统计文本.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        统计滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.统计文本 = 统计文本
    
    def 创建系统日志选项卡(self, notebook):
        """创建系统日志选项卡"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📋 系统日志")
        
        # 日志显示区域
        日志文本 = tk.Text(frame, wrap=tk.WORD, font=("Consolas", 9))
        日志滚动条 = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=日志文本.yview)
        日志文本.configure(yscrollcommand=日志滚动条.set)
        
        日志文本.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        日志滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.日志文本 = 日志文本
        
        # 加载日志
        self.加载系统日志()
    
    def 创建底部按钮(self, parent):
        """创建底部操作按钮"""
        按钮框架 = ttk.Frame(parent)
        按钮框架.pack(fill=tk.X, pady=5)
        
        ttk.Button(按钮框架, text="🔄 刷新数据", command=self.刷新数据).pack(side=tk.LEFT, padx=5)
        ttk.Button(按钮框架, text="💾 保存配置", command=self.保存配置).pack(side=tk.LEFT, padx=5)
        ttk.Button(按钮框架, text="🗑️ 重置统计", command=self.重置统计).pack(side=tk.LEFT, padx=5)
        ttk.Button(按钮框架, text="📊 导出报告", command=self.导出报告).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(按钮框架, text="❌ 关闭", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
    
    def 更新阈值显示(self, 题型, 标签, 变量):
        """更新阈值显示"""
        标签.config(text=str(变量.get()))
    
    def 刷新数据(self):
        """刷新所有数据"""
        try:
            # 获取性能报告
            报告 = get_performance_report()
            
            if "错误" not in 报告:
                # 更新性能指标
                self.性能指标["total_count"].config(text=str(报告["总识别次数"]))
                self.性能指标["success_rate"].config(text=报告["成功率"])
                self.性能指标["avg_confidence"].config(text=报告["平均确定度"])
                self.性能指标["avg_time"].config(text=报告["平均耗时"])
                self.性能指标["low_confidence_rate"].config(text=报告["低确定度比例"])
                
                # 更新题型分布
                self.分布文本.delete(1.0, tk.END)
                分布信息 = "题型识别分布统计:\n\n"
                for 题型, 次数 in 报告["各题型分布"].items():
                    分布信息 += f"{题型:8}: {次数:4} 次\n"
                self.分布文本.insert(1.0, 分布信息)
                
                # 更新统计分析
                self.统计文本.delete(1.0, tk.END)
                统计信息 = json.dumps(报告, ensure_ascii=False, indent=2)
                self.统计文本.insert(1.0, 统计信息)
            else:
                # 显示错误信息
                for 标签, 控件 in self.性能指标.items():
                    控件.config(text="暂无数据")
                
                self.分布文本.delete(1.0, tk.END)
                self.分布文本.insert(1.0, "暂无识别数据")
                
                self.统计文本.delete(1.0, tk.END)
                self.统计文本.insert(1.0, "暂无统计数据")
            
        except Exception as e:
            messagebox.showerror("错误", f"刷新数据失败: {e}")
    
    def 保存配置(self):
        """保存配置"""
        try:
            # 更新阈值配置
            for 题型, 控件 in self.阈值控件.items():
                新阈值 = 控件['variable'].get()
                adjust_confidence_threshold(题型, 新阈值)
            
            # 更新系统设置
            self.配置管理器.配置["系统设置"]["启用性能监控"] = self.性能监控开关.get()
            self.配置管理器.配置["系统设置"]["启用详细日志"] = self.详细日志开关.get()
            self.配置管理器.配置["系统设置"]["最小确定度阈值"] = self.最小阈值变量.get()
            
            # 保存配置文件
            self.配置管理器._保存配置(self.配置管理器.配置)
            
            messagebox.showinfo("成功", "配置已保存")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def 重置统计(self):
        """重置统计数据"""
        if messagebox.askyesno("确认", "确定要重置所有统计数据吗？"):
            try:
                reset_statistics()
                messagebox.showinfo("成功", "统计数据已重置")
                self.刷新数据()
            except Exception as e:
                messagebox.showerror("错误", f"重置统计失败: {e}")
    
    def 导出报告(self):
        """导出性能报告"""
        try:
            from tkinter import filedialog
            from datetime import datetime
            
            文件路径 = filedialog.asksaveasfilename(
                title="导出性能报告",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("文本文件", "*.txt")]
            )
            
            if 文件路径:
                报告 = get_performance_report()
                报告["导出时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                with open(文件路径, 'w', encoding='utf-8') as f:
                    json.dump(报告, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("成功", f"报告已导出到: {文件路径}")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出报告失败: {e}")
    
    def 加载系统日志(self):
        """加载系统日志"""
        try:
            日志文件 = self.配置管理器.日志文件
            if 日志文件.exists():
                with open(日志文件, 'r', encoding='utf-8') as f:
                    日志内容 = f.read()
                
                # 只显示最后1000行
                日志行 = 日志内容.split('\n')
                if len(日志行) > 1000:
                    日志行 = 日志行[-1000:]
                
                self.日志文本.delete(1.0, tk.END)
                self.日志文本.insert(1.0, '\n'.join(日志行))
                
                # 滚动到底部
                self.日志文本.see(tk.END)
            else:
                self.日志文本.insert(1.0, "暂无日志文件")
                
        except Exception as e:
            self.日志文本.insert(1.0, f"加载日志失败: {e}")

def 打开管理界面(parent=None):
    """打开题型识别管理界面"""
    管理界面 = 题型识别管理界面(parent)
    return 管理界面

if __name__ == "__main__":
    # 独立运行测试
    打开管理界面()
    tk.mainloop()
