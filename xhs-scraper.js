#!/usr/bin/env node
/**
 * Xiaohongshu Search Scraper
 * Uses Playwright to fetch real-time hot content
 */
const { chromium } = require('playwright');

async function searchXiaohongshu(keyword) {
    const browser = await chromium.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport: { width: 1280, height: 800 }
    });
    
    const page = await context.newPage();
    
    try {
        // Navigate to Xiaohongshu search
        const searchUrl = `https://www.xiaohongshu.com/search_result?keyword=${encodeURIComponent(keyword)}`;
        console.error(`Navigating to: ${searchUrl}`);
        
        await page.goto(searchUrl, { waitUntil: 'networkidle', timeout: 60000 });
        
        // Wait for content to load
        await page.waitForTimeout(5000);
        
        // Extract note data
        const notes = await page.evaluate(() => {
            const results = [];
            const cards = document.querySelectorAll('[class*="note-item"], [class*="feeds-page"], .note-card, [data-v-]');
            
            cards.forEach((card, index) => {
                if (index >= 20) return; // Limit to 20 results
                
                const titleEl = card.querySelector('a[title], .title, h3, .note-title');
                const linkEl = card.querySelector('a[href]');
                const authorEl = card.querySelector('.author, .user-name, [class*="author"]');
                const likeEl = card.querySelector('.like-count, .count, [class*="like"]');
                const imgEl = card.querySelector('img');
                
                if (titleEl || linkEl) {
                    results.push({
                        title: titleEl?.textContent?.trim() || titleEl?.getAttribute('title') || '无标题',
                        url: linkEl?.href || '',
                        author: authorEl?.textContent?.trim() || '未知作者',
                        likes: likeEl?.textContent?.trim() || '',
                        image: imgEl?.src || ''
                    });
                }
            });
            
            return results;
        });
        
        await browser.close();
        
        return {
            keyword,
            timestamp: new Date().toISOString(),
            count: notes.length,
            notes: notes
        };
        
    } catch (error) {
        await browser.close();
        throw error;
    }
}

// Main
const keyword = process.argv[2] || '花粉过敏';
searchXiaohongshu(keyword)
    .then(result => console.log(JSON.stringify(result, null, 2)))
    .catch(err => {
        console.error('Error:', err.message);
        process.exit(1);
    });
