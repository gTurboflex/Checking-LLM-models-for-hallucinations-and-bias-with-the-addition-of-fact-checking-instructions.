"""Compare regenerated outputs with the hashes recorded for the original analysis.

Run after analyse_main.py, make_figures.py and manuscript_extra_analysis.py.
Standard library only. Exit code 0 = all result tables identical.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Extra table added for the manuscript (not in reproduction_record.json).
EXTRA = {'manuscript_extra.csv': 'ed8ddcfc9c51f51b12bdd18c532c9e194710c5792d57fe48599bd64df35ede6d'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_crlf(path):
    """Hash with Windows line endings, for text files written on Linux/macOS."""
    data = path.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
    return hashlib.sha256(data).hexdigest()


def check(group, folder, expected, hard):
    bad = 0
    print(f'\n{group}:')
    for name, want in sorted(expected.items()):
        path = ROOT / folder / name.replace('\\', '/')
        if not path.exists():
            print(f'  MISSING   {folder}/{name}')
            bad += 1
            continue
        ok = sha(path) == want
        note = ''
        if not ok and path.suffix in ('.json', '.csv') and sha_crlf(path) == want:
            ok, note = True, '  (same content; only line endings differ)'
        bad += not ok
        print(f'  {"OK       " if ok else "DIFFERENT"} {folder}/{name}{note}')
    if bad and not hard:
        print('  Note: PNG bytes can differ with fonts or OS even when the plotted numbers are the same.')
    return bad if hard else 0


def main():
    record = json.loads((ROOT / 'reproduction_record.json').read_text(encoding='utf-8'))
    inputs = {k.replace('\\', '/'): v for k, v in record['input_sha256'].items()}
    failures = check('Frozen inputs (must be unchanged)', '.', inputs, hard=True)
    tables = dict(record['table_sha256'])
    tables.update(EXTRA)
    failures += check('Result tables (must be byte-identical)', 'results', tables, hard=True)
    check('Figures (informative only)', 'figures', record['figure_sha256'], hard=False)
    print()
    if failures:
        print(f'FAILED: {failures} input or table file(s) differ from the recorded hashes.')
        sys.exit(1)
    print('SUCCESS: every input and result table matches the recorded SHA-256 hashes.')


if __name__ == '__main__':
    main()
