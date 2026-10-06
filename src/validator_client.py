import httpx
import json
from .config import VALIDATOR_URL, MAX_SOURCE_SIZE_BYTES, REQUEST_TIMEOUT_SECONDS, USER_AGENT

class ValidatorError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

async def validate_luau_source(code: str) -> dict:
    if len(code.encode('utf-8')) > MAX_SOURCE_SIZE_BYTES:
        raise ValidatorError(
            "EXTERNAL_VALIDATION_INPUT_TOO_LARGE", 
            "Input exceeds the maximum allowed size of 200 KB."
        )

    payload = {"code": code}
    headers = {
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(VALIDATOR_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        raise ValidatorError(
            "EXTERNAL_VALIDATION_TIMEOUT", 
            f"The upstream validator timed out after {REQUEST_TIMEOUT_SECONDS}s."
        )
    except httpx.HTTPStatusError as e:
        raise ValidatorError(
            "EXTERNAL_VALIDATION_HTTP_ERROR", 
            f"Upstream validator returned HTTP {e.response.status_code}."
        )
    except httpx.RequestError as e:
         raise ValidatorError(
            "EXTERNAL_VALIDATION_UNAVAILABLE", 
            f"Failed to connect to upstream validator: {str(e)}"
        )
    except json.JSONDecodeError:
        raise ValidatorError(
            "EXTERNAL_VALIDATION_INVALID_RESPONSE", 
            "Upstream validator returned malformed JSON."
        )
