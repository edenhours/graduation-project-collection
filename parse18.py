# -*- coding: utf-8 -*-
"""解析设计竞赛网 2018 届生活工作室两篇文章：标题/作者/描述/图片组配对"""
import re, html, json

def tokens(fn):
    s = open(fn, encoding='utf-8', errors='ignore').read()
    # WordPress 正文：entry-content
    m = re.search(r'entry-content[^>]*>', s)
    if m:
        s = s[m.end():]
        end = s.find('</article>')
        if end < 0: end = s.find('class="entry-footer"')
        if end > 0: s = s[:end]
    out = []
    # 顺序扫描：<img> 与文本块
    for mm in re.finditer(r'<img[^>]+?src="([^"]+)"[^>]*>|<p[^>]*>(.*?)</p>', s, re.S | re.I):
        if mm.group(1):
            u = html.unescape(mm.group(1)).split('#')[0]
            base = u.rsplit('/', 1)[-1]
            if 'uploads/' in u and not re.search(r'^(logo|tubiao|cropped|icon|avatar|emoji|qrcode)', base, re.I) and len(base) > 12:
                out.append(('i', u))
        else:
            body = mm.group(2)
            # p 内嵌图：先抽图
            for im in re.finditer(r'<img[^>]+?src="([^"]+)"', body, re.I):
                u = html.unescape(im.group(1)).split('#')[0]
                base = u.rsplit('/', 1)[-1]
                if 'uploads/' in u and not re.search(r'^(logo|tubiao|cropped|icon|avatar|emoji|qrcode)', base, re.I) and len(base) > 12:
                    out.append(('i', u))
            txt = re.sub(r'<[^>]+>', '', body)
            txt = html.unescape(txt).strip()
            txt = re.sub(r'&nbsp;?', ' ', txt)
            txt = re.sub(r'\s+', '', txt)
            if txt: out.append(('t', txt))
    return out

def parse(fn, year):
    items = tokens(fn)
    works, cur = [], None
    for typ, val in items:
        if typ == 't':
            mt = re.match(r'^[《《](.+?)[》》]', val)
            ma = re.match(r'设计[:：](.+)$', val)
            if mt:
                if cur: works.append(cur)
                cur = {'title': mt.group(1), 'author': '', 'desc': '', 'imgs': []}
            elif ma and cur and not cur['author']:
                cur['author'] = ma.group(1)
            elif cur:
                # 描述段（跳过导师介绍等长bio：含"导师"/"毕业于"/"研究方向"开头且无对应作品上下文）
                if not re.match(r'(导师|毕业|研究|讲师|副教授|教授)', val) or len(val) < 200:
                    cur['desc'] += val
        else:
            if cur: cur['imgs'].append(val)
    if cur: works.append(cur)
    for w in works: w['year'] = year
    return works

wa = parse('raw18a.html', '2018')
wb = parse('raw18b.html', '2018')
allw = wa + wb
print('article1:', len(wa), '| article2:', len(wb))
for i, w in enumerate(allw):
    print('%2d %-14s | %-6s | imgs %2d | %s' % (i, w['title'], w['author'], len(w['imgs']), w['desc'][:40]))
json.dump(allw, open('works18.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written works18.json')
