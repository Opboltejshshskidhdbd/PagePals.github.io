import asyncio
import json
import os
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

from src.validator_client import validate_luau_source, ValidatorError

# V2 Syntax: FastMCP instead of raw Server
mcp = FastMCP("luau-validator-bridge")

@mcp.tool()
async def validate_external_luau(code: str) -> str:
    """
    Sends Luau source code to an external validator API and returns the exact diagnostic results.
    code: The exact Luau source code to validate. Max size: 200KB.
    """
    try:
        result_json = await validate_luau_source(code)
        return json.dumps(result_json, indent=2)
    except ValidatorError as e:
        error_payload = {"error_code": e.code, "message": e.message}
        return json.dumps(error_payload, indent=2)
    except Exception as e:
        error_payload = {"error_code": "BRIDGE_INTERNAL_ERROR", "message": "An unexpected error occurred."}
        return json.dumps(error_payload, indent=2)

sse_transport: SseServerTransport = None

async def sse_endpoint(request: Request):
    global sse_transport
    sse_transport = SseServerTransport("/message")
    
    # Run the FastMCP internal server using SSE transport
    async def run_server():
        await mcp._mcp_server.run(
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
    await sse_transport.handle_post_message(request)
    return JSONResponse({"status": "accepted"})

async def health_endpoint(request: Request):
    return JSONResponse({"status": "ok", "service": "luau-validator-mcp-bridge"})

app = Starlette(
    routes=[
        Route("/sse", endpoint=sse_endpoint),
        Route("/message", endpoint=message_endpoint, methods=["POST"]),
        Route("/health", endpoint=health_endpoint),
    ]
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
