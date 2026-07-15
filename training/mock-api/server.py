"""Tiny local mock API for the Exercise Lab (localhost only)."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/health"):
            self._send(200, {"status": "ok"})
            return
        if self.path.startswith("/items"):
            self._send(200, {"items": [{"id": 1, "name": "widget"}]})
            return
        self._send(404, {"error": "not found"})

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def main() -> None:
    server = HTTPServer(("127.0.0.1", 8765), Handler)
    print("Mock API on http://127.0.0.1:8765")
    server.serve_forever()


if __name__ == "__main__":
    main()
