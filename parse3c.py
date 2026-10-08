# -*- coding: utf-8 -*-
"""raw3 修正版 v2：「图在上、文字在下」版式。图组 + 标题 + 作者行构成一个作品。"""
import re, html, json

s = open('raw3.html', encoding='utf-8', errors='ignore').read()
i = s.find('id="js_content"')
body = s[i:s.find('id="js_pc_qr_code"', i)]

tok = re.compile(r'(<img[^>]*>)|(<[^>]+>)')
items = []
last = 0
for m in tok.finditer(body):
    seg = html.unescape(re.sub(r'\s+', ' ', body[last:m.start()].replace('&nbsp;', ' ').replace('\u00a0', ' '))).strip()
    if seg and not seg.startswith('id='):
        items.append(('t', seg))
    last = m.end()
    if m.group(1):
        tag = m.group(1)
        ds = re.search(r'data-src="([^"]+)"', tag) or re.search(r'\ssrc="([^"]+)"', tag)
        if ds:
            items.append(('i', html.unescape(ds.group(1))))

AU = ('作者：', '学生：', '作者:')
SKIP = ('图文来源', '图文编辑', '校对', '审核', '终审')
works = []
pending_imgs, pending_title = [], ''
started = False   # 是否已进入正文（出现过作者行）

for k, v in items:
    if k == 'i':
        pending_imgs.append(v)
        continue
    t = v.strip()
    if t.startswith(AU):
        works.append({'title': pending_title, 'authors': re.sub(r'^(作者|学生)[：:]', '', t).strip(),
                      'tutors': '', 'desc': '', 'imgs': pending_imgs[:]})
        pending_imgs, pending_title = [], ''
        started = True
        continue
    if re.match(r'^(' + '|'.join(SKIP) + ')', t):
        continue
    if works:
        if not works[-1]['tutors'] and (t.startswith('指导教师') or t.startswith('指导老师')):
            works[-1]['tutors'] = re.sub(r'^指导(教师|老师)[：:]', '', t).strip()
            continue
        if not works[-1]['desc'] and (t.startswith('作品介绍') or len(t) > 50):
            works[-1]['desc'] += ' ' + re.sub(r'^作品介绍[：:]', '', t).strip()
            continue
        if t not in ('—', '-') and 1 < len(t) < 45:
            pending_title = t   # 下一作品的标题
        continue
    # 开场阶段：丢弃装饰图
    pending_imgs = []

works = [w for w in works if w['title'] and not re.match(r'^(' + '|'.join(SKIP) + ')', w['title'])]
print('total', len(works))
for n, w in enumerate(works):
    print(n, '|', w['title'][:26], '|', w['authors'][:14], '|', w['tutors'][:14], '| img', len(w['imgs']), '| desc', len(w['desc']))
json.dump(works, open('works3b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
