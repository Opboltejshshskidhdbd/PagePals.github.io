# Luau Validator MCP Bridge

This is a Model Context Protocol (MCP) server that acts as a secure bridge to an external Luau Validator API (Cloudflare Worker). It does NOT implement its own validator.

* **Tool Name:** `validate_external_luau`
* **Input:** `{"code": "<exact Luau source string>"}` (Max 200 KB)
* **Output:** Exact JSON response from the upstream validator.
* **Security:** Hardcoded upstream URL, strict payload limits, no arbitrary code execution, and no file system access.
* **Endpoints:** `/sse` (MCP Connection), `/message` (MCP POST), `/health` (Status).

## Deployment (Render or Hugging Face)
This bridge is Docker-ready. Deploy via the included `Dockerfile`. 
For Render, ensure you set the `PORT` environment variable to `7860` (or let the app default to it).
