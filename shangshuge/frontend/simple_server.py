import socket
import threading
import time

def handle_client(conn, addr, html_content):
    try:
        data = conn.recv(1024)
        if data:
            conn.send(b'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: ' + str(len(html_content)).encode() + b'\r\n\r\n' + html_content)
    finally:
        conn.close()

def run_server(port, html_content):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    print(f"Server running on http://localhost:{port}")
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, html_content))
        thread.start()

if __name__ == '__main__':
    with open('index.html', 'rb') as f:
        html_content = f.read()
    run_server(8080, html_content)