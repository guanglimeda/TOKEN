#!/usr/bin/env python3
"""
Webhook 接收服务 - 记录模式
接收数据并保存到日志，每天中午汇总分析
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime

# 配置
LOG_DIR = "/root/.openclaw/workspace/hotspots"
os.makedirs(LOG_DIR, exist_ok=True)

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            
            # 记录到日志文件
            self.save_to_log(data)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "message": "数据已记录"
            }).encode())
            
        except Exception as e:
            print(f"[Webhook] 错误: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "error": str(e)
            }).encode())
    
    def save_to_log(self, data):
        """保存数据到日志文件"""
        now = datetime.now()
        log_file = f"{LOG_DIR}/{now.strftime('%Y-%m-%d')}.jsonl"
        
        record = {
            "timestamp": now.isoformat(),
            "data": data
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        print(f"[Webhook] 已记录: {data.get('source', 'unknown')} - {data.get('message', '')[:50]}...")
    
    def log_message(self, format, *args):
        print(f"[Webhook] {format % args}")

def start_server(port=8080):
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    print(f"[Webhook] 记录模式启动在 http://0.0.0.0:{port}")
    print(f"[Webhook] 日志目录: {LOG_DIR}")
    server.serve_forever()

if __name__ == "__main__":
    start_server()
