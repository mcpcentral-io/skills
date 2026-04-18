---
name: whoami
description: "Identity & tenancy introspection. Reports who Claude is acting as in mcpcentral.io — tenant ID, customer ID, subscription plan, permissions (mcp.read/write/admin), and auth provider. Use when the user asks 'who am I logged in as', 'what plan do I have', 'do I have permission to X', or before any other skill performs a plan-gated action."
compatibility: "Requires the mcpcentral-mcp-gateway MCP server (https://gateway.mcpcentral.io/mcp). Bundled with the mcpcentral plugin's .mcp.json — no extra setup."
metadata:
  author: mcpcentral.io
  version: "1.0.0"
---

# whoami

A thin identity helper around `mcpcentral-mcp-gateway`. Two MCP tools, two read-only calls, one combined report.

## When to Use

- "Who am I?" / "What account am I on?"
- "What plan / tier do I have?"
- "Do I have admin / write / read permission?"
- Before any other skill performs an action that depends on plan or permissions (e.g., a future skill that gates expensive operations behind `mcp.admin`).

## Workflow

1. Call `mcp__mcpcentral-mcp-gateway__get_user_info()` (no parameters).
2. Call `mcp__mcpcentral-mcp-gateway__get_tenant_info()` (no parameters).
3. Merge into a single report (see schema below). Both calls are cheap and parameterless — fire them in parallel.

## Output Schema

```json
{
  "user": {
    "id": "...",
    "email": "...",
    "name": "...",
    "authType": "..."
  },
  "tenant": {
    "tenantId": "...",
    "subdomain": "...",
    "customerId": "...",
    "companyName": "...",
    "plan": "..."
  },
  "permissions": ["mcp.read", "mcp.write", "mcp.admin"],
  "session": {
    "authProvider": "...",
    "isServiceUser": true,
    "authenticatedAt": "ISO timestamp"
  }
}
```

Render as a compact table in chat — don't dump raw JSON unless the user asks for it.

## Permission Gating Helper

Other skills can call `whoami` first and branch on permissions:

```text
permissions = whoami().permissions
if "mcp.admin" not in permissions:
    refuse with: "This action requires mcp.admin. Your account has: ..."
```

## Gotchas

- **Both fields can return "Not configured" / "Not available".** When `customerId`, `subdomain`, `companyName`, or `plan` come back as those literal strings, treat them as missing — don't display them as real values.
- **`isServiceUser: true` is normal for OAuth-service tokens.** Don't flag it as a security issue; it just means the token was issued via the OAuth-service flow rather than a human login.
- **Permissions are coarse.** `mcp.read / write / admin` is the full set today. There is no per-server or per-tool ACL — assume any granted permission applies to every server reachable from this tenant.
- **Don't cache across sessions.** The gateway response includes `retrievedAt` for a reason; permissions can change. Re-call `whoami` at the start of any new session that gates behavior on plan.
