#!/usr/bin/env python3
"""
小红书实时爬取脚本
使用 Playwright + Chrome + Cookie
"""
import asyncio
import json
from playwright.async_api import async_playwright

# 请把你的小红书 Cookie 粘贴到这里
XIAOHONGSHU_COOKIES = [
    # 格式示例：
    # {"name": "webId", "value": "xxx", "domain": ".xiaohongshu.com"},
    # {"name": "xhsTracker", "value": "xxx", "domain": ".xiaohongshu.com"},
    # {"name": "sessionId", "value": "xxx", "domain": ".xiaohongshu.com"},
]

async def crawl_xiaohongshu(keyword, cookies=None):
    """
    爬取小红书搜索结果
    """
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800}
        )
        
        # 添加 Cookie
        if cookies:
            await context.add_cookies(cookies)
        
        page = await context.new_page()
        
        try:
            # 访问小红书搜索页
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
            print(f"正在访问: {search_url}")
            
            await page.goto(search_url, wait_until='networkidle', timeout=60000)
            await page.wait_for_timeout(5000)  # 等待内容加载
            
            # 提取笔记数据
            notes = await page.evaluate('''() => {
                const items = [];
                const cards = document.querySelectorAll('[class*="note-item"], [class*="feeds-page"], .note-card, a[href*="/explore/"]');
                
                cards.forEach((card, index) => {
                    if (index >= 20) return;
                    
                    const titleEl = card.querySelector('.title, h3, .note-title, a[title]');
                    const linkEl = card.querySelector('a[href*="/explore/"]');
                    const authorEl = card.querySelector('.author, .user-name');
                    const likeEl = card.querySelector('.like-count, .count');
                    
                    if (titleEl || linkEl) {
                        items.push({
                            title: titleEl?.textContent?.trim() || titleEl?.getAttribute('title') || '无标题',
                            url: linkEl?.href || '',
                            author: authorEl?.textContent?.trim() || '未知',
                            likes: likeEl?.textContent?.trim() || ''
                        });
                    }
                });
                
                return items;
            }''')
            
            await browser.close()
            
            return {
                "keyword": keyword,
                "timestamp": asyncio.get_event_loop().time(),
                "count": len(notes),
                "notes": notes
            }
            
        except Exception as e:
            await browser.close()
            raise e

def main():
    # 检查是否有 Cookie
    if not XIAOHONGSHU_COOKIES or len(XIAOHONGSHU_COOKIES) == 0:
        print("请先配置小红书 Cookie")
        print("获取方法：")
        print("1. 登录小红书网页版")
        print("2. 打开浏览器开发者工具 (F12)")
        print("3. 切换到 Application/应用 → Cookies")
        print("4. 复制 xiaohongshu.com 下的关键 Cookie")
        return
    
    # 爬取关键词
    keyword = "花粉过敏"  # 可以修改
    
    print(f"开始爬取关键词: {keyword}")
    result = asyncio.run(crawl_xiaohongshu(keyword, XIAOHONGSHU_COOKIES))
    
    # 保存结果
    output_file = f"/root/.openclaw/workspace/xhs_{keyword}_{int(asyncio.get_event_loop().time())}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"爬取完成，保存到: {output_file}")
    print(f"共获取 {result['count']} 条笔记")
    
    # 打印前5条
    for i, note in enumerate(result['notes'][:5], 1):
        print(f"{i}. {note['title']} - {note['author']}")

if __name__ == "__main__":
    main()
