"""Combined static + proxy server for production-like local testing"""
import http.server
import urllib.request
import urllib.error
import os
import sys
from io import BytesIO

BACKEND = "http://localhost:8000"
DIST = os.path.join(os.path.dirname(__file__), "frontend", "dist")
PORT = 8080


class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self.proxy_request("GET")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self.proxy_request("POST")
        else:
            self.send_error(404)

    def proxy_request(self, method):
        try:
            url = BACKEND + self.path
            body = None
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                body = self.rfile.read(content_length)

            req = urllib.request.Request(
                url,
                data=body,
                method=method,
            )
            # Forward relevant headers
            for key in ["Content-Type", "Authorization", "Accept"]:
                val = self.headers.get(key)
                if val:
                    req.add_header(key, val)

            resp = urllib.request.urlopen(req, timeout=60)
            self.send_response(resp.status)
            for key, val in resp.headers.items():
                if key.lower() not in ("transfer-encoding", "connection"):
                    self.send_header(key, val)
            self.end_headers()

            # Stream (for SSE)
            if "text/event-stream" in resp.headers.get("Content-Type", ""):
                self.wfile.write(resp.read())
            else:
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_error(502, str(e))

    def log_message(self, format, *args):
        print(f"[{self.command}] {self.path} -> {args}")


if __name__ == "__main__":
    os.chdir(DIST)
    server = http.server.HTTPServer(("0.0.0.0", PORT), ProxyHTTPRequestHandler)
    print(f"Serving at http://localhost:{PORT}")
    print(f"Backend proxy: /api/* -> {BACKEND}")
    print(f"Static files: {DIST}")
    server.serve_forever()
