import json
import sys
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

# Ensure backend package is importable when running from workspace root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.core import analyze_text


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status, obj):
        data = json.dumps(obj)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(data.encode('utf-8'))

    def do_POST(self):
        if self.path != '/analyze':
            return self._send_json(404, {'error': 'not found'})
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length).decode('utf-8') if length else ''
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            return self._send_json(400, {'error': 'invalid json'})

        text = payload.get('text')
        if not text:
            return self._send_json(400, {'error': 'text is required'})

        out = analyze_text(text)
        return self._send_json(200, out)


def run(port=8001):
    server = HTTPServer(('127.0.0.1', port), Handler)
    print(f'Smoke server listening on http://127.0.0.1:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == '__main__':
    run()
