"""Runs every test_* function in tests/test_*.py without pytest. Exit code 1 on any failure."""
import glob, importlib.util, os, sys, traceback
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root); sys.path.insert(0, os.path.join(root, 'scripts'))
passed = failed = 0
for path in sorted(glob.glob(os.path.join(root, 'tests', 'test_*.py'))):
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        failed += 1; print('IMPORT FAIL', os.path.basename(path)); traceback.print_exc(); continue
    for name in sorted(n for n in dir(mod) if n.startswith('test_') and callable(getattr(mod, n))):
        try:
            getattr(mod, name)(); passed += 1
        except Exception:
            failed += 1; print('FAIL', os.path.basename(path), name); traceback.print_exc(limit=2)
print(f'{passed} passed, {failed} failed')
sys.exit(1 if failed else 0)
