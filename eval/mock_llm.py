#!/usr/bin/env python3
"""A tiny fake Gemini endpoint for testing the n8n WIRING without an API key.

It answers with the keyword-rule baseline in Gemini's response shape. It does NOT measure LLM
quality: use it only to check that webhook -> classify -> parse -> respond works end to end.

  python eval/mock_llm.py            # listens on http://127.0.0.1:8099
Then point the workflow's `llm_base_url` (Normalize node) at http://127.0.0.1:8099/v1beta
and remove the auth credential from the "LLM Classify" node.
"""
import json
import pathlib
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import baseline_rules  # noqa: E402


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(length) or b"{}")
        message = req["contents"][0]["parts"][0]["text"]
        answer = json.dumps(baseline_rules.classify(message))
        body = json.dumps({"candidates": [{"content": {"parts": [{"text": answer}]}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print("mock Gemini listening on http://127.0.0.1:8099")
    HTTPServer(("127.0.0.1", 8099), Handler).serve_forever()
