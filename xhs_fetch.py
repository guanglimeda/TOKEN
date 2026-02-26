#!/usr/bin/env python3
"""
Xiaohongshu content fetcher - lightweight version using requests
"""
import requests
import json
import re
import urllib.parse

def fetch_xhs_search(keyword):
    """Fetch Xiaohongshu search results"""
    encoded_kw = urllib.parse.quote(keyword)
    url = f"https://www.xiaohongshu.com/search_result?keyword={encoded_kw}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.xiaohongshu.com/',
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        html = resp.text
        
        # Try to extract JSON data from script tags
        # XHS often embeds data in window.__INITIAL_STATE__ or similar
        results = []
        
        # Pattern 1: Look for note data in JSON
        note_pattern = r'"noteId":"([^"]+)".*?"title":"([^"]*)".*?"user":{"userId":"[^"]*","nickname":"([^"]*)".*?"likeCount":"?([^",}]*)"?'
        matches = re.findall(note_pattern, html, re.DOTALL)
        
        for note_id, title, author, likes in matches[:20]:
            results.append({
                'note_id': note_id,
                'title': title.encode('utf-8').decode('unicode_escape') if '\\u' in title else title,
                'author': author.encode('utf-8').decode('unicode_escape') if '\\u' in author else author,
                'likes': likes,
                'url': f'https://www.xiaohongshu.com/explore/{note_id}'
            })
        
        # Pattern 2: Alternative pattern for newer XHS format
        if not results:
            # Look for any JSON-like structures with note info
            json_pattern = r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});'
            json_match = re.search(json_pattern, html, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    # Extract from parsed JSON structure
                    if 'search' in data and 'notes' in data['search']:
                        for note in data['search']['notes'][:20]:
                            results.append({
                                'note_id': note.get('id', ''),
                                'title': note.get('title', '无标题'),
                                'author': note.get('user', {}).get('nickname', '未知'),
                                'likes': note.get('likes', '0'),
                                'url': f"https://www.xiaohongshu.com/explore/{note.get('id', '')}"
                            })
                except:
                    pass
        
        return {
            'keyword': keyword,
            'url': url,
            'count': len(results),
            'notes': results
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'keyword': keyword,
            'url': url
        }

if __name__ == '__main__':
    import sys
    keyword = sys.argv[1] if len(sys.argv) > 1 else '花粉过敏'
    result = fetch_xhs_search(keyword)
    print(json.dumps(result, ensure_ascii=False, indent=2))
