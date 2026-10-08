# -*- coding: utf-8 -*-
"""2018届生活工作室 23件入库：下载图片→缩略图→完整schema条目"""
import json, os, re, shutil, urllib.request
from PIL import Image

WORKS = json.load(open('works18.json', encoding='utf-8'))
# 标题规范化
FIX = {'天际线': '广州印象', '不倒翁': 'Swag·不倒翁衣帽架',
       '猫咪拘束器': '喵星来客·猫咪拘束器', 'Dancingvoice': 'Dancing Voice·舞动的声音',
       '光的故事': '光的故事·光影故事盒'}
for w in WORKS:
    w['title'] = FIX.get(w['title'], w['title'])
# 导师：0-6 磨炼，7-16 张剑，17-18 卢文英，19-22 赵斌
def teacher(i):
    return '磨炼' if i <= 6 else '张剑' if i <= 16 else '卢文英' if i <= 18 else '赵斌'

START = 128
HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120',
       'Referer': 'https://www.shejijingsai.com/'}

def dl(url, dst):
    from urllib.parse import quote
    req = urllib.request.Request(quote(url, safe=':/?&=%.[]'), headers=HDR)
    data = urllib.request.urlopen(req, timeout=30).read()
    open(dst, 'wb').write(data)
    return data

def thumb(src, dst):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    if w > 900:
        im = im.resize((900, int(h * 900 / w)), Image.LANCZOS)
    im.save(dst, 'JPEG', quality=82)

entries = []
fail = 0
for i, w in enumerate(WORKS):
    wid = 'a%d' % (START + i)
    names = []
    for gi, u in enumerate(w['imgs']):
        ext = '.png' if '.png' in u.lower() else '.gif' if '.gif' in u.lower() else '.jpg'
        name = '%s_%02d%s' % (wid, gi, ext)
        raw, th = 'art_images/' + name, 'art_thumb/' + name
        if not os.path.exists(raw):
            try:
                dl(u, raw)
            except Exception as e:
                print('FAIL', wid, gi, str(e)[:60]); fail += 1; continue
        if not os.path.exists(th):
            try:
                thumb(raw, th)
            except Exception as e:
                print('THUMBFAIL', name, str(e)[:50]); fail += 1; continue
        names.append(name)
    if not names:
        print('!! 无图', wid, w['title']); fail += 1; continue
    entries.append(build_entry(wid, w, names) if False else None)
print('download done, fail =', fail)

# —— 分类（逐件人工定）——
C = {
 '叠棋':          ('产品设计','游戏文化','实物/产品','功能—情境—叙事',['结构转译','功能转译']),
 '小皮灯笼':       ('产品设计','器物文化','实物/产品','材料—形态—感知',['材料转译','形态转译']),
 '合·视':         ('产品设计','生活智慧','实物/产品','功能—情境—叙事',['功能转译','色彩隐喻']),
 '正负':          ('产品设计','几何美学','实物/产品','符号—隐喻—观念',['形态转译','结构转译']),
 '第二空间':       ('家具/空间','空间想象','实物/产品','符号—隐喻—观念',['符号转译','形态转译']),
 '低语系列':       ('产品设计','收纳整理','实物/产品','材料—形态—感知',['形态转译']),
 '宠':            ('产品设计','动物形象','实物/产品','符号—隐喻—观念',['拟物转译','符号转译']),
 '碗形削笔刀':      ('产品设计','学习用具','实物/产品','功能—情境—叙事',['形态转译','功能转译']),
 '勺子烛台':       ('产品设计','光与温度','实物/产品','符号—隐喻—观念',['隐喻转译','形态转译']),
 'App-poker':    ('思辨/观念','数字生活','图像/视觉','行为—观察—反思',['概念转译','批判性设计']),
 '器·趣':         ('产品设计','自然仿生','实物/产品','符号—隐喻—观念',['仿生转译','形态转译']),
 '雾中楼宇':       ('产品设计','城市意象','实物/产品','功能—情境—叙事',['场景转译','功能转译']),
 '境见':          ('产品设计','自然意象','实物/产品','功能—情境—叙事',['行为转译','形态转译']),
 '拼图饼干':       ('产品设计','饮食文化','实物/产品','功能—情境—叙事',['功能转译','游戏化设计']),
 '囍之环':         ('首饰/配饰','婚庆文化','实物/产品','符号—隐喻—观念',['符号转译','文字转译']),
 '钻石之戒':        ('首饰/配饰','婚庆文化','实物/产品','符号—隐喻—观念',['符号转译','形态转译']),
 '煤气灶隔热垫':     ('产品设计','厨房物件','实物/产品','功能—情境—叙事',['形态转译','无意识设计']),
 '光的故事·光影故事盒': ('玩具/教具','民间故事','实物/产品','物—事—情—境',['媒介转译','叙事设计']),
 'Dancing Voice·舞动的声音': ('装置/互动','声音可视化','装置/空间','行为—观察—反思',['感官转译','媒介转译']),
 '变装花瓶':       ('产品设计','花器文化','实物/产品','功能—情境—叙事',['模块化设计','形态转译']),
 '广州印象':       ('产品设计','城市文化','实物/产品','符号—隐喻—观念',['符号转译','形态转译']),
 'Swag·不倒翁衣帽架': ('产品设计','生活趣味','实物/产品','功能—情境—叙事',['隐喻转译','功能转译']),
 '喵星来客·猫咪拘束器': ('产品设计','动物形象','实物/产品','符号—隐喻—观念',['场景转译','叙事设计']),
}

