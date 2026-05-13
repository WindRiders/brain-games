#!/usr/bin/env python3
"""Brain Games Web — 浏览器版脑力训练合集

纯 Python 标准库 HTTP 服务器，零外部依赖。
启动: python3 web/server.py
"""

import json
import os
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

PORT = 8686
STATIC_DIR = Path(__file__).parent / "static"
SCORES_FILE = Path.home() / ".brain-games" / "scores.json"


class BrainGamesHandler(SimpleHTTPRequestHandler):
    """请求处理器：静态文件 + 分数 API"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def log_message(self, format, *args):
        """简化日志"""
        sys.stdout.write(f"  {args[0]}\n")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/scores":
            self._handle_get_scores()
        elif path == "/api/highscore":
            self._handle_get_highscore(parsed.query)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/scores":
            self._handle_save_score()
        elif path == "/api/scores/reset":
            self._handle_reset_scores()
        else:
            self.send_error(404)

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length).decode("utf-8")

    def _load_scores(self) -> dict:
        try:
            SCORES_FILE.parent.mkdir(parents=True, exist_ok=True)
            if SCORES_FILE.exists():
                with open(SCORES_FILE) as f:
                    data = json.load(f)
                    return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, IOError):
            pass
        return {}

    def _save_scores(self, data: dict):
        SCORES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SCORES_FILE, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _handle_get_scores(self):
        self._send_json(self._load_scores())

    def _handle_get_highscore(self, query_string):
        params = parse_qs(query_string)
        game = params.get("game", [""])[0]
        diff = params.get("difficulty", ["normal"])[0]
        scores = self._load_scores()
        value = scores.get(game, {}).get(diff, 0)
        self._send_json({"game": game, "difficulty": diff, "high_score": value})

    def _handle_save_score(self):
        try:
            body = json.loads(self._read_body())
            game = body.get("game", "unknown")
            difficulty = body.get("difficulty", "normal")
            score = body.get("score", 0)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        scores = self._load_scores()
        current = scores.get(game, {}).get(difficulty, 0)
        is_new = score > current
        if is_new:
            scores.setdefault(game, {})[difficulty] = score
            self._save_scores(scores)

        self._send_json({
            "game": game,
            "difficulty": difficulty,
            "score": score,
            "high_score": max(score, current),
            "is_new_high": is_new,
        })

    def _handle_reset_scores(self):
        self._save_scores({})
        self._send_json({"ok": True})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def main():
    os.chdir(STATIC_DIR)

    server = HTTPServer(("0.0.0.0", PORT), BrainGamesHandler)
    url = f"http://localhost:{PORT}"

    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║   🧠  Brain Games Web — 浏览器版           ║")
    print("  ╚══════════════════════════════════════════════╝")
    print()
    print(f"  服务地址: {url}")
    print(f"  按 Ctrl+C 停止服务器")
    print()

    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  服务器已停止。")
        server.server_close()


if __name__ == "__main__":
    main()