"""Luau syntax validator (API-compatible with v1.x, now backed by a real parser).
Parses full Luau syntax (statements, expressions, types, if-expressions, compound assignment, interpolated strings,
continue) and a few compile-time errors (break outside loop, '...' outside vararg function).
NOT the official Roblox/Luau compiler, NOT a type checker, NOT a runtime test: SYNTAX_VERIFIED means
"this exact source parsed completely with the bundled Python parser"."""
from __future__ import annotations
import re
from dataclasses import dataclass, asdict
from hashlib import sha256
from time import perf_counter

from luau_parser import check as _check, tokenize, LuauSyntaxError  # noqa: F401  (re-exported)

VALIDATOR = 'Roblox Dev Master Luau parser (Python, not the official compiler)'
VERSION = '2.0.0'

@dataclass
class Diagnostic:
    file: str
    line: int
    column: int
    severity: str
    message: str
    category: str
    hint: str = ''
    def to_dict(self): return asdict(self)

@dataclass
class ValidationResult:
    status: str
    validator: str
    validator_version: str
    source_hash: str
    files_checked: list
    diagnostics: list
    error_count: int
    warning_count: int
    execution_time: float
    def to_dict(self): return asdict(self)

_POS = re.compile(r'^(\d+):(\d+): (.*)$', re.S)

def _convert(file, error, hint):
    m = _POS.match(error)
    line, col, msg = (int(m.group(1)), int(m.group(2)), m.group(3)) if m else (0, 0, error)
    category = 'syntax'
    if msg.startswith("expected 'end'"):
        opener = re.search(r"to close '(\w+)'", msg)
        msg = f"missing 'end' for {opener.group(1) if opener else 'block'} block: {msg}"
        category = 'block'
    elif msg.startswith("unexpected 'end'") or "expected 'until'" in msg:
        category = 'block'
    return Diagnostic(file, line, col, 'error', msg, category, hint or '')

def validate_source(source: str, file='<source>') -> ValidationResult:
    start = perf_counter()
    r = _check(source)
    diags = []
    if not r['ok']:
        diags.append(_convert(file, r['error'], r['hint']))
    for w in r['warnings']:
        m = _POS.match(w)
        diags.append(Diagnostic(file, int(m.group(1)), int(m.group(2)), 'warning', m.group(3), 'style') if m else Diagnostic(file, 0, 0, 'warning', w, 'style'))
    errors = sum(d.severity == 'error' for d in diags)
    return ValidationResult('SYNTAX_FAILED' if errors else 'SYNTAX_VERIFIED', VALIDATOR, VERSION,
                            sha256(source.encode('utf-8')).hexdigest(), [file], [d.to_dict() for d in diags],
                            errors, len(diags) - errors, perf_counter() - start)

def validate_luau_source(source: str, file='<source>') -> dict:
    return validate_source(source, file).to_dict()

def validate_luau_files(files: dict) -> dict:
    results = [validate_source(src, name) for name, src in files.items()]
    diags = [d for r in results for d in r.diagnostics]
    errors = sum(d['severity'] == 'error' for d in diags)
    return {'status': 'SYNTAX_FAILED' if errors else 'SYNTAX_VERIFIED', 'validator': VALIDATOR, 'validator_version': VERSION,
            'source_hash': sha256(''.join(name + '\0' + src for name, src in files.items()).encode('utf-8')).hexdigest(),
            'files_checked': list(files), 'diagnostics': diags, 'error_count': errors, 'warning_count': len(diags) - errors,
            'execution_time': sum(r.execution_time for r in results)}

if __name__ == '__main__':
    import sys
    sys.exit(__import__('luau_parser').main())
