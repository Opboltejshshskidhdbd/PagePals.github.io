# Roblox Dev Master v1.12.0-gate

Check generated Luau (Python 3, no dependencies):

    python scripts/luau_syntax.py script.luau      # syntax parse, line:col + hint
    python scripts/ui_lint.py UI.client.luau       # emoji icons, fake asset IDs, top-bar overlap, oversized panels
    python tests/run_all.py                        # every test (parser, corpus, UI lint, lint rules)

Limits: syntax and a few compile-time errors only; not types, API names, layout or runtime behavior.
