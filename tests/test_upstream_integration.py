import pytest
import json
from src.validator_client import validate_luau_source, ValidatorError

@pytest.mark.asyncio
async def test_real_upstream_valid_code():
    """ACTUALLY VERIFIED: Send real valid Luau code to Cloudflare."""
    code = "local x = 5\nprint(x)"
    
    try:
        response = await validate_luau_source(code)
    except ValidatorError as e:
        pytest.fail(f"Upstream unavailable or failed: {e.code} - {e.message}")
        
    assert "valid" in response, "Response missing 'valid' key"
    assert response["valid"] is True

@pytest.mark.asyncio
async def test_real_upstream_invalid_code():
    """ACTUALLY VERIFIED: Send intentionally invalid Luau code to Cloudflare."""
    code = "local x ="
    
    try:
        response = await validate_luau_source(code)
    except ValidatorError as e:
         pytest.fail(f"Upstream unavailable or failed: {e.code} - {e.message}")
         
    assert "valid" in response
    assert response["valid"] is False
    assert "errors" in response
    assert len(response["errors"]) > 0
  
