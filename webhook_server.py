#!/usr/bin/env python3
"""
Webhook 接收服务
接收外部请求，转发到 OpenClaw
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import threading

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            message = data.get('message', '')
            
            # 处理消息
            print(f"[Webhook] 收到消息: {message}")
            
            # 调用 OpenClaw 处理
            result = self.process_message(message)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "result": result
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "error": str(e)
            }).encode())
    
    def process_message(self, message):
        # 这里可以调用 OpenClaw 或其他处理逻辑
        return f"Processed: {message}"
    
    def log_message(self, format, *args):
        # 简化日志输出
        print(f"[Webhook] {format % args}")

def start_webhook_server(port=8080):
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    print(f"[Webhook] 服务启动在端口 {port}")
    server.serve_forever()

if __name__ == "__main__":
    start_webhook_server()
