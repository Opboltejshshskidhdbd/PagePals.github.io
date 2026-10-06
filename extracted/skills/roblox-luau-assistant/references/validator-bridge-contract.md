# Validator Bridge Contract

This is an integration contract, not a fake implementation.

## Required action
`validate_luau_source`

### Input
- `source: string` — exact current source
- `source_name: string` — Studio/export identity
- `source_hash: string` — hash computed by the caller over the exact source

### Output
```json
{
  "valid": true,
  "status": "SYNTAX_VERIFIED",
  "validator": "CUSTOM_LUAU_SYNTAX_VALIDATOR",
  "validator_version": "<version>",
  "source_hash": "<sha256>",
  "files_checked": ["<source_name>"],
  "diagnostics": [],
  "error_count": 0,
  "warning_count": 0,
  "execution_time": 0.0
}
```

Every returned `source_hash` must equal the hash of the exact `source` supplied in the same call. The bridge must never silently substitute a filesystem copy when a source string was supplied.

## Security
The bridge parses/analyzes source only. It must not execute generated Roblox code, invoke `loadstring`, run arbitrary shell commands, or make arbitrary network requests as part of syntax validation.

## Enforcement
A successful bridge call is still insufficient unless the generation flow compares the checked hash with the final delivery hash. Any source mutation after validation causes `VALIDATION_INVALIDATED` and requires a fresh bridge call.

## Host state machine
`VALIDATOR_PRESENT → VALIDATOR_LOCALLY_EXECUTABLE → VALIDATOR_HOST_CALLABLE → VALIDATION_ENFORCED → SYNTAX_VERIFIED`

A missing transition cannot be skipped by documentation, tests, or model confidence.
