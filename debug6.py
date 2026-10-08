# -*- coding: utf-8 -*-
import sys, re, html

def tokenize(fn):
    s = open(fn, encoding='utf-8', errors='ignore').read()
    a = s.find('id="js_content"'); b = s.find('id="js_pc_qr_code"')
    if a < 0: a = 0
    body = s[a:b] if b > a else s[a:]
    tok = re.compile(r'(<img[^>]*>)|(<[^>]+>)')
    items = []; last = 0
    for m in tok.finditer(body):
        seg = html.unescape(re.sub(r'\s+', ' ', body[last:m.start()]
                                   .replace('&nbsp;', ' ').replace(' ', ' '))).strip()
        if seg and not seg.startswith('id='):
            items.append(('t', seg))
        last = m.end()
        if m.group(1):
            ds = re.search(r'data-src="([^"]+)"', m.group(1)) or re.search(r'\ssrc="([^"]+)"', m.group(1))
            if ds:
                items.append(('i', html.unescape(ds.group(1))))
    return items

fn = sys.argv[1]
items = tokenize(fn)
print(f"=== {fn}: {len(items)} tokens ===")
imgc = 0
for idx,(k,v) in enumerate(items):
    if k == 't':
        s = v if len(v) <= 50 else v[:50] + f'…({len(v)})'
        print(f"{idx:3d} T: {s}")
    else:
        imgc += 1
        print(f"{idx:3d} I: <img {imgc}>")
