#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户设置管理模块
负责保存和恢复用户的学习进度、偏好设置等
"""

import json
import os
from pathlib import Path
from datetime import datetime

class 用户设置管理器:
    def __init__(self):
        """初始化设置管理器"""
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / '.data'
        self.data_dir.mkdir(exist_ok=True)
        
        self.设置文件 = self.data_dir / 'user_settings.json'
        self.进度文件 = self.data_dir / 'learning_progress.json'
        
        # 默认设置
        self.默认设置 = {
            'window_size': '1200x800',
            'window_position': None,
            'last_tiku': None,
            'last_mode': '顺序',
            'auto_save_progress': True,
            'show_hints': True,
            'auto_next_question': True,
            'auto_next_delay': 1500,
            'theme': 'modern_tech',
            'font_size': 12,
            'language': 'zh_CN'
        }
        
        # 加载设置
        self.设置 = self.加载设置()
    
    def 加载设置(self):
        """加载用户设置"""
        if not self.设置文件.exists():
            return self.默认设置.copy()
        
        try:
            with open(self.设置文件, 'r', encoding='utf-8') as f:
                设置 = json.load(f)
            
            # 合并默认设置，确保所有键都存在
            for key, value in self.默认设置.items():
                if key not in 设置:
                    设置[key] = value
            
            return 设置
        except Exception as e:
            print(f"加载设置失败: {e}")
            return self.默认设置.copy()
    
    def 保存设置(self):
        """保存用户设置"""
        try:
            with open(self.设置文件, 'w', encoding='utf-8') as f:
                json.dump(self.设置, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存设置失败: {e}")
            return False
    
    def 获取设置(self, key, default=None):
        """获取设置值"""
        return self.设置.get(key, default)
    
    def 设置值(self, key, value):
        """设置值"""
        self.设置[key] = value
        return self.保存设置()
    
    def 加载学习进度(self):
        """加载学习进度"""
        if not self.进度文件.exists():
            return {}
        
        try:
            with open(self.进度文件, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载学习进度失败: {e}")
            return {}
    
    def 保存学习进度(self, 进度数据):
        """保存学习进度"""
        try:
            with open(self.进度文件, 'w', encoding='utf-8') as f:
                json.dump(进度数据, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存学习进度失败: {e}")
            return False
    
    def 更新题库进度(self, 题库名称, 当前索引, 模式, 题目状态=None):
        """更新特定题库的学习进度"""
        进度数据 = self.加载学习进度()
        
        if 题库名称 not in 进度数据:
            进度数据[题库名称] = {
                'last_updated': datetime.now().isoformat(),
                'total_questions': 0,
                'current_index': 0,
                'mode': '顺序',
                'question_status': {},
                'correct_count': 0,
                'wrong_count': 0,
                'favorite_questions': []
            }
        
        进度数据[题库名称].update({
            'last_updated': datetime.now().isoformat(),
            'current_index': 当前索引,
            'mode': 模式
        })
        
        if 题目状态 is not None:
            进度数据[题库名称]['question_status'] = 题目状态
        
        return self.保存学习进度(进度数据)
    
    def 获取题库进度(self, 题库名称):
        """获取特定题库的学习进度"""
        进度数据 = self.加载学习进度()
        return 进度数据.get(题库名称, {
            'current_index': 0,
            'mode': '顺序',
            'question_status': {},
            'correct_count': 0,
            'wrong_count': 0,
            'favorite_questions': []
        })
    
    def 更新统计(self, 题库名称, 答对数, 答错数):
        """更新答题统计"""
        进度数据 = self.加载学习进度()
        
        if 题库名称 not in 进度数据:
            进度数据[题库名称] = {}
        
        进度数据[题库名称].update({
            'correct_count': 答对数,
            'wrong_count': 答错数,
            'last_updated': datetime.now().isoformat()
        })
        
        return self.保存学习进度(进度数据)
    
    def 更新收藏题目(self, 题库名称, 收藏列表):
        """更新收藏题目列表"""
        进度数据 = self.加载学习进度()
        
        if 题库名称 not in 进度数据:
            进度数据[题库名称] = {}
        
        进度数据[题库名称]['favorite_questions'] = list(收藏列表)
        进度数据[题库名称]['last_updated'] = datetime.now().isoformat()
        
        return self.保存学习进度(进度数据)
    
    def 保存窗口状态(self, 大小, 位置):
        """保存窗口大小和位置"""
        self.设置值('window_size', 大小)
        self.设置值('window_position', 位置)
    
    def 获取窗口状态(self):
        """获取窗口大小和位置"""
        大小 = self.获取设置('window_size', '1200x800')
        位置 = self.获取设置('window_position')
        return 大小, 位置
    
    def 重置设置(self):
        """重置所有设置为默认值"""
        self.设置 = self.默认设置.copy()
        return self.保存设置()
    
    def 重置进度(self, 题库名称=None):
        """重置学习进度"""
        if 题库名称:
            # 重置特定题库进度
            进度数据 = self.加载学习进度()
            if 题库名称 in 进度数据:
                del 进度数据[题库名称]
                return self.保存学习进度(进度数据)
        else:
            # 重置所有进度
            if self.进度文件.exists():
                self.进度文件.unlink()
            return True
    
    def 导出设置(self, 文件路径):
        """导出设置到文件"""
        try:
            导出数据 = {
                'settings': self.设置,
                'progress': self.加载学习进度(),
                'export_time': datetime.now().isoformat()
            }
            
            with open(文件路径, 'w', encoding='utf-8') as f:
                json.dump(导出数据, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出设置失败: {e}")
            return False
    
    def 导入设置(self, 文件路径):
        """从文件导入设置"""
        try:
            with open(文件路径, 'r', encoding='utf-8') as f:
                导入数据 = json.load(f)
            
            if 'settings' in 导入数据:
                self.设置.update(导入数据['settings'])
                self.保存设置()
            
            if 'progress' in 导入数据:
                self.保存学习进度(导入数据['progress'])
            
            return True
        except Exception as e:
            print(f"导入设置失败: {e}")
            return False
