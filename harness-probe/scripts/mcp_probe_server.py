#!/usr/bin/env python3
"""A minimal MCP server for probe P15, over stdio, standard library only.

It offers one tool, ``probe_challenge``, which answers a nonce with a keyed
digest. The key is created in ``<run>/state/mcp-secret`` the first time the
server starts, and every call is appended to ``<run>/state/mcp-calls.jsonl``,
so ``hprobe.py check P15`` can tell a real call from a described one.

Register it with your harness, for example:

    claude mcp add hprobe -- python3 /path/to/harness-probe/scripts/mcp_probe_server.py --run /path/to/run

or, in a JSON MCP configuration:

    {"mcpServers": {"hprobe": {"command": "python3",
      "args": ["/path/to/harness-probe/scripts/mcp_probe_server.py", "--run", "/path/to/run"]}}}
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import hmac
import json
import os
import secrets
import sys
from pathlib import Path
from typing import Any, Dict, Optional

PROTOCOL = "2025-06-18"
SERVER = {"name": "lq-harness-probe", "version": "1.0.0"}
TOOL = {
    "name": "probe_challenge",
    "description": (
        "Harness probe P15. Returns a keyed digest of the nonce you pass. "
        "Call it with the nonce `hprobe.py check P15 --phase nonce` printed."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {"nonce": {"type": "string", "description": "the probe nonce"}},
        "required": ["nonce"],
    },
}


def digest(secret: bytes, nonce: str) -> str:
    return hmac.new(secret, nonce.encode("utf-8"), hashlib.sha256).hexdigest()[:24]


class Server:
    def __init__(self, run: Path):
        self.state = run / "state"
        self.state.mkdir(parents=True, exist_ok=True)
        secret_path = self.state / "mcp-secret"
        if not secret_path.is_file():
            secret_path.write_bytes(secrets.token_bytes(32))
            try:
                os.chmod(secret_path, 0o600)
            except OSError:
                pass
        self.secret = secret_path.read_bytes()
        self.log = self.state / "mcp-calls.jsonl"

    def handle(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        method = message.get("method")
        msg_id = message.get("id")
        if msg_id is None:
            return None  # a notification, such as notifications/initialized
        if method == "initialize":
            requested = (message.get("params") or {}).get("protocolVersion") or PROTOCOL
            result: Dict[str, Any] = {
                "protocolVersion": requested,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER,
            }
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {"tools": [TOOL]}
        elif method == "tools/call":
            params = message.get("params") or {}
            if params.get("name") != TOOL["name"]:
                return _error(msg_id, -32602, f"unknown tool {params.get('name')}")
            nonce = str((params.get("arguments") or {}).get("nonce", "")).strip()
            if not nonce:
                return _error(msg_id, -32602, "nonce is required")
            value = digest(self.secret, nonce)
            with open(self.log, "a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
                            "nonce": nonce,
                        }
                    )
                    + "\n"
                )
            result = {
                "content": [{"type": "text", "text": value}],
                "structuredContent": {"digest": value},
                "isError": False,
            }
        else:
            return _error(msg_id, -32601, f"method not found: {method}")
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _error(msg_id: Any, code: int, text: str) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": text}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run", default=os.environ.get("HPROBE_RUN", "hprobe-run"))
    args = parser.parse_args()
    server = Server(Path(args.run).resolve())
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            reply = _error(None, -32700, "parse error")
        else:
            reply = server.handle(message)
        if reply is not None:
            sys.stdout.write(json.dumps(reply) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
