import re, html, json

s = open('raw.html', encoding='utf-8', errors='ignore').read()
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

DEPS = ['工业与交互设计系', '产品设计系', '艺术设计系', '染织艺术设计系', '服装与服饰设计系']
works = []
intro = {}
cur = None
dep = None


def flush():
    global cur
    if cur and (cur.get('imgs') or cur.get('desc') or cur.get('authors')):
        works.append(cur)
    cur = None


def new(title):
    global cur
    flush()
    cur = {'title': title, 'authors': '', 'teachers': '', 'desc': '', 'imgs': [], 'dep': dep}


for k, v in items:
    if k == 't':
        t = v.strip()
        if t in DEPS:
            flush(); dep = t; continue
        if re.match(r'^(广州美术学院|图文来源|校对|审核|终审)', t):
            continue
        if t.startswith('作者：') or t.startswith('指导老师：') or t.startswith('共创者：'):
            if cur is None:
                new('')
            if t.startswith('作者：'):
                if cur['authors']:
                    new('')  # 缺标题的新作品
                cur['authors'] = t[3:].strip()
            elif t.startswith('共创者'):
                cur['authors'] = (cur['authors'] + ' / 共创 ' + t[4:].strip()).strip(' /')
            else:
                cur['teachers'] = t[5:].strip()
            continue
        if cur is None:
            if len(t) > 60:
                intro[dep] = t
            else:
                new(t)
            continue
        # 已有作品
        if len(t) > 60 and not cur['desc']:
            cur['desc'] = t
        elif cur['desc'] and len(t) > 40:
            cur['desc'] += ' ' + t
        elif cur['authors'] or cur['imgs'] or cur['desc']:
            new(t)  # 新作品标题
        else:
            cur['title'] = t
    else:
        if cur is not None:
            cur['imgs'].append(v)
flush()

print('works', len(works), 'imgs', sum(len(w['imgs']) for w in works))
for n, w in enumerate(works):
    print(n, '|', w['dep'], '|', w['title'][:32], '|', w['authors'][:20], '|', w['teachers'][:16], '| imgs', len(w['imgs']))
json.dump({'works': works, 'intro': intro}, open('works.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
