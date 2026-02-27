#!/usr/bin/env python3
"""
小红书笔记爬取脚本 - 使用网页版API
功能：根据关键词搜索小红书笔记，采集健康相关内容
"""

import requests
import json
import re
import time
import os
import random
from datetime import datetime
from urllib.parse import quote, urlencode

class XiaoHongShuCrawler:
    def __init__(self):
        self.cookie = self._load_cookie()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.xiaohongshu.com/',
            'Cookie': self.cookie,
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def _load_cookie(self):
        """加载Cookie"""
        try:
            with open('/root/.openclaw/workspace/config/xiaohongshu_cookie.txt', 'r') as f:
                return f.read().strip()
        except Exception as e:
            print(f"读取Cookie失败: {e}")
            return None
    
    def search_notes_feed(self, keyword, cursor=None):
        """使用feed接口搜索笔记"""
        # 小红书网页版搜索API
        url = 'https://www.xiaohongshu.com/api/sns/web/v1/search/notes'
        
        params = {
            'keyword': keyword,
            'page': 1,
            'page_size': 20,
            'sort': 'general',
            'note_type': 'normal',
        }
        
        if cursor:
            params['cursor'] = cursor
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            print(f"请求URL: {response.url}")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    return response.json()
                except:
                    print(f"解析JSON失败: {response.text[:500]}")
                    return None
            else:
                print(f"请求失败: {response.text[:500]}")
                return None
        except Exception as e:
            print(f"请求异常: {e}")
            return None
    
    def search_via_explore(self, keyword):
        """通过explore页面获取"""
        encoded_keyword = quote(keyword)
        url = f'https://www.xiaohongshu.com/search_result?keyword={encoded_keyword}'
        
        try:
            response = self.session.get(url, timeout=15)
            print(f"Explore页面状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 从HTML中提取初始数据
                # 小红书通常在window.__INITIAL_STATE__中嵌入数据
                match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?});', response.text)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        return data
                    except:
                        pass
                
                # 备选：提取其他数据格式
                match2 = re.search(r'window\._SSR_HYDRATED_DATA\s*=\s*({.+?})<', response.text)
                if match2:
                    try:
                        data = json.loads(match2.group(1))
                        return data
                    except:
                        pass
            return None
        except Exception as e:
            print(f"请求异常: {e}")
            return None
    
    def parse_note_from_html(self, html_content, keyword):
        """从HTML内容中解析笔记"""
        notes = []
        
        # 尝试多种模式提取笔记数据
        # 模式1: 从JSON数据中提取
        json_patterns = [
            r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
            r'window\._SSR_HYDRATED_DATA\s*=\s*({.+?})<',
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, html_content, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    # 根据数据结构提取笔记
                    # 这里需要根据实际返回结构调整
                    print(f"找到JSON数据，结构: {list(data.keys())[:10]}")
                    return self._extract_notes_from_json(data, keyword)
                except Exception as e:
                    print(f"解析JSON失败: {e}")
                    continue
        
        return notes
    
    def _extract_notes_from_json(self, data, keyword):
        """从JSON数据中提取笔记列表"""
        notes = []
        
        # 尝试不同的数据路径
        possible_paths = [
            ['search', 'notes'],
            ['searchResult', 'notes'],
            ['note', 'noteList'],
            ['main', 'notes'],
        ]
        
        for path in possible_paths:
            current = data
            found = True
            for key in path:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    found = False
                    break
            
            if found and isinstance(current, list):
                print(f"找到笔记列表，数量: {len(current)}")
                for item in current:
                    note = self._parse_note_item(item, keyword)
                    if note:
                        notes.append(note)
                break
        
        return notes
    
    def _parse_note_item(self, item, keyword):
        """解析单个笔记项"""
        try:
            # 处理不同的数据结构
            note_data = item.get('note', item)  # 有些包裹在note里，有些直接是note
            
            note = {
                'keyword': keyword,
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'note_id': note_data.get('id', note_data.get('note_id', '')),
                'title': note_data.get('title', ''),
                'desc': note_data.get('desc', note_data.get('content', '')),
                'url': f"https://www.xiaohongshu.com/explore/{note_data.get('id', note_data.get('note_id', ''))}",
                'author': note_data.get('user', {}).get('nickname', '') if isinstance(note_data.get('user'), dict) else '',
                'likes': str(note_data.get('likes', note_data.get('like_count', 0))),
                'collects': str(note_data.get('collects', note_data.get('collect_count', 0))),
                'comments': str(note_data.get('comments', note_data.get('comment_count', 0))),
                'publish_time': note_data.get('time', note_data.get('create_time', '')),
            }
            
            # 内容分析
            content = note['title'] + ' ' + note['desc']
            note['symptoms'] = self._extract_symptoms(content)
            note['triggers'] = self._extract_triggers(content)
            note['solutions'] = self._extract_solutions(content)
            note['products'] = self._extract_products(content)
            
            return note
        except Exception as e:
            print(f"解析笔记项失败: {e}")
            return None
    
    def _extract_symptoms(self, content):
        """提取症状关键词"""
        symptoms = []
        symptom_keywords = [
            '喷嚏', '鼻痒', '流鼻涕', '鼻塞', '咳嗽', '发烧', '发热', 
            '头痛', '头晕', '乏力', '喉咙痛', '咽痛', '呼吸困难', '喘息',
            '皮疹', '瘙痒', '红肿', '腹泻', '呕吐', '恶心', '腹痛'
        ]
        for symptom in symptom_keywords:
            if symptom in content:
                symptoms.append(symptom)
        return symptoms[:5]
    
    def _extract_triggers(self, content):
        """提取诱因/场景"""
        triggers = []
        trigger_keywords = [
            '花粉', '尘螨', '冷空气', '空调', '换季', '春天', '秋天',
            '宠物', '灰尘', '雾霾', '食物', '药物', '压力', '熬夜'
        ]
        for trigger in trigger_keywords:
            if trigger in content:
                triggers.append(trigger)
        return triggers[:5]
    
    def _extract_solutions(self, content):
        """提取解决方案"""
        solutions = []
        solution_keywords = [
            '吃药', '用药', '喷雾', '冲洗', '洗鼻', '雾化', '打针',
            '手术', '中医', '西医', '调理', '忌口', '运动', '休息'
        ]
        for solution in solution_keywords:
            if solution in content:
                solutions.append(solution)
        return solutions[:5]
    
    def _extract_products(self, content):
        """提取产品/药品"""
        products = []
        product_keywords = [
            '雷诺考特', '辅舒良', '内舒拿', '氯雷他定', '西替利嗪',
            '孟鲁司特', '布地奈德', '洗鼻器', '生理盐水', '鼻炎康'
        ]
        for product in product_keywords:
            if product in content:
                products.append(product)
        return products[:5]
    
    def crawl_keyword(self, keyword, target_count=100):
        """爬取指定关键词的笔记"""
        print(f"\n开始爬取关键词: {keyword}")
        print(f"目标数量: {target_count}条")
        
        all_notes = []
        
        # 方法1: 通过explore页面获取
        print("\n尝试方法1: Explore页面...")
        html_content = self.search_via_explore(keyword)
        if html_content:
            notes = self.parse_note_from_html(html_content, keyword)
            all_notes.extend(notes)
            print(f"方法1获取: {len(notes)} 条")
        
        print(f"\n✅ 关键词 [{keyword}] 采集完成: {len(all_notes)} 条")
        return all_notes
    
    def save_data(self, notes, keyword):
        """保存数据"""
        if not notes:
            print(f"关键词 [{keyword}] 没有数据，跳过保存")
            return None
        
        # 确保目录存在
        raw_dir = '/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/raw'
        os.makedirs(raw_dir, exist_ok=True)
        
        # 文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{keyword}_{timestamp}_{len(notes)}.json"
        filepath = os.path.join(raw_dir, filename)
        
        # 保存JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据已保存: {filepath}")
        return filepath


def main():
    # 第一批P0关键词
    keywords = ['过敏性鼻炎', '花粉过敏', '流感']
    
    crawler = XiaoHongShuCrawler()
    
    if not crawler.cookie:
        print("❌ Cookie加载失败，请检查配置文件")
        return
    
    print("="*60)
    print("小红书流行病词条爬取任务")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    for keyword in keywords:
        notes = crawler.crawl_keyword(keyword, target_count=100)
        if notes:
            crawler.save_data(notes, keyword)
        print("\n" + "-"*60)
        time.sleep(3)
    
    print("\n" + "="*60)
    print("✅ 所有关键词爬取完成")
    print("="*60)


if __name__ == '__main__':
    main()
