#!/usr/bin/env python3
"""
微博热搜获取脚本 - 使用 Cookie 认证
筛选健康相关话题，排除娱乐/综艺误匹配
"""

import requests
import re
import json
import sys
from datetime import datetime
from urllib.parse import unquote

# 健康相关关键词
HEALTH_KEYWORDS = [
    '健康', '医疗', '医院', '医生', '疾病', '病症', '症状', '治疗', '手术',
    '养生', '保健', '营养', '饮食', '减肥', '健身', '运动', '睡眠', '心理',
    '癌症', '肿瘤', '糖尿病', '高血压', '心脏病', '感冒', '发烧', '流感',
    '疫苗', '接种', '过敏', '鼻炎', '哮喘', '近视', '眼科', '牙科', '口腔',
    '体检', '检查', '诊断', '药物', '药品', '中医', '西医', '护理', '康复',
    '新冠', '病毒', '感染', '传染', '免疫力', '维生素', '蛋白', '脂肪', '糖',
    '猝死', '急救', '医保', '医药', '卫生', '口罩', '防护', '消毒', '杀菌',
    '抑郁', '焦虑', '精神', '失眠', '头痛', '胃痛', '咳嗽', '发烧', '发热',
    '卫健委', '急救中心', '结石', '肾', '肝', '胃', '肺', '心', '脑', '血',
    '孕', '胎', '婴', '儿', '老', '病', '痛', '药', '诊', '疗'
]

# 排除关键词（娱乐/综艺等）
EXCLUDE_KEYWORDS = [
    '恋综', '综艺', '电视剧', '电影', '明星', '演员', '歌手', '偶像',
    'CP', '恋爱', '分手', '结婚', '离婚', '出轨', '爆料', '路透',
    '直播', '网红', '主播', '粉丝', '应援', '打榜', '投票', '选秀'
]

def load_cookie():
    """从文件加载 Cookie"""
    try:
        with open('/root/.openclaw/workspace/config/weibo_cookie.txt', 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"读取 Cookie 失败: {e}")
        return None

def fetch_weibo_hotsearch():
    """获取微博热搜榜"""
    cookie = load_cookie()
    if not cookie:
        return None
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cookie': cookie,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://weibo.com/',
        'Connection': 'keep-alive',
    }
    
    try:
        session = requests.Session()
        session.headers.update(headers)
        
        url = 'https://s.weibo.com/top/summary?cate=realtimehot'
        response = session.get(url, timeout=15, allow_redirects=True)
        response.encoding = 'utf-8'
        
        if 'passport.weibo.com' in response.url:
            print("Cookie 已失效或需要重新登录")
            return None
        
        return response.text
    except Exception as e:
        print(f"请求异常: {e}")
        return None

def parse_hotsearch(html):
    """解析热搜数据"""
    if not html:
        return []
    
    hot_list = []
    
    # 根据实际 HTML 结构解析
    pattern = r'<tr[^>]*>\s*<td[^>]*class=["\']td-01[^"\']*["\'][^>]*>\s*(?:<i[^>]*>)?([^\s<]*)(?:</i>)?\s*</td>\s*<td[^>]*class=["\']td-02["\'][^>]*>\s*<a[^\u003e]*href=["\']([^"\']+)["\'][^\u003e]*target=["\']_blank["\'][^\u003e]*>([^\u003c]+)</a>\s*(?:<i[^>]*>[^\u003c]*</i>)?\s*(?:<span[^\u003e]*>([^\u003c]*)\u003c/span>)?\s*</td>'
    
    matches = re.findall(pattern, html, re.DOTALL)
    
    for match in matches:
        rank, link, title, hot_count = match
        rank = rank.strip()
        title = title.strip()
        hot_count = hot_count.strip() if hot_count else ''
        
        # 处理排名（可能是 "icon-top" 或数字）
        if not rank or 'icon' in rank:
            rank = '置顶'
        
        # 确保链接完整
        if link.startswith('/'):
            link = f'https://s.weibo.com{link}'
        elif not link.startswith('http'):
            link = f'https://s.weibo.com/weibo?q={link}'
        
        if title:
            hot_list.append({
                'rank': rank,
                'title': title,
                'link': link,
                'hot_count': hot_count
            })
    
    return hot_list

def filter_health_topics(hot_list):
    """筛选健康相关话题，排除娱乐内容"""
    health_topics = []
    
    for item in hot_list:
        title = item.get('title', '')
        hot_count = item.get('hot_count', '')
        
        # 检查是否包含健康关键词
        is_health = False
        for keyword in HEALTH_KEYWORDS:
            if keyword in title:
                is_health = True
                break
        
        if not is_health:
            continue
        
        # 检查是否是娱乐内容（标题或热度标签中包含综艺等关键词）
        is_entertainment = False
        for exclude in EXCLUDE_KEYWORDS:
            if exclude in title or exclude in hot_count:
                is_entertainment = True
                break
        
        if not is_entertainment:
            health_topics.append(item)
    
    return health_topics

def format_output(health_topics, all_count=0):
    """格式化输出"""
    if not health_topics:
        return "本轮暂无健康相关热搜"
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    output = [f"📊 微博健康热搜（{now}）"]
    output.append(f"共监测 {all_count} 条热搜，发现 {len(health_topics)} 条健康相关\n")
    
    for i, topic in enumerate(health_topics[:10], 1):
        output.append(f"{i}. #{topic['title']}#")
        output.append(f"   排名：第{topic['rank']}位")
        output.append(f"   链接：{topic['link']}")
        if topic.get('hot_count'):
            output.append(f"   热度：{topic['hot_count']}")
        output.append("")
    
    return '\n'.join(output)

def main():
    print("="*50)
    print("微博健康热搜监测")
    print("="*50)
    
    html = fetch_weibo_hotsearch()
    
    if not html:
        print("\n❌ 获取失败，Cookie 可能已失效")
        print("请更新 Cookie 后重试")
        sys.exit(1)
    
    print("\n解析热搜数据...")
    hot_list = parse_hotsearch(html)
    
    if not hot_list:
        # 保存 HTML 用于调试
        debug_file = '/root/.openclaw/workspace/data/weibo_debug.html'
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(html[:50000])
        print(f"未解析到热搜数据，HTML 已保存到: {debug_file}")
    
    print(f"共获取 {len(hot_list)} 条热搜")
    
    health_topics = filter_health_topics(hot_list)
    print(f"找到 {len(health_topics)} 条健康相关热搜")
    
    output = format_output(health_topics, len(hot_list))
    print("\n" + "="*50)
    print(output)
    print("="*50)
    
    # 保存结果到文件
    result_file = '/root/.openclaw/workspace/data/weibo_health_hotsearch.txt'
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(output)
    print(f"\n✅ 结果已保存到: {result_file}")

if __name__ == '__main__':
    main()
