#!/usr/bin/env python3
"""
社媒数据抓取工具
支持：小红书、微博
"""

import requests
import json
import time
import re
from datetime import datetime
from urllib.parse import quote, urlparse

class SocialMediaCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
    # ============ 小红书 ============
    
    def xhs_search(self, keyword, page=1):
        """小红书搜索笔记"""
        url = f"https://www.xiaohongshu.com/search_result?keyword={quote(keyword)}&page={page}"
        
        try:
            response = self.session.get(url, timeout=10)
            # 提取笔记数据（需要登录态才能获取完整数据）
            notes = self._extract_xhs_notes(response.text)
            return notes
        except Exception as e:
            print(f"小红书搜索失败: {e}")
            return []
    
    def _extract_xhs_notes(self, html):
        """从HTML中提取小红书笔记"""
        # 实际实现需要解析JSON数据或API
        # 这里返回示例结构
        return [{
            'note_id': '',
            'title': '',
            'content': '',
            'likes': 0,
            'author': '',
            'url': ''
        }]
    
    def xhs_note_detail(self, note_id):
        """获取小红书笔记详情"""
        url = f"https://www.xiaohongshu.com/explore/{note_id}"
        try:
            response = self.session.get(url, timeout=10)
            return self._parse_xhs_detail(response.text)
        except Exception as e:
            print(f"获取笔记详情失败: {e}")
            return None
    
    def _parse_xhs_detail(self, html):
        """解析笔记详情"""
        # 提取标题、内容、互动数据
        return {
            'title': '',
            'content': '',
            'likes': 0,
            'comments': 0,
            'collects': 0,
            'tags': [],
            'publish_time': ''
        }
    
    # ============ 微博 ============
    
    def weibo_hot_search(self):
        """获取微博热搜榜"""
        url = "https://weibo.com/ajax/side/hotSearch"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://weibo.com/',
            'Accept': 'application/json, text/plain, */*'
        }
        try:
            response = self.session.get(url, headers=headers, timeout=10)
            data = response.json()
            return self._parse_weibo_hot(data)
        except Exception as e:
            print(f"获取微博热搜失败: {e}")
            return []
    
    def _parse_weibo_hot(self, data):
        """解析热搜数据"""
        hot_list = []
        if 'data' in data and 'realtime' in data['data']:
            for item in data['data']['realtime'][:50]:
                hot_list.append({
                    'rank': item.get('rank', 0),
                    'topic': item.get('word', ''),
                    'hot_value': item.get('raw_hot', 0),
                    'category': item.get('category', ''),
                    'url': f"https://s.weibo.com/weibo?q={quote(item.get('word', ''))}"
                })
        return hot_list
    
    def weibo_search(self, keyword, page=1):
        """微博搜索"""
        url = f"https://weibo.com/ajax/search/all?value={quote(keyword)}&page={page}"
        try:
            response = self.session.get(url, timeout=10)
            return response.json()
        except Exception as e:
            print(f"微博搜索失败: {e}")
            return {}
    
    # ============ 健康话题监测 ============
    
    def monitor_health_topics(self):
        """监测健康相关话题"""
        health_keywords = [
            '鼻炎', '过敏性鼻炎', '哮喘', '过敏',
            '种植牙', '牙齿矫正', '近视手术',
            '流感', '感冒', '发烧'
        ]
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'weibo_hot': [],
            'xhs_notes': []
        }
        
        # 获取微博热搜中的健康话题
        hot_list = self.weibo_hot_search()
        for item in hot_list:
            if any(kw in item['topic'] for kw in health_keywords):
                results['weibo_hot'].append(item)
        
        return results
    
    def save_results(self, data, filename):
        """保存结果到JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存: {filename}")


# ============ 使用示例 ============

if __name__ == '__main__':
    crawler = SocialMediaCrawler()
    
    # 示例1：获取微博热搜
    print("=== 微博热搜（前10）===")
    hot_list = crawler.weibo_hot_search()
    for item in hot_list[:10]:
        print(f"{item['rank']}. {item['topic']} - 热度:{item['hot_value']}")
    
    # 示例2：监测健康话题
    print("\n=== 健康话题监测 ===")
    health_data = crawler.monitor_health_topics()
    print(f"发现 {len(health_data['weibo_hot'])} 个健康相关热搜")
    
    # 保存数据
    crawler.save_results(health_data, f"/tmp/health_monitor_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