def build(wid, w, names):
    title = w['title']
    tc, motif, pc, nm, tm = C[title]
    desc = w['desc'].strip()
    return {
        'id': wid, 'year': '2018', 'title': title,
        'authors': w['author'], 'teachers': teacher(WORKS.index(w)),
        'type': tc, 'typeCat': tc, 'motif': motif,
        'highlight': '《%s》：%s…' % (title, desc[:52]),
        'concept': '以「%s」为题，围绕%s展开设计探索。' % (title, motif),
        'culture': [motif],
        'cultureNote': '文化坐标落在「%s」：从日常观察出发，把生活经验转译为可触可感的产品语言。' % motif,
        'symbols': [],
        'transMethod': tm,
        'presentation': ['产品实物', '使用场景图', '细节特写'] if pc == '实物/产品' else ['装置现场', '过程记录', '效果呈现'],
        'presCat': pc,
        'presNote': '以作品图像为主，呈现从造型到使用/现场的信息。',
        'narration': nm, 'narrMethod': nm,
        'narrBreak': {
            'opening': '以作品概念开篇，先点明设计对象与动机。',
            'structure': '对象界定 → 形态/结构探索 → 功能/语义落地 → 使用情境呈现。',
            'rhetoric': '以产品本体叙述为主，靠形态与功能说话。',
            'closing': '落点在「让日常物件更好用 / 更有温度」。'},
        'narrNote': '生活工作室典型的「低技术+高情感」叙述：从小微处观察，从感知处入手。',
        'desc': desc,
        'descNote': '描述转录自作品自述（张剑设计公众号原文，经设计竞赛网转载页）。' if w['author'] else '',
        'kw': [t for t in re.split(r'[·\s—-]+', title) if t][:2],
        'imgs': names,
    }

entries = []
fail = 0
for i, w in enumerate(WORKS):
    wid = 'a%d' % (START + i)
    names = []
    for gi, u in enumerate(w['imgs']):
        ext = '.png' if '.png' in u.lower() else '.gif' if '.gif' in u.lower() else '.jpg'
        name = '%s_%02d%s' % (wid, gi, ext)
        raw, th = 'art_images/' + name, 'art_thumb/' + name
        if not os.path.exists(raw):
            try:
                dl(u, raw)
            except Exception as e:
                print('FAIL', wid, gi, str(e)[:60]); fail += 1; continue
        if not os.path.exists(th):
            try:
                thumb(raw, th)
            except Exception as e:
                print('THUMBFAIL', name, str(e)[:50]); fail += 1; continue
        names.append(name)
    if not names:
        print('!! 无图', wid, w['title']); continue
    entries.append(build(wid, w, names))

json.dump(entries, open('works18_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('built', len(entries), 'entries; imgs total', sum(len(e['imgs']) for e in entries), '; fail', fail)
