# Connecting the probe MCP server (P15)

P15 asks whether this harness can connect to an MCP server and route a tool
call to it. The skill ships a tiny server for that:
`<skill>/scripts/mcp_probe_server.py`. It speaks MCP over stdio, needs only
Python 3.8, and offers one tool, `probe_challenge`, which answers a nonce with
a keyed digest. The key is created in `<run>/state/mcp-secret` when the server
first starts and every call is logged to `<run>/state/mcp-calls.jsonl`, so the
checker can tell a real call from a described one.

## Register it

Use the absolute paths of this skill and of the run folder.

**Claude Code**

    claude mcp add hprobe -- python3 /abs/path/harness-probe/scripts/mcp_probe_server.py --run /abs/path/hprobe-run

then start a new session (servers are loaded at start-up).

**Any client with a JSON MCP configuration** (Claude Desktop, Cursor, VS Code
and others):

    {
      "mcpServers": {
        "hprobe": {
          "command": "python3",
          "args": ["/abs/path/harness-probe/scripts/mcp_probe_server.py", "--run", "/abs/path/hprobe-run"]
        }
      }
    }

**A remote-only harness** (one that connects to MCP servers over HTTP, such as
a Copilot declarative agent connector) cannot start a local stdio process.
Connect any read-only MCP server the harness is approved to use instead, call
one of its tools, quote the result, and have the user confirm it:

    python3 <skill>/scripts/hprobe.py record P15 pass --run <run> --observer user --evidence "<server and tool called, result quoted>"

## Run the probe

    python3 <skill>/scripts/hprobe.py check P15 --run <run> --phase nonce

Call the server's `probe_challenge` tool with the printed nonce, then:

    python3 <skill>/scripts/hprobe.py check P15 --run <run> --answer <the digest it returned>

If the harness cannot connect to the server at all, record
`hprobe.py record P15 fail --observer agent --evidence "<what happened>"`.
