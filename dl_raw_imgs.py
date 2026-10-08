# -*- coding: utf-8 -*-
"""下载 raw6b / raw6c 的原图到 cand6b/ cand6c/ (按文章顺序编号)，并保存 URL 顺序。
   用于人工看图分组。"""
import re, html, os

def extract_imgs(fn):
    s = open(fn, encoding='utf-8', errors='ignore').read()
    a = s.find('id="js_content"'); b = s.find('id="js_pc_qr_code"')
    body = s[a:b] if b > a else s[a:]
    urls = re.findall(r'data-src="(https://mmbiz\.qpic\.cn/[^"]+)"', body)
    clean = []
    for u in urls:
        u = html.unescape(u)
        if 'mmbiz.qpic.cn' in u:
            clean.append(u)
    return clean

def download(urls, outdir):
    import urllib.request
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for i, u in enumerate(urls):
        ext = '.jpg' if 'jpeg' in u or 'jpg' in u else ('.png' if 'png' in u else '.gif')
        if 'gif' in u:
            ext = '.gif'
        fn = os.path.join(outdir, '%03d%s' % (i, ext))
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=30).read()
            open(fn, 'wb').write(data)
            n += 1
        except Exception as e:
            print('FAIL', i, e)
    return n

for src, d in [('raw6b.html', 'cand6b'), ('raw6c.html', 'cand6c')]:
    urls = extract_imgs(src)
    print(src, 'images:', len(urls))
    open(src.replace('.html', '_imgs.txt'), 'w').write('\n'.join(urls))
    got = download(urls, d)
    print('  downloaded', got, '->', d)
