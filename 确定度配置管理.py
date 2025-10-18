#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工业化商用级确定度配置系统
提供完整的配置管理、性能监控、日志记录等商用功能
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class 识别统计:
    """识别统计数据"""
    总识别次数: int = 0
    成功识别次数: int = 0
    低确定度次数: int = 0
    各题型识别次数: Dict[str, int] = None
    平均确定度: float = 0.0
    识别耗时: List[float] = None
    
    def __post_init__(self):
        if self.各题型识别次数 is None:
            self.各题型识别次数 = {}
        if self.识别耗时 is None:
            self.识别耗时 = []

class 确定度配置管理器:
    """确定度识别系统配置管理器"""
    
    def __init__(self):
        self.配置文件 = Path(__file__).parent / '.config' / 'question_type_config.json'
        self.统计文件 = Path(__file__).parent / '.config' / 'recognition_stats.json'
        self.日志文件 = Path(__file__).parent / '.logs' / 'recognition.log'
        
        # 创建必要目录
        self.配置文件.parent.mkdir(exist_ok=True)
        self.统计文件.parent.mkdir(exist_ok=True)
        self.日志文件.parent.mkdir(exist_ok=True)
        
        # 初始化日志
        self._初始化日志系统()
        
        # 加载配置
        self.配置 = self._加载配置()
        self.统计 = self._加载统计()
        
        self.logger.info("确定度配置管理器初始化完成")
    
    def _初始化日志系统(self):
        """初始化日志系统"""
        self.logger = logging.getLogger('QuestionTypeRecognition')
        self.logger.setLevel(logging.INFO)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(self.日志文件, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理器（可选）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _加载配置(self) -> Dict:
        """加载配置文件"""
        默认配置 = {
            "题型特征": {
                "单选题": {
                    "确定度阈值": 70,
                    "特征权重": {
                        "有选项": 40,
                        "单字母答案": 30,
                        "单选关键词": 20,
                        "选项数量": 10
                    }
                },
                "多选题": {
                    "确定度阈值": 75,
                    "特征权重": {
                        "有选项": 35,
                        "多字母答案": 35,
                        "多选关键词": 20,
                        "选项数量": 10
                    }
                },
                "判断题": {
                    "确定度阈值": 60,
                    "特征权重": {
                        "判断答案": 40,
                        "判断关键词": 30,
                        "二选一选项": 20,
                        "是否表述": 10
                    }
                },
                "填空题": {
                    "确定度阈值": 65,
                    "特征权重": {
                        "填空标记": 35,
                        "数值答案": 25,
                        "单位答案": 20,
                        "填空关键词": 20
                    }
                },
                "简答题": {
                    "确定度阈值": 55,
                    "特征权重": {
                        "长答案": 30,
                        "简答关键词": 25,
                        "复杂内容": 25,
                        "无选项": 20
                    }
                }
            },
            "系统设置": {
                "启用性能监控": True,
                "启用详细日志": True,
                "自动调优": False,
                "最小确定度阈值": 50
            }
        }
        
        if self.配置文件.exists():
            try:
                with open(self.配置文件, 'r', encoding='utf-8') as f:
                    配置 = json.load(f)
                self.logger.info("配置文件加载成功")
                return 配置
            except Exception as e:
                self.logger.error(f"配置文件加载失败: {e}")
                return 默认配置
        else:
            # 创建默认配置文件
            self._保存配置(默认配置)
            return 默认配置
    
    def _保存配置(self, 配置: Dict):
        """保存配置文件"""
        try:
            with open(self.配置文件, 'w', encoding='utf-8') as f:
                json.dump(配置, f, ensure_ascii=False, indent=2)
            self.logger.info("配置文件保存成功")
        except Exception as e:
            self.logger.error(f"配置文件保存失败: {e}")
    
    def _加载统计(self) -> 识别统计:
        """加载统计数据"""
        if self.统计文件.exists():
            try:
                with open(self.统计文件, 'r', encoding='utf-8') as f:
                    数据 = json.load(f)
                return 识别统计(**数据)
            except Exception as e:
                self.logger.error(f"统计数据加载失败: {e}")
                return 识别统计()
        else:
            return 识别统计()
    
    def 保存统计(self):
        """保存统计数据"""
        try:
            with open(self.统计文件, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.统计), f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"统计数据保存失败: {e}")
    
    def 更新统计(self, 题型: str, 确定度: float, 耗时: float):
        """更新识别统计"""
        self.统计.总识别次数 += 1
        
        if "(低确定度)" not in 题型:
            self.统计.成功识别次数 += 1
        else:
            self.统计.低确定度次数 += 1
            题型 = 题型.replace("(低确定度)", "")
        
        # 更新各题型统计
        if 题型 not in self.统计.各题型识别次数:
            self.统计.各题型识别次数[题型] = 0
        self.统计.各题型识别次数[题型] += 1
        
        # 更新平均确定度
        总确定度 = self.统计.平均确定度 * (self.统计.总识别次数 - 1) + 确定度
        self.统计.平均确定度 = 总确定度 / self.统计.总识别次数
        
        # 更新耗时（保留最近100次）
        self.统计.识别耗时.append(耗时)
        if len(self.统计.识别耗时) > 100:
            self.统计.识别耗时 = self.统计.识别耗时[-100:]
        
        # 记录日志
        if self.配置["系统设置"]["启用详细日志"]:
            self.logger.info(f"识别完成: {题型}, 确定度: {确定度:.1f}%, 耗时: {耗时:.3f}s")
        
        # 定期保存统计数据
        if self.统计.总识别次数 % 10 == 0:
            self.保存统计()
    
    def 获取性能报告(self) -> Dict:
        """获取性能报告"""
        if not self.统计.识别耗时:
            return {"错误": "暂无性能数据"}
        
        平均耗时 = sum(self.统计.识别耗时) / len(self.统计.识别耗时)
        成功率 = (self.统计.成功识别次数 / self.统计.总识别次数 * 100) if self.统计.总识别次数 > 0 else 0
        
        return {
            "总识别次数": self.统计.总识别次数,
            "成功率": f"{成功率:.1f}%",
            "平均确定度": f"{self.统计.平均确定度:.1f}%",
            "平均耗时": f"{平均耗时:.3f}秒",
            "各题型分布": self.统计.各题型识别次数,
            "低确定度比例": f"{(self.统计.低确定度次数 / self.统计.总识别次数 * 100):.1f}%" if self.统计.总识别次数 > 0 else "0%"
        }
    
    def 调整阈值(self, 题型: str, 新阈值: int):
        """动态调整确定度阈值"""
        if 题型 in self.配置["题型特征"]:
            旧阈值 = self.配置["题型特征"][题型]["确定度阈值"]
            self.配置["题型特征"][题型]["确定度阈值"] = 新阈值
            self._保存配置(self.配置)
            self.logger.info(f"{题型}确定度阈值调整: {旧阈值} -> {新阈值}")
            return True
        return False
    
    def 重置统计(self):
        """重置统计数据"""
        self.统计 = 识别统计()
        self.保存统计()
        self.logger.info("统计数据已重置")

# 创建全局配置管理器
配置管理器 = 确定度配置管理器()
