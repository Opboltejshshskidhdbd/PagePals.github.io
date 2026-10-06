import os

# Upstream Validator Target
VALIDATOR_URL = os.getenv("VALIDATOR_URL", "https://luau-validator.oboltr895.workers.dev/validate")

# Limits & Timeouts
MAX_SOURCE_SIZE_BYTES = 200 * 1024  # 200 KB
REQUEST_TIMEOUT_SECONDS = 10.0

# HTTP Constants
USER_AGENT = "Luau-Validator-MCP-Bridge/1.0"
