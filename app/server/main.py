"""Zero-dependency HTTP server: JSON API + static frontend. Read-only."""
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from app.server.modules import MODULE_REGISTRY
from app.server.services.communities import graph_communities, sura_subgraph
from app.server.services.verses import verse_payload

WEB_DIR = Path(__file__).resolve().parents[1] / "web"
CONTENT_TYPES = {".html": "text/html", ".js": "text/javascript",
                 ".css": "text/css", ".json": "application/json"}


def _modules(m):
    return 200, [{"id": s["id"], "title": s["title"], "icon": s["icon"]} for s in MODULE_REGISTRY]


def _verse(m):
    p = verse_payload(int(m["s"]), int(m["a"]))
    return (200, p) if p else (404, {"error": "no such ayah"})


def _communities(m):
    return 200, graph_communities()


def _sura(m):
    return 200, sura_subgraph(int(m["s"]))


def build_routes():
    routes = [
        ("GET", r"^/api/modules$", _modules),
        ("GET", r"^/api/verse/(?P<s>\d+):(?P<a>\d+)$", _verse),
        ("GET", r"^/api/graph/communities$", _communities),
        ("GET", r"^/api/graph/sura/(?P<s>\d+)$", _sura),
    ]
    for spec in MODULE_REGISTRY:
        routes.extend(spec["routes"])
    return [(method, re.compile(pat), fn) for method, pat, fn in routes]


def dispatch(routes, method, path):
    for rmethod, rx, fn in routes:
        if rmethod == method:
            mt = rx.match(path)
            if mt:
                return fn(mt.groupdict())
    return 404, {"error": "not found"}


class Handler(BaseHTTPRequestHandler):
    routes = build_routes()

    def log_message(self, *a):
        pass

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_static(self):
        rel = self.path.split("?")[0].lstrip("/") or "index.html"
        target = (WEB_DIR / rel).resolve()
        if WEB_DIR not in target.parents and target != WEB_DIR or not target.is_file():
            target = WEB_DIR / "index.html"
        if not target.is_file():
            self._send_json(404, {"error": "not found"})
            return
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPES.get(target.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path.startswith("/api/"):
            status, payload = dispatch(self.routes, "GET", path)
            self._send_json(status, payload)
        else:
            self._send_static()


def run(port=8000):
    print(f"Monad engine → http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    run()
