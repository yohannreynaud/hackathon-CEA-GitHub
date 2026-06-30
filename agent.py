#!/usr/bin/env python3
"""
Minimal agent loop: Ollama model + MCP server, no external dependencies.

Configure the constants below, then:
    python3 agent.py "your prompt here"

If SOUL.md exists in the current directory it is used as the system prompt.
"""

import json
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

VERBOSE = False   # set to True or use -v flag

# ── Configuration ─────────────────────────────────────────────────────

# PROVIDER = "https://Bob:hiccup@ollama-sam.inria.fr"
PROVIDER = "https://Clanker:willrule@ollama.pl.sophia.inria.fr"
# MODEL    = "gemma4:e4b"
MODEL    = "mistral:7b"

MCP_URL     = "https://itk-pariscluster-regionaldb.ijclab.in2p3.fr/devel/mcp"
MCP_API_KEY = "itkornotitk"

MAX_TURNS = 10   # max tool-call rounds before giving up

# ── HTTP helpers ──────────────────────────────────────────────────────

def _ssl_ctx():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def http_post(url, payload, headers=None):
    """POST JSON, return parsed JSON response."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)

    # inject basic-auth if credentials are in the URL
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.username:
        import base64
        cred = base64.b64encode(f"{parsed.username}:{parsed.password or ''}".encode()).decode()
        req.add_header("Authorization", f"Basic {cred}")
        # rebuild URL without credentials
        clean = parsed._replace(netloc=parsed.hostname + (f":{parsed.port}" if parsed.port else ""))
        req = urllib.request.Request(clean.geturl(), data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        req.add_header("Authorization", f"Basic {cred}")
        for k, v in (headers or {}).items():
            req.add_header(k, v)

    resp = urllib.request.urlopen(req, context=_ssl_ctx(), timeout=60)
    return json.loads(resp.read())


# ── MCP client ────────────────────────────────────────────────────────

def mcp_post(method, params=None, session_id=None):
    headers = {"X-API-Key": MCP_API_KEY}
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    return http_post(MCP_URL, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}, headers)


def mcp_initialize():
    resp = mcp_post("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "agent.py", "version": "1.0"},
    })
    return resp.get("result", {}).get("sessionId")   # may be None; some servers use headers instead


def mcp_list_tools(session_id=None):
    resp = mcp_post("tools/list", session_id=session_id)
    raw_tools = resp.get("result", {}).get("tools", [])
    # reshape to OpenAI function-calling format
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("inputSchema", {"type": "object", "properties": {}}),
            },
        }
        for t in raw_tools
    ]


def mcp_call_tool(name, arguments, session_id=None):
    resp = mcp_post("tools/call", {"name": name, "arguments": arguments}, session_id=session_id)
    result = resp.get("result", {})
    # MCP returns a list of content blocks
    parts = result.get("content", [])
    return "\n".join(p.get("text", str(p)) for p in parts) if parts else json.dumps(result)


# ── Ollama helpers ────────────────────────────────────────────────────

def ollama_check_tools():
    """Exit early if the model doesn't advertise 'tools' capability."""
    from urllib.parse import urlparse
    import base64
    parsed = urlparse(PROVIDER)
    host = parsed.hostname + (f":{parsed.port}" if parsed.port else "")
    url = f"{parsed.scheme}://{host}/api/show"

    data = json.dumps({"name": MODEL}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if parsed.username:
        cred = base64.b64encode(f"{parsed.username}:{parsed.password or ''}".encode()).decode()
        req.add_header("Authorization", f"Basic {cred}")

    try:
        resp = urllib.request.urlopen(req, context=_ssl_ctx(), timeout=15)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"[model] {MODEL} — /api/show not exposed by proxy, skipping capability check", flush=True)
            return
        raise
    info = json.loads(resp.read())
    capabilities = info.get("capabilities", [])
    if "tools" not in capabilities:
        print(f"[error] model '{MODEL}' does not support tools (capabilities: {capabilities})", file=sys.stderr)
        sys.exit(1)
    print(f"[model] {MODEL} — capabilities: {capabilities}", flush=True)


# ── Ollama chat ───────────────────────────────────────────────────────

