from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'Practica TCPDUMP - Criptografia\nCaptura real de trafico HTTP local.\n'
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

HTTPServer(('127.0.0.1', 8080), Handler).serve_forever()
