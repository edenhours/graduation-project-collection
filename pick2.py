# -*- coding: utf-8 -*-
"""从 2025 届作品中挑选优秀者，下载图片并生成缩略图"""
import json, os, urllib.request, concurrent.futures as cf
from PIL import Image

W = json.load(open('works2.json', encoding='utf-8'))
# 入选的 2025 届作品（works2.json 索引 -> 新编号）
PICK = [0, 1, 2, 3, 4, 5, 7, 8, 9, 11, 15, 17, 19, 23, 29, 38, 39]

HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
       'Referer': 'https://mp.weixin.qq.com/'}
os.makedirs('art_images', exist_ok=True)
os.makedirs('art_thumb', exist_ok=True)

meta = json.load(open('meta.json'))
out = []
tasks = []
for k, idx in enumerate(PICK):
    w = W[idx]
    name = f'a{k+5:02d}_00.jpg'
    url = w['imgs'][0]
    tasks.append((name, url))
    out.append({'idx': idx, 'file': name, 'title': w['title'], 'sub': w['sub'],
                'authors': w['authors'], 'tutors': w['tutors'], 'topic': w['topic'], 'desc': w['desc']})


def get(t):
    name, url = t
    p = os.path.join('art_images', name)
    for _ in range(3):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=30).read()
            if len(data) > 2000:
                open(p, 'wb').write(data)
                return name, len(data)
        except Exception as e:
            err = str(e)
    return name, 'FAIL ' + err


ok = 0
with cf.ThreadPoolExecutor(10) as ex:
    for name, r in ex.map(get, tasks):
        if isinstance(r, int):
            ok += 1
        else:
            print(r)
print('downloaded', ok, '/', len(tasks))

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
json.dump(out, open('pick2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for o in out:
    print(o['file'], '|', o['title'], '|', o['sub'], '|', o['authors'], '|导师', o['tutors'])
