#!/usr/bin/env python3
"""
小红书流行病词条真实数据采集脚本
使用Playwright + Cookie登录方式
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path

# 尝试导入playwright
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright未安装，使用requests方式")

# 配置
COOKIE_FILE = "/root/.openclaw/workspace/config/xiaohongshu_cookie.txt"
OUTPUT_DIR = "/root/.openclaw/workspace/knowledge/xiaohongshu_epidemic/raw"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# 呼吸系统关键词列表（P0优先级）
KEYWORDS_P0 = [
    "过敏性鼻炎",
    "花粉过敏", 
    "哮喘",
    "流感",
    "甲流",
    "支原体肺炎"
]

# 更多呼吸系统关键词（P1优先级）
KEYWORDS_P1 = [
    "咳嗽变异性哮喘",
    "鼻窦炎",
    "鼻病毒",
    "乙流",
    "呼吸道合胞病毒",
    "腺病毒",
    "慢性咽炎",
    "扁桃体炎"
]

def load_cookies():
    """加载Cookie"""
    with open(COOKIE_FILE, 'r') as f:
        cookie_str = f.read().strip()
    
    cookies = []
    for item in cookie_str.split(';'):
        item = item.strip()
        if '=' in item:
            name, value = item.split('=', 1)
            cookies.append({
                'name': name,
                'value': value,
                'domain': '.xiaohongshu.com',
                'path': '/'
            })
    return cookies

def crawl_with_playwright(keyword, max_notes=100):
    """使用Playwright爬取小红书数据"""
    if not PLAYWRIGHT_AVAILABLE:
        return None
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        # 添加Cookie
        cookies = load_cookies()
        context.add_cookies(cookies)
        
        page = context.new_page()
        
        try:
            # 访问搜索页面
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&type=51"
            print(f"🔍 正在搜索: {keyword}")
            page.goto(search_url, wait_until='networkidle', timeout=60000)
            
            # 等待内容加载
            time.sleep(3)
            
            # 滚动加载更多内容
            for i in range(5):
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(2)
                print(f"  滚动加载... {i+1}/5")
            
            # 提取笔记数据
            notes = page.evaluate('''() => {
                const items = document.querySelectorAll('[data-testid="note-item"]');
                const data = [];
                items.forEach(item => {
                    const titleEl = item.querySelector('.title');
                    const authorEl = item.querySelector('.author');
                    const likeEl = item.querySelector('.like-count');
                    
                    if (titleEl) {
                        data.push({
                            title: titleEl.textContent?.trim() || '',
                            author: authorEl?.textContent?.trim() || '',
                            likes: likeEl?.textContent?.trim() || '0'
                        });
                    }
                });
                return data;
            }''')
            
            results = notes[:max_notes]
            print(f"✅ 成功获取 {len(results)} 条笔记")
            
        except Exception as e:
            print(f"❌ 爬取失败: {e}")
        finally:
            browser.close()
    
    return results

def save_results(keyword, results):
    """保存结果到JSON文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{keyword}_{timestamp}_{len(results)}.json"
    filepath = Path(OUTPUT_DIR) / filename
    
    data = {
        'keyword': keyword,
        'crawl_time': datetime.now().isoformat(),
        'total_count': len(results),
        'notes': results
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 数据已保存: {filepath}")
    return filepath

def main():
    """主函数"""
    print("="*60)
    print("小红书流行病词条数据采集")
    print("="*60)
    
    # 检查Cookie
    if not Path(COOKIE_FILE).exists():
        print(f"❌ Cookie文件不存在: {COOKIE_FILE}")
        return
    
    print(f"✅ Cookie文件已加载")
    
    # 先采集P0关键词
    print(f"\n🎯 开始采集P0优先级关键词（共{len(KEYWORDS_P0)}个）")
    
    for i, keyword in enumerate(KEYWORDS_P0, 1):
        print(f"\n[{i}/{len(KEYWORDS_P0)}] {keyword}")
        print("-"*40)
        
        if PLAYWRIGHT_AVAILABLE:
            results = crawl_with_playwright(keyword, max_notes=100)
            if results:
                save_results(keyword, results)
        else:
            print("⚠️ Playwright未安装，跳过真实爬取")
        
        # 随机延迟，避免被封
        delay = random.uniform(3, 6)
        print(f"⏳ 等待 {delay:.1f} 秒...")
        time.sleep(delay)
    
    print("\n" + "="*60)
    print("✅ P0关键词采集完成")
    print("="*60)

if __name__ == '__main__':
    main()
