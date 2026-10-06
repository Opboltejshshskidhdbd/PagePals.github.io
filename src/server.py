import asyncio
import json
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

from src.validator_client import validate_luau_source, ValidatorError

# Initialize MCP Server
mcp = Server("luau-validator-bridge")

@mcp.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    Exposes exactly one primary tool: validate_external_luau.
    """
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
    """
    Executes the requested tool, handling all external state errors transparently.
    """
    if name != "validate_external_luau":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments or "code" not in arguments:
        raise ValueError("Missing required argument: 'code'")

    code = arguments["code"]
    
    if not isinstance(code, str):
         raise ValueError("Argument 'code' must be a string.")

    try:
        # Call upstream without modification
        result_json = await validate_luau_source(code)
        
        # Return exact JSON response wrapped in MCP TextContent
        return [TextContent(type="text", text=json.dumps(result_json, indent=2))]
        
    except ValidatorError as e:
        # Return structured error block so the client sees the exact failure state
        error_payload = {
            "error_code": e.code,
            "message": e.message
        }
        return [TextContent(type="text", text=json.dumps(error_payload, indent=2))]
    except Exception as e:
        # Catch unexpected bridge errors safely without exposing stack traces
        error_payload = {
            "error_code": "BRIDGE_INTERNAL_ERROR",
            "message": "An unexpected error occurred in the MCP bridge."
        }
        return [TextContent(type="text", text=json.dumps(error_payload, indent=2))]

# --- HTTP Transport Setup for Hugging Face Spaces (SSE) ---

sse_transport: SseServerTransport = None

async def sse_endpoint(request: Request):
    global sse_transport
    sse_transport = SseServerTransport("/message")
    
    async def run_server():
        await mcp.run(
            sse_transport.create_initialization_options(),
            sse_transport.create_message_handler(),
            sse_transport.create_error_handler(),
        )
        
    asyncio.create_task(run_server())
    return await sse_transport.handle_sse(request)

async def message_endpoint(request: Request):
    global sse_transport
    if sse_transport is None:
        return JSONResponse({"error": "SSE connection not established"}, status_code=400)
    
    # Process incoming MCP JSON-RPC messages sent via POST
    await sse_transport.handle_post_message(request)
    return JSONResponse({"status": "accepted"})

async def health_endpoint(request: Request):
    return JSONResponse({
        "status": "ok",
        "service": "luau-validator-mcp-bridge"
    })

# Starlette App configuration
app = Starlette(
    routes=[
        Route("/sse", endpoint=sse_endpoint),
        Route("/message", endpoint=message_endpoint, methods=["POST"]),
        Route("/health", endpoint=health_endpoint),
    ]
)

if __name__ == "__main__":
    # Hugging face spaces default to port 7860
    uvicorn.run(app, host="0.0.0.0", port=7860)
  
