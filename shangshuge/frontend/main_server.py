# -*- coding: utf-8 -*-
import os
import sys
import http.server
import socketserver
from pathlib import Path

def start_server():
    """启动HTTP服务器"""
    frontend_path = Path(__file__).parent
    
    os.chdir(frontend_path)
    
    PORT = 8888
    
    Handler = http.server.SimpleHTTPRequestHandler
    Handler.extensions_map.update({
        '.js': 'application/javascript',
        '.css': 'text/css',
    })
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"服务器启动于 http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    start_server()
