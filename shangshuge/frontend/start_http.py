import http.server
import socketserver

PORT = 8888

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running on http://localhost:{PORT}")
    httpd.serve_forever()
