# -*- coding: utf-8 -*-
"""修复：损坏图重下 / a117 补 wx 图 / a33 梦鼎富化"""
import json, os, re, hashlib, shutil, urllib.request, time
from PIL import Image

def md5(p): return hashlib.md5(open(p,'rb').read()).hexdigest()

def try_dl(url, dst, referer):
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36','Referer':referer})
        data = urllib.request.urlopen(req, timeout=40).read()
        if len(data) < 1500: return False   # 错误页一般很小
        open(dst,'wb').write(data)
        im = Image.open(dst); im.load()      # 验证是图
        return True
    except Exception as e:
        print('  FAIL', url[:70], str(e)[:60]); return False

def make_thumb(src, dst, tw=900):
    try:
        im = Image.open(src); im.load()
        w,h = im.size
        if w > tw: im = im.resize((tw, max(1, round(h*tw/w))), Image.LANCZOS)
        if im.mode in ('RGBA','P','LA'):
            bg = Image.new('RGB', im.size, (255,255,255)); im = im.convert('RGBA')
            bg.paste(im, mask=im.split()[-1]); im = bg
        else: im = im.convert('RGB')
        im.save(dst,'JPEG',quality=88); return True
    except Exception as e:
        print('  thumb fail', src, e); return False

# ---------- 1. 修复损坏的 sid 图 ----------
ws = json.load(open('works_sid.json', encoding='utf-8'))
sid = {r['col']: r for r in json.load(open('sid_data.json', encoding='utf-8'))}
col_by_id = {'a117':'2218_57304','a118':'2398_61824','a119':'2398_61694','a120':'2398_61814',
             'a121':'2398_61764','a122':'2098_50434','a123':'2098_50244','a124':'2098_50514',
             'a125':'2098_50204','a126':'2098_50274','a127':'2098_50354'}

for w in ws:
    urls = sid[col_by_id[w['id']]]['imgs']
    keep = []
    for i, im in enumerate(w['imgs']):
        p = os.path.join('art_images', im)
        ok = False
        try:
            img = Image.open(p); img.load()
            ok = os.path.getsize(p) >= 1500
        except Exception:
            ok = False
        if not ok and i < len(urls):
            print('重下', w['id'], i, urls[i][:60])
            ok = try_dl(urls[i], p, 'https://sid.gzarts.edu.cn/')
        if ok:
            if not os.path.exists(os.path.join('art_thumb', im)):
                make_thumb(p, os.path.join('art_thumb', im))
            keep.append(im)
        else:
            print('  丢弃', im)
            for f in (p, os.path.join('art_thumb', im)):
                os.path.exists(f) and os.remove(f)
    w['imgs'] = keep

# ---------- 2. a117 补公众号特奖报道图 ----------
a117 = ws[0]
wxhtml = open('raw7w.html', encoding='utf-8', errors='ignore').read()
wxurls = re.findall(r'data-src="(https://mmbiz[^"]+)"', wxhtml)
wxurls = [u.replace('refersize=0','').strip() for u in wxurls]
have = {md5(os.path.join('art_images', im)) for im in a117['imgs']}
seen = set()
idx = len(a117['imgs'])
for u in wxurls:
    tmp = os.path.join('_sidtmp', 'wx' + hashlib.md5(u.encode()).hexdigest() + '.jpg')
    if not os.path.exists(tmp):
        if not try_dl(u, tmp, 'https://mp.weixin.qq.com/'): continue
    h = md5(tmp)
    if h in seen or h in have: continue
    seen.add(h); have.add(h)
    name = 'a117_%02d.jpg' % idx; idx += 1
    shutil.copy(tmp, os.path.join('art_images', name))
    make_thumb(os.path.join('art_images', name), os.path.join('art_thumb', name))
    a117['imgs'].append(name)
print('a117 最终图片数:', len(a117['imgs']))

json.dump(ws, open('works_sid.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('works_sid.json 更新完成')
