# -*- coding: utf-8 -*-
import re, html, json

s = open('raw2.html', encoding='utf-8', errors='ignore').read()
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

# 预处理：导师行 -> 记录位置；课题名 = 导师行前最近的短文本
tutors = []          # (idx, names, topic)
for n, (k, v) in enumerate(items):
    if k == 't' and v.startswith('导师：'):
        topic = ''
        j = n - 1
        while j >= 0 and items[j][0] == 't' and len(items[j][1]) < 40 and not items[j][1].startswith(('作者', '导师')):
            topic = items[j][1]
            j -= 1
        tutors.append((n, v[3:].strip(), topic))

apos = [n for n, (k, v) in enumerate(items) if k == 't' and v.startswith('作者：')]
works = []
for ai, p in enumerate(apos):
    authors = items[p][1][3:].strip()
    # desc + imgs：作者行之后
    desc, imgs = [], []
    q = p + 1
    while q < len(items):
        k, v = items[q]
        if k == 'i':
            imgs.append(v); q += 1; continue
        if v.startswith(('导师：', '作者：')) or len(v) > 40:
            if v.startswith(('导师：', '作者：')):
                break
            desc.append(v); q += 1; continue
        if imgs:      # 图之后的短文本 = 下一个作品名，停止
            break
        q += 1
    # 标题：作者行之前，逆序收集短文本，遇导师行/图片停止，最多 2 行
    tlines = []
    j = p - 1
    while j >= 0 and len(tlines) < 2:
        k, v = items[j]
        if k == 'i':
            break
        if v.startswith(('导师：', '作者：')):
            break
        if v == '—' or v == '-':
            j -= 1; continue
        if len(v) < 40:
            tlines.append(v)
        j -= 1
    tlines.reverse()
    title = tlines[0] if tlines else ''
    sub = tlines[1] if len(tlines) > 1 else ''
    # 导师：取作者位置之前最近的一条
    tut, top = '', ''
    for (idx, names, tp) in tutors:
        if idx < p:
            tut, top = names, tp
        else:
            break
    works.append({'title': title, 'sub': sub, 'authors': authors, 'tutors': tut,
                  'topic': top, 'desc': ' '.join(desc).strip(), 'imgs': imgs})

print('total', len(works))
for n, w in enumerate(works):
    print(n, '|', w['topic'][:14], '|', w['title'][:22], '|', w['sub'][:22], '|', w['authors'][:16], '|导师', w['tutors'][:12], '| img', len(w['imgs']))
json.dump(works, open('works2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
