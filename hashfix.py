# -*- coding: utf-8 -*-
"""哈希比对：art_images/a7x 文件 <-> cand6a 文章顺序文件，定位真实文章位置。"""
import hashlib, os, re, json

def md5(p):
    return hashlib.md5(open(p,'rb').read()).hexdigest()

# 1. cand6a: 文章顺序 -> hash
art_order = {}   # hash -> [article_idx...]
for f in sorted(os.listdir('cand6a')):
    h = md5(os.path.join('cand6a', f))
    art_order.setdefault(h, []).append(int(f.split('.')[0]))

# 2. art_images a70-a74: 文件 -> 文章位置
result = {}
for d in ['art_images','art_thumb']:
    for f in sorted(os.listdir(d)):
        m = re.match(r'a(7[0-4])_(\d+)\.(jpg|png|gif)$', f)
        if not m: continue
        h = md5(os.path.join(d, f))
        idxs = art_order.get(h, [])
        result.setdefault(f.split('_')[0], {})[f] = idxs

for aid in sorted(result):
    print('===', aid, '===')
    for f, idxs in sorted(result[aid].items()):
        tag = 'RAW ' if f.startswith(os.path.join('art_images','')[-9:]) or not f.startswith('art_thumb') else 'THUMB'
        print('  ', f.replace('\\','/'), '-> article idx', idxs if idxs else 'NO MATCH')
