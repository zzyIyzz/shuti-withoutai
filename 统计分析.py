#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统计分析模块
负责答题数据的统计和分析
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

class StatsAnalyzer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / '.data'
        self.data_dir.mkdir(exist_ok=True)
    
    def show_statistics(self):
        """显示统计信息"""
        records = self.load_history()
        
        if not records:
            print("暂无答题记录")
            return
        
        print(f"总答题次数: {len(records)}")
        
        # 正确率统计
        correct_count = sum(1 for r in records if r.get('is_correct'))
        accuracy = (correct_count / len(records)) * 100 if records else 0
        print(f"总正确率: {accuracy:.1f}% ({correct_count}/{len(records)})")
        
        # 按题库统计
        print("\n各题库统计:")
        by_source = defaultdict(lambda: {'total': 0, 'correct': 0})
        for r in records:
            source = r.get('source', '未知')
            by_source[source]['total'] += 1
            if r.get('is_correct'):
                by_source[source]['correct'] += 1
        
        for source, stats in sorted(by_source.items()):
            acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {source}: {acc:.1f}% ({stats['correct']}/{stats['total']})")
        
        # 最近7天统计
        print("\n最近7天答题:")
        recent_stats = self.get_recent_days_stats(records, 7)
        for day, stats in recent_stats:
            if stats['total'] > 0:
                acc = (stats['correct'] / stats['total'] * 100)
                print(f"  {day}: {stats['total']}题, 正确率{acc:.1f}%")
        
        # 错题统计
        wrong_file = self.data_dir / 'wrong_questions.json'
        if wrong_file.exists():
            try:
                with open(wrong_file, 'r', encoding='utf-8') as f:
                    wrong_questions = json.load(f)
                print(f"\n错题本: {len(wrong_questions)}题")
            except:
                pass
    
    def load_history(self):
        """加载历史记录"""
        history_file = self.data_dir / 'history.jsonl'
        
        if not history_file.exists():
            return []
        
        records = []
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        except:
            pass
        
        return records
    
    def get_recent_days_stats(self, records, days=7):
        """获取最近几天的统计"""
        today = datetime.now().date()
        stats_by_day = {}
        
        for i in range(days):
            day = today - timedelta(days=i)
            stats_by_day[day.isoformat()] = {'total': 0, 'correct': 0}
        
        for r in records:
            try:
                timestamp = datetime.fromisoformat(r.get('timestamp', ''))
                day_key = timestamp.date().isoformat()
                
                if day_key in stats_by_day:
                    stats_by_day[day_key]['total'] += 1
                    if r.get('is_correct'):
                        stats_by_day[day_key]['correct'] += 1
            except:
                continue
        
        return sorted(stats_by_day.items(), reverse=True)