def ollama_chat(messages, tools=None):
    from urllib.parse import urlparse
    parsed = urlparse(PROVIDER)
    host = parsed.hostname + (f":{parsed.port}" if parsed.port else "")
    url = f"{parsed.scheme}://{host}/v1/chat/completions"

    payload = {"model": MODEL, "messages": messages, "stream": True}
    if tools:
        payload["tools"] = tools

    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if parsed.username:
        import base64
        cred = base64.b64encode(f"{parsed.username}:{parsed.password or ''}".encode()).decode()
        req.add_header("Authorization", f"Basic {cred}")

    if VERBOSE:
        print(f"[llm →] {json.dumps(payload, indent=2, ensure_ascii=False)}", flush=True)

    # accumulate streamed deltas into a single message
    role = "assistant"
    content_parts = []
    tool_calls = {}   # index → {id, type, function: {name, arguments}}

    with urllib.request.urlopen(req, context=_ssl_ctx(), timeout=120) as resp:
        for raw in resp:
            line = raw.decode().strip()
            if not line.startswith("data:"):
                continue
            payload_str = line[5:].strip()
            if payload_str == "[DONE]":
                break
            try:
                chunk = json.loads(payload_str)
            except json.JSONDecodeError:
                continue

            delta = chunk.get("choices", [{}])[0].get("delta", {})

            if "role" in delta:
                role = delta["role"]

            if "content" in delta and delta["content"]:
                token = delta["content"]
                content_parts.append(token)
                if VERBOSE:
                    print(token, end="", flush=True)

            for tc in delta.get("tool_calls", []):
                idx = tc["index"]
                if idx not in tool_calls:
                    tool_calls[idx] = {"id": "", "type": "function", "function": {"name": "", "arguments": ""}}
                entry = tool_calls[idx]
                if "id" in tc:
                    entry["id"] = tc["id"]
                fn = tc.get("function", {})
                if "name" in fn:
                    entry["function"]["name"] += fn["name"]
                if "arguments" in fn:
                    entry["function"]["arguments"] += fn["arguments"]

    if VERBOSE and content_parts:
        print(flush=True)   # newline after streamed tokens

    message = {"role": role, "content": "".join(content_parts) or None}
    if tool_calls:
        message["tool_calls"] = [tool_calls[i] for i in sorted(tool_calls)]

    if VERBOSE:
        print(f"[llm ←] {json.dumps(message, indent=2, ensure_ascii=False)}", flush=True)

    return message


# ── Agent loop ────────────────────────────────────────────────────────

def run(prompt):
    # system prompt from SOUL.md if present
    soul = Path("SOUL.md")
    messages = []
    if soul.exists():
        messages.append({"role": "system", "content": soul.read_text()})

    messages.append({"role": "user", "content": prompt})

    # show context
    from urllib.parse import urlparse
    parsed = urlparse(PROVIDER)
    safe_url = parsed._replace(netloc=parsed.hostname + (f":{parsed.port}" if parsed.port else "")).geturl()
    print(f"[config] provider : {safe_url}")
    print(f"[config] model    : {MODEL}")
    print(f"[config] mcp      : {MCP_URL}", flush=True)

    # fail fast if model can't do tool calling
    ollama_check_tools()

    # MCP bootstrap
    print("[mcp] initializing...", flush=True)
    session_id = mcp_initialize()
    tools = mcp_list_tools(session_id)
    print(f"[mcp] {len(tools)} tools available", flush=True)

    for turn in range(MAX_TURNS):
        prompt_bytes = len(json.dumps({"messages": messages, "tools": tools}).encode())
        prompt_tokens_est = prompt_bytes // 4
        print(f"[turn {turn + 1}] prompt size: {prompt_bytes:,} bytes (~{prompt_tokens_est:,} tokens est.) — calling model...", flush=True)
        message = ollama_chat(messages, tools)
        messages.append(message)

        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            # plain answer — we're done
            print("\n" + message.get("content", ""), flush=True)
            return

        # execute each tool call
        for call in tool_calls:
            fn   = call["function"]
            name = fn["name"]
            args = json.loads(fn.get("arguments", "{}"))
            print(f"[tool] {name}({json.dumps(args)[:120]})", flush=True)
            result = mcp_call_tool(name, args, session_id)
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": result,
            })

    print("[agent] reached MAX_TURNS without a final answer", file=sys.stderr)


# ── Entry point ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Minimal Ollama+MCP agent")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print full LLM request/response traffic")
    parser.add_argument("prompt", nargs="+", help="Prompt to send")
    args = parser.parse_args()

    if args.verbose:
        VERBOSE = True

    try:
        run(" ".join(args.prompt))
    except TimeoutError:
        print("[error] request timed out", file=sys.stderr)
        sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"[error] HTTP {e.code} {e.reason} — {e.url}", file=sys.stderr)
        sys.exit(1)
