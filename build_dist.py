import os, base64, json

ROOT = 'C:/Users/23515/Desktop/优秀毕设'
html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
datajs = open(os.path.join(ROOT, 'data.js'), encoding='utf-8').read()
assert 'window.ART_DATA' in datajs, 'data.js 内容异常'

# 1) site/index.html —— 内联新 data.js（部署时 art_thumb/ 文件夹随行）
site_html = html.replace('<script src="data.js"></script>', '<script>\n' + datajs + '\n</script>')
open(os.path.join(ROOT, 'site', 'index.html'), 'w', encoding='utf-8').write(site_html)
print('site/index.html written, bytes=', len(site_html))

# 2) 手机版 —— 内联新 data.js + 内联 art_web 图 base64（按 data.js 引用名查找，扩展名回退到最小可用图）
import re
emb = {}
aw = os.path.join(ROOT, 'art_web')
def find_in_aw(name):
    base = name[:name.rfind('.')] if '.' in name else name
    for c in [name, base+'.jpg', base+'.jpeg', base+'.png', base+'.gif']:
        p = os.path.join(aw, c)
        if os.path.exists(p):
            return p
    return None
names = set()
_data = json.loads(re.search(r'window\.ART_DATA\s*=\s*(\{[\s\S]*\})\s*;', datajs).group(1))
for w in _data['works']:
    for im in w.get('imgs', []):
        names.add(im)
missing = []
for n in names:
    p = find_in_aw(n)
    if not p:
        missing.append(n); continue
    with open(p, 'rb') as f:
        b = f.read()
    low = p.lower()
    mime = 'image/png' if low.endswith('.png') else 'image/gif' if low.endswith('.gif') else 'image/jpeg'
    emb[n] = 'data:%s;base64,%s' % (mime, base64.b64encode(b).decode())
if missing:
    print('WARNING 手机版缺失图(回退art_thumb):', len(missing), missing[:5])
emb_js = '<script>window.EMB=' + json.dumps(emb, ensure_ascii=False) + ';</script>'
phone_html = html.replace('<script src="data.js"></script>', '<script>\n' + datajs + '\n</script>\n' + emb_js)
phone_html = phone_html.replace(
    "const TH = n => 'art_thumb/' + n, IM = n => 'art_images/' + n;",
    "const TH = n => (window.EMB && EMB[n]) ? EMB[n] : 'art_thumb/'+n, IM = n => (window.EMB && EMB[n]) ? EMB[n] : 'art_images/'+n;")
open(os.path.join(ROOT, '毕设档案库-手机版.html'), 'w', encoding='utf-8').write(phone_html)
print('phone written, bytes=', len(phone_html), 'emb images=', len(emb))
