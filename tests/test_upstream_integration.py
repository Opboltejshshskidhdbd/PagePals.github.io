import pytest
from src.validator_client import validate_luau_source, ValidatorError

@pytest.mark.asyncio
async def test_real_upstream_valid_code():
    code = "local x = 5\nprint(x)"
    try:
        response = await validate_luau_source(code)
    except ValidatorError as e:
        pytest.fail(f"Upstream unavailable: {e.code} - {e.message}")
    assert "valid" in response
    assert response["valid"] is True

@pytest.mark.asyncio
async def test_real_upstream_invalid_code():
    code = "local x ="
    try:
        response = await validate_luau_source(code)
    except ValidatorError as e:
         pytest.fail(f"Upstream unavailable: {e.code} - {e.message}")
    assert "valid" in response
    assert response["valid"] is False
    assert "errors" in response
