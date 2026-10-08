# -*- coding: utf-8 -*-
"""按修正后的归属重新下载 2026 特辑（a22-a31）图片"""
import json, os, glob, urllib.request, concurrent.futures as cf
from PIL import Image

W = json.load(open('works3b.json', encoding='utf-8'))
# 原入选的作品在 works3b 中的索引 -> 新编号（与 data.js 一致）
MAP = [(0,'a22'),(1,'a23'),(2,'a24'),(3,'a25'),(4,'a26'),(5,'a27'),(6,'a28'),(7,'a29'),(13,'a30'),(14,'a31')]

HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36',
       'Referer': 'https://mp.weixin.qq.com/'}

tasks = []
plan = []
for idx, pre in MAP:
    w = W[idx]
    files = [f'{pre}_{j:02d}.jpg' for j in range(len(w['imgs']))]
    for fn, u in zip(files, w['imgs']):
        tasks.append((fn, u))
    plan.append((pre, w['title'], len(files)))


def get(t):
    name, url = t
    p = os.path.join('art_images', name)
    for _ in range(3):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=40).read()
            if len(data) > 2000:
                open(p, 'wb').write(data)
                return name, len(data)
        except Exception as e:
            err = str(e)
    return name, 'FAIL ' + err


ok = 0
with cf.ThreadPoolExecutor(12) as ex:
    for name, r in ex.map(get, tasks):
        if isinstance(r, int):
            ok += 1
        else:
            print(r)
print('downloaded', ok, '/', len(tasks))

meta = json.load(open('meta.json'))
for name, _ in tasks:
    p = os.path.join('art_images', name)
    if not os.path.exists(p):
        continue
    im = Image.open(p); im.load()
    meta[name] = list(im.size)
    tw = 900
    if im.size[0] > tw:
        im = im.resize((tw, round(im.size[1] * tw / im.size[0])), Image.LANCZOS)
    if im.mode in ('RGBA', 'P', 'LA'):
        bg = Image.new('RGB', im.size, (255, 255, 255)); rgba = im.convert('RGBA')
        bg.paste(rgba, mask=rgba.split()[-1]); im = bg
    else:
        im = im.convert('RGB')
    im.save(os.path.join('art_thumb', name), 'JPEG', quality=82, optimize=True)
json.dump(meta, open('meta.json', 'w'))

# 输出 data.js 需要更新的 imgs 字段
print('\n--- 更新后的 imgs ---')
for pre, title, n in plan:
    print(f'{pre} {title} -> ' + str([f'{pre}_{j:02d}.jpg' for j in range(n)]))
