#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
错题记忆管理模块
负责错题的持久化存储、分类管理和智能复习
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

class 错题记忆管理器:
    def __init__(self):
        """初始化错题记忆管理器"""
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / '.data'
        self.data_dir.mkdir(exist_ok=True)
        
        # 错题数据文件
        self.错题文件 = self.data_dir / 'wrong_questions_enhanced.json'
        self.错题统计文件 = self.data_dir / 'wrong_questions_stats.json'
        
        # 错题数据结构
        self.错题数据 = self.加载错题数据()
        self.错题统计 = self.加载错题统计()
    
    def 加载错题数据(self):
        """加载错题数据"""
        if not self.错题文件.exists():
            return {}
        
        try:
            with open(self.错题文件, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载错题数据失败: {e}")
            return {}
    
    def 保存错题数据(self):
        """保存错题数据"""
        try:
            with open(self.错题文件, 'w', encoding='utf-8') as f:
                json.dump(self.错题数据, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存错题数据失败: {e}")
            return False
    
    def 加载错题统计(self):
        """加载错题统计"""
        if not self.错题统计文件.exists():
            return {}
        
        try:
            with open(self.错题统计文件, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载错题统计失败: {e}")
            return {}
    
    def 保存错题统计(self):
        """保存错题统计"""
        try:
            with open(self.错题统计文件, 'w', encoding='utf-8') as f:
                json.dump(self.错题统计, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存错题统计失败: {e}")
            return False
    
    def 添加错题(self, 题目, 题库名称, 用户答案='', 错误原因=''):
        """添加错题到记忆系统"""
        try:
            题目ID = self.生成题目ID(题目)
            当前时间 = datetime.now().isoformat()
            
            # 错题记录
            错题记录 = {
                'question': 题目,
                'tiku_name': 题库名称,
                'user_answer': 用户答案,
                'correct_answer': 题目.get('answer', ''),
                'error_reason': 错误原因,
                'first_wrong_time': 当前时间,
                'last_wrong_time': 当前时间,
                'wrong_count': 1,
                'review_count': 0,
                'mastery_level': 0,  # 掌握程度 0-5
                'tags': self.自动标签(题目),
                'difficulty': self.评估难度(题目),
                'review_history': []
            }
            
            # 如果题目已存在，更新记录
            if 题目ID in self.错题数据:
                现有记录 = self.错题数据[题目ID]
                现有记录['last_wrong_time'] = 当前时间
                现有记录['wrong_count'] += 1
                现有记录['mastery_level'] = max(0, 现有记录['mastery_level'] - 1)
            else:
                self.错题数据[题目ID] = 错题记录
            
            # 更新统计
            self.更新错题统计(题库名称, 题目.get('type', '未知'))
            
            return self.保存错题数据()
            
        except Exception as e:
            print(f"添加错题失败: {e}")
            return False
    
    def 移除错题(self, 题目):
        """从错题本移除题目"""
        try:
            题目ID = self.生成题目ID(题目)
            if 题目ID in self.错题数据:
                del self.错题数据[题目ID]
                return self.保存错题数据()
            return True
        except Exception as e:
            print(f"移除错题失败: {e}")
            return False
    
    def 记录复习(self, 题目, 是否正确):
        """记录错题复习结果"""
        try:
            题目ID = self.生成题目ID(题目)
            if 题目ID not in self.错题数据:
                return False
            
            记录 = self.错题数据[题目ID]
            当前时间 = datetime.now().isoformat()
            
            # 更新复习记录
            复习记录 = {
                'time': 当前时间,
                'is_correct': 是否正确,
                'mastery_change': 1 if 是否正确 else -1
            }
            
            记录['review_history'].append(复习记录)
            记录['review_count'] += 1
            
            # 更新掌握程度
            if 是否正确:
                记录['mastery_level'] = min(5, 记录['mastery_level'] + 1)
            else:
                记录['mastery_level'] = max(0, 记录['mastery_level'] - 1)
            
            # 如果掌握程度达到5，可以考虑移除
            if 记录['mastery_level'] >= 5 and 记录['review_count'] >= 3:
                记录['status'] = 'mastered'
            
            return self.保存错题数据()
            
        except Exception as e:
            print(f"记录复习失败: {e}")
            return False
    
    def 获取错题列表(self, 题库名称=None, 题型=None, 掌握程度=None):
        """获取错题列表"""
        try:
            错题列表 = []
            
            for 题目ID, 记录 in self.错题数据.items():
                # 过滤条件
                if 题库名称 and 记录.get('tiku_name') != 题库名称:
                    continue
                if 题型 and 记录.get('question', {}).get('type') != 题型:
                    continue
                if 掌握程度 is not None and 记录.get('mastery_level', 0) != 掌握程度:
                    continue
                
                错题列表.append({
                    'id': 题目ID,
                    'question': 记录['question'],
                    'wrong_count': 记录.get('wrong_count', 1),
                    'mastery_level': 记录.get('mastery_level', 0),
                    'last_wrong_time': 记录.get('last_wrong_time'),
                    'tags': 记录.get('tags', [])
                })
            
            # 按最后错误时间排序（最新的在前）
            错题列表.sort(key=lambda x: x['last_wrong_time'], reverse=True)
            return 错题列表
            
        except Exception as e:
            print(f"获取错题列表失败: {e}")
            return []
    
    def 获取智能复习题目(self, 数量=10):
        """获取智能复习题目（基于遗忘曲线）"""
        try:
            复习题目 = []
            当前时间 = datetime.now()
            
            for 题目ID, 记录 in self.错题数据.items():
                # 跳过已掌握的题目
                if 记录.get('mastery_level', 0) >= 5:
                    continue
                
                # 计算复习优先级
                优先级 = self.计算复习优先级(记录, 当前时间)
                
                复习题目.append({
                    'id': 题目ID,
                    'question': 记录['question'],
                    'priority': 优先级,
                    'mastery_level': 记录.get('mastery_level', 0),
                    'wrong_count': 记录.get('wrong_count', 1)
                })
            
            # 按优先级排序
            复习题目.sort(key=lambda x: x['priority'], reverse=True)
            
            return 复习题目[:数量]
            
        except Exception as e:
            print(f"获取智能复习题目失败: {e}")
            return []
    
    def 计算复习优先级(self, 记录, 当前时间):
        """计算复习优先级（基于遗忘曲线）"""
        try:
            掌握程度 = 记录.get('mastery_level', 0)
            错误次数 = 记录.get('wrong_count', 1)
            
            # 获取最后错误时间
            最后错误时间 = datetime.fromisoformat(记录.get('last_wrong_time', 当前时间.isoformat()))
            时间间隔 = (当前时间 - 最后错误时间).days
            
            # 基于遗忘曲线的优先级计算
            # 掌握程度越低，错误次数越多，时间间隔越长，优先级越高
            基础优先级 = (5 - 掌握程度) * 10 + 错误次数 * 5 + 时间间隔 * 2
            
            return 基础优先级
            
        except Exception as e:
            print(f"计算复习优先级失败: {e}")
            return 0
    
    def 生成题目ID(self, 题目):
        """生成题目的唯一ID"""
        try:
            # 使用题目的前50个字符作为ID基础
            题目文本 = 题目.get('question', '')[:50]
            答案 = 题目.get('answer', '')
            return f"{hash(题目文本 + 答案)}"
        except:
            return f"{hash(str(题目))}"
    
    def 自动标签(self, 题目):
        """为题目自动生成标签"""
        标签 = []
        
        # 基于题型的标签
        题型 = 题目.get('type', '')
        if 题型:
            标签.append(f"题型_{题型}")
        
        # 基于关键词的标签
        题目文本 = 题目.get('question', '').lower()
        关键词标签 = {
            '安全': '安全相关',
            '规程': '规程相关',
            '操作': '操作相关',
            '设备': '设备相关',
            '检查': '检查相关',
            '维护': '维护相关'
        }
        
        for 关键词, 标签名 in 关键词标签.items():
            if 关键词 in 题目文本:
                标签.append(标签名)
        
        return 标签
    
    def 评估难度(self, 题目):
        """评估题目难度"""
        try:
            难度 = 1  # 基础难度
            
            # 基于题型调整难度
            题型 = 题目.get('type', '')
            if 题型 == '多选题':
                难度 += 1
            elif 题型 == '填空题':
                难度 += 0.5
            
            # 基于题目长度调整难度
            题目长度 = len(题目.get('question', ''))
            if 题目长度 > 100:
                难度 += 0.5
            
            # 基于选项数量调整难度
            选项数量 = 0
            for key in ['A', 'B', 'C', 'D', 'E', 'F']:
                if 题目.get(key):
                    选项数量 += 1
            
            if 选项数量 > 4:
                难度 += 0.5
            
            return min(5, max(1, 难度))
            
        except:
            return 1
    
    def 更新错题统计(self, 题库名称, 题型):
        """更新错题统计"""
        try:
            if 题库名称 not in self.错题统计:
                self.错题统计[题库名称] = {
                    'total_wrong': 0,
                    'by_type': {},
                    'last_updated': datetime.now().isoformat()
                }
            
            self.错题统计[题库名称]['total_wrong'] += 1
            
            if 题型 not in self.错题统计[题库名称]['by_type']:
                self.错题统计[题库名称]['by_type'][题型] = 0
            
            self.错题统计[题库名称]['by_type'][题型] += 1
            self.错题统计[题库名称]['last_updated'] = datetime.now().isoformat()
            
            self.保存错题统计()
            
        except Exception as e:
            print(f"更新错题统计失败: {e}")
    
    def 获取错题统计(self):
        """获取错题统计信息"""
        try:
            统计信息 = {
                'total_wrong_questions': len(self.错题数据),
                'by_tiku': {},
                'by_type': {},
                'mastery_distribution': {i: 0 for i in range(6)},
                'recent_wrong': 0
            }
            
            当前时间 = datetime.now()
            最近7天 = 当前时间 - timedelta(days=7)
            
            for 记录 in self.错题数据.values():
                # 按题库统计
                题库名称 = 记录.get('tiku_name', '未知')
                if 题库名称 not in 统计信息['by_tiku']:
                    统计信息['by_tiku'][题库名称] = 0
                统计信息['by_tiku'][题库名称] += 1
                
                # 按题型统计
                题型 = 记录.get('question', {}).get('type', '未知')
                if 题型 not in 统计信息['by_type']:
                    统计信息['by_type'][题型] = 0
                统计信息['by_type'][题型] += 1
                
                # 掌握程度分布
                掌握程度 = 记录.get('mastery_level', 0)
                统计信息['mastery_distribution'][掌握程度] += 1
                
                # 最近7天错题数
                try:
                    最后错误时间 = datetime.fromisoformat(记录.get('last_wrong_time', ''))
                    if 最后错误时间 >= 最近7天:
                        统计信息['recent_wrong'] += 1
                except:
                    pass
            
            return 统计信息
            
        except Exception as e:
            print(f"获取错题统计失败: {e}")
            return {}
    
    def 清理已掌握错题(self, 掌握程度阈值=5):
        """清理已掌握的错题"""
        try:
            清理数量 = 0
            待清理 = []
            
            for 题目ID, 记录 in self.错题数据.items():
                if 记录.get('mastery_level', 0) >= 掌握程度阈值:
                    待清理.append(题目ID)
            
            for 题目ID in 待清理:
                del self.错题数据[题目ID]
                清理数量 += 1
            
            if 清理数量 > 0:
                self.保存错题数据()
            
            return 清理数量
            
        except Exception as e:
            print(f"清理已掌握错题失败: {e}")
            return 0
    
    def 导出错题数据(self, 文件路径):
        """导出错题数据"""
        try:
            导出数据 = {
                'wrong_questions': self.错题数据,
                'statistics': self.错题统计,
                'export_time': datetime.now().isoformat(),
                'version': '2.0'
            }
            
            with open(文件路径, 'w', encoding='utf-8') as f:
                json.dump(导出数据, f, ensure_ascii=False, indent=2)
            return True
            
        except Exception as e:
            print(f"导出错题数据失败: {e}")
            return False
    
    def 导入错题数据(self, 文件路径):
        """导入错题数据"""
        try:
            with open(文件路径, 'r', encoding='utf-8') as f:
                导入数据 = json.load(f)
            
            if 'wrong_questions' in 导入数据:
                self.错题数据.update(导入数据['wrong_questions'])
                self.保存错题数据()
            
            if 'statistics' in 导入数据:
                self.错题统计.update(导入数据['statistics'])
                self.保存错题统计()
            
            return True
            
        except Exception as e:
            print(f"导入错题数据失败: {e}")
            return False
