import os
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import JSONResponse
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
import anyio

from src.validator_client import validate_luau_source, ValidatorError

# Initialize MCP Server
mcp = Server("luau-validator-bridge")

@mcp.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="validate_external_luau",
            description="Sends Luau source code to an external validator API and returns the exact diagnostic results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The exact Luau source code to validate. Max size: 200KB."
                    }
                },
                "required": ["code"]
            }
        )
    ]

@mcp.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    if name != "validate_external_luau":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments or "code" not in arguments:
        raise ValueError("Missing required argument: 'code'")

    code = arguments["code"]
    if not isinstance(code, str):
         raise ValueError("Argument 'code' must be a string.")

    try:
        import json
        result_json = await validate_luau_source(code)
        return [TextContent(type="text", text=json.dumps(result_json, indent=2))]
    except ValidatorError as e:
        error_payload = {"error_code": e.code, "message": e.message}
        import json
        return [TextContent(type="text", text=json.dumps(error_payload, indent=2))]
    except Exception as e:
        error_payload = {"error_code": "BRIDGE_INTERNAL_ERROR", "message": "An unexpected error occurred."}
        import json
        return [TextContent(type="text", text=json.dumps(error_payload, indent=2))]


# --- Corrected SSE Transport Layer ---

sse = SseServerTransport("/message")

async def handle_sse(request: Request):
    # This natively handles the Starlette request and establishes the stream
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp.run(
            streams[0],
            streams[1],
            mcp.create_initialization_options()
        )

async def handle_messages(request: Request):
    # This natively handles the incoming POST messages from the client
    await sse.handle_post_message(
        request.scope, request.receive, request._send
    )

async def health_endpoint(request: Request):
    return JSONResponse({
        "status": "ok",
        "service": "luau-validator-mcp-bridge"
    })

app = Starlette(
    routes=[
        Route("/health", endpoint=health_endpoint),
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Route("/message", endpoint=handle_messages, methods=["POST"]),
    ]
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run("src.server:app", host="0.0.0.0", port=port, reload=False)
