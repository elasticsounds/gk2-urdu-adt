#!/usr/bin/env python3
"""Validate the English edition fields of content/pNNN.json.  usage: validate_en.py content/p006.json ..."""
import json, re, sys
AR = re.compile(r'[؀-ۿ]')
def check(fn):
    errs = []
    try: d = json.load(open(fn, encoding='utf-8'))
    except Exception as ex: return ['bad JSON: %s' % ex]
    def walk(o, path):
        if isinstance(o, dict):
            if 'words' in o and isinstance(o['words'], list):          # easy-read sentence
                en = o.get('en', '')
                we = o.get('words_en')
                if not isinstance(we, list) or not we: errs.append(f'{path}: sentence needs words_en')
                else:
                    for w in we:
                        if not isinstance(w, dict) or not isinstance(w.get('en'), str) or not w['en'].strip(): errs.append(f'{path}: words_en item needs "en"'); break
                        if 'sym' not in w and 'img' not in w: errs.append(f'{path}: words_en item "{w["en"]}" needs "sym" (keyword or null) or "img"')
                        if 'ur' in w: errs.append(f'{path}: words_en items must not have "ur"')
                    else:
                        j = ' '.join(w['en'].strip() for w in we)
                        if j != en.strip(): errs.append(f'{path}: words_en joined = "{j}" but en = "{en}"')
                        n = len(en.split())
                        if n > 9: errs.append(f'{path}: easy sentence too long ({n} words): "{en}"')
                        if not any(w.get('sym') or w.get('img') for w in we): errs.append(f'{path}: no symbols in words_en')
            elif isinstance(o.get('ur'), str) and o['ur'].strip() and not path.endswith('words'):
                en = o.get('en')
                if not isinstance(en, str) or not en.strip(): errs.append(f'{path}: missing en for "{o["ur"][:30]}"')
                elif AR.search(en): errs.append(f'{path}: Urdu script inside en: "{en[:50]}"')
                elif o['ur'].count('___') != en.count('___'): errs.append(f'{path}: blank count differs: "{en[:50]}"')
            if o.get('kind') == 'fill':
                for i, q in enumerate(o.get('questions', [])):
                    if q.get('q', {}).get('en', '').count('___') != 1: errs.append(f'{path}.q{i}: fill q.en needs exactly one ___')
            for k, v in o.items():
                if k in ('words_en',): continue
                walk(v, f'{path}.{k}' if path else k)
        elif isinstance(o, list):
            for i, v in enumerate(o): walk(v, f'{path}[{i}]' if not path.endswith('words') else path)
    walk(d, '')
    return errs
bad = 0
for fn in sys.argv[1:]:
    e = check(fn)
    if e:
        bad += 1; print(fn, 'FAIL'); [print('   ', x) for x in e[:40]]
    else: print(fn, 'OK')
sys.exit(1 if bad else 0)
