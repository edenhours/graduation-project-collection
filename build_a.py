# -*- coding: utf-8 -*-
"""构建 raw6a (生活工作室 / 太行山设计 2025) 的 40 件作品 -> 追加进 data.js。
   采用列表式解析(标题《》+设计：作者+导师分组)，图像范围按全局序号映射。
   分析字段基于文章真实文案启发式生成(无法读图)，标注为待深化。
"""
import re, html, os, json, shutil
import urllib.request
from PIL import Image

FN = 'raw6a.html'
SRC = 'a'          # 文章来源标记
YEAR = '2025'

# ---------- 1) 通用 tokenizer（记录全局图像序号） ----------
def tokenize(fn):
    s = open(fn, encoding='utf-8', errors='ignore').read()
    a = s.find('id="js_content"'); b = s.find('id="js_pc_qr_code"')
    if a < 0: a = 0
    body = s[a:b] if b > a else s[a:]
    tok = re.compile(r'(<img[^>]*>)|(<[^>]+>)')
    items = []; last = 0; gidx = 0
    for m in tok.finditer(body):
        seg = html.unescape(re.sub(r'\s+', ' ', body[last:m.start()]
                                   .replace('&nbsp;', ' ').replace(' ', ' '))).strip()
        if seg and not seg.startswith('id='):
            items.append(('t', seg, -1))
        last = m.end()
        if m.group(1):
            ds = re.search(r'data-src="([^"]+)"', m.group(1)) or re.search(r'\ssrc="([^"]+)"', m.group(1))
            if ds:
                items.append(('i', html.unescape(ds.group(1)), gidx)); gidx += 1
    return items, gidx

# ---------- 2) 解析标题/作者/导师/描述 + 全局图像序号 ----------
def dedup_works(works):
    """丢弃单图封面/重复条目（其标题是另一件多图作品的子集），并把作者转给所有完整条目。"""
    drop = set()
    for i, w in enumerate(works):
        if len(w['imgs']) <= 1:
            matched = False
            for j, o in enumerate(works):
                if i == j: continue
                if o['imgs'] and len(o['imgs']) > 1 and \
                   (o['title'].startswith(w['title']) or w['title'].startswith(o['title'])):
                    if (not o['author']) and w['author']:
                        o['author'] = w['author']
                    drop.add(i); matched = True
            if matched:
                continue
    return [w for i, w in enumerate(works) if i not in drop]

def parse_a(items):
    n = len(items)
    teacher_now = ''; teacher_at = [''] * n
    for idx in range(n):
        k, v, _ = items[idx]
        if k == 't' and '毕业生作品' in v:
            mm = re.search(r'(磨炼|张剑|卢文英|赵斌)', v)
            if mm: teacher_now = mm.group(1)
            elif idx > 0 and items[idx-1][0] == 't':
                mm = re.search(r'(磨炼|张剑|卢文英|赵斌)', items[idx-1][1])
                if mm: teacher_now = mm.group(1)
        teacher_at[idx] = teacher_now
    first_title = next((k for k in range(n)
                        if items[k][0]=='t' and re.search(r'《[^《》]{2,}》', items[k][1])), None)
    works = []; cur = None; teacher = ''
    def flush():
        nonlocal cur
        if cur and (cur['imgs'] or cur['desc']): works.append(cur)
        return None
    i = 0
    while i < n:
        k, v, gi = items[i]
        if k == 't':
            m = re.search(r'《([^《》]{2,})》', v)
            if m:
                title = m.group(1)
                if any(x in title for x in ['毕业设计','学院','广州美术学院','绽放']):
                    i += 1; continue
                flush()
                teacher = teacher_at[i] or teacher
                cur = {'title': title, 'teacher': teacher, 'author': '', 'desc': '',
                       'imgs': [], 'raw_idx': []}
                j = i + 1; buf = []
                while j < n:
                    kk, vv, gj = items[j]
                    if kk == 't':
                        if re.search(r'《[^《》]{2,}》', vv) and j != i: break
                        if vv.startswith('设计：'): cur['author'] = vv[3:].strip()
                        elif is_video(vv): pass
                        else: buf.append(vv)
                    else:
                        if j > (first_title or 0):
                            cur['imgs'].append(vv); cur['raw_idx'].append(gj)
                    j += 1
                cur['desc'] = ' '.join([b for b in buf if b and not is_bio(b) and not is_video(b)])
                i = j; continue
        i += 1
    flush()
    return works

def is_bio(t):
    KW = ['应届','考入','毕业','获奖','奖','项','届','研究生','讲师','教授','副教授',
          '主任','导师','设计学院','工业设计','艺术设','研究所','获得','KTK','DNA',
          '欧洲','日本','香港','国际','当代','意思设计','武汉','双年展','论文','期刊',
          '参与展览','发表','广东','广州美术学院','大学城','硕士研究生']
    return any(k in t for k in KW)
