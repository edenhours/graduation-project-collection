# -*- coding: utf-8 -*-
"""解析三篇公众号文章 -> works6.json 候选作品 (清洗版)。
   raw6a (太行山设计/生活工作室): 《》标题 + 导师分组
   raw6b/raw6c: 图文簇「前文+簇内短注」规则 + 作者捕获 + 去头像/去废/排除糖
"""
import re, html, json

def tokenize(fn):
    s = open(fn, encoding='utf-8', errors='ignore').read()
    a = s.find('id="js_content"'); b = s.find('id="js_pc_qr_code"')
    if a < 0: a = 0
    body = s[a:b] if b > a else s[a:]
    tok = re.compile(r'(<img[^>]*>)|(<[^>]+>)')
    items = []; last = 0
    for m in tok.finditer(body):
        seg = html.unescape(re.sub(r'\s+', ' ', body[last:m.start()]
                                   .replace('&nbsp;', ' ').replace(' ', ' '))).strip()
        if seg and not seg.startswith('id='):
            items.append(('t', seg))
        last = m.end()
        if m.group(1):
            ds = re.search(r'data-src="([^"]+)"', m.group(1)) or re.search(r'\ssrc="([^"]+)"', m.group(1))
            if ds:
                items.append(('i', html.unescape(ds.group(1))))
    return items

BIO_KW = ['应届','考入','毕业','获奖','奖','项','届','研究生','讲师','教授','副教授',
          '主任','导师','设计学院','工业设计','艺术设','研究所','获得','KTK','DNA',
          '欧洲','日本','香港','国际','当代','意思设计','武汉','双年展','论文','期刊',
          '参与展览','发表','设计：','广东','广州美术学院','大学城','硕士研究生']
EXHIBIT = ['展览现场','展览时间','展览地址','参展作者','end','预览时标签','修改于',
           '设计感知','本质','主观','并非将','主题介绍','毕业设计分为','工作室期间设计作品']
PURE_NUM = re.compile(r'^[\d\s、，。.,：:·\-\s]+$')
BIO_NEAR = ['应届','考入','毕业','研究生','届毕业生','产品设计专业']

def is_bio(t):
    return any(k in t for k in BIO_KW)

def is_exhibit(t):
    return any(k in t for k in EXHIBIT)

def is_short_cap(t):
    if not t or is_exhibit(t): return False
    if PURE_NUM.match(t): return False
    return 0 < len(t) <= 32 and not is_bio(t)

def is_desc_para(t):
    if not t or is_exhibit(t) or is_bio(t): return False
    if PURE_NUM.match(t): return False
    return len(t) > 32

def is_name_and_bio(items, i):
    # token i is an author name if followed soon by bio marker
    if i >= len(items): return None
    t = items[i][1]
    if items[i][0] != 't': return None
    if is_bio(t) or is_exhibit(t): return None
    if PURE_NUM.match(t): return None
    if len(t) > 12: return None
    # look ahead up to 3 tokens
    for j in range(i+1, min(i+4, len(items))):
        if items[j][0] == 't' and any(k in items[j][1] for k in BIO_NEAR):
            return t.strip()
    return None

def is_video_url(t):
    return t.startswith('http') and ('qq.com' in t or 'iqiyi' in t or 'v.' in t or 'youku' in t)

# ---------- raw6a: 《》 based ----------
def parse_a():
    items = tokenize('raw6a.html')
    works = []
    teacher = ''
    i = 0; n = len(items)
    cur = None
    def flush():
        nonlocal cur
        if cur and (cur['imgs'] or cur['desc']):
            works.append(cur)
        cur = None
    # precompute teacher per token index (scan once, independent of title loop)
    teacher_now = ''
    teacher_at = ['' ] * n
    for idx in range(n):
        k, v = items[idx]
        if k == 't' and '毕业生作品' in v:
            mm = re.search(r'(磨炼|张剑|卢文英|赵斌)', v)
            if mm:
                teacher_now = mm.group(1)
            elif idx > 0 and items[idx-1][0] == 't':
                mm = re.search(r'(磨炼|张剑|卢文英|赵斌)', items[idx-1][1])
                if mm:
                    teacher_now = mm.group(1)
        teacher_at[idx] = teacher_now
    first_title = next((k for k in range(n)
                        if items[k][0]=='t' and re.search(r'《[^《》]{2,}》', items[k][1])), None)
    while i < n:
        k, v = items[i]
        if k == 't':
            m = re.search(r'《([^《》]{2,})》', v)
            if m:
                title = m.group(1)
                if any(x in title for x in ['毕业设计','学院','广州美术学院','绽放']):
                    i += 1; continue
                flush()
                teacher = teacher_at[i] or teacher
                cur = {'title': title, 'teacher': teacher, 'author': '', 'desc': '',
                       'imgs': [], 'video': ''}
                j = i + 1; buf = []
                while j < n:
                    kk, vv = items[j]
                    if kk == 't':
                        if re.search(r'《[^《》]{2,}》', vv) and j != i:
                            break
                        if vv.startswith('设计：'):
                            cur['author'] = vv[3:].strip()
                        elif vv.startswith('视频链接'):
                            pass
                        elif is_video_url(vv):
                            cur['video'] = vv
                        else:
                            buf.append(vv)
                    else:
                        if j > (first_title or 0):
                            cur['imgs'].append(vv)
                    j += 1
                cur['desc'] = ' '.join([b for b in buf if b and not is_bio(b) and not is_video_url(b)])
                i = j
                continue
        i += 1
    flush()
    # drop duplicate covers: imgs<=1 and a sibling with related title
    out = []
    for w in works:
        w['src'] = 'a'; w['year'] = '2025'
        out.append(w)
    drop = set()
    for a in out:
        if a['imgs'] and len(a['imgs']) <= 1:
            for b in out:
                if b is a: continue
                if (b['title'].startswith(a['title']) or a['title'].startswith(b['title'])) and b['imgs']:
                    drop.add(id(a))
    out = [w for w in out if id(w) not in drop]
    return out

