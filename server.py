#!/usr/bin/env python3
"""Servidor local do Inventário de TI - Belfort. Sem dependências além do Python 3."""
import json, os, re, socket, sys, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQ = os.path.join(PASTA, "dados.json")
COLS = ("extras", "edits", "removed")
lock = threading.Lock()

def ler():
    try:
        with open(ARQ, encoding="utf-8") as f:
            s = json.load(f)
    except (FileNotFoundError, ValueError):
        s = {}
    return {c: s.get(c, {}) for c in COLS}

def gravar(s):
    tmp = ARQ + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False)
    os.replace(tmp, ARQ)

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, tipo="application/json; charset=utf-8"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/api/state":
            with lock:
                self._send(200, json.dumps(ler(), ensure_ascii=False))
        elif self.path in ("/", "/index.html"):
            with open(os.path.join(PASTA, "index.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        else:
            self._send(404, "{}")

    def do_POST(self):
        if self.path != "/api/write":
            return self._send(404, "{}")
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n > 50000:
                raise ValueError("grande")
            p = json.loads(self.rfile.read(n))
            c, op, i = p["c"], p["op"], p["id"]
            if c not in COLS or op not in ("set", "delete") or not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", i):
                raise ValueError("invalido")
            if op == "set" and not isinstance(p.get("data"), dict):
                raise ValueError("dados")
        except Exception:
            return self._send(400, '{"erro":"requisicao invalida"}')
        with lock:
            s = ler()
            if op == "set":
                s[c][i] = p["data"]
            else:
                s[c].pop(i, None)
            gravar(s)
        self._send(200, '{"ok":true}')

    def log_message(self, *a):
        pass

def ips():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Inventário de TI - Belfort no ar.\n  Neste computador: http://localhost:{porta}\n  Na rede:          http://{ips()}:{porta}\nDeixe esta janela aberta. Para encerrar, feche-a ou pressione Ctrl+C.")
    ThreadingHTTPServer(("0.0.0.0", porta), H).serve_forever()