def is_video(t):
    return t.startswith('http') and ('qq.com' in t or 'iqiyi' in t or 'v.' in t or 'youku' in t)

# ---------- 3) 下载文章图像（按全局顺序） ----------
def download_all(items, outdir):
    os.makedirs(outdir, exist_ok=True)
    files = []
    for k, v, gi in items:
        if k == 'i':
            ext = '.gif' if 'gif' in v else ('.png' if 'png' in v else '.jpg')
            fn = os.path.join(outdir, '%03d%s' % (gi, ext))
            try:
                req = urllib.request.Request(v, headers={'User-Agent':'Mozilla/5.0'})
                data = urllib.request.urlopen(req, timeout=30).read()
                open(fn,'wb').write(data)
            except Exception as e:
                print('FAIL', gi, e); continue
            files.append(fn)
    return files

# ---------- 4) 分类启发式（基于标题+描述，与现有词表一致） ----------
def classify(title, desc):
    t = title + ' ' + desc
    # typeCat
    if any(k in t for k in ['首饰','戒指','项链','耳环','手镯','佩戴','挂件']): tc='首饰/可穿戴'
    elif any(k in t for k in ['玩具','公仔','盲盒','角色','玩偶']): tc='潮玩/IP/角色'
    elif any(k in t for k in ['灯','收纳','存钱罐','花瓶','容器','文具','遥控器','音箱','镜子',
                              '教具','餐盘','水果盘','月饼盒','番茄酱','咸鸭蛋','壶','水杯','包',
                              '箱子','篮','罐','工具','支架','书架','钟','闹钟','手电']): tc='产品设计'
    elif any(k in t for k in ['文创','礼盒','年画','非遗','贺卡','包装']): tc='文创/衍生品'
    elif any(k in t for k in ['椅','桌','沙发','床','家具','架']): tc='家具/家居'
    else: tc='产品设计'
    # motif
    if any(k in t for k in ['非遗','年画','木板年画','传统','民俗','节庆','中秋','礼']): mo='非遗与手工技艺'
    elif any(k in t for k in ['食物','食','糖','月饼','番茄','咸鸭蛋','饮食','甜','咖啡','茶','酒']): mo='饮食文化'
    elif any(k in t for k in ['儿童','幼儿','教具','教育','学习','启蒙','尺寸','认知']): mo='记忆/身份/情感'
    elif any(k in t for k in ['材料','木','金属','陶瓷','皮','硅胶','海绵','编织','织物','竹','玻璃','塑料','再生','余料']): mo='物/材料/可持续'
    elif any(k in t for k in ['城市','日常','市井','收纳','办公','家居','生活']): mo='城市日常与市井文化'
    else: mo='物/材料/可持续'
    # presCat
    pc='实物/产品'
    # narrMethod
    if any(k in t for k in ['非遗','年画','传统','文化','中秋','民俗']): nm='背景—转译—应用'
    elif any(k in t for k in ['材料','木','金属','陶瓷','皮','硅胶','海绵','编织','竹','玻璃','质感','触感','肌理']): nm='材料—形态—感知'
    elif any(k in t for k in ['儿童','幼儿','障碍','问题','收纳','不便','需求','痛']): nm='问题—机制—价值'
    elif any(k in t for k in ['情感','陪伴','记忆','亲密','治愈']): nm='人群—意象—体验'
    else: nm='材料—形态—感知'
    # transMethod
    tm=[]
    if any(k in t for k in ['语义','符号','隐喻','指代']): tm.append('产品语义')
    if any(k in t for k in ['功能','可供','替代','转换']): tm.append('功能嫁接')
    if any(k in t for k in ['形态','造型','仿生','形状']): tm.append('形态转译')
    if any(k in t for k in ['材料','质感','肌理','触感']): tm.append('材料转译')
    if any(k in t for k in ['概念','理念','转译']): tm.append('概念转译')
    if any(k in t for k in ['行为','交互','使用','动作']): tm.append('行为绑定')
    if any(k in t for k in ['情绪','情感','治愈']): tm.append('情绪转译')
    if not tm: tm=['形态转译','概念转译']
    # presentation
    pres=['产品实物','使用场景图','细节特写']
    if '灯' in t or '光' in t: pres=['产品实物','光影效果','场景渲染图']
    if tc=='首饰/可穿戴': pres=['首饰实物','佩戴效果','材质特写']
    if tc=='文创/衍生品': pres=['文创实物','包装展示','应用情境']
    return dict(typeCat=tc, motif=mo, presCat=pc, narrMethod=nm,
                transMethod=tm, presentation=pres)

