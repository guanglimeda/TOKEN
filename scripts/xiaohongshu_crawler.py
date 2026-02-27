#!/usr/bin/env python3
"""
小红书笔记爬取脚本
功能：根据关键词搜索小红书笔记，采集健康相关内容
"""

import requests
import json
import re
import time
import os
import random
from datetime import datetime
from urllib.parse import quote

class XiaoHongShuCrawler:
    def __init__(self):
        self.cookie = self._load_cookie()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://www.xiaohongshu.com',
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
    
    def search_notes(self, keyword, page=1, page_size=20):
        """搜索笔记"""
        url = 'https://www.xiaohongshu.com/api/sns/web/v1/search/notes'
        
        params = {
            'keyword': keyword,
            'page': page,
            'page_size': page_size,
            'sort': 'general',  # 综合排序
            'note_type': 'normal',
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"请求异常: {e}")
            return None
    
    def parse_note(self, note_item, keyword):
        """解析单条笔记数据"""
        try:
            note = note_item.get('note', {})
            user = note_item.get('user', {})
            
            # 基础信息
            parsed = {
                'keyword': keyword,
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'note_id': note.get('id', ''),
                'title': note.get('title', ''),
                'desc': note.get('desc', ''),
                'url': f"https://www.xiaohongshu.com/explore/{note.get('id', '')}",
                'author': user.get('nickname', ''),
                'author_id': user.get('user_id', ''),
                'likes': self._format_count(note.get('likes', 0)),
                'collects': self._format_count(note.get('collects', 0)),
                'comments': self._format_count(note.get('comments', 0)),
                'publish_time': note.get('time', ''),
                'tags': [tag.get('name', '') for tag in note.get('tag_list', [])],
            }
            
            # 内容分析（从标题和描述中提取）
            content = parsed['title'] + ' ' + parsed['desc']
            parsed['symptoms'] = self._extract_symptoms(content)
            parsed['triggers'] = self._extract_triggers(content)
            parsed['solutions'] = self._extract_solutions(content)
            parsed['products'] = self._extract_products(content)
            parsed['content_type'] = self._classify_content(content)
            parsed['target_audience'] = self._extract_audience(content)
            
            return parsed
        except Exception as e:
            print(f"解析笔记失败: {e}")
            return None
    
    def _format_count(self, count):
        """格式化数字"""
        if isinstance(count, str):
            return count
        if count >= 10000:
            return f"{count/10000:.1f}w"
        elif count >= 1000:
            return f"{count/1000:.1f}k"
        return str(count)
    
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
        return symptoms[:5]  # 最多返回5个
    
    def _extract_triggers(self, content):
        """提取诱因/场景"""
        triggers = []
        trigger_keywords = [
            '花粉', '尘螨', '冷空气', '空调', '换季', '春天', '秋天',
            '宠物', '灰尘', '雾霾', '食物', '药物', '压力', '熬夜',
            '运动', '接触', '吸入', '食用'
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
            '手术', '中医', '西医', '调理', '忌口', '运动', '休息',
            '戴口罩', '远离', '避免', '清洁', '消毒', '就医'
        ]
        for solution in solution_keywords:
            if solution in content:
                solutions.append(solution)
        return solutions[:5]
    
    def _extract_products(self, content):
        """提取产品/药品"""
        products = []
        # 常见药品/产品
        product_keywords = [
            '雷诺考特', '辅舒良', '内舒拿', '氯雷他定', '西替利嗪',
            '孟鲁司特', '布地奈德', '沙丁胺醇', '洗鼻器', '生理盐水',
            '鼻炎康', '通窍鼻炎片', '口罩', '空气净化器'
        ]
        for product in product_keywords:
            if product in content:
                products.append(product)
        return products[:5]
    
    def _classify_content(self, content):
        """分类内容类型"""
        if any(word in content for word in ['经验', '分享', '经历', '心得']):
            return '经验分享'
        elif any(word in content for word in ['科普', '知识', '医生', '专家']):
            return '科普知识'
        elif any(word in content for word in ['推荐', '种草', '好用', '测评']):
            return '种草推荐'
        elif any(word in content for word in ['求助', '怎么办', '请问']):
            return '求助问答'
        return '其他'
    
    def _extract_audience(self, content):
        """提取目标人群"""
        audiences = []
        audience_keywords = [
            ('宝宝', '婴幼儿'), ('孩子', '儿童'), ('孕妇', '孕妇'),
            ('妈妈', '宝妈'), ('老人', '老年人'), ('上班族', '上班族'),
            ('学生', '学生'), ('女性', '女性'), ('男性', '男性')
        ]
        for keyword, label in audience_keywords:
            if keyword in content:
                audiences.append(label)
        return audiences[:3]
    
    def crawl_keyword(self, keyword, target_count=100):
        """爬取指定关键词的笔记"""
        print(f"\n开始爬取关键词: {keyword}")
        print(f"目标数量: {target_count}条")
        
        all_notes = []
        page = 1
        max_pages = (target_count // 20) + 2  # 预留一些冗余
        
        while len(all_notes) < target_count and page <= max_pages:
            print(f"正在获取第 {page} 页...")
            
            result = self.search_notes(keyword, page=page)
            if not result or 'data' not in result:
                print("获取失败，可能Cookie已失效")
                break
            
            items = result['data'].get('items', [])
            if not items:
                print("没有更多数据了")
                break
            
            for item in items:
                if len(all_notes) >= target_count:
                    break
                
                parsed = self.parse_note(item, keyword)
                if parsed:
                    # 过滤低互动笔记
                    likes_str = parsed.get('likes', '0')
                    likes_num = self._parse_count(likes_str)
                    if likes_num >= 10:  # 点赞数>=10
                        all_notes.append(parsed)
                        print(f"  ✓ 已采集: {parsed['title'][:30]}... (点赞:{likes_str})")
                
                time.sleep(random.uniform(0.5, 1.5))  # 随机延迟
            
            page += 1
            time.sleep(random.uniform(1, 2))
        
        print(f"\n✅ 关键词 [{keyword}] 采集完成: {len(all_notes)} 条")
        return all_notes
    
    def _parse_count(self, count_str):
        """解析数字"""
        if not count_str:
            return 0
        count_str = str(count_str).lower()
        if 'w' in count_str:
            return int(float(count_str.replace('w', '')) * 10000)
        elif 'k' in count_str:
            return int(float(count_str.replace('k', '')) * 1000)
        try:
            return int(count_str)
        except:
            return 0
    
    def save_data(self, notes, keyword):
        """保存数据"""
        if not notes:
            return
        
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
    
    def generate_summary(self, notes, keyword):
        """生成汇总报告"""
        if not notes:
            return None
        
        # 统计
        total = len(notes)
        
        # 症状统计
        symptom_count = {}
        for note in notes:
            for s in note.get('symptoms', []):
                symptom_count[s] = symptom_count.get(s, 0) + 1
        top_symptoms = sorted(symptom_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 解决方案统计
        solution_count = {}
        for note in notes:
            for s in note.get('solutions', []):
                solution_count[s] = solution_count.get(s, 0) + 1
        top_solutions = sorted(solution_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 产品统计
        product_count = {}
        for note in notes:
            for p in note.get('products', []):
                product_count[p] = product_count.get(p, 0) + 1
        top_products = sorted(product_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 生成Markdown
        lines = [f"# {keyword} - 数据报告"]
        lines.append(f"**采集时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**样本数量**: {total}条笔记\n")
        
        lines.append("## 热门症状提及")
        lines.append("| 症状 | 提及次数 | 占比 |")
        lines.append("|------|----------|------|")
        for symptom, count in top_symptoms:
            pct = count / total * 100
            lines.append(f"| {symptom} | {count} | {pct:.1f}% |")
        lines.append("")
        
        lines.append("## 热门解决方案")
        lines.append("| 方案 | 提及次数 | 占比 |")
        lines.append("|------|----------|------|")
        for solution, count in top_solutions:
            pct = count / total * 100
            lines.append(f"| {solution} | {count} | {pct:.1f}% |")
        lines.append("")
        
        lines.append("## 热门产品提及")
        lines.append("| 产品 | 提及次数 | 占比 |")
        lines.append("|------|----------|------|")
        for product, count in top_products:
            pct = count / total * 100
            lines.append(f"| {product} | {count} | {pct:.1f}% |")
        lines.append("")
        
        lines.append("## 高互动笔记TOP5")
        sorted_notes = sorted(notes, key=lambda x: self._parse_count(x.get('likes', '0')), reverse=True)[:5]
        for i, note in enumerate(sorted_notes, 1):
            lines.append(f"{i}. [{note['title']}]({note['url']})")
            lines.append(f"   - 作者: {note['author']}")
            lines.append(f"   - 点赞: {note['likes']} | 收藏: {note['collects']} | 评论: {note['comments']}")
            lines.append("")
        
        # 保存
        processed_dir = '/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/processed'
        os.makedirs(processed_dir, exist_ok=True)
        
        filename = f"{keyword}_summary.md"
        filepath = os.path.join(processed_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ 报告已生成: {filepath}")
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
            crawler.generate_summary(notes, keyword)
        print("\n" + "-"*60)
        time.sleep(5)  # 关键词间隔
    
    print("\n" + "="*60)
    print("✅ 所有关键词爬取完成")
    print("="*60)


if __name__ == '__main__':
    main()
