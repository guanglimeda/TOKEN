#!/usr/bin/env python3
"""
Webhook 接收服务 - 接收爬虫数据
监听指定端口，接收 POST 请求，处理后发送到钉钉群
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import threading
import requests

# 配置
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=3db7259b8553e2bc2b61d16481c998a6443f3f223196412381d2a7f8d9bfe2ef"
OPENCLAW_GATEWAY = "http://127.0.0.1:18789"

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            print(f"[Webhook] 收到数据: {json.dumps(data, ensure_ascii=False)[:200]}...")
            
            # 处理数据
            result = self.process_data(data)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "message": "数据已接收并处理"
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
    
    def process_data(self, data):
        """处理接收到的数据"""
        # 提取关键信息
        message = data.get('message', '')
        source = data.get('source', 'unknown')
        
        print(f"[Webhook] 来源: {source}, 消息: {message[:100]}...")
        
        # 这里可以添加筛选逻辑
        # 比如只转发包含特定关键词的消息
        
        # 发送到钉钉
        self.send_to_dingtalk(f"【{source}】{message}")
        
        return {"processed": True}
    
    def send_to_dingtalk(self, message):
        """发送消息到钉钉"""
        try:
            payload = {
                "msgtype": "text",
                "text": {
                    "content": f"微博 - {message}"
                }
            }
            resp = requests.post(DINGTALK_WEBHOOK, json=payload, timeout=30)
            print(f"[Webhook] 钉钉发送结果: {resp.json()}")
        except Exception as e:
            print(f"[Webhook] 钉钉发送失败: {e}")
    
    def log_message(self, format, *args):
        print(f"[Webhook] {format % args}")

def start_server(port=8080):
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    print(f"[Webhook] 服务启动在 http://0.0.0.0:{port}")
    print(f"[Webhook] 接收地址: http://你的服务器IP:{port}/webhook")
    server.serve_forever()

if __name__ == "__main__":
    start_server()
