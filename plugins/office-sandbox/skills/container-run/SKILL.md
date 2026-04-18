---
name: container-run
description: "Run user-provided Python, Node.js, or shell code in an ephemeral Ubuntu container with internet access. Handles container lifecycle, file IO, and artifact retrieval. Use when the user wants to execute code in a clean environment, fetch and parse remote data, run a one-off script, or test code without affecting their machine. NEVER use for code that needs persistence — the container is ephemeral."
compatibility: "Requires the mcpcentral-office MCP server (auto-wired by the office-sandbox plugin). The container is short-lived and may be reaped between sessions — always run container_initialize before exec."
metadata:
  author: mcpcentral.io
  version: "1.0.0"
---

# container-run

Execute snippets in a sandboxed Ubuntu container with `python3`, `node`, `npm`, `git`, `curl`, and `build-essential`. Internet is on. Disk is ephemeral.

## Workflow

1. **Ping** with `container_ping`. If the container is not running, you'll see `"container is not running, consider calling start()"`.
2. **Initialize** with `container_initialize` if needed (idempotent — safe to call when unsure).
3. **Write inputs** with `container_file_write` if the snippet expects local files. Avoid manual `cat <<EOF` via `container_exec` — use the dedicated file tool.
4. **Execute** with `container_exec`. Always use `python3` (not `python`) and install deps explicitly.
5. **Read outputs** with `container_file_read` (text) or `container_file_download_url` (binaries / artifacts to share).
6. **Report** stdout, stderr, exit code, and a download URL for any output files the user wants back.

## Output Template

```
Container: <ping_status>

Setup
  • wrote inputs/data.csv (1.2 KB)
  • installed: pandas==2.x

Execution
  exit: 0
  stdout: <truncated to ~2KB; full output via download URL>
  stderr: (empty)

Artifacts
  • outputs/result.json   → <download_url>
  • outputs/chart.png     → <download_url>
```

## Gotchas

- **Container is ephemeral.** Do not assume state survives between sessions. Re-install dependencies every time.
- **Always `python3`, never `python`.** Plain `python` is not on PATH in the base image.
- **Dependencies are not preinstalled.** Always `pip install` (or `npm install`) before importing third-party packages.
- **Don't read files via `container_exec cat`.** Use `container_file_read` — it returns the right MIME type (including binary base64) and is more reliable.
- **Long-running scripts time out.** The exec endpoint has its own timeout; for anything > a few minutes, write the script to a file, fork it into the background, and poll status via `container_ping` + file reads.
- **Working directory persists across `_exec` calls within a session, but shell environment does not.** `cd` in one call has no effect on the next; always pass absolute paths.
- **Network calls succeed but are not free.** Egress is shared — don't run aggressive scrapers without telling the user.

## Examples

**User:** "Run `python3 -c 'print(2**40)'`."
→ `container_initialize` → `container_exec("python3 -c 'print(2**40)'")` → return stdout.

**User:** "Fetch this CSV and tell me the column means."
→ `container_initialize` → `container_exec("pip install pandas requests")` → write a small Python script via `container_file_write` → `container_exec("python3 /tmp/analyze.py")` → read result.

**User:** "Compile this Rust file."
→ Rust isn't in the base image — `container_exec("apt-get install -y rustc")` first, then `rustc`.