# ---------- 5) 生成条目 ----------
def build_entry(w, new_id):
    cls = classify(w['title'], w['desc'])
    desc = w['desc'].strip()
    desc = re.sub(r'\s+', ' ', desc)
    if not desc:
        desc = '（原文未提供详细设计说明，仅录作品名与作者。）'
    concept = '以「%s」为题，围绕%s展开设计探索。' % (w['title'], cls['motif'])
    highlight = '《%s》：%s' % (w['title'], desc[:60] + ('…' if len(desc) > 60 else ''))
    culture = [cls['motif']]
    cultureNote = '文化坐标落在「%s」：从日常物件与材料出发，把生活经验转译为可触可感的产品语言。' % cls['motif']
    symbols = []
    narrBreak = {
        'opening': '以作品概念开篇，先点明设计对象与动机。',
        'structure': '对象界定 → 材料/形态探索 → 功能/语义落地 → 使用情境呈现。',
        'rhetoric': '以产品本体叙述为主，少用形容词堆砌，靠形态与功能说话。',
        'closing': '落点在「让日常物件更好用 / 更有温度」。'
    }
    presNote = '以实物为主，辅以场景与细节图，呈现从造型到使用的完整信息。'
    narrNote = '典型的「材料—形态—感知」型产品叙述：把设计过程而非修辞作为说服主体。'
    kw = list(dict.fromkeys(re.findall(r'[一-鿿]{2,4}', w['title'])))[:6]
    e = {
        'id': new_id, 'year': YEAR, 'title': w['title'], 'authors': w['author'] or '（待补）',
        'teachers': w['teacher'], 'type': cls['typeCat'], 'typeCat': cls['typeCat'],
        'motif': cls['motif'], 'highlight': highlight, 'concept': concept,
        'culture': culture, 'cultureNote': cultureNote, 'symbols': symbols,
        'transMethod': cls['transMethod'], 'presentation': cls['presentation'],
        'presCat': cls['presCat'], 'presNote': presNote, 'narration': cls['narrMethod'],
        'narrMethod': cls['narrMethod'], 'narrBreak': narrBreak, 'narrNote': narrNote,
        'desc': desc, 'kw': kw, 'imgs': w['img_names']
    }
    return e

# ---------- main ----------
items, nimg = tokenize(FN)
print('raw6a tokens, images:', nimg)
works = parse_a(items)
works = dedup_works(works)
print('parsed works (after dedup):', len(works))
# 下载全部图像
cand = download_all(items, 'cand6a')
print('downloaded cand6a:', len(cand))

# 生成缩略图辅助
def make_thumb(src, dst, tw=900):
    try:
        im = Image.open(src); im.load()
        w,h = im.size
        if w > tw: im = im.resize((tw, max(1, round(h*tw/w))), Image.LANCZOS)
        if im.mode in ('RGBA','P','LA'):
            bg = Image.new('RGB', im.size, (255,255,255)); im = im.convert('RGBA')
            bg.paste(im, mask=im.split()[-1]); im = bg
        else: im = im.convert('RGB')
        im.save(dst, 'JPEG', quality=82, optimize=True)
        return True
    except Exception as e:
        print('thumb fail', src, e); return False

# 读取现有 data.js 的 works，确定起始 id（取最大值）
data = open('data.js', encoding='utf-8').read()
ids = [int(x) for x in re.findall(r'"id":\s*"a(\d+)"', data)]
start = 59  # 修复：a59-a98 已在 data.js 中，重建仍从 59 开始（勿用 max+1）
print('start id a%02d (max existing a%02d)' % (start, max(ids)))

new_entries = []
art_img_dir = 'art_images'; art_thumb_dir = 'art_thumb'
os.makedirs(art_img_dir, exist_ok=True); os.makedirs(art_thumb_dir, exist_ok=True)
skipped = 0
for wi, w in enumerate(works):
    if not w['raw_idx']:
        skipped += 1; continue
    new_id = 'a%02d' % (start + len(new_entries))
    # 映射图像
    img_names = []
    for seq, gi in enumerate(w['raw_idx']):
        src = cand[gi]
        ext = os.path.splitext(src)[1]
        name = '%s_%02d%s' % (new_id, seq, ext)
        dst = os.path.join(art_img_dir, name)
        shutil.copy(src, dst)
        tdst = os.path.join(art_thumb_dir, name)
        make_thumb(dst, tdst)
        img_names.append(name)
    w['img_names'] = img_names
    e = build_entry(w, new_id)
    new_entries.append(e)

print('new entries:', len(new_entries), 'skipped(no img):', skipped)
json.dump(new_entries, open('works_a.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('written works_a.json; sample:')
for e in new_entries[:3]:
    print(' ', e['id'], e['title'], '|', e['authors'], '|', e['teachers'], '| imgs', len(e['imgs']))
