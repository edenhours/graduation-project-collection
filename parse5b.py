# -*- coding: utf-8 -*-
"""解析 2022 届 raw5 v2：区分「独立作品（图在文后）」与「子作品（图在文前）」。"""
import re, html, json

s = open('raw5.html', encoding='utf-8', errors='ignore').read()
body = s[s.find('id="js_content"'):s.find('id="js_pc_qr_code"')]

# tokenize
tok = re.compile(r'(<img[^>]*>)|(<[^>]+>)')
items = []; last = 0
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

# find title anchors
anchors = []
for idx, (k, v) in enumerate(items):
    if k != 't': continue
    for m in re.finditer(r'《([^《》]{2,80})》', v):
        title = m.group(1)
        if any(x in title for x in ['毕业设计','学院','绽放','广州美术学院']):
            continue
        is_sub = '|' in v or '｜' in v
        # sub-work author after |
        author = ''
        mm = re.search(r'》\s*[|\\/]\s*([^\n]{2,40}?)(?:<br|$)', v)
        if not mm:
            mm = re.search(r'》\s*[|\\/]\s*([\u4e00-\u9fa5·\.a-zA-Z\s、，,]+?)(?=\s|$)', v)
        if mm:
            author = mm.group(1).strip()
        anchors.append({'idx': idx, 'title': title, 'is_sub': is_sub, 'author_hint': author, 'full': v})

works = []
for n, a in enumerate(anchors):
    p = a['idx']
    prev_p = anchors[n-1]['idx'] if n > 0 else 0
    next_p = anchors[n+1]['idx'] if n+1 < len(anchors) else len(items)
    next_is_sub = anchors[n+1]['is_sub'] if n+1 < len(anchors) else False
    
    # image assignment
    if a['is_sub']:
        # images between previous anchor and this title
        imgs = [v for k, v in items[prev_p:p] if k == 'i']
    else:
        if next_is_sub:
            # group header with sub-works: no own images
            imgs = []
        else:
            # standalone: images after this title until next title
            imgs = [v for k, v in items[p:next_p] if k == 'i']
    
    # text region for metadata: from this title to next anchor
    region_texts = [v for k, v in items[p:next_p] if k == 't']
    my_title = a['title']
    authors = a['author_hint']
    tutors = ''
    desc = ''
    for t in region_texts:
        if my_title in t and len(t) < len(my_title) + 30:
            continue
        if not authors and re.search(r'^(作者|学生)[:：\s\\]', t):
            authors = re.sub(r'^(作者|学生)[:：\s\\]+', '', t).strip()
        elif not tutors and re.search(r'^指导(老师|教师)[:：\s\\]', t):
            tutors = re.sub(r'^指导(老师|教师)[:：\s\\]+', '', t).strip()
        elif len(t) > 50:
            desc = re.sub(r'^作品介绍[:：\s\\]+', '', t).strip()
            break
        elif len(t) > 25 and not desc:
            desc = t
    
    # if sub-work has no desc, inherit from last non-sub group header
    if a['is_sub'] and not desc:
        for prev in reversed(works):
            if not prev.get('is_sub') and prev.get('desc'):
                desc = '(子作品，共享课题说明) ' + prev['desc']
                break
    
    works.append({'title': my_title, 'authors': authors, 'tutors': tutors, 'desc': desc,
                  'imgs': imgs, 'n_img': len(imgs), 'is_sub': a['is_sub']})

print('parsed works:', len(works))
for n, w in enumerate(works):
    print(f'{n:02d}', '|', w['title'][:26], '|A:', w['authors'][:18], '|T:', w['tutors'][:14], '|img', w['n_img'])

json.dump(works, open('works5b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
