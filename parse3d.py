# -*- coding: utf-8 -*-
"""raw3 修正版 v3：「图在上、文字在下」。图组 → 其后最近的作者行对应的作品。"""
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
SKIP = r'^(图文来源|图文编辑|校对|审核|终审)'

# 1) 作者行 -> 作品
apos = [n for n, (k, v) in enumerate(items) if k == 't' and v.startswith(AU)]
works = []
for ai, p in enumerate(apos):
    authors = re.sub(r'^(作者|学生)[：:]', '', items[p][1]).strip()
    # 标题：作者行之前最近的、长度合适的短文本
    title = ''
    for j in range(p - 1, -1, -1):
        k, v = items[j]
        if k == 'i':
            continue
        if v.startswith(AU) or re.match(SKIP, v) or v.startswith(('指导教师', '指导老师')) or len(v) > 50:
            continue
        if v in ('—', '-'):
            continue
        title = v
        break
    # 介绍与导师：作者行之后
    desc, tutors = '', ''
    stop = apos[ai + 1] if ai + 1 < len(apos) else len(items)
    for q in range(p + 1, stop):
        k, v = items[q]
        if k == 'i':
            continue
        if not tutors and v.startswith(('指导教师', '指导老师')):
            tutors = re.sub(r'^指导(教师|老师)[：:]', '', v).strip()
        elif len(v) > 50 or v.startswith('作品介绍'):
            desc += ' ' + re.sub(r'^作品介绍[：:]', '', v).strip()
    works.append({'title': title, 'authors': authors, 'tutors': tutors, 'desc': desc.strip(), 'imgs': []})

# 2) 图组 -> 其后最近的作者行
groups, cur = [], None
for n, (k, v) in enumerate(items):
    if k == 'i':
        if cur is None:
            cur = {'s': n, 'imgs': []}
        cur['imgs'].append(v)
    else:
        if cur is not None:
            cur['e'] = n - 1
            groups.append(cur)
            cur = None
if cur is not None:
    cur['e'] = len(items) - 1
    groups.append(cur)

for g in groups:
    # 图组后第一个文本
    nxt = None
    for q in range(g['e'] + 1, len(items)):
        if items[q][0] == 't':
            nxt = (q, items[q][1])
            break
    if nxt is None:
        continue
    q, txt = nxt
    # 图组后紧跟长开场语（非作品介绍）=> 装饰图，丢弃
    if len(txt) > 50 and not txt.startswith('作品介绍'):
        continue
    if re.match(SKIP, txt):
        continue
    # 找其后最近的作者行
    tgt = next((ai for ai, p in enumerate(apos) if p >= g['e']), None)
    if tgt is None:
        continue
    works[tgt]['imgs'].extend(g['imgs'])

print('total', len(works))
for n, w in enumerate(works):
    print(n, '|', w['title'][:24], '|', w['authors'][:14], '|', w['tutors'][:12], '| img', len(w['imgs']))
json.dump(works, open('works3b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
