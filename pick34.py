# -*- coding: utf-8 -*-
"""下载 2026 特辑 + 2024 届入选作品图片，生成缩略图"""
import json, os, urllib.request, urllib.parse, concurrent.futures as cf
from PIL import Image

W3 = json.load(open('works3.json', encoding='utf-8'))
W4 = json.load(open('works4.json', encoding='utf-8'))

# (源, 索引, 主标题, 副标题, 视频vid或None)
PICKS = [
    ('W3', 0,  '微光构造',   '科创文化艺术衍生品',            None),
    ('W3', 1,  '“工具”系列', '人体护理品牌',                  None),
    ('W3', 2,  '占嬉',       '基于传统占卜文化研究的体验产品设计', None),
    ('W3', 3,  '？！',       '',                              None),
    ('W3', 4,  '前童十四夜', '',                              None),
    ('W3', 5,  '盒藏南沙',   '',                              None),
    ('W3', 6,  '新莨乡记',   '香云纱非遗研学体系',            None),
    ('W3', 7,  '好运事务所', '岭南吉祥文化 IP 品牌',          None),
    ('W3', 13, '罐头猫才',   '',                              None),
    ('W3', 14, '瓷渊',       '海丝沉船瓷器潮玩设计',          None),
    ('W4', 0,  '随福',       '春节户外产品',                  None),
    ('W4', 1,  '梦鼎',       '文物数字叙事',                  'wxv_3471829309860397060'),
    ('W4', 3,  '完形',       '音形联想',                      None),
    ('W4', 4,  '清悦',       '熏香生活产品设计',              None),
    ('W4', 5,  '沿途的风景', '墙边的慰藉',                    'wxv_3472252056914673665'),
    ('W4', 6,  '待定',       'TO BE RECOGNIZED',              None),
    ('W4', 7,  '莲脉传情',   '',                              None),
    ('W4', 8,  '莲谱',       '',                              None),
    ('W4', 9,  '节节高灯',   '',                              None),
    ('W4', 10, '金玉满棠',   '方寸之间',                      None),
]

HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36',
       'Referer': 'https://mp.weixin.qq.com/'}
os.makedirs('art_images', exist_ok=True)
os.makedirs('art_thumb', exist_ok=True)
meta = json.load(open('meta.json'))

# 视频封面
COVER = {
    'wxv_3471829309860397060': 'http://mmbiz.qpic.cn/mmbiz_jpg/1VXV0QewoMFRghib9WPudEyWx7v1xCwUoAkF3EZAOk1B3nicDtHP5lIicqGsjlvsdweibyx4qibPDiaE0fAv0C2SVDYw/0?wx_fmt=jpeg',
    'wxv_3472252056914673665': 'http://mmbiz.qpic.cn/mmbiz_jpg/1VXV0QewoMFRghib9WPudEyWx7v1xCwUohUHicx9cib3d9HJWQV6ibG5ibtQ2nOAvR1cibc8wN2SEoib9bcKM0g3ic8nmw/0?wx_fmt=jpeg',
}

tasks = []   # (name, url)
out = []
for k, (src, idx, title, sub, vid) in enumerate(PICKS):
    w = (W3 if src == 'W3' else W4)[idx]
    n = k + 22
    files = []
    if vid and COVER.get(vid):
        fn = f'a{n:02d}_00.jpg'
        tasks.append((fn, COVER[vid]))
        files.append(fn)
    for j, u in enumerate(w['imgs']):
        fn = f'a{n:02d}_{len(files):02d}.jpg'
        tasks.append((fn, u))
        files.append(fn)
    desc = w['desc']
    if 'var first_sceen__time' in desc:
        desc = desc.split('var first_sceen__time')[0].strip()
    out.append({'file': f'a{n:02d}', 'title': title, 'sub': sub, 'authors': w['authors'],
                'tutors': w['tutors'], 'desc': desc, 'imgs': files,
                'video': (f'https://mp.weixin.qq.com/mp/readtemplate?t=pages/video_player_tmpl&action=mpvideo&auto=0&vid={vid}' if vid else '')})


def get(t):
    name, url = t
    p = os.path.join('art_images', name)
    if os.path.exists(p) and os.path.getsize(p) > 2000:
        return name, 'skip'
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
        if r == 'skip' or isinstance(r, int):
            ok += 1
        else:
            print(r)
print('downloaded', ok, '/', len(tasks))

for name, _ in tasks:
    p = os.path.join('art_images', name)
    if not os.path.exists(p):
        continue
    try:
        im = Image.open(p); im.load()
    except Exception as e:
        print('bad img', name, e); continue
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
json.dump(out, open('pick34.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for o in out:
    print(o['file'], '|', o['title'], '|', o['sub'], '|', o['authors'][:20], '|导师', o['tutors'], '| img', len(o['imgs']), '| vid', bool(o['video']))
