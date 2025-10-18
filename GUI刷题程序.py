#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安规刷题系统 - GUI版本
基于tkinter的图形界面
"""

import os
import sys

# 禁用Qt警告
os.environ['QT_LOGGING_RULES'] = '*=false'

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import random

from 题库管理 import TikuManager
from 刷题引擎 import ShuatiEngine
from 统计分析 import StatsAnalyzer
from 用户设置 import 用户设置管理器
from 错题记忆 import 错题记忆管理器

class 刷题应用(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("安规刷题系统 v2.0")
        self.geometry("1400x900")  # 增大窗口尺寸
        
        # 设置最小窗口尺寸
        self.minsize(1200, 700)
        
        # 设置窗口缩放 - 强制缩放
        self.state('zoomed')  # Windows最大化
        
        # 取消复杂的缩放功能，使用简单的布局
        
        # 强制DPI缩放设置
        try:
            import ctypes
            from ctypes import wintypes
            
            # 设置DPI感知
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            
            # 获取系统DPI
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            
        except:
            pass
        
        # 设置窗口图标和样式
        try:
            self.iconbitmap(default='')  # 可以添加图标
        except:
            pass
        
        # 主题配色方案
        self.themes = {
            'light': {
                'primary': '#007ACC',      # 主色-Cursor蓝
                'primary_light': '#1E90FF', # 浅蓝
                'success': '#28A745',      # 成功-绿色
                'warning': '#FFC107',      # 警告-黄色
                'danger': '#DC3545',       # 危险-红色
                'background': '#FFFFFF',   # 背景-纯白
                'card_bg': '#F8F9FA',      # 卡片背景-浅灰
                'text': '#212529',         # 文字-深黑
                'text_secondary': '#6C757D', # 次要文字-灰色
                'text_light': '#ADB5BD',   # 浅色文字-浅灰
                'border': '#DEE2E6',       # 边框-浅灰
                'hover': '#E9ECEF',        # 悬停-浅灰
                'accent': '#17A2B8',       # 强调色-青色
            },
            'dark': {
                'primary': '#007ACC',      # 主色-Cursor蓝
                'primary_light': '#1E90FF', # 浅蓝
                'success': '#4CAF50',      # 成功-绿色
                'warning': '#FF9800',      # 警告-橙色
                'danger': '#F44336',       # 危险-红色
                'background': '#1E1E1E',   # 背景-Cursor深色
                'card_bg': '#252526',      # 卡片背景-稍浅
                'text': '#CCCCCC',         # 文字-浅灰
                'text_secondary': '#969696', # 次要文字-中灰
                'text_light': '#6A6A6A',   # 浅色文字-深灰
                'border': '#3C3C3C',       # 边框-深灰
                'hover': '#2A2D2E',        # 悬停-深灰
                'accent': '#00BCD4',       # 强调色-青色
            }
        }
        
        # 当前主题
        self.current_theme = 'light'
        self.colors = self.themes[self.current_theme]
        
        # 设置整体背景色
        self.configure(bg=self.colors['background'])
        
        # 初始化变量
        self.设置管理器 = 用户设置管理器()  # 创建设置管理器
        self.题库管理器 = TikuManager()
        self.错题记忆管理器 = 错题记忆管理器()
        
        # 检查是否首次使用（在设置管理器创建后）
        if not self.设置管理器.获取设置('已显示新手引导', False):
            self.after(1000, self.显示首次使用提示)
        self.当前题库 = None
        self.题目列表 = []
        self.当前题目索引 = 0
        
        # 字体设置
        self.字体设置 = {
            'family': '微软雅黑',
            'size': 10,
            'weight': 'normal',
            'slant': 'roman'
        }
        
        # 布局设置
        self.布局设置 = {
            '左侧面板宽度': 350,
            '右侧面板宽度': 800,
            '窗口状态': 'zoomed'
        }
        
        # 字体缩放设置
        self.字体缩放比例 = 1.0
        self.基础字体大小 = {
            'title': 14,
            'heading': 12,
            'normal': 10,
            'small': 8,
            'large': 13
        }
        self.答对数 = 0
        self.答错数 = 0
        self.模式 = "顺序"
        
        # 题目状态记录（用于颜色标记）
        self.题目状态 = {}  # {索引: 'correct'/'wrong'/'unseen'}
        
        # 收藏题目记录
        self.收藏题目 = set()
        
        # 答案填空模式
        self.填空模式 = False
        
        # 删除学习目标设置，简化界面
        
        # 恢复窗口状态
        self.恢复窗口状态()
        
        # 恢复主题设置
        self.恢复主题设置()
        
        # 配置样式
        self.配置样式()
        
        # 创建界面
        self.创建菜单栏()
        self.创建主界面()
        self.加载题库列表()
        self.更新统计显示()
        
        # 加载布局设置
        self.after(100, self.加载布局设置)  # 延迟加载，确保界面已创建
        
        # 设置窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.退出程序)
    
    def 配置样式(self):
        """配置ttk样式"""
        style = ttk.Style()
        style.theme_use('clam')  # 使用clam主题作为基础
        
        # 配置按钮样式
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('微软雅黑', 10, 'bold'),
                       padding=(15, 8))
        style.map('Primary.TButton',
                 background=[('active', '#1976D2'), ('pressed', '#1565C0')])
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=0,
                       font=('微软雅黑', 10),
                       padding=(12, 6))
        style.map('Success.TButton',
                 background=[('active', '#45A049')])
        
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground='white',
                       borderwidth=0,
                       font=('微软雅黑', 10),
                       padding=(12, 6))
        style.map('Warning.TButton',
                 background=[('active', '#FB8C00')])
        
        style.configure('TButton',
                       background='#ECEFF1',
                       foreground=self.colors['text'],
                       borderwidth=0,
                       font=('微软雅黑', 9),
                       padding=(10, 5))
        style.map('TButton',
                 background=[('active', '#CFD8DC')])
        
        # 配置Frame样式
        style.configure('Card.TFrame',
                       background=self.colors['card_bg'],
                       borderwidth=1,
                       relief='flat')
        
        # 配置Label样式
        style.configure('Title.TLabel',
                       background=self.colors['card_bg'],
                       foreground=self.colors['text'],
                       font=('微软雅黑', 12, 'bold'))
        
        style.configure('Heading.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['text'],
                       font=('微软雅黑', 11, 'bold'))
        
        style.configure('TLabel',
                       background=self.colors['card_bg'],
                       foreground=self.colors['text'],
                       font=('微软雅黑', 10))
    
    def 创建菜单栏(self):
        """创建顶部菜单栏"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # 题库菜单
        题库菜单 = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="题库", menu=题库菜单)
        题库菜单.add_command(label="📚 导入题库", command=self.导入题库)
        题库菜单.add_separator()
        题库菜单.add_command(label="刷新题库列表", command=self.刷新题库)
        题库菜单.add_separator()
        题库菜单.add_command(label="查看收藏题目", command=self.查看收藏)
        题库菜单.add_separator()
        题库菜单.add_command(label="错题管理", command=self.错题管理)
        题库菜单.add_command(label="智能复习", command=self.智能复习)
        题库菜单.add_separator()
        题库菜单.add_command(label="退出", command=self.退出程序)
        
        # 工具菜单
        工具菜单 = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=工具菜单)
        工具菜单.add_command(label="🧠 题型识别管理", command=self.打开题型识别管理)
        工具菜单.add_separator()
        工具菜单.add_command(label="📊 识别性能报告", command=self.显示识别性能报告)
        
        # 统计菜单
        统计菜单 = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="统计", menu=统计菜单)
        统计菜单.add_command(label="查看详细统计", command=self.查看统计)
        统计菜单.add_command(label="清空错题本", command=self.清空错题本)
        
        # 帮助菜单
        帮助菜单 = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=帮助菜单)
        帮助菜单.add_command(label="📖 使用指南", command=self.显示使用指南)
        帮助菜单.add_command(label="🎯 新手引导", command=self.新手引导)
        帮助菜单.add_command(label="❓ 常见问题", command=self.显示常见问题)
        帮助菜单.add_separator()
        帮助菜单.add_command(label="📝 问题反馈", command=self.问题反馈)
        帮助菜单.add_separator()
        帮助菜单.add_command(label="ℹ️ 关于", command=self.显示关于信息)
        帮助菜单.add_command(label="关于", command=self.显示关于)
        
        # 视图菜单 - 添加缩放控制和主题切换
        视图菜单 = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=视图菜单)
        
        # 主题切换
        主题子菜单 = tk.Menu(视图菜单, tearoff=0)
        视图菜单.add_cascade(label="主题", menu=主题子菜单)
        主题子菜单.add_command(label="🌞 亮色主题", command=lambda: self.切换主题('light'))
        主题子菜单.add_command(label="🌙 暗色主题", command=lambda: self.切换主题('dark'))
        
        视图菜单.add_separator()
        
        # 字体缩放
        视图菜单.add_command(label="🎨 自定义字体", command=self.自定义字体)
        视图菜单.add_separator()
        视图菜单.add_command(label="放大字体", command=self.放大字体)
        视图菜单.add_command(label="缩小字体", command=self.缩小字体)
        视图菜单.add_command(label="重置字体", command=self.重置字体)
        视图菜单.add_separator()
        
        # 布局管理
        视图菜单.add_command(label="💾 保存布局", command=self.保存布局设置)
        视图菜单.add_command(label="🔄 重置布局", command=self.重置布局)
        视图菜单.add_separator()
        
        # 删除窗口管理菜单（已简化界面）
        # 主题设置保留在视图菜单中
    
    def 保存布局设置(self):
        """保存当前布局设置"""
        try:
            if hasattr(self, '主分割器'):
                # 获取分割器位置 - 使用正确的方法
                分割器位置 = self.主分割器.sash_coord(0)[0] if self.主分割器.sash_coord(0) else 350
                self.布局设置['左侧面板宽度'] = 分割器位置
                self.布局设置['右侧面板宽度'] = self.winfo_width() - 分割器位置 - 20
            
            # 保存窗口状态
            self.布局设置['窗口状态'] = self.state()
            
            # 保存到文件
            import json
            with open('.data/layout_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.布局设置, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存布局设置失败: {e}")
    
    def 加载布局设置(self):
        """加载保存的布局设置"""
        try:
            import json
            import os
            if os.path.exists('.data/layout_settings.json'):
                with open('.data/layout_settings.json', 'r', encoding='utf-8') as f:
                    self.布局设置 = json.load(f)
                    
                # 应用布局设置（延迟执行，等待界面完全创建）
                if hasattr(self, '主分割器'):
                    width = self.布局设置.get('左侧面板宽度', 350)
                    self.after(100, lambda: self.主分割器.sash_place(0, width, 0))
                    
        except Exception as e:
            print(f"加载布局设置失败: {e}")
    
    def 重置布局(self):
        """重置布局到默认状态"""
        try:
            if hasattr(self, '主分割器'):
                self.主分割器.sash_place(0, 350, 0)
            self.布局设置 = {
                '左侧面板宽度': 350,
                '右侧面板宽度': 800,
                '窗口状态': 'zoomed'
            }
            messagebox.showinfo("提示", "布局已重置为默认状态！")
        except Exception as e:
            print(f"重置布局失败: {e}")
    
    def 开始拖拽(self, event):
        """开始拖拽分割器"""
        self.拖拽中状态 = True
        self.拖拽开始位置 = event.x
    
    def 拖拽中(self, event):
        """拖拽分割器过程中"""
        if hasattr(self, '拖拽中状态') and self.拖拽中状态:
            # 更新状态栏显示当前宽度
            if hasattr(self, '状态栏'):
                try:
                    当前宽度 = self.主分割器.sash_coord(0)[0] if self.主分割器.sash_coord(0) else 350
                    self.状态栏.config(text=f"左侧面板宽度: {当前宽度}px | 拖拽调整布局中...")
                except:
                    pass
    
    def 结束拖拽(self, event):
        """结束拖拽分割器"""
        if hasattr(self, '拖拽中状态') and self.拖拽中状态:
            self.拖拽中状态 = False
            # 自动保存布局
            self.保存布局设置()
            # 更新状态栏
            if hasattr(self, '状态栏'):
                try:
                    当前宽度 = self.主分割器.sash_coord(0)[0] if self.主分割器.sash_coord(0) else 350
                    self.状态栏.config(text=f"左侧面板宽度: {当前宽度}px | 布局已保存")
                except:
                    pass
    
    # 删除复杂的缩放功能，使用简单布局
    
    def 创建主界面(self):
        """创建主界面布局 - 可拖拽版本"""
        # 创建主分割器
        self.主分割器 = tk.PanedWindow(self, orient=tk.HORIZONTAL, 
                                     sashwidth=8, sashrelief=tk.RAISED,
                                     bg=self.colors['border'],
                                     cursor='sb_h_double_arrow')  # 添加拖拽光标
        self.主分割器.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 绑定分割器移动事件
        self.主分割器.bind('<Button-1>', self.开始拖拽)
        self.主分割器.bind('<B1-Motion>', self.拖拽中)
        self.主分割器.bind('<ButtonRelease-1>', self.结束拖拽)
        
        # 左侧面板（题库选择和题目列表）- 添加滚动支持
        左侧面板容器 = tk.Frame(self.主分割器, bg=self.colors['background'])
        self.主分割器.add(左侧面板容器, width=350, minsize=250)
        
        # 创建Canvas和滚动条
        左侧画布 = tk.Canvas(左侧面板容器, bg=self.colors['background'], highlightthickness=0)
        左侧滚动条 = ttk.Scrollbar(左侧面板容器, orient=tk.VERTICAL, command=左侧画布.yview)
        
        左侧滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        左侧画布.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建可滚动的内容框架
        左侧面板 = tk.Frame(左侧画布, bg=self.colors['background'])
        左侧画布_窗口 = 左侧画布.create_window((0, 0), window=左侧面板, anchor="nw")
        
        # 配置滚动
        左侧画布.configure(yscrollcommand=左侧滚动条.set)
        
        # 绑定鼠标滚轮
        def _左侧滚动(event):
            左侧画布.yview_scroll(int(-1*(event.delta/120)), "units")
        左侧画布.bind_all("<MouseWheel>", _左侧滚动)
        
        # 更新滚动区域
        def _更新左侧滚动区域(event=None):
            左侧画布.configure(scrollregion=左侧画布.bbox("all"))
            # 设置canvas窗口宽度与canvas相同
            canvas_width = 左侧画布.winfo_width()
            if canvas_width > 1:
                左侧画布.itemconfig(左侧画布_窗口, width=canvas_width)
        
        左侧面板.bind('<Configure>', _更新左侧滚动区域)
        左侧画布.bind('<Configure>', _更新左侧滚动区域)
        
        # 保存左侧面板引用
        self.左侧面板 = 左侧面板
        
        # 题库选择卡片
        题库卡片 = tk.Frame(左侧面板, bg=self.colors['card_bg'], 
                         relief='flat', borderwidth=0)
        题库卡片.pack(fill=tk.X, pady=(0, 10))
        
        # 添加卡片阴影效果（通过边框模拟）
        题库卡片.configure(highlightbackground=self.colors['border'],
                       highlightthickness=1)
        
        ttk.Label(题库卡片, text="📚 题库", 
                 style='Heading.TLabel').pack(pady=(10, 5), padx=10, anchor=tk.W)
        
        # 创建题库列表框架（包含列表框和滚动条）
        题库列表框架 = tk.Frame(题库卡片, bg=self.colors['card_bg'])
        题库列表框架.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        
        # 创建滚动条
        题库滚动条 = tk.Scrollbar(题库列表框架, orient=tk.VERTICAL)
        题库滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建题库列表框
        self.题库列表框 = tk.Listbox(题库列表框架, height=6,  # 增大高度
                                  font=("微软雅黑", 11),  # 增大字体
                                  bg=self.colors['card_bg'],
                                  fg=self.colors['text'],
                                  selectbackground=self.colors['primary'],
                                  selectforeground='white',
                                  borderwidth=0,
                                  highlightthickness=0,
                                  activestyle='none',
                                  yscrollcommand=题库滚动条.set)
        self.题库列表框.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        题库滚动条.config(command=self.题库列表框.yview)
        
        # 绑定事件
        self.题库列表框.bind('<<ListboxSelect>>', self.选择题库)
        
        # 搜索卡片
        搜索卡片 = tk.Frame(左侧面板, bg=self.colors['card_bg'],
                         relief='flat', borderwidth=0)
        搜索卡片.pack(fill=tk.X, pady=(0, 10))
        搜索卡片.configure(highlightbackground=self.colors['border'],
                       highlightthickness=1)
        
        ttk.Label(搜索卡片, text="🔍 搜索", 
                 style='Heading.TLabel').pack(pady=(10, 5), padx=10, anchor=tk.W)
        
        搜索输入框架 = tk.Frame(搜索卡片, bg=self.colors['card_bg'])
        搜索输入框架.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.搜索输入框 = tk.Entry(搜索输入框架, 
                                font=("微软雅黑", 10),
                                bg='#F8F9FA',
                                fg=self.colors['text'],
                                relief='flat',
                                borderwidth=0,
                                insertbackground=self.colors['primary'])
        self.搜索输入框.pack(fill=tk.X, ipady=8)
        self.搜索输入框.insert(0, "输入关键字搜索...")
        self.搜索输入框.bind('<FocusIn>', self.清除搜索提示)
        self.搜索输入框.bind('<FocusOut>', self.恢复搜索提示)
        self.搜索输入框.bind('<Return>', lambda e: self.搜索题目())
        self.搜索输入框.bind('<KeyRelease>', lambda e: self.实时搜索())
        
        # 添加搜索框底部边框
        tk.Frame(搜索输入框架, height=2, bg=self.colors['primary']).pack(fill=tk.X)
        
        # 题目列表卡片
        题目列表卡片 = tk.Frame(左侧面板, bg=self.colors['card_bg'],
                           relief='flat', borderwidth=0)
        题目列表卡片.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        题目列表卡片.configure(highlightbackground=self.colors['border'],
                           highlightthickness=1)
        
        ttk.Label(题目列表卡片, text="📋 题目列表", 
                 style='Heading.TLabel').pack(pady=(10, 5), padx=10, anchor=tk.W)
        
        # 颜色说明标签
        颜色说明 = tk.Label(题目列表卡片, 
                          text="🟢 已答对  🔴 已答错  🔵 当前题目  ⭐ 已收藏",
                          font=("微软雅黑", 8),
                          bg=self.colors['card_bg'],
                          fg=self.colors['text_secondary'])
        颜色说明.pack(pady=(0, 5), padx=10, anchor=tk.W)
        
        题目列表框架 = tk.Frame(题目列表卡片, bg=self.colors['card_bg'])
        题目列表框架.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 垂直滚动条
        题目滚动条 = ttk.Scrollbar(题目列表框架, orient=tk.VERTICAL)
        题目滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 水平滚动条
        题目水平滚动条 = ttk.Scrollbar(题目列表框架, orient=tk.HORIZONTAL)
        题目水平滚动条.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 配置滚动条样式
        题目滚动条.configure(style='Custom.Vertical.TScrollbar')
        题目水平滚动条.configure(style='Custom.Horizontal.TScrollbar')
        
        self.题目列表框 = tk.Listbox(题目列表框架, 
                                  height=6,  # 进一步减小高度，为滑动栏留出空间
                                  font=("微软雅黑", 9, "normal"),  # 减小字体
                                  bg=self.colors['card_bg'],
                                  fg=self.colors['text'],
                                  selectbackground=self.colors['hover'],
                                  selectforeground=self.colors['primary'],
                                  borderwidth=0,
                                  highlightthickness=0,
                                  activestyle='none',
                                  yscrollcommand=题目滚动条.set,
                                  xscrollcommand=题目水平滚动条.set)
        self.题目列表框.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        题目滚动条.config(command=self.题目列表框.yview)
        题目水平滚动条.config(command=self.题目列表框.xview)
        self.题目列表框.bind('<<ListboxSelect>>', self.从列表选择题目)
        self.题目列表框.bind('<Double-Button-1>', self.从列表选择题目)
        
        # 底部控制面板
        底部面板 = tk.Frame(左侧面板, bg=self.colors['card_bg'],
                         relief='flat', borderwidth=0)
        底部面板.pack(fill=tk.X, pady=(10, 0))  # 改为正常pack，添加顶部间距
        底部面板.configure(highlightbackground=self.colors['border'],
                       highlightthickness=1)
        
        # 模式选择
        ttk.Label(底部面板, text="🎯 学习模式", 
                 style='Heading.TLabel').pack(pady=(10, 8), padx=10, anchor=tk.W)
        
        self.模式变量 = tk.StringVar(value="顺序")
        模式框架 = tk.Frame(底部面板, bg=self.colors['card_bg'])
        模式框架.pack(fill=tk.X, padx=10)
        
        模式按钮配置 = [
            ("📝 顺序", "顺序"),
            ("🔀 随机", "随机"),
            ("❌ 错题", "错题"),
            ("📖 浏览", "浏览")
        ]
        
        for i, (文本, 值) in enumerate(模式按钮配置):
            rb = tk.Radiobutton(模式框架, text=文本, 
                               variable=self.模式变量,
                               value=值,
                               command=self.切换模式,
                               bg=self.colors['card_bg'],
                               fg=self.colors['text'],
                               selectcolor=self.colors['card_bg'],
                               activebackground=self.colors['card_bg'],
                               activeforeground=self.colors['primary'],
                               font=("微软雅黑", 9),
                               borderwidth=0,
                               highlightthickness=0)
            rb.grid(row=i//2, column=i%2, sticky=tk.W, pady=2)
        
        # 添加题目滑动栏
        滑动栏框架 = tk.Frame(底部面板, bg=self.colors['card_bg'])
        滑动栏框架.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        tk.Label(滑动栏框架, text="📊 快速跳转:", 
                font=("微软雅黑", 9), 
                bg=self.colors['card_bg'],
                fg=self.colors['text']).pack(side=tk.LEFT, padx=(0, 5))
        
        self.题目滑动栏 = tk.Scale(滑动栏框架, 
                                 from_=1, to=1, 
                                 orient=tk.HORIZONTAL,
                                 command=self.滑动栏跳转题目,
                                 bg=self.colors['card_bg'],
                                 fg=self.colors['text'],
                                 highlightthickness=0,
                                 troughcolor=self.colors['border'],
                                 activebackground=self.colors['hover'],
                                 sliderrelief='raised',
                                 length=200)
        self.题目滑动栏.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # 滑动栏数值显示
        self.滑动栏数值标签 = tk.Label(滑动栏框架, text="1/1", 
                                   font=("微软雅黑", 8), 
                                   bg=self.colors['card_bg'],
                                   fg=self.colors['text_secondary'])
        self.滑动栏数值标签.pack(side=tk.RIGHT)
        
        # 开始按钮
        ttk.Button(底部面板, text="🚀 开始学习", 
                  style='Primary.TButton',
                  command=self.开始刷题).pack(fill=tk.X, padx=10, pady=(10, 8))  # 减少间距
        
        # 学习目标区域
        tk.Frame(底部面板, height=1, bg=self.colors['border']).pack(fill=tk.X, pady=5)  # 减少间距
        
        # 删除学习目标区域，简化界面
        
        # 统计信息
        tk.Frame(底部面板, height=1, bg=self.colors['border']).pack(fill=tk.X, pady=5)  # 减少间距
        
        ttk.Label(底部面板, text="📊 本次统计", 
                 style='Heading.TLabel').pack(pady=(0, 5), padx=10, anchor=tk.W)  # 减少间距
        
        统计框架 = tk.Frame(底部面板, bg=self.colors['card_bg'])
        统计框架.pack(fill=tk.X, padx=10, pady=(0, 5))  # 减少间距
        
        # 使用网格布局，更紧凑
        统计网格 = tk.Frame(统计框架, bg=self.colors['card_bg'])
        统计网格.pack(fill=tk.X)
        
        self.统计标签 = {
            '已答': tk.Label(统计网格, text="0", 
                          font=("微软雅黑", 16, 'bold'),
                          bg=self.colors['card_bg'],
                          fg=self.colors['text']),
            '正确': tk.Label(统计网格, text="0", 
                          font=("微软雅黑", 16, 'bold'),
                          bg=self.colors['card_bg'],
                          fg=self.colors['success']),
            '错误': tk.Label(统计网格, text="0", 
                          font=("微软雅黑", 16, 'bold'),
                          bg=self.colors['card_bg'],
                          fg=self.colors['danger']),
            '正确率': tk.Label(统计网格, text="0%", 
                            font=("微软雅黑", 16, 'bold'),
                            bg=self.colors['card_bg'],
                            fg=self.colors['primary'])
        }
        
        # 添加小标签
        tk.Label(统计网格, text="已答", font=("微软雅黑", 8),
                bg=self.colors['card_bg'], fg=self.colors['text_light']).grid(row=0, column=0, pady=(0, 2))
        self.统计标签['已答'].grid(row=1, column=0, pady=(0, 8))
        
        tk.Label(统计网格, text="正确", font=("微软雅黑", 8),
                bg=self.colors['card_bg'], fg=self.colors['text_light']).grid(row=0, column=1, pady=(0, 2))
        self.统计标签['正确'].grid(row=1, column=1, pady=(0, 8))
        
        tk.Label(统计网格, text="错误", font=("微软雅黑", 8),
                bg=self.colors['card_bg'], fg=self.colors['text_light']).grid(row=2, column=0, pady=(0, 2))
        self.统计标签['错误'].grid(row=3, column=0)
        
        tk.Label(统计网格, text="正确率", font=("微软雅黑", 8),
                bg=self.colors['card_bg'], fg=self.colors['text_light']).grid(row=2, column=1, pady=(0, 2))
        self.统计标签['正确率'].grid(row=3, column=1)
        
        # 配置列权重
        统计网格.columnconfigure(0, weight=1, uniform="stats")
        统计网格.columnconfigure(1, weight=1, uniform="stats")
        
        # 右侧面板（答题区域）
        右侧面板 = tk.Frame(self.主分割器, bg=self.colors['background'])
        self.主分割器.add(右侧面板, width=800, minsize=600)
        
        # 保存右侧面板引用
        self.右侧面板 = 右侧面板
        
        # 创建滚动画布
        右侧滚动画布 = tk.Canvas(右侧面板, bg=self.colors['background'], 
                               highlightthickness=0)
        右侧滚动画布.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 右侧滚动条
        右侧滚动条 = ttk.Scrollbar(右侧面板, orient=tk.VERTICAL, 
                                command=右侧滚动画布.yview)
        右侧滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置滚动画布
        右侧滚动画布.configure(yscrollcommand=右侧滚动条.set)
        
        # 创建可滚动的内容框架
        右侧内容框架 = tk.Frame(右侧滚动画布, bg=self.colors['background'])
        右侧滚动画布.create_window((0, 0), window=右侧内容框架, anchor="nw")
        
        # 保存内容框架引用
        self.右侧内容框架 = 右侧内容框架
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            右侧滚动画布.yview_scroll(int(-1*(event.delta/120)), "units")
        
        右侧滚动画布.bind("<MouseWheel>", _on_mousewheel)
        
        # 更新滚动区域
        def _configure_scroll_region(event=None):
            右侧滚动画布.configure(scrollregion=右侧滚动画布.bbox("all"))
        
        右侧内容框架.bind('<Configure>', _configure_scroll_region)
        
        # 题目信息栏卡片
        信息栏卡片 = tk.Frame(右侧内容框架, bg=self.colors['card_bg'],
                          relief='flat', borderwidth=0)
        信息栏卡片.pack(fill=tk.X, pady=(0, 5))  # 减少间距
        信息栏卡片.configure(highlightbackground=self.colors['border'],
                         highlightthickness=1)
        
        信息栏 = tk.Frame(信息栏卡片, bg=self.colors['card_bg'])
        信息栏.pack(fill=tk.X, padx=15, pady=12)
        
        self.题目序号标签 = tk.Label(信息栏, text="📝 题目 0/0", 
                                   font=("微软雅黑", 12, "bold"),
                                   bg=self.colors['card_bg'],
                                   fg=self.colors['primary'])
        self.题目序号标签.pack(side=tk.LEFT)
        
        self.题型标签 = tk.Label(信息栏, text="[题型]", 
                               font=("微软雅黑", 10),
                               bg=self.colors['card_bg'],
                               fg=self.colors['text_light'])
        self.题型标签.pack(side=tk.LEFT, padx=20)
        
        # 题目显示卡片
        题目卡片 = tk.Frame(右侧内容框架, bg=self.colors['card_bg'],
                         relief='flat', borderwidth=0)
        题目卡片.pack(fill=tk.BOTH, expand=True, pady=(0, 5))  # 减少间距
        题目卡片.configure(highlightbackground=self.colors['border'],
                       highlightthickness=1)
        
        tk.Label(题目卡片, text="📋 题目内容", 
                font=("微软雅黑", 11, "bold"),
                bg=self.colors['card_bg'],
                fg=self.colors['text']).pack(anchor=tk.W, pady=(12, 8), padx=15)
        
        题目框架 = tk.Frame(题目卡片, bg=self.colors['card_bg'])
        题目框架.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 12))
        
        self.题目文本 = tk.Text(题目框架, wrap=tk.WORD, 
                              font=("微软雅黑", 12),  # 增大字体
                              height=12,  # 增大高度
                              bg=self.colors['card_bg'],
                              fg=self.colors['text'],
                              relief='flat',
                              borderwidth=0,
                              padx=15,
                              pady=10,
                              spacing1=5,  # 增加行间距
                              spacing3=5)
        self.题目文本.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        题目滚动条 = ttk.Scrollbar(题目框架, command=self.题目文本.yview)
        题目滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        self.题目文本.config(yscrollcommand=题目滚动条.set)
        
        # 选项区域
        self.选项框架 = tk.Frame(右侧内容框架, bg=self.colors['background'])
        self.选项框架.pack(fill=tk.X, pady=(0, 5))  # 减少间距
        
        # 答案输入卡片
        self.答案框架 = tk.Frame(右侧内容框架, bg=self.colors['card_bg'],
                              relief='flat', borderwidth=0)
        self.答案框架.pack(fill=tk.X, pady=(0, 5))  # 减少间距
        self.答案框架.configure(highlightbackground=self.colors['border'],
                             highlightthickness=1)
        
        答案内容区 = tk.Frame(self.答案框架, bg=self.colors['card_bg'])
        答案内容区.pack(fill=tk.X, padx=15, pady=12)
        
        tk.Label(答案内容区, text="✏️ 你的答案", 
                font=("微软雅黑", 10, "bold"),
                bg=self.colors['card_bg'],
                fg=self.colors['text']).pack(side=tk.LEFT, padx=(0, 10))
        
        self.答案输入框 = tk.Entry(答案内容区, 
                                font=("微软雅黑", 11),
                                bg=self.colors['card_bg'],
                                fg=self.colors['text'],
                                relief='solid',
                                borderwidth=1,
                                width=30)
        self.答案输入框.pack(side=tk.LEFT, ipady=6, padx=5)
        self.答案输入框.bind('<Return>', lambda e: self.提交答案())
        
        ttk.Button(答案内容区, text="✓ 提交", 
                  style='Success.TButton',
                  command=self.提交答案).pack(side=tk.LEFT, padx=3)
        ttk.Button(答案内容区, text="👁 看答案", 
                  style='Warning.TButton',
                  command=self.看答案并记错题).pack(side=tk.LEFT, padx=3)
        
        # 填空答案按钮（动态显示）
        self.填空答案按钮 = ttk.Button(答案内容区, text="📝 显示填空答案", 
                                    style='Primary.TButton',
                                    command=self.显示填空答案)
        
        ttk.Button(答案内容区, text="跳过", 
                  command=self.跳过题目).pack(side=tk.LEFT, padx=3)
        
        # 答案显示/隐藏卡片（浏览模式）
        self.答案显示框架 = tk.Frame(右侧内容框架, bg=self.colors['card_bg'],
                                  relief='flat', borderwidth=0)
        self.答案显示框架.configure(highlightbackground=self.colors['border'],
                                highlightthickness=1)
        
        答案显示内容 = tk.Frame(self.答案显示框架, bg=self.colors['card_bg'])
        答案显示内容.pack(fill=tk.X, padx=15, pady=12)
        
        self.答案显示按钮 = ttk.Button(答案显示内容, text="👁 显示答案", 
                                    style='Primary.TButton',
                                    command=self.切换答案显示)
        self.答案显示按钮.pack(side=tk.LEFT, padx=5)
        
        self.正确答案标签 = tk.Label(答案显示内容, text="", 
                                   font=("微软雅黑", 11, "bold"),
                                   bg=self.colors['card_bg'],
                                   fg=self.colors['primary'])
        self.正确答案标签.pack(side=tk.LEFT, padx=15)
        
        self.答案已显示 = False
        
        # 反馈和操作卡片
        操作反馈卡片 = tk.Frame(右侧内容框架, bg=self.colors['card_bg'],
                             relief='flat', borderwidth=0)
        操作反馈卡片.pack(fill=tk.X, pady=(0, 5))  # 减少间距
        操作反馈卡片.configure(highlightbackground=self.colors['border'],
                            highlightthickness=1)
        
        操作反馈内容 = tk.Frame(操作反馈卡片, bg=self.colors['card_bg'])
        操作反馈内容.pack(fill=tk.X, padx=15, pady=12)
        
        self.反馈标签 = tk.Label(操作反馈内容, text="", 
                              font=("微软雅黑", 11, "bold"),
                              bg=self.colors['card_bg'])
        self.反馈标签.pack(side=tk.LEFT, padx=5)
        
        # 收藏按钮
        self.收藏按钮 = ttk.Button(操作反馈内容, text="⭐ 收藏", 
                                 command=self.切换收藏)
        self.收藏按钮.pack(side=tk.RIGHT, padx=5)
        
        # 解析区域 - 折叠式设计
        self.解析卡片 = tk.Frame(右侧内容框架, bg=self.colors['card_bg'],
                             relief='flat', borderwidth=0)
        self.解析卡片.pack(fill=tk.X, pady=(0, 5))  # 减少间距
        self.解析卡片.configure(highlightbackground=self.colors['border'],
                            highlightthickness=1)
        
        # 解析标题栏（可点击展开/收起）
        解析标题栏 = tk.Frame(self.解析卡片, bg=self.colors['card_bg'], cursor='hand2')
        解析标题栏.pack(fill=tk.X, padx=15, pady=12)
        解析标题栏.bind('<Button-1>', lambda e: self.切换解析显示())
        
        self.解析展开图标 = tk.Label(解析标题栏, text="▶", 
                                  font=("微软雅黑", 10),
                                  bg=self.colors['card_bg'],
                                  fg=self.colors['text_secondary'],
                                  cursor='hand2')
        self.解析展开图标.pack(side=tk.LEFT, padx=(0, 8))
        self.解析展开图标.bind('<Button-1>', lambda e: self.切换解析显示())
        
        tk.Label(解析标题栏, text="💡 题目解析", 
                font=("微软雅黑", 10, "bold"),
                bg=self.colors['card_bg'],
                fg=self.colors['text'],
                cursor='hand2').pack(side=tk.LEFT)
        
        tk.Label(解析标题栏, text="(点击展开)", 
                font=("微软雅黑", 9),
                bg=self.colors['card_bg'],
                fg=self.colors['text_light'],
                cursor='hand2').pack(side=tk.LEFT, padx=(8, 0))
        
        # 解析内容框架（默认隐藏）
        self.解析内容框架 = tk.Frame(self.解析卡片, bg=self.colors['card_bg'])
        self.解析已展开 = False
        
        解析文本框架 = tk.Frame(self.解析内容框架, bg=self.colors['card_bg'])
        解析文本框架.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 12))
        
        self.解析文本 = tk.Text(解析文本框架, wrap=tk.WORD, 
                              font=("微软雅黑", 10), 
                              height=4,
                              bg='#F8F9FA',
                              fg=self.colors['text_secondary'],
                              relief='flat',
                              borderwidth=0,
                              padx=12,
                              pady=10,
                              state=tk.DISABLED)
        self.解析文本.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        解析滚动条 = ttk.Scrollbar(解析文本框架, command=self.解析文本.yview)
        解析滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        self.解析文本.config(yscrollcommand=解析滚动条.set)
        
        # 底部导航卡片
        底部导航 = tk.Frame(右侧内容框架, bg=self.colors['card_bg'],
                         relief='flat', borderwidth=0)
        底部导航.pack(fill=tk.X, pady=(0, 5))  # 减少间距
        底部导航.configure(highlightbackground=self.colors['border'],
                       highlightthickness=1)
        
        导航内容 = tk.Frame(底部导航, bg=self.colors['card_bg'])
        导航内容.pack(fill=tk.X, padx=15, pady=12)
        
        ttk.Button(导航内容, text="⬅ 上一题", 
                  command=self.上一题).pack(side=tk.LEFT, padx=3)
        ttk.Button(导航内容, text="下一题 ➡", 
                  command=self.下一题).pack(side=tk.LEFT, padx=3)
        
        # 题目跳转
        跳转框架 = tk.Frame(导航内容, bg=self.colors['card_bg'])
        跳转框架.pack(side=tk.LEFT, padx=(20, 0))
        
        tk.Label(跳转框架, text="跳转到第", 
                font=("微软雅黑", 9),
                bg=self.colors['card_bg'],
                fg=self.colors['text']).pack(side=tk.LEFT, padx=(0, 5))
        
        self.跳转输入框 = tk.Entry(跳转框架, width=6, 
                                font=("微软雅黑", 10),
                                relief='solid',
                                borderwidth=1)
        self.跳转输入框.pack(side=tk.LEFT, ipady=3)
        self.跳转输入框.bind('<Return>', lambda e: self.跳转题目())
        
        tk.Label(跳转框架, text="题", 
                font=("微软雅黑", 9),
                bg=self.colors['card_bg'],
                fg=self.colors['text']).pack(side=tk.LEFT, padx=(5, 5))
        
        ttk.Button(跳转框架, text="跳转", 
                  command=self.跳转题目).pack(side=tk.LEFT)
        
        ttk.Button(导航内容, text="🏁 结束", 
                  command=self.结束刷题).pack(side=tk.RIGHT, padx=5)
        
        # 绑定键盘快捷键
        self.bind('<Left>', lambda e: self.上一题())
        self.bind('<Right>', lambda e: self.下一题())
        self.bind('<space>', lambda e: self.快捷键_显示答案())
        self.bind('<Control-f>', lambda e: self.快捷键_搜索())
        self.bind('<Control-s>', lambda e: self.切换收藏())
        self.bind('<Control-plus>', lambda e: self.放大字体())
        self.bind('<Control-minus>', lambda e: self.缩小字体())
        self.bind('<Control-0>', lambda e: self.重置字体())
        
        # 绑定数字键快速选择
        for i in range(1, 5):
            self.bind(str(i), lambda e, num=i: self.快捷键_选择选项(num))
    
    def 加载题库列表(self):
        """加载题库列表（支持子文件夹）"""
        self.题库列表框.delete(0, tk.END)
        题库列表 = self.题库管理器.get_tiku_list()
        
        for 题库名, 文件路径 in 题库列表:
            题数 = self.题库管理器.get_question_count(题库名)
            显示名 = f"{题库名[:30]}... ({题数}题)" if len(题库名) > 30 else f"{题库名} ({题数}题)"
            self.题库列表框.insert(tk.END, 显示名)
    
    def 选择题库(self, event=None):
        """选择题库（优化版，避免重复加载）"""
        selection = self.题库列表框.curselection()
        if not selection:
            return
            
        索引 = selection[0]
        题库列表 = self.题库管理器.get_tiku_list()
        
        if 索引 >= len(题库列表):
            return
            
        题库名, 文件路径 = 题库列表[索引]
        
        # 检查是否已经加载过这个题库
        if hasattr(self, '当前题库') and self.当前题库 == 题库名:
            print(f"题库 {题库名} 已经加载，无需重新加载")
            return
        
        self.当前题库 = 题库名
        
        # 使用缓存机制加载题库
        try:
            print(f"正在加载题库: {题库名}")
            self.题目列表 = self.题库管理器.load_tiku(题库名)
            
            if self.题目列表:
                self.当前题目索引 = 0
                self.更新题目列表显示()
                self.显示题目()
                print(f"成功加载题库: {题库名}, 共 {len(self.题目列表)} 道题")
            else:
                print(f"题库加载失败: {题库名}")
                messagebox.showerror("错误", f"题库加载失败：{题库名}")
        except Exception as e:
            print(f"加载题库时出错: {e}")
            messagebox.showerror("错误", f"加载题库时出错：\n{e}")
    
    def 切换模式(self):
        """切换刷题模式"""
        self.模式 = self.模式变量.get()
    
    def 搜索题目(self):
        """搜索题目"""
        关键字 = self.搜索输入框.get().strip()
        if not 关键字:
            messagebox.showwarning("提示", "请输入搜索关键字！")
            return
        
        if not self.题目列表:
            messagebox.showinfo("提示", "请先选择题库！")
            return
        
        # 搜索包含关键字的题目
        搜索结果 = []
        for i, 题目 in enumerate(self.题目列表):
            题目文本 = 题目.get('question', '')
            if 关键字.lower() in 题目文本.lower():
                搜索结果.append(i)
        
        if 搜索结果:
            # 更新题目列表显示
            self.题目列表框.delete(0, tk.END)
            for idx in 搜索结果:
                题目 = self.题目列表[idx]
                显示文本 = f"{idx+1}. {题目.get('question', '')[:40]}..."
                self.题目列表框.insert(tk.END, 显示文本)
            
            messagebox.showinfo("搜索结果", f"找到 {len(搜索结果)} 个相关题目")
        else:
            messagebox.showinfo("搜索结果", "未找到相关题目")
    
    def 实时搜索(self):
        """实时搜索（输入时）"""
        关键字 = self.搜索输入框.get().strip()
        
        if not 关键字:
            # 恢复显示所有题目
            self.更新题目列表显示()
            return
        
        if not self.题目列表:
            return
        
        # 实时过滤
        self.题目列表框.delete(0, tk.END)
        for i, 题目 in enumerate(self.题目列表):
            题目文本 = 题目.get('question', '')
            if 关键字.lower() in 题目文本.lower():
                显示文本 = f"{i+1}. {题目文本[:40]}..."
                self.题目列表框.insert(tk.END, 显示文本)
    
    def 更新题目列表显示(self):
        """更新题目列表显示（带颜色标记）"""
        self.题目列表框.delete(0, tk.END)
        
        if not self.题目列表:
            return
        
        for i, 题目 in enumerate(self.题目列表):
            题目文本 = 题目.get('question', '')
            题型 = 题目.get('type', '')
            
            # 添加状态和收藏标记
            状态标记 = ""
            if i in self.收藏题目:
                状态标记 = "★ "
            
            # 显示：序号. [题型] 题目内容...
            显示文本 = f"{状态标记}{i+1}. [{题型}] {题目文本[:30]}..."
            self.题目列表框.insert(tk.END, 显示文本)
            
            # 设置颜色
            状态 = self.题目状态.get(i, 'unseen')
            if 状态 == 'correct':
                self.题目列表框.itemconfig(i, fg='green')  # 绿色 = 答对
            elif 状态 == 'wrong':
                self.题目列表框.itemconfig(i, fg='red')    # 红色 = 答错
            elif i == self.当前题目索引:
                self.题目列表框.itemconfig(i, fg='blue')   # 蓝色 = 当前
    
    def 更新题目列表颜色(self):
        """更新题目列表颜色标记"""
        try:
            if not self.题目列表:
                return
            
            for i in range(len(self.题目列表)):
                状态 = self.题目状态.get(i, 'unseen')
                if 状态 == 'correct':
                    self.题目列表框.itemconfig(i, fg='green')  # 绿色 = 答对
                elif 状态 == 'wrong':
                    self.题目列表框.itemconfig(i, fg='red')    # 红色 = 答错
                elif i == self.当前题目索引:
                    self.题目列表框.itemconfig(i, fg='blue')   # 蓝色 = 当前
                else:
                    self.题目列表框.itemconfig(i, fg=self.colors['text'])  # 默认颜色
        except Exception as e:
            print(f"更新题目列表颜色失败: {e}")
    
    def 从列表选择题目(self, event=None):
        """从题目列表选择并跳转"""
        selection = self.题目列表框.curselection()
        if not selection:
            return
        
        # 获取显示文本
        显示文本 = self.题目列表框.get(selection[0])
        
        # 提取序号
        try:
            序号文本 = 显示文本.split('.')[0].strip()
            题目序号 = int(序号文本)
            
            if 1 <= 题目序号 <= len(self.题目列表):
                self.当前题目索引 = 题目序号 - 1
                self.显示题目()
        except:
            pass
    
    def 切换界面模式(self):
        """根据模式切换界面"""
        if self.模式 == "浏览":
            # 浏览模式：隐藏答案输入，显示答案按钮
            self.答案框架.pack_forget()
            self.答案显示框架.pack(fill=tk.X, pady=5)  # 减少间距
        else:
            # 刷题模式：显示答案输入，隐藏答案按钮
            self.答案显示框架.pack_forget()
            self.答案框架.pack(fill=tk.X, pady=5)  # 减少间距
    
    def 切换答案显示(self):
        """切换显示/隐藏答案"""
        if not self.题目列表 or self.当前题目索引 >= len(self.题目列表):
            return
        
        题目 = self.题目列表[self.当前题目索引]
        
        if self.答案已显示:
            # 隐藏答案
            self.答案显示按钮.config(text="显示答案")
            self.正确答案标签.config(text="")
            self.答案已显示 = False
            
            # 隐藏解析
            self.解析文本.config(state=tk.NORMAL)
            self.解析文本.delete(1.0, tk.END)
            self.解析文本.config(state=tk.DISABLED)
        else:
            # 显示答案
            self.答案显示按钮.config(text="隐藏答案")
            答案文本 = f"答案：{题目.get('answer', '无')}"
            self.正确答案标签.config(text=答案文本)
            self.答案已显示 = True
            
            # 显示解析
            if 题目.get('explanation'):
                self.解析文本.config(state=tk.NORMAL)
                self.解析文本.delete(1.0, tk.END)
                self.解析文本.insert(1.0, 题目.get('explanation', ''))
                self.解析文本.config(state=tk.DISABLED)
    
    def 开始刷题(self):
        """开始刷题"""
        if not self.当前题库:
            messagebox.showwarning("提示", "请先选择一个题库！")
            return
        
        # 加载题目
        if self.模式 == "错题":
            # 使用智能复习功能获取错题
            智能错题 = self.错题记忆管理器.获取智能复习题目(50)  # 获取50道智能复习题目
            if not 智能错题:
                messagebox.showinfo("提示", "错题本为空，没有错题可练习！")
                return
            
            # 提取题目数据
            self.题目列表 = [item['question'] for item in 智能错题]
            
            # 显示智能复习信息
            if len(智能错题) > 0:
                平均掌握程度 = sum(item['mastery_level'] for item in 智能错题) / len(智能错题)
                messagebox.showinfo("智能复习", 
                                  f"已为您准备了 {len(智能错题)} 道智能复习题目\n"
                                  f"平均掌握程度：{平均掌握程度:.1f}/5\n"
                                  f"将优先显示掌握程度较低的题目")
        else:
            questions = self.题库管理器.load_tiku(self.当前题库)
            if not questions:
                messagebox.showerror("错误", "加载题库失败！")
                return
            
            self.题目列表 = questions.copy()
            if self.模式 == "随机":
                random.shuffle(self.题目列表)
        
        # 恢复学习进度（如果不是错题模式）
        if self.模式 != "错题":
            self.恢复题库进度(self.当前题库)
        else:
            # 错题模式重置统计
            self.当前题目索引 = 0
            self.答对数 = 0
            self.答错数 = 0
            self.题目状态 = {}
        
        # 切换界面模式
        self.切换界面模式()
        
        # 显示第一题
        self.显示题目()
        self.更新统计显示()
        
        # 更新题目列表显示
        self.更新题目列表显示()
        
        # 更新滑动栏
        self.更新滑动栏()
        
        模式说明 = {
            "顺序": "顺序刷题",
            "随机": "随机刷题",
            "错题": "错题重做",
            "浏览": "浏览背题"
        }
        
        提示文本 = "提示：\n"
        提示文本 += "- 左侧列表可点击查看任意题目\n"
        提示文本 += "- 使用搜索框快速查找题目\n"
        if self.模式 == '浏览':
            提示文本 += "- 使用左右方向键快速翻页"
        else:
            提示文本 += "- 答题后自动跳转下一题"
        
        messagebox.showinfo("开始学习", 
                          f"已加载 {len(self.题目列表)} 道题目\n"
                          f"模式：{模式说明.get(self.模式, self.模式)}\n\n"
                          f"{提示文本}")
    
    def 切换主题(self, 主题名称):
        """切换主题"""
        if 主题名称 not in self.themes:
            return False
        
        self.current_theme = 主题名称
        self.colors = self.themes[self.current_theme]
        
        # 更新主窗口背景
        self.configure(bg=self.colors['background'])
        
        # 更新所有组件颜色
        self.更新所有组件颜色()
        
        # 保存主题设置
        self.设置管理器.设置值('current_theme', 主题名称)
        
        return True
    
    def 更新所有组件颜色(self):
        """更新所有组件的颜色"""
        try:
            # 更新主要框架
            for widget in self.winfo_children():
                self.递归更新组件颜色(widget)
        except Exception as e:
            print(f"更新组件颜色失败: {e}")
    
    def 递归更新组件颜色(self, widget):
        """递归更新组件颜色"""
        try:
            widget_type = widget.winfo_class()
            
            if widget_type == 'Frame':
                if hasattr(widget, 'cget') and 'bg' in widget.cget('configure'):
                    widget.configure(bg=self.colors['card_bg'])
            elif widget_type == 'Label':
                if hasattr(widget, 'cget') and 'fg' in widget.cget('configure'):
                    widget.configure(fg=self.colors['text'])
                if hasattr(widget, 'cget') and 'bg' in widget.cget('configure'):
                    widget.configure(bg=self.colors['card_bg'])
            elif widget_type == 'Button':
                if hasattr(widget, 'cget') and 'fg' in widget.cget('configure'):
                    widget.configure(fg=self.colors['text'])
                if hasattr(widget, 'cget') and 'bg' in widget.cget('configure'):
                    widget.configure(bg=self.colors['card_bg'])
                if hasattr(widget, 'cget') and 'activebackground' in widget.cget('configure'):
                    widget.configure(activebackground=self.colors['hover'])
            elif widget_type == 'Text':
                if hasattr(widget, 'cget') and 'fg' in widget.cget('configure'):
                    widget.configure(fg=self.colors['text'])
                if hasattr(widget, 'cget') and 'bg' in widget.cget('configure'):
                    widget.configure(bg='white' if self.current_theme == 'light' else '#2A2A2A')
            
            # 递归更新子组件
            for child in widget.winfo_children():
                self.递归更新组件颜色(child)
                
        except Exception as e:
            pass  # 忽略无法更新的组件
    
    def 安全执行(self, 方法, *args, **kwargs):
        """安全执行方法，捕获异常"""
        try:
            return 方法(*args, **kwargs)
        except Exception as e:
            print(f"执行 {方法.__name__} 时出错: {e}")
            return None
    
    def 配置组件颜色(self, 组件, 组件类型='default'):
        """通用组件颜色配置"""
        颜色配置 = {
            'button': {
                'bg': self.colors['card_bg'],
                'fg': self.colors['text'],
                'activebackground': self.colors['hover']
            },
            'label': {
                'bg': self.colors['card_bg'],
                'fg': self.colors['text']
            },
            'frame': {
                'bg': self.colors['card_bg']
            },
            'text': {
                'bg': 'white',
                'fg': self.colors['text']
            }
        }
        
        配置 = 颜色配置.get(组件类型, 颜色配置['default'])
        for 属性, 值 in 配置.items():
            try:
                组件.configure(**{属性: 值})
            except:
                pass
    
    def 更新题目文本(self, 内容, 状态=tk.DISABLED):
        """通用题目文本更新方法（自动去除答案）"""
        # 去除题目中的答案显示
        清理内容 = self.清理题目答案(内容)
        
        self.题目文本.config(state=tk.NORMAL)
        self.题目文本.delete(1.0, tk.END)
        self.题目文本.insert(1.0, 清理内容)
        self.题目文本.config(state=状态)
    
    def 清理题目答案(self, 题目内容):
        """清理题目中的答案显示和选项（增强版）"""
        import re
        
        # 1. 去除括号中的答案，如 (B)、(A)、(C) 等
        清理内容 = re.sub(r'\([A-Z]\)', '', 题目内容)
        
        # 2. 去除判断题的答案符号，如 (√)、(×) 等
        清理内容 = re.sub(r'\([√×✓✗对错]\)', '', 清理内容)
        
        # 3. 去除其他可能的答案格式
        清理内容 = re.sub(r'答案[：:]\s*[A-Z]', '', 清理内容)
        清理内容 = re.sub(r'正确答案[：:]\s*[A-Z]', '', 清理内容)
        清理内容 = re.sub(r'参考答案[：:]\s*[A-Z]', '', 清理内容)
        
        # 4. 去除"答案："后面的内容（防止简答题答案泄露）
        清理内容 = re.sub(r'答案[：:].*$', '', 清理内容, flags=re.MULTILINE)
        清理内容 = re.sub(r'正确答案[：:].*$', '', 清理内容, flags=re.MULTILINE)
        清理内容 = re.sub(r'参考答案[：:].*$', '', 清理内容, flags=re.MULTILINE)
        
        # 5. 分离选项（如果题目中包含选项）
        清理内容 = self._分离题目和选项(清理内容)
        
        # 6. 去除多余的空格和标点
        清理内容 = re.sub(r'\s+', ' ', 清理内容).strip()
        
        # 7. 去除末尾可能残留的标点
        清理内容 = re.sub(r'[：:]\s*$', '', 清理内容)
        
        return 清理内容
    
    def _分离题目和选项(self, 题目内容):
        """从题目中分离出选项"""
        import re
        
        # 查找选项模式：A、内容B、内容C、内容D、内容
        选项模式 = r'([A-L][、\.]\s*[^A-L]*(?=[A-L][、\.]|$))'
        选项匹配 = re.findall(选项模式, 题目内容)
        
        if 选项匹配:
            # 找到选项开始的位置
            选项开始位置 = 题目内容.find(选项匹配[0])
            if 选项开始位置 > 0:
                # 分离题目和选项
                纯题目 = 题目内容[:选项开始位置].strip()
                return 纯题目
        
        return 题目内容
    
    def _从题目中提取选项(self, 题目内容):
        """从题目中提取选项"""
        import re
        
        选项数据 = {}
        
        # 查找选项模式：A、内容B、内容C、内容D、内容
        选项模式 = r'([A-L][、\.][^A-L]*)'
        选项匹配 = re.findall(选项模式, 题目内容)
        
        for 选项文本 in 选项匹配:
            # 提取选项字母
            选项字母 = 选项文本[0]
            # 提取选项内容（去掉开头的、或.）
            选项内容 = 选项文本[1:].strip()
            # 清理选项内容
            选项内容 = self.清理选项内容(选项内容)
            
            if 选项内容:
                选项数据[选项字母] = 选项内容
        
        return 选项数据
    
    def 清理选项内容(self, 选项内容):
        """清理选项内容，去除答案标记"""
        import re
        
        # 去除选项中的答案标记
        清理内容 = re.sub(r'\([A-Z]\)', '', 选项内容)
        清理内容 = re.sub(r'答案[：:]\s*[A-Z]', '', 清理内容)
        
        # 去除多余的空格
        清理内容 = re.sub(r'\s+', ' ', 清理内容).strip()
        
        return 清理内容
    
    def 显示题目(self):
        """显示当前题目"""
        if not self.题目列表 or self.当前题目索引 >= len(self.题目列表):
            return
        
        题目 = self.题目列表[self.当前题目索引]
        
        # 更新题目序号
        self.题目序号标签.config(
            text=f"题目 {self.当前题目索引 + 1}/{len(self.题目列表)}")
        
        # 更新题型
        self.题型标签.config(text=f"[{题目.get('type', '未知')}]")
        
        # 显示题目内容
        self.更新题目文本(题目.get('question', ''))
        
        # 清空选项框架
        for widget in self.选项框架.winfo_children():
            widget.destroy()
        
        # 根据题型显示不同的输入方式
        题型 = 题目.get('type', '未知')
        
        # 强制检查：如果有选项，就按选择题处理
        if 题目.get('options') and 题型 not in ['单选题', '多选题']:
            # 根据答案长度判断单选/多选
            answer = 题目.get('answer', '')
            if len(answer) > 1 and all(c in 'ABCDEF' for c in answer.upper()):
                题型 = '多选题'
            else:
                题型 = '单选题'
            # 更新题型显示
            self.题型标签.config(text=f"[{题型}]")
        
        # 选择题：显示选项按钮
        if 题型 in ['单选题', '多选题']:
            # 检查是否有选项，如果没有则从题目中提取
            选项数据 = 题目.get('options', {})
            if not 选项数据:
                选项数据 = self._从题目中提取选项(题目.get('question', ''))
            
            if 选项数据:
                选择题框架 = tk.Frame(self.选项框架, bg=self.colors['card_bg'],
                                relief='flat', borderwidth=0)
                选择题框架.pack(fill=tk.X)
                选择题框架.configure(highlightbackground=self.colors['border'],
                               highlightthickness=1)
                
                # 添加选项按钮框架
                按钮框架 = tk.Frame(选择题框架, bg=self.colors['card_bg'])
                按钮框架.pack(fill=tk.X, padx=15, pady=10)
                
                # 根据题型显示不同的提示
                if 题型 == '单选题':
                    提示文本 = "💡 点击选项直接答题（单选题）："
                else:
                    提示文本 = "💡 点击选项选择答案，选择完成后点击确定（多选题）："
                
                ttk.Label(按钮框架, text=提示文本, 
                         font=("微软雅黑", 9), 
                         foreground=self.colors['text_secondary']).pack(anchor=tk.W)
                
                选项按钮框架 = tk.Frame(按钮框架, bg=self.colors['card_bg'])
                选项按钮框架.pack(fill=tk.BOTH, expand=True, pady=5)
                
                # 存储选项按钮引用，用于多选题状态管理
                self.选项按钮列表 = []
                
                for i, key in enumerate(sorted(选项数据.keys())):
                    选项内容 = 选项数据[key]
                    
                    # 清理选项内容，去除可能的答案标记
                    选项内容 = self.清理选项内容(选项内容)
                    选项文本 = f"{key}. {选项内容}"
                    
                    # 创建选项按钮
                    选项按钮 = tk.Button(选项按钮框架, 
                                       text=选项文本,
                                       command=lambda k=key: self.选择选项(k),
                                       font=("微软雅黑", 10),
                                       bg=self.colors['card_bg'],
                                       fg=self.colors['text'],
                                       relief='raised',
                                       borderwidth=1,
                                       highlightthickness=1,
                                       highlightbackground=self.colors['primary'],
                                       activebackground=self.colors['hover'],
                                       wraplength=400,
                                       justify=tk.LEFT,
                                       anchor=tk.W,
                                       width=50)
                    选项按钮.grid(row=i, column=0, sticky='ew', padx=5, pady=3, ipady=8)
                    
                    # 存储按钮引用
                    self.选项按钮列表.append((key, 选项按钮))
                
                # 配置网格权重，使按钮等比例缩放
                选项按钮框架.grid_columnconfigure(0, weight=1)
            
            # 多选题需要确定按钮
            if 题型 == '多选题':
                确定按钮框架 = tk.Frame(按钮框架, bg=self.colors['card_bg'])
                确定按钮框架.pack(fill=tk.X, pady=(10, 0))
                
                self.确定按钮 = tk.Button(确定按钮框架, 
                                       text="✅ 确定答案",
                                       command=self.确定多选题答案,
                                       font=("微软雅黑", 10, 'bold'),
                                       bg='#27ae60', fg='white',
                                       relief='raised', borderwidth=2,
                                       padx=30, pady=8,
                                       state='disabled')  # 初始状态为禁用
                self.确定按钮.pack(side=tk.RIGHT)
                
                # 显示已选择的答案
                self.已选答案标签 = tk.Label(确定按钮框架, 
                                         text="已选择：无",
                                         font=("微软雅黑", 9),
                                         bg=self.colors['card_bg'],
                                         fg=self.colors['text_secondary'])
                self.已选答案标签.pack(side=tk.LEFT, padx=(0, 20))
            
            # 分隔线
            tk.Frame(选择题框架, height=1, bg=self.colors['border']).pack(fill=tk.X, padx=15)
        
        # 简答题：显示大文本框
        elif 题型 == '简答题':
            简答题框架 = tk.Frame(self.选项框架, bg=self.colors['card_bg'],
                            relief='flat', borderwidth=0)
            简答题框架.pack(fill=tk.BOTH, expand=True)
            简答题框架.configure(highlightbackground=self.colors['border'],
                           highlightthickness=1)
            
            ttk.Label(简答题框架, text="📝 请在此输入您的答案：", 
                     font=("微软雅黑", 10, "bold"), 
                     foreground=self.colors['text']).pack(anchor=tk.W, padx=15, pady=(10, 5))
            
            # 简答题答案输入框
            简答题输入框架 = tk.Frame(简答题框架, bg=self.colors['card_bg'])
            简答题输入框架.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
            
            self.简答题答案框 = tk.Text(简答题输入框架, 
                                    font=("微软雅黑", 10),
                                    height=6,
                                    bg='white',
                                    fg=self.colors['text'],
                                    relief='flat',
                                    borderwidth=1,
                                    highlightthickness=1,
                                    highlightbackground=self.colors['border'],
                                    wrap=tk.WORD)
            self.简答题答案框.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # 简答题滚动条
            简答题滚动条 = ttk.Scrollbar(简答题输入框架, command=self.简答题答案框.yview)
            简答题滚动条.pack(side=tk.RIGHT, fill=tk.Y)
            self.简答题答案框.config(yscrollcommand=简答题滚动条.set)
            
            # 简答题提交按钮
            简答题按钮框架 = tk.Frame(简答题框架, bg=self.colors['card_bg'])
            简答题按钮框架.pack(fill=tk.X, padx=15, pady=(0, 10))
            
            ttk.Button(简答题按钮框架, text="📤 提交简答题答案", 
                      command=self.提交简答题答案,
                      style='Primary.TButton').pack(side=tk.LEFT)
            
            ttk.Button(简答题按钮框架, text="👁 查看标准答案", 
                      command=self.显示简答题答案,
                      style='Warning.TButton').pack(side=tk.LEFT, padx=(10, 0))
        
        # 显示选项（如果有）- 使用卡片样式和按钮
        elif 题目.get('options'):
            选项卡片 = tk.Frame(self.选项框架, bg=self.colors['card_bg'],
                            relief='flat', borderwidth=0)
            选项卡片.pack(fill=tk.X)
            选项卡片.configure(highlightbackground=self.colors['border'],
                           highlightthickness=1)
            
            # 添加选项按钮框架
            按钮框架 = tk.Frame(选项卡片, bg=self.colors['card_bg'])
            按钮框架.pack(fill=tk.X, padx=15, pady=10)
            
            ttk.Label(按钮框架, text="💡 点击选项直接答题：", 
                     font=("微软雅黑", 9), 
                     foreground=self.colors['text_secondary']).pack(anchor=tk.W)
            
            选项按钮框架 = tk.Frame(按钮框架, bg=self.colors['card_bg'])
            选项按钮框架.pack(fill=tk.BOTH, expand=True, pady=5)
            
            for i, key in enumerate(sorted(题目['options'].keys())):
                选项文本 = f"{key}. {题目['options'][key]}"
                
                # 创建选项按钮 - 使用网格布局实现等比例缩放
                选项按钮 = tk.Button(选项按钮框架, 
                                    text=选项文本,
                                    command=lambda k=key: self.选择选项(k),
                                    font=("微软雅黑", 10),
                                    bg=self.colors['card_bg'],
                                    fg=self.colors['text'],
                                    relief='raised',
                                    borderwidth=1,
                                    highlightthickness=1,
                                    highlightbackground=self.colors['primary'],
                                    activebackground=self.colors['hover'],
                                    wraplength=300,  # 减少换行长度
                                    justify=tk.LEFT,
                                    anchor=tk.W)
                选项按钮.grid(row=i, column=0, sticky='ew', padx=5, pady=3, ipady=5)
            
            # 配置网格权重，使按钮等比例缩放
            选项按钮框架.grid_columnconfigure(0, weight=1)
            
            # 分隔线
            tk.Frame(选项卡片, height=1, bg=self.colors['border']).pack(fill=tk.X, padx=15)
            
            # 显示选项内容（用于查看）
            ttk.Label(选项卡片, text="📋 选项内容：", 
                     font=("微软雅黑", 9), 
                     foreground=self.colors['text_secondary']).pack(anchor=tk.W, padx=15, pady=(10, 5))
            
            for i, key in enumerate(sorted(题目['options'].keys())):
                选项文本 = f"{key}. {题目['options'][key]}"
                选项标签 = tk.Label(选项卡片, text=选项文本, 
                                 font=("微软雅黑", 10),
                                 bg=self.colors['card_bg'],
                                 fg=self.colors['text'],
                                 anchor=tk.W,
                                 padx=15,
                                 pady=2)
                选项标签.pack(fill=tk.X)
                
                # 添加分隔线（除最后一项）
                if i < len(题目['options']) - 1:
                    tk.Frame(选项卡片, height=1, bg=self.colors['border']).pack(fill=tk.X, padx=15)
        
        # 动态显示填空答案按钮
        self.更新填空答案按钮(题目)
        
        # 根据模式切换界面
        if self.模式 == "浏览":
            # 浏览模式：重置答案显示状态
            self.答案已显示 = False
            self.答案显示按钮.config(text="显示答案")
            self.正确答案标签.config(text="")
            self.反馈标签.config(text="")
            
            # 清空解析
            self.解析文本.config(state=tk.NORMAL)
            self.解析文本.delete(1.0, tk.END)
            self.解析文本.config(state=tk.DISABLED)
        else:
            # 刷题模式
            self.答案输入框.delete(0, tk.END)
            self.答案输入框.focus()
            self.反馈标签.config(text="")
            
            # 清空解析
            self.解析文本.config(state=tk.NORMAL)
            self.解析文本.delete(1.0, tk.END)
            self.解析文本.config(state=tk.DISABLED)
    
    def 提交答案(self):
        """提交答案"""
        if not self.题目列表 or self.当前题目索引 >= len(self.题目列表):
            return
        
        题目 = self.题目列表[self.当前题目索引]
        用户答案 = self.答案输入框.get().strip().upper()
        
        if not 用户答案:
            messagebox.showwarning("提示", "请输入答案！")
            return
        
        正确答案 = 题目.get('answer', '').upper()
        
        # 判断答案
        是否正确 = self.检查答案(用户答案, 正确答案, 题目.get('type', ''))
        
        # 更新统计
        if 是否正确:
            self.答对数 += 1
            self.反馈标签.config(text="✓ 回答正确！", foreground="green")
        else:
            self.答错数 += 1
            self.反馈标签.config(
                text=f"✗ 回答错误！正确答案：{题目.get('answer', '')}", 
                foreground="red")
        
        # 显示解析
        if 题目.get('explanation'):
            self.解析文本.config(state=tk.NORMAL)
            self.解析文本.delete(1.0, tk.END)
            self.解析文本.insert(1.0, 题目.get('explanation', ''))
            self.解析文本.config(state=tk.DISABLED)
        
        # 记录答题（使用刷题引擎的记录功能）
        if hasattr(self, '当前引擎'):
            self.当前引擎.record_answer(题目, 用户答案, 是否正确)
        
        # 使用增强的错题记忆功能
        if not 是否正确:
            # 添加到错题记忆
            错误原因 = f"用户答案：{用户答案}，正确答案：{正确答案}"
            self.错题记忆管理器.添加错题(题目, self.当前题库, 用户答案, 错误原因)
        else:
            # 如果答对了，记录复习结果
            self.错题记忆管理器.记录复习(题目, True)
        
        # 更新题目状态
        if 是否正确:
            self.题目状态[self.当前题目索引] = 'correct'
        else:
            self.题目状态[self.当前题目索引] = 'wrong'
        
        # 记录今日答题
        self.记录今日答题()
        
        self.更新统计显示()
        
        # 更新题目列表颜色标记
        self.更新题目列表颜色()
        
        # 自动保存进度
        self.自动保存进度()
        
        # 自动跳转到下一题（1秒后）
        self.after(1500, self.下一题)
    
    def 检查答案(self, 用户答案, 正确答案, 题型):
        """检查答案是否正确"""
        try:
            # 标准化答案格式
            用户答案 = self.标准化答案格式(用户答案)
            正确答案 = self.标准化答案格式(正确答案)
            
            # 判断题特殊处理
            if 题型 == '判断题':
                用户答案 = self.标准化判断答案(用户答案)
                正确答案 = self.标准化判断答案(正确答案)
            
            # 多选题：顺序无关
            if 题型 == '多选题':
                # 标准化多选题答案
                用户答案 = self.标准化多选题答案(用户答案)
                正确答案 = self.标准化多选题答案(正确答案)
                return set(用户答案) == set(正确答案)
            
            # 简答题：模糊匹配（包含关键词即可）
            if 题型 == '简答题':
                return self.简答题匹配(用户答案, 正确答案)
            
            return 用户答案 == 正确答案
        except Exception as e:
            print(f"检查答案时出错: {e}")
            return False
    
    def 简答题匹配(self, 用户答案, 正确答案):
        """简答题模糊匹配"""
        if not 用户答案 or not 正确答案:
            return False
        
        # 转换为小写进行比较
        用户答案 = 用户答案.lower().strip()
        正确答案 = 正确答案.lower().strip()
        
        # 完全匹配
        if 用户答案 == 正确答案:
            return True
        
        # 关键词匹配 - 检查用户答案是否包含正确答案的主要关键词
        import re
        
        # 提取关键词（去除标点符号）
        关键词列表 = re.findall(r'[\u4e00-\u9fff]+', 正确答案)
        
        if 关键词列表:
            # 如果用户答案包含大部分关键词，认为正确
            匹配关键词数 = sum(1 for 关键词 in 关键词列表 if 关键词 in 用户答案)
            匹配率 = 匹配关键词数 / len(关键词列表)
            
            # 匹配率超过60%认为正确
            return 匹配率 >= 0.6
        
        return False
    
    def 提交简答题答案(self):
        """提交简答题答案"""
        if not hasattr(self, '简答题答案框'):
            return
        
        用户答案 = self.简答题答案框.get(1.0, tk.END).strip()
        if not 用户答案:
            messagebox.showwarning("提示", "请输入答案")
            return
        
        self.提交答案(用户答案)
    
    def 显示简答题答案(self):
        """显示简答题标准答案（修复版）"""
        if not self.题目列表 or self.当前题目索引 >= len(self.题目列表):
            return
        
        题目 = self.题目列表[self.当前题目索引]
        正确答案 = 题目.get('answer', '')
        
        if not 正确答案:
            messagebox.showinfo("提示", "该题目没有标准答案")
            return
        
        # 创建答案显示窗口
        答案窗口 = tk.Toplevel(self)
        答案窗口.title("标准答案")
        答案窗口.geometry("700x500")
        答案窗口.configure(bg=self.colors['background'])
        
        # 设置窗口居中
        答案窗口.transient(self)
        答案窗口.grab_set()
        
        # 题目标题
        题目框架 = tk.Frame(答案窗口, bg=self.colors['card_bg'], relief='flat', bd=1)
        题目框架.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(题目框架, text="📋 题目", 
                font=("微软雅黑", 12, "bold"),
                bg=self.colors['card_bg'],
                fg=self.colors['text']).pack(pady=(10, 5))
        
        题目内容 = tk.Text(题目框架, 
                        font=("微软雅黑", 10),
                        wrap=tk.WORD,
                        height=4,
                        bg=self.colors['card_bg'],
                        fg=self.colors['text'],
                        relief='flat',
                        borderwidth=0)
        题目内容.pack(fill=tk.X, padx=10, pady=(0, 10))
        题目内容.insert(1.0, 题目.get('question', ''))
        题目内容.config(state=tk.DISABLED)
        
        # 答案标题
        答案框架 = tk.Frame(答案窗口, bg=self.colors['card_bg'], relief='flat', bd=1)
        答案框架.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        tk.Label(答案框架, text="✅ 标准答案", 
                font=("微软雅黑", 12, "bold"),
                bg=self.colors['card_bg'],
                fg=self.colors['success']).pack(pady=(10, 5))
        
        # 答案内容
        答案文本 = tk.Text(答案框架, 
                        font=("微软雅黑", 11),
                        wrap=tk.WORD,
                        bg=self.colors['card_bg'],
                        fg=self.colors['text'],
                        relief='flat',
                        borderwidth=0,
                        padx=10,
                        pady=10)
        答案文本.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 插入答案内容
        答案文本.insert(1.0, 正确答案)
        答案文本.config(state=tk.DISABLED)
        
        # 关闭按钮
        按钮框架 = tk.Frame(答案窗口, bg=self.colors['background'])
        按钮框架.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        ttk.Button(按钮框架, text="关闭", 
                  command=答案窗口.destroy).pack(side=tk.RIGHT)
    
    def 显示完整答案窗口(self, 题目, 标题="查看答案"):
        """显示完整的答案窗口"""
        正确答案 = 题目.get('answer', '')
        
        if not 正确答案:
            messagebox.showinfo("提示", "该题目没有标准答案")
            return
        
        # 创建完整的答案显示窗口
        答案窗口 = tk.Toplevel(self)
        答案窗口.title(标题)
        答案窗口.geometry("800x700")
        答案窗口.configure(bg=self.colors['background'])
        
        # 设置窗口居中
        答案窗口.transient(self)
        答案窗口.grab_set()
        
        # 创建滚动框架
        主框架 = tk.Frame(答案窗口, bg=self.colors['background'])
        主框架.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 题目显示
        题目框架 = tk.Frame(主框架, bg=self.colors['card_bg'], relief='flat', bd=1)
        题目框架.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(题目框架, text="📋 题目", 
                font=("微软雅黑", 14, "bold"),
                bg=self.colors['card_bg'],
                fg=self.colors['text']).pack(pady=(15, 10))
        
        题目内容 = tk.Text(题目框架, 
                        font=("微软雅黑", 11),
                        wrap=tk.WORD,
                        height=6,
                        bg=self.colors['card_bg'],
                        fg=self.colors['text'],
                        relief='flat',
                        borderwidth=0,
                        padx=15,
                        pady=10)
        题目内容.pack(fill=tk.X, padx=15, pady=(0, 15))
        题目内容.insert(1.0, 题目.get('question', ''))
        题目内容.config(state=tk.DISABLED)
        
        # 选项显示（如果有）
        if 题目.get('options'):
            选项框架 = tk.Frame(主框架, bg=self.colors['card_bg'], relief='flat', bd=1)
            选项框架.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(选项框架, text="📝 选项", 
                    font=("微软雅黑", 14, "bold"),
                    bg=self.colors['card_bg'],
                    fg=self.colors['text']).pack(pady=(15, 10))
            
            选项内容框架 = tk.Frame(选项框架, bg=self.colors['card_bg'])
            选项内容框架.pack(fill=tk.X, padx=15, pady=(0, 15))
            
            for key, value in sorted(题目['options'].items()):
                选项标签 = tk.Label(选项内容框架, 
                                 text=f"{key}. {value}",
                                 font=("微软雅黑", 11),
                                 bg=self.colors['card_bg'],
                                 fg=self.colors['text'],
                                 anchor='w',
                                 justify='left',
                                 wraplength=700)
                选项标签.pack(fill=tk.X, pady=3)
        
        # 答案显示
        答案框架 = tk.Frame(主框架, bg=self.colors['card_bg'], relief='flat', bd=1)
        答案框架.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(答案框架, text="✅ 正确答案", 
                font=("微软雅黑", 14, "bold"),
                bg=self.colors['card_bg'],
                fg=self.colors['success']).pack(pady=(15, 10))
        
        答案文本 = tk.Text(答案框架, 
                        font=("微软雅黑", 12, "bold"),
                        wrap=tk.WORD,
                        height=4,
                        bg=self.colors['card_bg'],
                        fg=self.colors['success'],
                        relief='flat',
                        borderwidth=0,
                        padx=15,
                        pady=10)
        答案文本.pack(fill=tk.X, padx=15, pady=(0, 15))
        答案文本.insert(1.0, 正确答案)
        答案文本.config(state=tk.DISABLED)
        
        # 解析显示（如果有）
        解析内容 = 题目.get('explanation', '')
        if 解析内容:
            解析框架 = tk.Frame(主框架, bg=self.colors['card_bg'], relief='flat', bd=1)
            解析框架.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(解析框架, text="💡 题目解析", 
                    font=("微软雅黑", 14, "bold"),
                    bg=self.colors['card_bg'],
                    fg=self.colors['text']).pack(pady=(15, 10))
            
            解析文本 = tk.Text(解析框架, 
                            font=("微软雅黑", 11),
                            wrap=tk.WORD,
                            height=5,
                            bg=self.colors['card_bg'],
                            fg=self.colors['text'],
                            relief='flat',
                            borderwidth=0,
                            padx=15,
                            pady=10)
            解析文本.pack(fill=tk.X, padx=15, pady=(0, 15))
            解析文本.insert(1.0, 解析内容)
            解析文本.config(state=tk.DISABLED)
        
        # 按钮框架
        按钮框架 = tk.Frame(主框架, bg=self.colors['background'])
        按钮框架.pack(fill=tk.X, pady=10)
        
        ttk.Button(按钮框架, text="关闭", 
                  command=答案窗口.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(按钮框架, text="下一题", 
                  command=lambda: [答案窗口.destroy(), self.下一题()]).pack(side=tk.RIGHT)
    
    def 标准化答案格式(self, 答案):
        """标准化答案格式，支持多种输入格式"""
        try:
            if not 答案:
                return ''
            
            答案 = str(答案).strip()
            
            # 处理括号格式：(a), (A), (1) 等
            import re
            括号匹配 = re.match(r'\(([^)]+)\)', 答案)
            if 括号匹配:
                答案 = 括号匹配.group(1)
            
            # 处理点号格式：a., A., 1. 等
            点号匹配 = re.match(r'([^.]+)\.', 答案)
            if 点号匹配:
                答案 = 点号匹配.group(1)
            
            # 处理中文括号格式：（a）、（A）、（1）等
            中文括号匹配 = re.match(r'（([^）]+)）', 答案)
            if 中文括号匹配:
                答案 = 中文括号匹配.group(1)
            
            # 处理中文逗号格式：A、B、C等
            中文逗号匹配 = re.match(r'([^、]+)、', 答案)
            if 中文逗号匹配:
                答案 = 中文逗号匹配.group(1)
            
            # 处理数字格式：1, 2, 3等
            if 答案.isdigit():
                数字 = int(答案)
                if 1 <= 数字 <= 26:
                    答案 = chr(ord('A') + 数字 - 1)
            
            # 转换为大写
            答案 = 答案.upper()
            
            return 答案
        except Exception as e:
            print(f"标准化答案格式时出错: {e}, 输入答案: {答案}")
            return str(答案) if 答案 else ''
    
    def 标准化判断答案(self, 答案):
        """标准化判断题答案"""
        try:
            答案 = 答案.upper()
            if 答案 in ['对', '√', 'T', 'TRUE', '正确', 'Y', 'YES']:
                return '对'
            if 答案 in ['错', '×', 'X', 'F', 'FALSE', '错误', 'N', 'NO']:
                return '错'
            return 答案
        except Exception as e:
            print(f"标准化判断答案时出错: {e}, 输入答案: {答案}")
            return str(答案) if 答案 else ''
    
    def 标准化多选题答案(self, 答案):
        """标准化多选题答案格式"""
        try:
            if not 答案:
                return ''
            
            import re
            # 移除空格和特殊字符，只保留字母
            答案 = re.sub(r'[^A-Za-z]', '', str(答案).upper())
            
            # 去重并排序
            答案列表 = list(set(答案))
            答案列表.sort()
            
            return ''.join(答案列表)
        except Exception as e:
            print(f"标准化多选题答案时出错: {e}, 输入答案: {答案}")
            return str(答案) if 答案 else ''
    
    def 跳过题目(self):
        """跳过当前题目"""
        self.下一题()
    
    def 看答案并记错题(self):
        """点击'不会-看答案'按钮，显示答案并记为错题（修复版）"""
        if not self.题目列表 or self.当前题目索引 >= len(self.题目列表):
            return
        
        题目 = self.题目列表[self.当前题目索引]
        正确答案 = 题目.get('answer', '')
        
        # 调用完整的答案显示窗口
        self.显示完整答案窗口(题目, "查看答案")
        
        # 记为错题（使用增强的错题记忆功能）
        错误原因 = "用户主动查看答案"
        self.错题记忆管理器.添加错题(题目, self.当前题库, '', 错误原因)
        
        # 更新统计
        self.答错数 += 1
        self.题目状态[self.当前题目索引] = 'wrong'
        self.更新统计显示()
    
    def 上一题(self):
        """上一题"""
        # 清理多选题状态
        self.清理多选题状态()
        
        if self.当前题目索引 > 0:
            self.当前题目索引 -= 1
            self.切换题目时保存()  # 保存进度
            self.显示题目()
    
    def 下一题(self):
        """下一题"""
        # 清理多选题状态
        self.清理多选题状态()
        
        if self.当前题目索引 < len(self.题目列表) - 1:
            self.当前题目索引 += 1
            self.切换题目时保存()  # 保存进度
            self.显示题目()
        else:
            # 已经是最后一题
            if self.模式 == "浏览":
                # 浏览模式：简单提示
                if messagebox.askyesno("完成", 
                                      f"已浏览完所有题目！\n\n是否重新开始？"):
                    self.当前题目索引 = 0
                    self.显示题目()
            else:
                # 刷题模式：显示统计
                已答 = self.答对数 + self.答错数
                if 已答 > 0:
                    if messagebox.askyesno("完成", 
                                          f"已完成所有题目！\n\n"
                                          f"答对：{self.答对数}\n"
                                          f"答错：{self.答错数}\n"
                                          f"正确率：{self.答对数/已答*100:.1f}%\n\n"
                                          f"是否重新开始？"):
                        self.当前题目索引 = 0
                        if self.模式 == "随机":
                            random.shuffle(self.题目列表)
                        self.答对数 = 0
                        self.答错数 = 0
                        self.显示题目()
                        self.更新统计显示()
                else:
                    messagebox.showinfo("提示", "已到最后一题")
    
    def 滑动栏跳转题目(self, value):
        """滑动栏跳转题目"""
        if not self.题目列表:
            return
        
        try:
            题目索引 = int(value) - 1
            if 0 <= 题目索引 < len(self.题目列表):
                self.当前题目索引 = 题目索引
                self.显示题目()
                self.更新题目列表颜色()
                # 更新滑动栏数值显示
                self.滑动栏数值标签.config(text=f"{int(value)}/{len(self.题目列表)}")
        except (ValueError, IndexError):
            pass
    
    def 更新滑动栏(self):
        """更新滑动栏范围"""
        if not self.题目列表:
            self.题目滑动栏.config(from_=1, to=1)
            self.滑动栏数值标签.config(text="1/1")
        else:
            题目总数 = len(self.题目列表)
            self.题目滑动栏.config(from_=1, to=题目总数)
            self.题目滑动栏.set(self.当前题目索引 + 1)
            self.滑动栏数值标签.config(text=f"{self.当前题目索引 + 1}/{题目总数}")
    
    def 跳转题目(self):
        """跳转到指定题目"""
        try:
            目标序号 = int(self.跳转输入框.get().strip())
            if 1 <= 目标序号 <= len(self.题目列表):
                self.当前题目索引 = 目标序号 - 1
                self.显示题目()
                self.跳转输入框.delete(0, tk.END)
            else:
                messagebox.showwarning("提示", 
                                     f"题号超出范围！\n请输入 1-{len(self.题目列表)} 之间的数字")
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的题号！")
    
    def 结束刷题(self):
        """结束刷题"""
        if self.题目列表 and (self.答对数 + self.答错数) > 0:
            messagebox.showinfo("本次刷题总结",
                              f"已答题数：{self.答对数 + self.答错数}\n"
                              f"答对：{self.答对数}\n"
                              f"答错：{self.答错数}\n"
                              f"正确率：{self.答对数/(self.答对数+self.答错数)*100:.1f}%")
        
        self.题目列表 = []
        self.当前题目索引 = 0
        self.答对数 = 0
        self.答错数 = 0
        self.更新统计显示()
        
        # 清空显示
        self.更新题目文本('请选择题库并点击"开始刷题"')
    
    def 更新统计显示(self):
        """更新统计显示"""
        已答 = self.答对数 + self.答错数
        正确率 = (self.答对数 / 已答 * 100) if 已答 > 0 else 0
        
        self.统计标签['已答'].config(text=f"{已答}")
        self.统计标签['正确'].config(text=f"{self.答对数}")
        self.统计标签['错误'].config(text=f"{self.答错数}")
        self.统计标签['正确率'].config(text=f"{正确率:.0f}%")
        
        # 更新题目列表显示（刷新颜色）
        self.更新题目列表显示()
        
        # 高亮当前题目
        if self.题目列表:
            self.题目列表框.selection_clear(0, tk.END)
            self.题目列表框.selection_set(self.当前题目索引)
            self.题目列表框.see(self.当前题目索引)
        
        # 更新收藏按钮状态
        if self.当前题目索引 in self.收藏题目:
            self.收藏按钮.config(text="★ 已收藏")
        else:
            self.收藏按钮.config(text="☆ 收藏")
    
    def 刷新题库(self):
        """刷新题库列表"""
        self.题库管理器.refresh()
        self.加载题库列表()
        messagebox.showinfo("提示", "题库列表已刷新！")
    
    def 导入题库(self):
        """导入题库文件（直接支持Word/Excel/PDF）"""
        try:
            from tkinter import filedialog
            
            # 选择文件
            文件路径 = filedialog.askopenfilename(
                title="选择题库文件",
                filetypes=[
                    ("所有支持格式", "*.docx;*.xlsx;*.pdf"),
                    ("Word文档", "*.docx"),
                    ("Excel表格", "*.xlsx"),
                    ("PDF文档", "*.pdf"),
                    ("所有文件", "*.*")
                ]
            )
            
            if not 文件路径:
                return
            
            # 直接复制到题库文件夹
            import shutil
            from pathlib import Path
            
            目标路径 = Path("题库") / Path(文件路径).name
            
            try:
                shutil.copy2(文件路径, 目标路径)
                messagebox.showinfo("成功", f"题库文件已导入：\n{目标路径.name}")
                
                # 刷新题库列表
                self.刷新题库()
                
            except Exception as e:
                messagebox.showerror("错误", f"导入失败：\n{e}")
                
        except Exception as e:
            messagebox.showerror("错误", f"导入功能出错：\n{e}")
    
    def 加载新题库(self, 标准文件路径):
        """加载新导入的题库"""
        try:
            if 标准文件路径 and Path(标准文件路径).exists():
                # 加载新题库
                self.题目列表 = self.题库管理器.load_tiku(标准文件路径)
                self.当前题库 = Path(标准文件路径).stem
                self.当前题目索引 = 0
                
                # 更新界面
                self.更新题目列表显示()
                self.显示题目()
                
                # 刷新题库列表
                self.刷新题库列表()
                
                messagebox.showinfo("提示", 
                                  f"已自动加载题库：{self.当前题库}\n"
                                  f"共 {len(self.题目列表)} 道题")
        except Exception as e:
            messagebox.showerror("错误", f"加载新题库失败：\n{e}")
    
    def 打开Word转换界面(self):
        """打开Word转换界面"""
        try:
            from tkinter import filedialog
            from Word题库转换工具 import word_to_excel
            
            # 选择Word文件
            word_file = filedialog.askopenfilename(
                title="选择Word题库文件",
                filetypes=[("Word文档", "*.docx"), ("所有文件", "*.*")]
            )
            
            if word_file:
                # 选择保存位置
                excel_file = filedialog.asksaveasfilename(
                    title="保存Excel文件",
                    defaultextension=".xlsx",
                    filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
                )
                
                if excel_file:
                    # 执行转换
                    result = word_to_excel(word_file, excel_file)
                    if result:
                        messagebox.showinfo("成功", f"转换完成！\n保存位置：{excel_file}")
                    else:
                        messagebox.showerror("错误", "转换失败，请检查文件格式")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开Word转换界面：\n{e}")
    
    def Word转换(self):
        """Word转Excel（保留原方法以兼容）"""
        self.打开Word转换界面()
    
    def 打开PDF转换界面(self):
        """打开PDF转换界面"""
        try:
            from tkinter import filedialog
            from PDF题库转换工具 import pdf_to_excel
            
            # 选择PDF文件
            pdf_file = filedialog.askopenfilename(
                title="选择PDF题库文件",
                filetypes=[("PDF文档", "*.pdf"), ("所有文件", "*.*")]
            )
            
            if pdf_file:
                # 选择保存位置
                excel_file = filedialog.asksaveasfilename(
                    title="保存Excel文件",
                    defaultextension=".xlsx",
                    filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
                )
                
                if excel_file:
                    # 执行转换
                    result = pdf_to_excel(pdf_file, excel_file)
                    if result:
                        messagebox.showinfo("成功", f"转换完成！\n保存位置：{excel_file}")
                    else:
                        messagebox.showerror("错误", "转换失败，请检查文件格式")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开PDF转换界面：\n{e}")
    
    def PDF转换(self):
        """PDF转Excel（保留原方法以兼容）"""
        self.打开PDF转换界面()
    
    def 打开题型识别管理(self):
        """打开题型识别管理界面"""
        try:
            from 题型识别管理界面 import 打开管理界面
            打开管理界面(self)
        except Exception as e:
            messagebox.showerror("错误", f"打开管理界面失败：\n{e}")
    
    def 显示识别性能报告(self):
        """显示识别性能报告"""
        try:
            from 智能题型识别 import get_performance_report
            
            报告 = get_performance_report()
            
            if "错误" not in 报告:
                报告文本 = f"""
🧠 智能题型识别系统 - 性能报告

📊 总体统计:
• 总识别次数: {报告['总识别次数']}
• 识别成功率: {报告['成功率']}
• 平均确定度: {报告['平均确定度']}
• 平均识别耗时: {报告['平均耗时']}
• 低确定度比例: {报告['低确定度比例']}

📈 题型分布:
"""
                for 题型, 次数 in 报告['各题型分布'].items():
                    报告文本 += f"• {题型}: {次数} 次\n"
                
                # 创建报告显示窗口
                报告窗口 = tk.Toplevel(self)
                报告窗口.title("📊 识别性能报告")
                报告窗口.geometry("500x400")
                报告窗口.configure(bg=self.colors['background'])
                
                文本框 = tk.Text(报告窗口, wrap=tk.WORD, font=("微软雅黑", 10),
                               bg=self.colors['card_bg'], fg=self.colors['text'])
                文本框.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                文本框.insert(1.0, 报告文本)
                文本框.config(state=tk.DISABLED)
                
            else:
                messagebox.showinfo("提示", "暂无识别统计数据")
                
        except Exception as e:
            messagebox.showerror("错误", f"获取性能报告失败：\n{e}")
    
    def 查看统计(self):
        analyzer = StatsAnalyzer()
        
        # 创建统计窗口
        统计窗口 = tk.Toplevel(self)
        统计窗口.title("答题统计")
        统计窗口.geometry("600x400")
        
        # 创建文本框显示统计
        text = tk.Text(统计窗口, wrap=tk.WORD, font=("微软雅黑", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(统计窗口, command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)
        
        # 获取统计信息（重定向输出）
        import io
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        try:
            analyzer.show_statistics()
            统计文本 = buffer.getvalue()
            text.insert(1.0, 统计文本)
        finally:
            sys.stdout = old_stdout
        
        text.config(state=tk.DISABLED)
    
    def 清空错题本(self):
        """清空错题本"""
        if messagebox.askyesno("确认", "确定要清空错题本吗？"):
            错题文件 = Path(__file__).parent / '.data' / 'wrong_questions.json'
            if 错题文件.exists():
                错题文件.unlink()
                messagebox.showinfo("成功", "错题本已清空！")
            else:
                messagebox.showinfo("提示", "错题本已经是空的！")
    
    def 查看收藏(self):
        """查看收藏的题目"""
        if not self.收藏题目:
            messagebox.showinfo("收藏题目", "还没有收藏任何题目")
            return
        
        # 创建收藏列表窗口
        收藏窗口 = tk.Toplevel(self)
        收藏窗口.title("收藏的题目")
        收藏窗口.geometry("600x400")
        
        ttk.Label(收藏窗口, text=f"共收藏 {len(self.收藏题目)} 道题目", 
                 font=("微软雅黑", 11, "bold")).pack(pady=10)
        
        # 创建列表框
        列表框架 = ttk.Frame(收藏窗口)
        列表框架.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        滚动条 = ttk.Scrollbar(列表框架)
        滚动条.pack(side=tk.RIGHT, fill=tk.Y)
        
        收藏列表 = tk.Listbox(列表框架, font=("微软雅黑", 10),
                           yscrollcommand=滚动条.set)
        收藏列表.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        滚动条.config(command=收藏列表.yview)
        
        # 填充收藏题目
        for idx in sorted(self.收藏题目):
            if idx < len(self.题目列表):
                题目 = self.题目列表[idx]
                显示 = f"{idx+1}. {题目.get('question', '')[:50]}..."
                收藏列表.insert(tk.END, 显示)
        
        # 双击跳转
        def 跳转到题目(event):
            selection = 收藏列表.curselection()
            if selection:
                显示文本 = 收藏列表.get(selection[0])
                序号 = int(显示文本.split('.')[0])
                self.当前题目索引 = 序号 - 1
                self.显示题目()
                收藏窗口.destroy()
        
        收藏列表.bind('<Double-Button-1>', 跳转到题目)
        
        ttk.Button(收藏窗口, text="关闭", 
                  command=收藏窗口.destroy).pack(pady=10)
    
    def 导入题库引导(self):
        """导入题库引导功能"""
        引导窗口 = tk.Toplevel(self)
        引导窗口.title("导入题库引导")
        引导窗口.geometry("700x600")
        引导窗口.resizable(False, False)
        引导窗口.transient(self)
        引导窗口.grab_set()
        
        # 居中显示
        引导窗口.update_idletasks()
        x = (引导窗口.winfo_screenwidth() // 2) - (700 // 2)
        y = (引导窗口.winfo_screenheight() // 2) - (600 // 2)
        引导窗口.geometry(f"700x600+{x}+{y}")
        
        # 主框架
        主框架 = tk.Frame(引导窗口, bg=self.colors['card_bg'])
        主框架.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        tk.Label(主框架, text="📚 导入题库引导", 
                font=("微软雅黑", 18, "bold"),
                bg=self.colors['card_bg'],
                fg=self.colors['primary']).pack(pady=(0, 20))
        
        # 步骤框架
        步骤框架 = tk.Frame(主框架, bg=self.colors['card_bg'])
        步骤框架.pack(fill=tk.BOTH, expand=True)
        
        # 步骤1：选择文件格式
        步骤1框架 = tk.LabelFrame(步骤框架, text="步骤1: 选择文件格式", 
                                  font=("微软雅黑", 12, "bold"),
                                  bg=self.colors['card_bg'],
                                  fg=self.colors['text'])
        步骤1框架.pack(fill=tk.X, pady=(0, 15))
        
        格式说明 = tk.Text(步骤1框架, height=4, width=70,
                         font=("微软雅黑", 10),
                         bg='white', fg='black', relief='sunken', borderwidth=1)
        格式说明.pack(fill=tk.X, padx=10, pady=10)
        格式说明.insert(tk.END, """支持的文件格式：
• Excel文件 (.xlsx) - 推荐格式，支持完整的题目、选项、答案、解析
• Word文件 (.docx) - 支持表格格式的题库
• PDF文件 (.pdf) - 仅支持文本型PDF，扫描版需要OCR处理""")
        格式说明.config(state=tk.DISABLED)
        
        # 步骤2：准备文件
        步骤2框架 = tk.LabelFrame(步骤框架, text="步骤2: 准备文件", 
                                  font=("微软雅黑", 12, "bold"),
                                  bg=self.colors['card_bg'],
                                  fg=self.colors['text'])
        步骤2框架.pack(fill=tk.X, pady=(0, 15))
        
        准备说明 = tk.Text(步骤2框架, height=6, width=70,
                         font=("微软雅黑", 10),
                         bg='white', fg='black', relief='sunken', borderwidth=1)
        准备说明.pack(fill=tk.X, padx=10, pady=10)
        准备说明.insert(tk.END, """Excel格式要求：
• 第一行：表头（题目、答案、选项A、选项B、选项C、选项D、题型、解析）
• 题目列：包含题目内容
• 答案列：包含正确答案
• 选项列：包含各选项内容（可选）
• 题型列：题目类型（单选题、多选题、判断题、填空题、简答题）
• 解析列：题目解析（可选）

Word格式要求：
• 使用表格格式
• 每行一道题目
• 包含题目、答案等信息

PDF格式要求：
• 文本型PDF（非扫描版）
• 题目格式规范
• 包含选项和答案""")
        准备说明.config(state=tk.DISABLED)
        
        # 步骤3：导入操作
        步骤3框架 = tk.LabelFrame(步骤框架, text="步骤3: 导入操作", 
                                  font=("微软雅黑", 12, "bold"),
                                  bg=self.colors['card_bg'],
                                  fg=self.colors['text'])
        步骤3框架.pack(fill=tk.X, pady=(0, 15))
        
        操作说明 = tk.Text(步骤3框架, height=4, width=70,
                         font=("微软雅黑", 10),
                         bg='white', fg='black', relief='sunken', borderwidth=1)
        操作说明.pack(fill=tk.X, padx=10, pady=10)
        操作说明.insert(tk.END, """导入方法：
1. 将题库文件放入"题库"文件夹
2. 点击"刷新题库列表"按钮
3. 在题库列表中选择要使用的题库
4. 点击"开始学习"开始刷题

注意事项：
• 确保文件格式正确
• 检查题目内容是否完整
• 建议先测试少量题目""")
        操作说明.config(state=tk.DISABLED)
        
        # 按钮框架
        按钮框架 = tk.Frame(主框架, bg=self.colors['card_bg'])
        按钮框架.pack(fill=tk.X, pady=(20, 0))
        
        def 打开题库文件夹():
            import os
            import subprocess
            题库路径 = os.path.join(os.path.dirname(__file__), '题库')
            if os.path.exists(题库路径):
                subprocess.Popen(f'explorer "{题库路径}"')
            else:
                messagebox.showwarning("提示", "题库文件夹不存在！")
        
        def 刷新题库列表():
            self.刷新题库()
            引导窗口.destroy()
            messagebox.showinfo("提示", "题库列表已刷新！")
        
        ttk.Button(按钮框架, text="📁 打开题库文件夹", 
                  command=打开题库文件夹,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(按钮框架, text="🔄 刷新题库列表", 
                  command=刷新题库列表).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(按钮框架, text="关闭", 
                  command=引导窗口.destroy).pack(side=tk.RIGHT)
    
    # 删除复杂的高级设置，使用简单功能
    
    # 删除复杂的UI布局设置，使用简单布局
    
    def 自定义字体(self):
        """打开字体自定义对话框 - 简化版本"""
        字体窗口 = tk.Toplevel(self)
        字体窗口.title("字体设置")
        字体窗口.geometry("300x200")
        字体窗口.resizable(False, False)
        字体窗口.transient(self)
        字体窗口.grab_set()
        
        # 居中显示
        字体窗口.update_idletasks()
        x = (字体窗口.winfo_screenwidth() // 2) - (300 // 2)
        y = (字体窗口.winfo_screenheight() // 2) - (200 // 2)
        字体窗口.geometry(f"300x200+{x}+{y}")
        
        # 主框架
        主框架 = tk.Frame(字体窗口, bg=self.colors['card_bg'])
        主框架.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        tk.Label(主框架, text="🎨 字体设置", 
                font=("微软雅黑", 14, "bold"),
                bg=self.colors['card_bg'],
                fg=self.colors['primary']).pack(pady=(0, 15))
        
        # 字体大小选择
        字体大小框架 = tk.Frame(主框架, bg=self.colors['card_bg'])
        字体大小框架.pack(fill=tk.X, pady=10)
        
        tk.Label(字体大小框架, text="字体大小:", 
                font=("微软雅黑", 10),
                bg=self.colors['card_bg'],
                fg=self.colors['text']).pack(side=tk.LEFT)
        
        字体大小变量 = tk.StringVar(value="10")
        字体大小选择 = ttk.Combobox(字体大小框架, textvariable=字体大小变量,
                                values=['8', '9', '10', '11', '12', '13', '14', '15', '16'],
                                state='readonly', width=10)
        字体大小选择.pack(side=tk.RIGHT)
        
        # 按钮框架
        按钮框架 = tk.Frame(主框架, bg=self.colors['card_bg'])
        按钮框架.pack(fill=tk.X, pady=(20, 0))
        
        def 应用字体设置():
            新字体大小 = int(字体大小变量.get())
            # 直接更新主要组件
            if hasattr(self, '题目文本'):
                self.题目文本.configure(font=("微软雅黑", 新字体大小))
            if hasattr(self, '题目列表框'):
                self.题目列表框.configure(font=("微软雅黑", 新字体大小))
            if hasattr(self, '题库列表框'):
                self.题库列表框.configure(font=("微软雅黑", 新字体大小))
            
            字体窗口.destroy()
            messagebox.showinfo("提示", f"字体大小已设置为 {新字体大小} 号")
        
        ttk.Button(按钮框架, text="应用", 
                  command=应用字体设置,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(按钮框架, text="取消", 
                  command=字体窗口.destroy).pack(side=tk.RIGHT)
    
    def 应用字体设置(self):
        """应用字体设置到所有组件"""
        try:
            # 更新所有文本组件的字体
            self.递归更新字体(self)
        except Exception as e:
            print(f"应用字体设置失败: {e}")
    
    def 递归更新字体(self, widget):
        """递归更新组件字体"""
        try:
            widget_type = widget.winfo_class()
            
            if widget_type in ['Label', 'Button', 'Text', 'Entry', 'Listbox']:
                if hasattr(widget, 'configure'):
                    try:
                        widget.configure(font=(self.字体设置['family'], 
                                             self.字体设置['size'], 
                                             self.字体设置['weight']))
                    except:
                        pass
            
            # 递归处理子组件
            for child in widget.winfo_children():
                self.递归更新字体(child)
                
        except Exception as e:
            pass
    
    def 放大字体(self):
        """放大字体"""
        self.字体缩放比例 = min(2.0, self.字体缩放比例 + 0.1)
        self.应用字体缩放()
    
    def 缩小字体(self):
        """缩小字体"""
        self.字体缩放比例 = max(0.5, self.字体缩放比例 - 0.1)
        self.应用字体缩放()
    
    def 重置字体(self):
        """重置字体"""
        self.字体缩放比例 = 1.0
        self.应用字体缩放()
    
    def 强制缩放(self):
        """强制缩放"""
        try:
            import ctypes
            # 设置DPI感知
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            messagebox.showinfo("强制缩放", "已启用强制DPI缩放")
        except:
            messagebox.showwarning("强制缩放", "强制缩放功能不可用")
    
    def 自适应缩放(self):
        """自适应缩放"""
        try:
            import ctypes
            # 禁用DPI感知
            ctypes.windll.shcore.SetProcessDpiAwareness(0)
            messagebox.showinfo("自适应缩放", "已启用自适应缩放")
        except:
            messagebox.showwarning("自适应缩放", "自适应缩放功能不可用")
    
    def 应用字体缩放(self):
        """应用字体缩放 - 简化版本"""
        try:
            # 只更新主要组件的字体
            if hasattr(self, '题目文本'):
                新字体大小 = int(12 * self.字体缩放比例)
                self.题目文本.configure(font=("微软雅黑", 新字体大小))
            
            if hasattr(self, '题目列表框'):
                新字体大小 = int(9 * self.字体缩放比例)
                self.题目列表框.configure(font=("微软雅黑", 新字体大小))
            
            if hasattr(self, '题库列表框'):
                新字体大小 = int(9 * self.字体缩放比例)
                self.题库列表框.configure(font=("微软雅黑", 新字体大小))
                
        except Exception as e:
            print(f"应用字体缩放失败: {e}")
    
    def 新手引导(self):
        """显示新手引导"""
        引导内容 = """📖 安规刷题系统 - 快速上手指南

🎯 第一步：导入题库
  将题库文件（Excel/Word/PDF）放入"题库"文件夹
  点击左侧的题库名称选择要学习的题库

📝 第二步：选择学习模式
  • 顺序刷题：按顺序练习
  • 随机刷题：随机打乱
  • 错题练习：专门练习错题
  • 浏览模式：快速浏览

✏️ 第三步：开始答题
  • 单选题：直接点击选项
  • 多选题：点击多个选项后点"确定答案"
  • 判断题：点击"对"或"错"
  • 填空题：输入答案或点"显示填空答案"

🔍 高级功能：
  • 搜索：输入关键词搜索题目
  • 收藏：标记重要题目
  • 统计：查看学习进度和正确率
  • 错题记录：自动记录错题供复习

💡 提示：
  使用菜单栏可以转换PDF/Word题库为Excel格式
  点击"帮助"查看更多使用说明"""
        
        messagebox.showinfo("新手引导", 引导内容)
    
    def 显示使用指南(self):
        """显示使用指南"""
        指南内容 = """📖 安规刷题系统使用指南

🎯 快速开始：
1. 将题库文件放入"题库"文件夹
2. 点击"刷新题库列表"
3. 选择题库和学习模式
4. 点击"开始刷题"

📚 支持的题库格式：
• Excel文件 (.xlsx) - 推荐格式
• Word文件 (.docx)
• PDF文件 (.pdf) - 需要是文本格式

🎮 学习模式：
• 顺序刷题：按顺序逐题练习
• 随机刷题：随机打乱题目
• 错题练习：专门练习错题
• 浏览模式：快速浏览题目
• 模拟考试：模拟考试环境

📝 答题方式：
• 单选题：点击选项直接答题
• 多选题：选择多个选项后点击确定
• 判断题：点击对/错按钮
• 填空题：输入答案或点击显示答案
• 简答题：在文本框中输入答案

🔍 高级功能：
• 搜索功能：按关键词搜索题目
• 错题记忆：自动记录和复习错题
• 学习统计：查看学习进度和正确率
• 界面定制：主题切换、字体调整、面板分离

💡 使用技巧：
• 使用搜索功能快速找到特定题目
• 定期查看错题记录进行复习
• 尝试不同学习模式找到最适合的方式
• 使用面板分离功能自定义界面布局

📞 获取帮助：
• 查看"帮助"菜单中的其他选项
• 参考完整使用文档
• 查看常见问题解答"""
        
        messagebox.showinfo("使用指南", 指南内容)
    
    def 显示常见问题(self):
        """显示常见问题"""
        问题内容 = """❓ 常见问题解答

Q1: 如何导入题库？
A: 将题库文件放入"题库"文件夹，然后点击"刷新题库列表"。

Q2: PDF转换失败怎么办？
A: 确保PDF是文本格式，不是扫描版。检查题目格式是否规范。

Q3: 多选题如何答题？
A: 点击选项进行选择（变蓝色），选择完成后点击"确定答案"。

Q4: 如何查看学习统计？
A: 在左侧面板的"统计信息"区域查看，或点击菜单"统计"。

Q5: 如何分离面板？
A: 点击面板右上角的"⊞"按钮，或使用菜单"视图" → "窗口管理"。

Q6: 程序支持哪些操作系统？
A: 主要支持Windows系统，需要Python 3.7+环境。

Q7: 如何切换主题？
A: 点击菜单"视图" → "主题" → 选择"亮色主题"或"暗色主题"。

Q8: 如何调整字体大小？
A: 点击菜单"视图" → "自定义字体"，调整字体大小。

Q9: 错题记录在哪里？
A: 错题记录保存在".data/wrong_questions.json"文件中。

Q10: 如何备份学习进度？
A: 学习进度保存在".data/user_settings.json"文件中，可以复制备份。"""
        
        messagebox.showinfo("常见问题", 问题内容)
    
    def 显示关于信息(self):
        """显示关于信息"""
        关于内容 = """ℹ️ 关于安规刷题系统

版本：v2.0
开发者：AI助手
更新日期：2024年

🎯 系统特点：
• 支持多种题库格式（Excel、Word、PDF）
• 智能题目类型识别
• 多种学习模式
• 现代化可拖拽界面
• 智能错题记忆系统
• 详细学习统计

🔧 技术信息：
• 开发语言：Python 3.7+
• GUI框架：Tkinter
• 依赖库：openpyxl, python-docx, pdfplumber

📄 许可证：
本软件仅供学习和研究使用，请勿用于商业用途。

🎉 感谢使用！"""
        
        messagebox.showinfo("关于", 关于内容)
    
    def 显示首次使用提示(self):
        """显示首次使用提示"""
        result = messagebox.askyesno("欢迎使用", 
                                   "欢迎使用安规刷题系统！\n\n"
                                   "这是您第一次使用本系统，是否需要查看新手引导？\n\n"
                                   "新手引导将帮助您快速了解系统功能。")
        if result:
            self.新手引导()
            # 标记已显示新手引导
            self.设置管理器.设置值('已显示新手引导', True)
    
    def 显示帮助(self):
        """显示使用说明"""
        帮助文本 = """
安规刷题系统 - 使用说明

【四种模式】
1. 顺序刷题 - 按顺序练习，需要答题
2. 随机刷题 - 打乱顺序练习，需要答题
3. 错题重做 - 专门练习错题
4. 浏览背题 - 只看题目和答案，不答题

【刷题功能】
- 提交答案：输入答案后回车或点击"提交答案"
- 不会做：点击"不会-看答案"，查看答案并记入错题
- 收藏题目：点击"☆收藏"或按Ctrl+S
- 题目列表：绿色=答对，红色=答错，★=已收藏

【浏览背题模式】
- 点击"显示答案"查看答案和解析
- 点击"隐藏答案"隐藏答案
- 使用左右方向键快速翻页

【快捷键】
- 回车：提交答案
- 空格：显示/隐藏答案（浏览模式）或看答案（刷题模式）
- ← → 方向键：上一题/下一题
- 1/2/3/4：快速选择选项（选择题）
- Ctrl+F：快速搜索
- Ctrl+S：收藏/取消收藏当前题

【题型说明】
- 单选题：输入 A/B/C/D 或按数字键1-4
- 多选题：输入 ABC/ABD 等
- 判断题：输入 对/错、T/F
- 填空题：输入答案内容
        """
        
        messagebox.showinfo("使用说明", 帮助文本)
    
    def 显示关于(self):
        """显示关于信息"""
        messagebox.showinfo("关于", 
                          "安规刷题系统 v2.0\n\n"
                          "功能特点：\n"
                          "- 支持Excel/Word/PDF题库\n"
                          "- 多种刷题模式\n"
                          "- 智能题型识别\n"
                          "- 智能错题管理\n"
                          "- 详细数据统计\n\n"
                          "遇到问题？点击'帮助' → '问题反馈'\n\n"
                          "祝你考试顺利！")
    
    def 问题反馈(self):
        """问题反馈功能"""
        反馈窗口 = tk.Toplevel(self)
        反馈窗口.title("问题反馈")
        反馈窗口.geometry("600x500")
        反馈窗口.configure(bg=self.colors['background'])
        
        # 标题
        tk.Label(反馈窗口, text="📝 问题反馈", 
                font=("微软雅黑", 16, "bold"),
                bg=self.colors['background'],
                fg=self.colors['primary']).pack(pady=20)
        
        # 说明
        说明框架 = tk.Frame(反馈窗口, bg=self.colors['card_bg'])
        说明框架.pack(fill=tk.X, padx=20, pady=10)
        
        说明文本 = """
        感谢您使用安规刷题系统！
        
        如果遇到问题或有改进建议，请通过以下方式反馈：
        
        📱 微信号：zzzaaatom
        📧 添加微信时请注明：刷题系统反馈
        
        您的反馈将帮助我们不断改进系统！
        """
        
        tk.Label(说明框架, text=说明文本,
                font=("微软雅黑", 10),
                bg=self.colors['card_bg'],
                fg=self.colors['text'],
                justify=tk.LEFT).pack(padx=20, pady=20)
        
        # 反馈模板
        模板框架 = tk.Frame(反馈窗口, bg=self.colors['card_bg'])
        模板框架.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(模板框架, text="反馈模板（复制后发送给开发者）：",
                font=("微软雅黑", 10, "bold"),
                bg=self.colors['card_bg'],
                fg=self.colors['text']).pack(anchor=tk.W, padx=10, pady=5)
        
        模板文本 = tk.Text(模板框架,
                        font=("微软雅黑", 9),
                        bg='white',
                        fg=self.colors['text'],
                        wrap=tk.WORD)
        模板文本.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        反馈模板 = f"""
【问题反馈】安规刷题系统

问题描述：
（请详细描述您遇到的问题）

复现步骤：
1. 
2. 
3. 

期望结果：
（您期望的结果是什么）

实际结果：
（实际发生了什么）

系统信息：
- 程序版本：v2.0
- 操作系统：Windows
- 题库类型：（Excel/PDF/Word）

其他信息：
（截图或其他补充信息）

---
感谢您的反馈！
微信号：zzzaaatom
"""
        
        模板文本.insert('1.0', 反馈模板)
        模板文本.config(state=tk.NORMAL)
        
        # 按钮
        按钮框架 = tk.Frame(反馈窗口, bg=self.colors['background'])
        按钮框架.pack(fill=tk.X, padx=20, pady=10)
        
        def 复制模板():
            反馈窗口.clipboard_clear()
            反馈窗口.clipboard_append(模板文本.get('1.0', tk.END))
            messagebox.showinfo("提示", "反馈模板已复制到剪贴板！\n请打开微信粘贴发送")
        
        ttk.Button(按钮框架, text="📋 复制反馈模板", 
                  command=复制模板).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(按钮框架, text="关闭", 
                  command=反馈窗口.destroy).pack(side=tk.RIGHT, padx=5)
    
    def 切换收藏(self):
        """切换当前题目的收藏状态"""
        if not self.题目列表 or self.当前题目索引 >= len(self.题目列表):
            return
        
        if self.当前题目索引 in self.收藏题目:
            # 取消收藏
            self.收藏题目.remove(self.当前题目索引)
            self.收藏按钮.config(text="☆ 收藏")
            messagebox.showinfo("提示", "已取消收藏")
        else:
            # 添加收藏
            self.收藏题目.add(self.当前题目索引)
            self.收藏按钮.config(text="★ 已收藏")
            messagebox.showinfo("提示", "已添加到收藏")
        
        # 刷新题目列表显示
        self.更新题目列表显示()
        self.题目列表框.selection_set(self.当前题目索引)
        self.题目列表框.see(self.当前题目索引)
        
        # 保存收藏状态
        self.自动保存进度()
    
    def 快捷键_显示答案(self):
        """空格键快捷键：显示/隐藏答案"""
        if self.模式 == "浏览":
            # 浏览模式：切换答案显示
            self.切换答案显示()
        else:
            # 刷题模式：显示答案并记错题
            if self.题目列表:
                self.看答案并记错题()
        return 'break'  # 阻止空格键的默认行为
    
    def 快捷键_搜索(self):
        """Ctrl+F：聚焦到搜索框"""
        self.搜索输入框.focus()
        self.搜索输入框.select_range(0, tk.END)
        return 'break'
    
    def 快捷键_选择选项(self, 选项编号):
        """数字键1-4快速选择选项"""
        if self.模式 == "浏览":
            return
        
        if not self.题目列表 or self.当前题目索引 >= len(self.题目列表):
            return
        
        题目 = self.题目列表[self.当前题目索引]
        
        # 只对选择题有效
        if 题目.get('type') in ['单选题', '多选题']:
            选项映射 = {1: 'A', 2: 'B', 3: 'C', 4: 'D'}
            if 选项编号 in 选项映射:
                选项 = 选项映射[选项编号]
                
                # 单选题：直接替换
                if 题目.get('type') == '单选题':
                    self.答案输入框.delete(0, tk.END)
                    self.答案输入框.insert(0, 选项)
                # 多选题：追加
                else:
                    当前答案 = self.答案输入框.get().upper()
                    if 选项 not in 当前答案:
                        self.答案输入框.insert(tk.END, 选项)
    
    def 清除搜索提示(self, event=None):
        """清除搜索框提示文字"""
        if self.搜索输入框.get() == "输入关键字搜索...":
            self.搜索输入框.delete(0, tk.END)
            self.搜索输入框.config(fg=self.colors['text'])
    
    def 恢复搜索提示(self, event=None):
        """恢复搜索框提示文字"""
        if not self.搜索输入框.get():
            self.搜索输入框.insert(0, "输入关键字搜索...")
            self.搜索输入框.config(fg=self.colors['text_light'])
    
    def 切换解析显示(self):
        """切换解析区域的显示/隐藏"""
        if self.解析已展开:
            # 收起
            self.解析内容框架.pack_forget()
            self.解析展开图标.config(text="▶")
            self.解析已展开 = False
        else:
            # 展开
            self.解析内容框架.pack(fill=tk.BOTH, expand=True)
            self.解析展开图标.config(text="▼")
            self.解析已展开 = True
    
    def 退出程序(self):
        """退出程序"""
        # 保存当前状态
        self.保存当前状态()
        
        # 保存布局设置
        self.保存布局设置()
        
        self.quit()
    
    # 删除学习目标相关方法，简化界面
    
    def 记录今日答题(self):
        """记录今日答题数量"""
        try:
            from datetime import datetime
            今日日期 = datetime.now().strftime('%Y-%m-%d')
            self.今日已答 += 1
            
            # 保存到设置
            self.设置管理器.设置值(f'daily_progress_{今日日期}', self.今日已答)
            
            # 更新显示
            self.更新目标进度显示()
            
            # 检查是否完成目标
            if self.今日已答 >= self.每日目标:
                messagebox.showinfo("🎉 恭喜！", f"您已完成今日学习目标！\n答题数量: {self.今日已答}/{self.每日目标}")
        except Exception as e:
            print(f"记录今日答题失败: {e}")
    
    def 恢复主题设置(self):
        """恢复主题设置"""
        try:
            保存的主题 = self.设置管理器.获取设置('current_theme', 'light')
            if 保存的主题 in self.themes:
                self.切换主题(保存的主题)
        except Exception as e:
            print(f"恢复主题设置失败: {e}")
    
    def 恢复窗口状态(self):
        """恢复窗口大小和位置"""
        try:
            大小, 位置 = self.设置管理器.获取窗口状态()
            
            # 设置窗口大小
            if 大小 and 'x' in 大小:
                self.geometry(大小)
            
            # 设置窗口位置
            if 位置 and isinstance(位置, list) and len(位置) == 2:
                self.geometry(f"+{位置[0]}+{位置[1]}")
            
            # 恢复上次的题库和学习模式
            self.恢复学习状态()
            
        except Exception as e:
            print(f"恢复窗口状态失败: {e}")
    
    def 恢复学习状态(self):
        """恢复学习状态"""
        try:
            # 获取上次的题库
            上次题库 = self.设置管理器.获取设置('last_tiku')
            if 上次题库:
                # 检查题库是否还存在
                题库列表 = self.题库管理器.get_tiku_list()
                if 上次题库 in 题库列表:
                    self.当前题库 = 上次题库
                    # 恢复学习进度
                    self.恢复题库进度(上次题库)
            
            # 恢复学习模式
            上次模式 = self.设置管理器.获取设置('last_mode', '顺序')
            if 上次模式 in ['顺序', '随机', '错题', '浏览']:
                self.模式 = 上次模式
                if hasattr(self, '模式选择框'):
                    self.模式选择框.set(上次模式)
            
        except Exception as e:
            print(f"恢复学习状态失败: {e}")
    
    def 恢复题库进度(self, 题库名称):
        """恢复特定题库的学习进度"""
        try:
            进度 = self.设置管理器.获取题库进度(题库名称)
            
            # 恢复题目状态
            self.题目状态 = 进度.get('question_status', {})
            
            # 恢复统计
            self.答对数 = 进度.get('correct_count', 0)
            self.答错数 = 进度.get('wrong_count', 0)
            
            # 恢复收藏题目
            self.收藏题目 = set(进度.get('favorite_questions', []))
            
            # 恢复当前题目索引
            self.当前题目索引 = 进度.get('current_index', 0)
            
            # 更新统计显示（延迟执行，确保界面已创建）
            self.after(100, self.更新统计显示)
            
            # 更新题目列表颜色（延迟执行）
            if hasattr(self, '更新题目列表颜色'):
                self.after(100, self.更新题目列表颜色)
            
        except Exception as e:
            print(f"恢复题库进度失败: {e}")
    
    def 保存当前状态(self):
        """保存当前学习状态"""
        try:
            # 保存窗口状态
            当前大小 = self.geometry()
            self.设置管理器.保存窗口状态(当前大小, None)
            
            # 保存学习状态
            if self.当前题库:
                self.设置管理器.设置值('last_tiku', self.当前题库)
                self.设置管理器.设置值('last_mode', self.模式)
                
                # 保存题库进度
                self.设置管理器.更新题库进度(
                    self.当前题库, 
                    self.当前题目索引, 
                    self.模式, 
                    self.题目状态
                )
                
                # 保存统计
                self.设置管理器.更新统计(
                    self.当前题库, 
                    self.答对数, 
                    self.答错数
                )
                
                # 保存收藏题目
                self.设置管理器.更新收藏题目(
                    self.当前题库, 
                    self.收藏题目
                )
            
        except Exception as e:
            print(f"保存当前状态失败: {e}")
    
    def 窗口大小变化(self, event):
        """窗口大小变化时保存状态"""
        if event.widget == self:
            # 延迟保存，避免频繁保存
            if hasattr(self, '_save_timer'):
                self.after_cancel(self._save_timer)
            self._save_timer = self.after(1000, self.保存窗口状态)
    
    def 保存窗口状态(self):
        """保存窗口状态"""
        try:
            当前大小 = self.geometry()
            self.设置管理器.保存窗口状态(当前大小, None)
        except Exception as e:
            print(f"保存窗口状态失败: {e}")
    
    def 自动保存进度(self):
        """自动保存学习进度"""
        try:
            if self.当前题库 and self.模式 != "错题":
                # 保存题库进度
                self.设置管理器.更新题库进度(
                    self.当前题库, 
                    self.当前题目索引, 
                    self.模式, 
                    self.题目状态
                )
                
                # 保存统计
                self.设置管理器.更新统计(
                    self.当前题库, 
                    self.答对数, 
                    self.答错数
                )
                
                # 保存收藏题目
                self.设置管理器.更新收藏题目(
                    self.当前题库, 
                    self.收藏题目
                )
        except Exception as e:
            print(f"自动保存进度失败: {e}")
    
    def 切换题目时保存(self):
        """切换题目时保存当前进度"""
        try:
            if self.当前题库 and self.模式 != "错题":
                self.设置管理器.更新题库进度(
                    self.当前题库, 
                    self.当前题目索引, 
                    self.模式, 
                    self.题目状态
                )
        except Exception as e:
            print(f"切换题目时保存失败: {e}")
    
    def 错题管理(self):
        """错题管理窗口"""
        try:
            # 获取错题统计
            统计信息 = self.错题记忆管理器.获取错题统计()
            
            # 创建错题管理窗口
            管理窗口 = tk.Toplevel(self)
            管理窗口.title("错题管理")
            管理窗口.geometry("800x600")
            管理窗口.configure(bg=self.colors['background'])
            
            # 标题
            标题框架 = tk.Frame(管理窗口, bg=self.colors['card_bg'], relief='flat', bd=1)
            标题框架.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Label(标题框架, text="📚 错题管理中心", 
                     font=("微软雅黑", 16, "bold")).pack(pady=10)
            
            # 统计信息
            统计框架 = tk.Frame(管理窗口, bg=self.colors['card_bg'], relief='flat', bd=1)
            统计框架.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(统计框架, text="📊 错题统计", 
                     font=("微软雅黑", 12, "bold")).pack(anchor=tk.W, padx=10, pady=5)
            
            # 显示统计信息
            统计文本 = f"总错题数：{统计信息.get('total_wrong_questions', 0)}\n"
            统计文本 += f"最近7天新增：{统计信息.get('recent_wrong', 0)}\n\n"
            
            统计文本 += "按题库分布：\n"
            for 题库, 数量 in 统计信息.get('by_tiku', {}).items():
                统计文本 += f"  {题库}：{数量}题\n"
            
            统计文本 += "\n按题型分布：\n"
            for 题型, 数量 in 统计信息.get('by_type', {}).items():
                统计文本 += f"  {题型}：{数量}题\n"
            
            统计文本 += "\n掌握程度分布：\n"
            掌握分布 = 统计信息.get('mastery_distribution', {})
            for i in range(6):
                数量 = 掌握分布.get(i, 0)
                统计文本 += f"  {i}级：{数量}题\n"
            
            统计标签 = tk.Label(统计框架, text=统计文本, 
                               font=("微软雅黑", 10), 
                               bg=self.colors['card_bg'],
                               justify=tk.LEFT)
            统计标签.pack(anchor=tk.W, padx=10, pady=5)
            
            # 操作按钮
            操作框架 = tk.Frame(管理窗口, bg=self.colors['card_bg'], relief='flat', bd=1)
            操作框架.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Button(操作框架, text="🧹 清理已掌握错题", 
                      command=lambda: self.清理已掌握错题()).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(操作框架, text="📤 导出错题数据", 
                      command=lambda: self.导出错题数据()).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(操作框架, text="📥 导入错题数据", 
                      command=lambda: self.导入错题数据()).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(操作框架, text="🔄 刷新统计", 
                      command=lambda: self.错题管理()).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(操作框架, text="关闭", 
                      command=管理窗口.destroy).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("错误", f"打开错题管理失败：\n{e}")
    
    def 智能复习(self):
        """智能复习功能"""
        try:
            # 获取智能复习题目
            智能题目 = self.错题记忆管理器.获取智能复习题目(20)
            
            if not 智能题目:
                messagebox.showinfo("智能复习", "当前没有需要复习的错题！")
                return
            
            # 显示智能复习信息
            复习信息 = f"智能复习推荐\n\n"
            复习信息 += f"推荐题目数：{len(智能题目)}\n"
            复习信息 += f"平均掌握程度：{sum(item['mastery_level'] for item in 智能题目) / len(智能题目):.1f}/5\n\n"
            
            复习信息 += "推荐理由：\n"
            for i, item in enumerate(智能题目[:5]):  # 只显示前5个
                掌握程度 = item['mastery_level']
                错误次数 = item['wrong_count']
                复习信息 += f"{i+1}. 掌握程度{掌握程度}/5，错误{错误次数}次\n"
            
            if len(智能题目) > 5:
                复习信息 += f"... 还有{len(智能题目)-5}道题目\n"
            
            复习信息 += "\n是否开始智能复习？"
            
            if messagebox.askyesno("智能复习", 复习信息):
                # 切换到错题模式并开始复习
                self.模式 = "错题"
                if hasattr(self, '模式选择框'):
                    self.模式选择框.set("错题")
                self.开始刷题()
            
        except Exception as e:
            messagebox.showerror("错误", f"智能复习失败：\n{e}")
    
    def 清理已掌握错题(self):
        """清理已掌握的错题"""
        try:
            清理数量 = self.错题记忆管理器.清理已掌握错题()
            messagebox.showinfo("清理完成", f"已清理 {清理数量} 道已掌握的错题！")
            # 刷新错题管理窗口
            self.错题管理()
        except Exception as e:
            messagebox.showerror("错误", f"清理失败：\n{e}")
    
    def 导出错题数据(self):
        """导出错题数据"""
        try:
            文件路径 = filedialog.asksaveasfilename(
                title="导出错题数据",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
            )
            
            if 文件路径:
                if self.错题记忆管理器.导出错题数据(文件路径):
                    messagebox.showinfo("导出成功", f"错题数据已导出到：\n{文件路径}")
                else:
                    messagebox.showerror("导出失败", "导出错题数据失败！")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：\n{e}")
    
    def 导入错题数据(self):
        """导入错题数据"""
        try:
            文件路径 = filedialog.askopenfilename(
                title="导入错题数据",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
            )
            
            if 文件路径:
                if self.错题记忆管理器.导入错题数据(文件路径):
                    messagebox.showinfo("导入成功", f"错题数据已从以下文件导入：\n{文件路径}")
                    # 刷新错题管理窗口
                    self.错题管理()
                else:
                    messagebox.showerror("导入失败", "导入错题数据失败！")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败：\n{e}")
    
    def 选择选项(self, 选项):
        """选择选项按钮点击事件"""
        try:
            if not self.题目列表 or self.当前题目索引 >= len(self.题目列表):
                return
            
            题目 = self.题目列表[self.当前题目索引]
            题型 = 题目.get('type', '未知')
            
            # 强制检查：如果有选项，就按选择题处理
            if 题目.get('options') and 题型 not in ['单选题', '多选题']:
                # 根据答案长度判断单选/多选
                answer = 题目.get('answer', '')
                if len(answer) > 1 and all(c in 'ABCDEF' for c in answer.upper()):
                    题型 = '多选题'
                else:
                    题型 = '单选题'
            
            # 单选题：立即检查答案
            if 题型 == '单选题':
                正确答案 = 题目.get('answer', '').upper()
                是否正确 = self.检查答案(选项, 正确答案, 题型)
                
                # 更新统计
                if 是否正确:
                    self.答对数 += 1
                    self.反馈标签.config(text="✓ 回答正确！", foreground="green")
                else:
                    self.答错数 += 1
                    self.反馈标签.config(
                        text=f"✗ 回答错误！正确答案：{题目.get('answer', '')}", 
                        foreground="red")
                
                # 显示解析
                if 题目.get('explanation'):
                    self.解析文本.config(state=tk.NORMAL)
                    self.解析文本.delete(1.0, tk.END)
                    self.解析文本.insert(1.0, 题目.get('explanation', ''))
                    self.解析文本.config(state=tk.DISABLED)
                
                # 记录答题（使用刷题引擎的记录功能）
                if hasattr(self, '当前引擎'):
                    self.当前引擎.record_answer(题目, 选项, 是否正确)
                
                # 使用增强的错题记忆功能
                if not 是否正确:
                    # 添加到错题记忆
                    错误原因 = f"用户选择：{选项}，正确答案：{正确答案}"
                    self.错题记忆管理器.添加错题(题目, self.当前题库, 选项, 错误原因)
                else:
                    # 如果答对了，记录复习结果
                    self.错题记忆管理器.记录复习(题目, True)
                
                # 更新题目状态
                if 是否正确:
                    self.题目状态[self.当前题目索引] = 'correct'
                else:
                    self.题目状态[self.当前题目索引] = 'wrong'
                
                # 更新统计显示
                self.更新统计显示()
                self.更新题目列表颜色()
                
                # 自动保存进度
                self.自动保存进度()
                
                # 自动跳转到下一题（1秒后）
                self.after(1500, self.下一题)
            
            # 多选题：添加到已选答案列表
            elif 题型 == '多选题':
                if not hasattr(self, '已选答案列表'):
                    self.已选答案列表 = []
                
                if 选项 in self.已选答案列表:
                    # 取消选择
                    self.已选答案列表.remove(选项)
                    # 更新按钮状态
                    self.更新选项按钮状态(选项, False)
                else:
                    # 添加选择
                    self.已选答案列表.append(选项)
                    # 更新按钮状态
                    self.更新选项按钮状态(选项, True)
                
                # 更新已选答案显示
                self.更新已选答案显示()
                
                # 更新确定按钮状态
                if hasattr(self, '确定按钮'):
                    if self.已选答案列表:
                        self.确定按钮.config(state='normal')
                    else:
                        self.确定按钮.config(state='disabled')
                
                return  # 多选题不立即检查答案
            
            # 其他题型：默认处理
            else:
                # 对于其他题型，也进行答案检查
                正确答案 = 题目.get('answer', '').upper()
                是否正确 = self.检查答案(选项, 正确答案, 题型)
                
                # 更新统计
                if 是否正确:
                    self.答对数 += 1
                    self.反馈标签.config(text="✓ 回答正确！", foreground="green")
                else:
                    self.答错数 += 1
                    self.反馈标签.config(
                        text=f"✗ 回答错误！正确答案：{题目.get('answer', '')}", 
                        foreground="red")
                
                # 显示解析
                if 题目.get('explanation'):
                    self.解析文本.config(state=tk.NORMAL)
                    self.解析文本.delete(1.0, tk.END)
                    self.解析文本.insert(1.0, 题目.get('explanation', ''))
                    self.解析文本.config(state=tk.DISABLED)
                
                # 记录答题（使用刷题引擎的记录功能）
                if hasattr(self, '当前引擎'):
                    self.当前引擎.record_answer(题目, 选项, 是否正确)
                
                # 使用增强的错题记忆功能
                if not 是否正确:
                    # 添加到错题记忆
                    错误原因 = f"用户选择：{选项}，正确答案：{正确答案}"
                    self.错题记忆管理器.添加错题(题目, self.当前题库, 选项, 错误原因)
                else:
                    # 如果答对了，记录复习结果
                    self.错题记忆管理器.记录复习(题目, True)
                
                # 更新题目状态
                if 是否正确:
                    self.题目状态[self.当前题目索引] = 'correct'
                else:
                    self.题目状态[self.当前题目索引] = 'wrong'
                
                # 更新统计显示
                self.更新统计显示()
                self.更新题目列表颜色()
                
                # 自动保存进度
                self.自动保存进度()
                
                # 自动跳转到下一题（1秒后）
                self.after(1500, self.下一题)
            
        except Exception as e:
            messagebox.showerror("错误", f"选择选项失败：\n{e}")
    
    def 显示填空答案(self):
        """显示填空题答案按钮点击事件"""
        try:
            if not self.题目列表 or self.当前题目索引 >= len(self.题目列表):
                return
            
            题目 = self.题目列表[self.当前题目索引]
            正确答案 = 题目.get('answer', '')
            
            # 显示答案在题目中
            self.显示填空模式(题目, 正确答案)
            
            # 记录为正确答题
            self.答对数 += 1
            self.反馈标签.config(text="✓ 已显示答案！", foreground="green")
            
            # 显示解析
            if 题目.get('explanation'):
                self.解析文本.config(state=tk.NORMAL)
                self.解析文本.delete(1.0, tk.END)
                self.解析文本.insert(1.0, 题目.get('explanation', ''))
                self.解析文本.config(state=tk.DISABLED)
            
            # 记录答题（使用刷题引擎的记录功能）
            if hasattr(self, '当前引擎'):
                self.当前引擎.record_answer(题目, 正确答案, True)
            
            # 记录复习结果
            self.错题记忆管理器.记录复习(题目, True)
            
            # 更新题目状态
            self.题目状态[self.当前题目索引] = 'correct'
            
            self.更新统计显示()
            
            # 更新题目列表颜色标记
            self.更新题目列表颜色()
            
            # 自动保存进度
            self.自动保存进度()
            
            # 自动跳转到下一题（2秒后）
            self.after(2000, self.下一题)
            
        except Exception as e:
            messagebox.showerror("错误", f"显示填空答案失败：\n{e}")
    
    def 显示填空模式(self, 题目, 答案):
        """显示填空模式（答案直接显示在题目中，带颜色区分）"""
        try:
            题目文本 = 题目.get('question', '')
            
            # 如果题目中有下划线或空格，替换为答案
            if '____' in 题目文本:
                填空后文本 = 题目文本.replace('____', f'[{答案}]')
            elif '_____' in 题目文本:
                填空后文本 = 题目文本.replace('_____', f'[{答案}]')
            elif '______' in 题目文本:
                填空后文本 = 题目文本.replace('______', f'[{答案}]')
            elif ' ' in 题目文本:
                # 如果有空格，在空格处插入答案
                填空后文本 = 题目文本.replace(' ', f' [{答案}] ', 1)
            else:
                # 如果没有明显的填空标记，在题目末尾添加答案
                填空后文本 = f"{题目文本} → 答案：[{答案}]"
            
            # 更新题目显示
            self.更新题目文本(填空后文本, tk.NORMAL)
            
            # 添加颜色标记（如果支持）
            try:
                # 查找答案部分并添加颜色
                答案开始 = 填空后文本.find(f'[{答案}]')
                if 答案开始 != -1:
                    答案结束 = 答案开始 + len(f'[{答案}]')
                    self.题目文本.tag_add("answer", f"1.{答案开始}", f"1.{答案结束}")
                    self.题目文本.tag_config("answer", foreground=self.colors['success'], 
                                           font=("微软雅黑", 12, "bold"))
            except:
                pass  # 如果颜色设置失败，继续执行
            
            self.题目文本.config(state=tk.DISABLED)
            
            # 标记为填空模式
            self.填空模式 = True
            
        except Exception as e:
            print(f"显示填空模式失败: {e}")
    
    def 切换填空模式(self):
        """切换填空模式"""
        try:
            if not self.题目列表 or self.当前题目索引 >= len(self.题目列表):
                return
            
            题目 = self.题目列表[self.当前题目索引]
            
            if self.填空模式:
                # 切换回正常模式
                self.更新题目文本(题目.get('question', ''))
                self.填空模式 = False
            else:
                # 切换到填空模式
                正确答案 = 题目.get('answer', '')
                self.显示填空模式(题目, 正确答案)
                
        except Exception as e:
            print(f"切换填空模式失败: {e}")
    
    def 更新填空答案按钮(self, 题目):
        """更新填空答案按钮的显示状态"""
        try:
            题型 = 题目.get('type', '')
            题目文本 = 题目.get('question', '')
            
            # 判断是否为填空题
            是填空题 = (
                题型 == '填空题' or 
                '____' in 题目文本 or 
                '_____' in 题目文本 or 
                '______' in 题目文本 or
                (' ' in 题目文本 and len(题目文本.split()) <= 10)  # 短文本可能是填空
            )
            
            if 是填空题 and self.模式 != "浏览":
                # 显示填空答案按钮
                self.填空答案按钮.pack(side=tk.LEFT, padx=3)
            else:
                # 隐藏填空答案按钮
                self.填空答案按钮.pack_forget()
                
        except Exception as e:
            print(f"更新填空答案按钮失败: {e}")


    def 更新选项按钮状态(self, 选项, 已选择):
        """更新选项按钮的视觉状态"""
        if hasattr(self, '选项按钮列表'):
            for key, button in self.选项按钮列表:
                if key == 选项:
                    if 已选择:
                        button.config(
                            bg='#e74c3c',  # 更明显的选中颜色
                            fg='white', 
                            relief='sunken',
                            font=("微软雅黑", 10, "bold")
                        )
                    else:
                        button.config(
                            bg=self.colors['card_bg'], 
                            fg=self.colors['text'], 
                            relief='raised',
                            font=("微软雅黑", 10)
                        )
                    break
    
    def 更新已选答案显示(self):
        """更新已选答案的显示"""
        if hasattr(self, '已选答案标签'):
            if hasattr(self, '已选答案列表') and self.已选答案列表:
                已选文本 = f"已选择：{', '.join(sorted(self.已选答案列表))} ({len(self.已选答案列表)}个)"
                self.已选答案标签.config(text=已选文本, fg=self.colors['primary'])
            else:
                self.已选答案标签.config(text="请选择答案（可多选）", fg=self.colors['text_secondary'])
    
    def 清理多选题状态(self):
        """清理多选题相关状态"""
        if hasattr(self, '已选答案列表'):
            self.已选答案列表 = []
        
        if hasattr(self, '确定按钮'):
            self.确定按钮.config(state='disabled')
        
        if hasattr(self, '已选答案标签'):
            self.已选答案标签.config(text="请选择答案（可多选）", fg=self.colors['text_secondary'])
        
        # 重置所有选项按钮状态
        if hasattr(self, '选项按钮列表'):
            for key, button in self.选项按钮列表:
                button.config(
                    bg=self.colors['card_bg'], 
                    fg=self.colors['text'], 
                    relief='raised'
                )
    
    def 确定多选题答案(self):
        """确定多选题答案"""
        if not hasattr(self, '已选答案列表') or not self.已选答案列表:
            messagebox.showwarning("提示", "请至少选择一个答案！")
            return
        
        try:
            题目 = self.题目列表[self.当前题目索引]
            正确答案 = 题目.get('answer', '').upper()
            
            # 将已选答案合并为字符串
            用户答案 = "".join(sorted(self.已选答案列表))
            
            # 检查答案
            是否正确 = self.检查答案(用户答案, 正确答案, '多选题')
            
            # 更新统计
            if 是否正确:
                self.答对数 += 1
                self.反馈标签.config(text="✓ 回答正确！", foreground="green")
            else:
                self.答错数 += 1
                self.反馈标签.config(
                    text=f"✗ 回答错误！正确答案：{题目.get('answer', '')}", 
                    foreground="red")
            
            # 显示解析
            if 题目.get('explanation'):
                self.解析文本.config(state=tk.NORMAL)
                self.解析文本.delete(1.0, tk.END)
                self.解析文本.insert(1.0, 题目.get('explanation', ''))
                self.解析文本.config(state=tk.DISABLED)
            
            # 记录答题（使用刷题引擎的记录功能）
            if hasattr(self, '当前引擎'):
                self.当前引擎.record_answer(题目, 用户答案, 是否正确)
            
            # 更新统计显示
            self.更新统计显示()
            self.更新题目列表颜色()
            
            # 清理多选题状态
            self.已选答案列表 = []
            if hasattr(self, '确定按钮'):
                self.确定按钮.config(state='disabled')
            self.更新已选答案显示()
            
        except Exception as e:
            print(f"确定多选题答案时出错: {e}")

def main():
    """主函数"""
    try:
        app = 刷题应用()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("错误", f"程序启动失败：\n{e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

