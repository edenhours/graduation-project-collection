# -*- coding: utf-8 -*-
"""按「作者：/学生：」锚点切分 raw3（2026 特辑）"""
import re, html, json, sys

src = sys.argv[1] if len(sys.argv) > 1 else 'raw3.html'
out = sys.argv[2] if len(sys.argv) > 2 else 'works3.json'
s = open(src, encoding='utf-8', errors='ignore').read()
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
apos = [n for n, (k, v) in enumerate(items) if k == 't' and v.startswith(AU)]
works = []
for ai, p in enumerate(apos):
    authors = re.sub(r'^(作者|学生)[：:]', '', items[p][1]).strip()
    desc, imgs = [], []
    q = p + 1
    stop = apos[ai + 1] if ai + 1 < len(apos) else len(items)
    while q < stop:
        k, v = items[q]
        if k == 'i':
            imgs.append(v)
        elif v.startswith('指导教师') or v.startswith('指导老师'):
            tut = re.sub(r'^指导(教师|老师)[：:]', '', v).strip()
        elif v.startswith('作品介绍'):
            desc.append(re.sub(r'^作品介绍[：:]', '', v).strip())
        elif len(v) > 50:
            desc.append(v)
        q += 1
    tut = ''
    for q in range(p + 1, stop):
        if items[q][0] == 't' and (items[q][1].startswith('指导教师') or items[q][1].startswith('指导老师')):
            tut = re.sub(r'^指导(教师|老师)[：:]', '', items[q][1]).strip()
            break
    # 标题：作者行之前最近的短文本
    title = ''
    j = p - 1
    while j >= 0:
        k, v = items[j]
        if k == 'i':
            break
        if v.startswith(AU) or v.startswith('指导教师'):
            break
        if 1 < len(v) < 40:
            title = v
            break
        j -= 1
    works.append({'title': title, 'authors': authors, 'tutors': tut,
                  'desc': ' '.join(desc).strip(), 'imgs': imgs})

print('total', len(works))
for n, w in enumerate(works):
    print(n, '|', w['title'][:26], '|', w['authors'][:18], '|导师', w['tutors'][:16], '| img', len(w['imgs']))
json.dump(works, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
