#!/usr/bin/env python3
import argparse, json, pathlib, sys
from luau_syntax import validate_luau_files

def main():
    p=argparse.ArgumentParser(description='Validate exact Luau source without executing Roblox code.')
    p.add_argument('files', nargs='+')
    a=p.parse_args(); files={str(pathlib.Path(f)): pathlib.Path(f).read_text(encoding='utf-8') for f in a.files}
    r=validate_luau_files(files); print(json.dumps(r,indent=2)); return 0 if r['status']=='SYNTAX_VERIFIED' else 1
if __name__=='__main__': raise SystemExit(main())