# ---------- cluster: 前文+簇内短注 ----------
def parse_cluster(fn, src, year, single_author=None, exclude_kw=None, teacher=''):
    items = tokenize(fn)
    exclude_kw = exclude_kw or []
    n = len(items)
    # 1) detect author markers
    author_at = {}
    cur_author = single_author or ''
    for i in range(n):
        nm = is_name_and_bio(items, i)
        if nm:
            cur_author = nm
        author_at[i] = cur_author
    # 2) build image groups; inside short-caps recorded
    groups = []  # each: {'imgs':[], 'inside':[], 'start':idx, 'end':idx}
    i = 0
    while i < n:
        if items[i][0] == 'i':
            g = {'imgs': [], 'inside': [], 'start': i, 'end': i}
            j = i
            while j < n:
                if items[j][0] == 'i':
                    g['imgs'].append(items[j][1]); g['end'] = j; j += 1
                elif items[j][0] == 't' and is_short_cap(items[j][1]):
                    g['inside'].append(items[j][1]); g['end'] = j; j += 1
                else:
                    break
            if g['imgs']:
                groups.append(g)
            i = j
        else:
            i += 1
    # 3) preceding text for each group
    text_idx = {}  # idx -> text token
    for idx,(k,v) in enumerate(items):
        if k=='t': text_idx[idx]=v
    works = []
    prev_end = -1
    for g in groups:
        preceding = []
        for idx in range(prev_end+1, g['start']):
            if idx in text_idx:
                t = text_idx[idx]
                if is_desc_para(t) or is_short_cap(t):
                    preceding.append(t)
        desc = ' '.join(preceding + g['inside'])
        author = author_at[g['start']] or single_author or ''
        works.append({'title':'', 'teacher': teacher, 'author': author, 'desc': desc,
                      'imgs': g['imgs'][:8], 'video':'', 'src': src, 'year': year})
        prev_end = g['end']
    # 4) orphan trailing desc_para -> append to last work
    tail = []
    for idx in range(prev_end+1, n):
        if idx in text_idx:
            t = text_idx[idx]
            if is_desc_para(t):
                tail.append(t)
    if tail and works:
        works[-1]['desc'] = works[-1]['desc'] + ' ' + ' '.join(tail)
    # 5) post-process
    out = []
    for w in works:
        d = w['desc'].strip()
        imgs = w['imgs']
        if not imgs:
            continue
        if not d:
            continue  # empty-desc stray (avatar etc.)
        if len(imgs) <= 1 and (len(d) <= 6 or is_pure_name(d) or '展览现场' in d):
            continue  # avatar/cover
        if any(x in d for x in ['展览现场','NEW GENERATION','是指我们对事物的知觉',
                                 '期刊论文','论文','初探','实践方法介入','毕业设计分为两个部分']):
            continue
        if d in {'作品'} or is_pure_name(d):
            continue
        if any(k in d for k in exclude_kw):
            continue
        w['title'] = derive_title(d)
        out.append(w)
    return out

def is_pure_name(t):
    return bool(re.match(r'^[一-鿿]{2,4}$', t.strip())) or bool(re.match(r'^[一-鿿]{2,4}\s+[一-鿿]{2,4}$', t.strip()))

def derive_title(d):
    d2 = re.sub(r'^[\s（(】].*?[:：]', '', d)
    s = re.split(r'[。！？；\n]', d2)[0]
    s = re.sub(r'^(这是一款|本设计|本作品|作品|我们|这是|一款|设计说明[:：]?|设计[:：]?|将|利用|通过|在|一只|一个|这是一只|这是一款)', '', s).strip()
    s = s.strip('，,。 ')
    if len(s) > 18:
        s = s[:18]
    return s or '作品'

if __name__ == '__main__':
    wa = parse_a()
    wb = parse_cluster('raw6b.html', 'b', '2025', single_author='', exclude_kw=[], teacher='张剑')
    wc = parse_cluster('raw6c.html', 'c', '2026', single_author='黄治权',
                       exclude_kw=['糖','培养皿','结晶','相框','融化','肌理','糖果'], teacher='张剑')
    allw = wa + wb + wc
    for w in allw:
        w.pop('pending_raw', None) if 'pending_raw' in w else None
    json.dump(allw, open('works6.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('=== raw6a (生活工作室) ===')
    for w in wa:
        print(f"  [{w['teacher']}] 《{w['title']}》 {w['author']} | img {len(w['imgs'])}")
    print(f'raw6a: {len(wa)}')
    print('\n=== raw6b (设计感知研究所2025) ===')
    for w in wb:
        print(f"  [{w['author']}] {w['title'][:16]:18} | img {len(w['imgs'])}")
    print(f'raw6b: {len(wb)}')
    print('\n=== raw6c (黄治权2026, 糖已排除) ===')
    for w in wc:
        print(f"  {w['title'][:16]:18} | img {len(w['imgs'])}")
    print(f'raw6c: {len(wc)}')
    print('\nTOTAL:', len(allw))
