#!/usr/bin/env python3
"""
微博健康热搜监测脚本 - 每小时执行
功能：
1. 爬取微博热搜
2. 筛选健康相关话题
3. 发送到钉钉群
4. 记录到知识库
"""

import requests
import re
import json
import sys
import os
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
        
        # 检查是否是娱乐内容
        is_entertainment = False
        for exclude in EXCLUDE_KEYWORDS:
            if exclude in title or exclude in hot_count:
                is_entertainment = True
                break
        
        if not is_entertainment:
            health_topics.append(item)
    
    return health_topics

def save_to_knowledge_base(health_topics):
    """保存到知识库"""
    if not health_topics:
        return
    
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M')
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    
    # 确保知识库目录存在
    kb_dir = '/root/.openclaw/workspace/knowledge/weibo_hotsearch'
    os.makedirs(kb_dir, exist_ok=True)
    
    # 按日期存储
    kb_file = f'{kb_dir}/{date_str}.md'
    
    # 读取现有内容
    existing_content = ""
    if os.path.exists(kb_file):
        with open(kb_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    # 构建新记录
    new_records = []
    new_records.append(f"\n## {time_str} 健康热搜\n")
    new_records.append(f"**采集时间**: {timestamp}\n")
    new_records.append("| 排名 | 话题 | 链接 | 热度 |")
    new_records.append("|------|------|------|------|")
    
    for topic in health_topics:
        rank = topic['rank']
        title = topic['title']
        link = topic['link']
        hot = topic.get('hot_count', '')
        new_records.append(f"| {rank} | {title} | [{link}]({link}) | {hot} |")
    
    new_content = '\n'.join(new_records)
    
    # 如果是新文件，添加标题
    if not existing_content:
        existing_content = f"# 微博健康热搜记录 - {date_str}\n"
    
    # 追加新记录
    with open(kb_file, 'w', encoding='utf-8') as f:
        f.write(existing_content + new_content + '\n')
    
    print(f"✅ 已记录到知识库: {kb_file}")
    return kb_file

def format_dingtalk_message(health_topics, all_count=0):
    """格式化钉钉消息"""
    if not health_topics:
        return None
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    lines = [f"📊 微博健康热搜（{now}）\n"]
    lines.append(f"共监测 {all_count} 条热搜，发现 {len(health_topics)} 条健康相关\n")
    
    for i, topic in enumerate(health_topics[:10], 1):
        lines.append(f"{i}. #{topic['title']}#")
        lines.append(f"   排名：第{topic['rank']}位")
        lines.append(f"   链接：{topic['link']}")
        if topic.get('hot_count'):
            lines.append(f"   热度：{topic['hot_count']}")
        lines.append("")
    
    return '\n'.join(lines)

def send_to_dingtalk(message):
    """发送到钉钉群"""
    if not message:
        return
    
    # 使用 OpenClaw 的消息发送机制
    # 这里通过写入文件，由调用者处理发送
    msg_file = '/root/.openclaw/workspace/data/last_hotsearch_message.txt'
    with open(msg_file, 'w', encoding='utf-8') as f:
        f.write(message)
    print(f"✅ 消息已准备: {msg_file}")

def main():
    print("="*60)
    print("微博健康热搜监测任务")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 1. 获取热搜
    html = fetch_weibo_hotsearch()
    if not html:
        print("\n❌ 获取失败，Cookie 可能已失效")
        # 记录失败日志
        log_file = '/root/.openclaw/workspace/data/hotsearch_error.log'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Cookie失效\n")
        sys.exit(1)
    
    # 2. 解析数据
    print("\n解析热搜数据...")
    hot_list = parse_hotsearch(html)
    print(f"共获取 {len(hot_list)} 条热搜")
    
    # 3. 筛选健康话题
    health_topics = filter_health_topics(hot_list)
    print(f"找到 {len(health_topics)} 条健康相关热搜")
    
    # 4. 记录到知识库
    if health_topics:
        kb_file = save_to_knowledge_base(health_topics)
    
    # 5. 准备钉钉消息
    message = format_dingtalk_message(health_topics, len(hot_list))
    if message:
        send_to_dingtalk(message)
        print("\n" + "="*60)
        print(message)
        print("="*60)
    else:
        print("\n本轮暂无健康相关热搜")
    
    # 6. 保存原始数据
    raw_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total': len(hot_list),
        'health_count': len(health_topics),
        'health_topics': health_topics
    }
    raw_file = f"/root/.openclaw/workspace/data/raw_hotsearch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 任务完成")
    print(f"   - 原始数据: {raw_file}")
    if health_topics:
        print(f"   - 知识库: {kb_file}")

if __name__ == '__main__':
    main()
