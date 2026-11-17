"""Check that Ollama is running and that the six study models are available.

Standard library only. It does not run any experiment and creates no files.
Usage:  python check_ollama_models.py
"""
import json
import sys
import urllib.request

BASE = 'http://localhost:11434'
STUDY_OLLAMA_VERSION = '0.40.15'

# Digests recorded by /api/tags at the time of the main run (main_runs/main_100_v1/metadata.json).
LOCAL = {
    'qwen3:1.7b': '8f68893c685c3ddff2aa3fffce2aa60a30bb2da65ca488b61fff134a4d1730e7',
    'qwen3:4b-q4_K_M': '2bfd38a7daaf4b1037efe517ccb73d1a3bbd4822cf89f1a82be1569050a114e0',
    'qwen3:8b': '500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41',
    'gemma4:e2b': 'b37049369adfe3d2b653af0ab301a062ca5cbe96ace6aa0d3f2559ee9b563fc2',
}
CLOUD = ['beam:cloud', 'gemma4:31b-cloud']


def get(path, payload=None):
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(BASE + path, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)


def main():
    try:
        version = get('/api/version')['version']
        tags = get('/api/tags')['models']
    except Exception as e:
        print('Ollama is not reachable at', BASE, '-', e)
        print('Install Ollama from https://ollama.com/download and start it, then run this again.')
        sys.exit(1)
    print('Ollama version:', version, '' if version == STUDY_OLLAMA_VERSION else
          f'(study used {STUDY_OLLAMA_VERSION}; results may differ slightly)')
    installed = {m['name']: m.get('digest', '') for m in tags}
    missing = []
    print('\nLocal models (run on your own computer):')
    for name, digest in LOCAL.items():
        if name not in installed:
            print(f'  MISSING  {name}')
            missing.append(name)
        elif installed[name] == digest:
            print(f'  OK       {name}  digest {digest[:12]} (same build as the study)')
        else:
            print(f'  OK*      {name}  digest {installed[name][:12]} differs from study {digest[:12]}')
    print('\nCloud models (need "ollama signin" and free cloud quota):')
    for name in CLOUD:
        try:
            get('/api/show', {'model': name})
            print(f'  OK       {name}')
        except Exception as e:
            print(f'  MISSING  {name}  ({e})')
            missing.append(name)
    if missing:
        print('\nTo install the missing models run:')
        for name in missing:
            print('  ollama pull', name)
        sys.exit(2)
    print('\nAll six study models are available.')
    print('OK* means a newer build of the model; new answers may then differ from the saved ones.')


if __name__ == '__main__':
    main()
