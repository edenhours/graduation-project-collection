# -*- coding: utf-8 -*-
"""sid 官网 12 作品入库：11 新条目(a117起) + 梦鼎(a33)富化 + 过番补充wx报道"""
import json, os, re, html as H, hashlib, shutil, urllib.request
from PIL import Image

D = json.load(open('sid_data.json', encoding='utf-8'))
BY = {r['col']: r for r in D}

def dl(url, dst):
    if os.path.exists(dst): return True
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Referer':'https://sid.gzarts.edu.cn/'})
        open(dst,'wb').write(urllib.request.urlopen(req, timeout=40).read())
        return True
    except Exception as e:
        print('FAIL', url[:60], e); return False

def md5(p):
    return hashlib.md5(open(p,'rb').read()).hexdigest()

def make_thumb(src, dst, tw=900):
    try:
        im = Image.open(src); im.load()
        w,h = im.size
        if w > tw: im = im.resize((tw, max(1, round(h*tw/w))), Image.LANCZOS)
        if im.mode in ('RGBA','P','LA'):
            bg = Image.new('RGB', im.size, (255,255,255)); im = im.convert('RGBA')
            bg.paste(im, mask=im.split()[-1]); im = bg
        else: im = im.convert('RGB')
        im.save(dst, 'JPEG', quality=88)
        return True
    except Exception as e:
        print('thumb fail', src, e); return False

def grab(urls, work_id):
    """下载图片去重，返回文件名列表"""
    names, seen = [], set()
    for u in urls:
        ext = '.gif' if 'gif' in u.lower() else ('.png' if '.png' in u.lower() else '.jpg')
        tmp = os.path.join('_sidtmp', hashlib.md5(u.encode()).hexdigest() + ext)
        if not os.path.exists(tmp) and not dl(u, tmp): continue
        h = md5(tmp)
        if h in seen: continue
        seen.add(h)
        name = '%s_%02d%s' % (work_id, len(names), ext)
        shutil.copy(tmp, os.path.join('art_images', name))
        make_thumb(os.path.join('art_images', name), os.path.join('art_thumb', name))
        names.append(name)
    return names

def W(work_id, year, r, **kw):
    e = {
        'id': work_id, 'year': year,
        'title': r['title'], 'sub': r['eng'],
        'authors': r['authors'], 'teachers': r['teacher'],
        'imgs': grab(r['imgs'], work_id),
    }
    if r['video_main']: e['video'] = r['video_main']
    if r['video_sub']:
        e['desc'] = kw['desc'] + '（另有过程视频：%s）' % r['video_sub']
    e.update(kw)
    return e

E = []

# a117 过番（2021·麦扬·胡好）+ wx 特奖报道补充
r = BY['2218_57304']
wximgs = re.findall(r'data-src="(https://mmbiz[^"]+)"', open('raw7w.html',encoding='utf-8',errors='ignore').read())
E.append(W('a117','2021', r,
    type='装置与首饰 · 侨批文化',
    typeCat='首饰/可穿戴', motif='跨文化/海上丝路',
    highlight='从潮州金漆木雕神龛——这一「宗族容器」里，拆出一段下南洋的侨批史：把祭祖的木雕转译成可佩戴的海洋叙事，2021 中意青年未来时尚设计大赛特奖作品。',
    concept='以「侨批文化」为主体，以潮州木雕和侨批的紧密关联性为发展线，研究潮汕海洋文化中重要的潮侨文化，挖掘潮汕先侨下南洋谋生的历史文本，以艺术装置衍生首饰，实验性地钩沉「海外香馥」的过番史实。',
    culture=['潮州金漆木雕','侨批文化','潮汕海洋文化与过番史','宗族观念'],
    cultureNote='神龛是宗族观念的物质载体，侨批是跨洋家书的物质遗存。作品把两种「承载记忆的旧物」接到一条叙事线上：木雕技艺留在故乡，侨批寄往海外，首饰成为行走其间的第三种载体。',
    symbols=[
        {'src':'金漆木雕神龛','way':'装置化重构','out':'宗族观念的容器'},
        {'src':'侨批（跨洋家书）','way':'造型挪用','out':'可佩戴的海洋叙事'},
        {'src':'金漆木雕技艺','way':'材料/工艺转译','out':'首饰表面处理'},
        {'src':'下南洋航线','way':'概念转译','out':'叙事线索'}
    ],
    transMethod=['造型挪用','材料转译','概念转译'],
    presentation=['艺术装置','首饰系列','展陈'],
    presCat='空间/装置/展陈',
    presNote='装置与首饰并存：装置承担叙事规模感，首饰承担「把历史带在身上」的亲密性。',
    narration='技艺 — 载体 — 文本 — 佩戴',
    narrMethod='田野—叙事—在地',
    narrBreak={
        'opening':'「潮州金漆木雕，无论是技艺还是作品，都是潮汕文化的典型代表」——从技艺与作品的关系开场定锚。',
        'structure':'技艺 → 载体（神龛/宗族观念）→ 历史文本（侨批/下南洋）→ 设计产出（装置与首饰）。',
        'rhetoric':'以「载体」层层递进：从物（神龛）到信（侨批）再到人（先侨），最后回到可佩戴的物。',
        'closing':'落在「实验性地钩沉过番史实」——设计作为历史书写的方式。'
    },
    narrNote='文化转译型自述的典范：技艺、载体、文本三层材料都有实证依托，转译不悬空。',
    desc=r['desc'] + '【获奖】中意青年未来时尚设计大赛时尚设计赛道特奖（清华大学中意设计创新基地专题报道）。作者麦扬，本科毕业于广州美术学院产品设计专业，现于北京服装学院攻读珠宝首饰设计专业艺术学硕士。',
    kw=['过番','潮州金漆木雕','侨批','潮汕','神龛','首饰','装置','下南洋'],
    imgs_extra_wx = True,
))
# 过番：追加 wx 报道图片
a117 = E[-1]
wx_names = grab(wximgs, 'a117x_tmp')  # 先下到临时命名
seenh = set()
for n in a117['imgs']: seenh.add(md5(os.path.join('art_images', n)))
extra = []
for i, n in enumerate(wx_names):
    src = os.path.join('art_images', n)
    h = md5(src)
    if h in seenh: os.remove(src); t=os.path.join('art_thumb',n); os.path.exists(t) and os.remove(t); continue
    seenh.add(h)
    name = 'a117_%02d%s' % (len(a117['imgs'])+len(extra), os.path.splitext(n)[1])
    os.rename(src, os.path.join('art_images', name))
    t = os.path.join('art_thumb', name)
    os.path.exists(t) and os.remove(t)
    make_thumb(src, t)
    extra.append(name)
a117['imgs'] += extra

# a118 余音袅袅（2024·许泳诗·庄嘉菁、胡好）
r = BY['2398_61824']
E.append(W('a118','2024', r,
    type='声音装置 · 铝材余料再生',
    typeCat='思辨/装置', motif='物/材料/可持续',
    highlight='让工厂里的铝材余料「开口说话」：按乐器发声原理组合铝管，废料变成一件可以被敲响的公共装置。',
    concept='基于铝材余料的声音装置设计，基于声音的产生和传播原理、不同乐器的发声原理，考虑铝管的组合方式与声音效果，为观众提供一种方便的参与方式。',
    culture=['铝材余料','乐器发声原理','声音艺术','可持续设计'],
    cultureNote='余料设计通常止于「变小件」，这件作品反其道而行：把余料放大成占据空间的乐器，让「废」的价值被听见而不只是被看见。',
    symbols=[
        {'src':'铝材余料','way':'材料转译','out':'发声单元'},
        {'src':'乐器发声原理','way':'功能嫁接','out':'铝管音高与音色'},
        {'src':'敲击行为','way':'行为绑定','out':'公众参与'}
    ],
    transMethod=['材料转译','媒介转换','功能嫁接'],
    presentation=['声音装置','公共参与','展陈'],
    presCat='空间/装置/展陈',
    presNote='核心是可被敲响的空间装置，图像仅能记录形态，声音部分需现场或视频体验。',
    narration='余料 — 原理 — 装置 — 参与',
    narrMethod='余料—再生',
    narrBreak={
        'opening':'直接亮明材料身份：「基于铝材余料的声音装置设计」。',
        'structure':'材料（铝余料）→ 原理（声学/乐器）→ 形式（铝管组合）→ 价值（观众参与）。',
        'rhetoric':'「主要基于…考虑到…为观众提供…」三段式，工程感强。',
        'closing':'落在「方便的参与方式」——装置的公共性。'
    },
    narrNote='典型的「材料—原理—参与」链条，余料再生类叙事的干净样本。',
    desc=r['desc'],
    kw=['余音袅袅','铝材余料','声音装置','可持续','乐器','公共参与'],
))

# a119 晒·活动（2024·刘邓·庄嘉菁、胡好）
r = BY['2398_61694']
E.append(W('a119','2024', r,
    type='社会创新 · 活动体验设计',
    typeCat='社会创新/服务', motif='城市日常与市井文化',
    highlight='把记忆里的「大晒场」搬回社区：用一场可参与的晒物活动，让被阳台洗衣机取代的公共生活重新发生。',
    concept='基于社会创新视角下的活动体验设计，通过线下实地基础搭建与观众情感沟通的桥梁，根据前期分析将记忆中的「大晒场」场景转化为当代社区活动。',
    culture=['大晒场','社区公共生活','市井记忆','社会创新'],
    cultureNote='「晒」在南方市井里既是动作也是社交：晒被子、晒腊味、晒家常。作品把这一消失的公共场景转译为活动设计，唤起的是邻里关系而非怀旧情绪本身。',
    symbols=[
        {'src':'大晒场场景','way':'场景重构','out':'活动框架'},
        {'src':'晾晒行为','way':'行为绑定','out':'参与仪式'},
        {'src':'邻里记忆','way':'情绪转译','out':'社区连接'}
    ],
    transMethod=['行为绑定','情绪转译','概念转译'],
    presentation=['线下活动','现场布置','过程记录'],
    presCat='空间/装置/展陈',
    presNote='产出是活动本身，图像多为现场与流程记录。',
    narration='记忆 — 场景 — 活动 — 连接',
    narrMethod='田野—叙事—在地',
    narrBreak={
        'opening':'先立视角：「基于社会创新视角下的活动体验设计」。',
        'structure':'视角 → 方法（线下实地/前期分析）→ 原型（大晒场记忆）→ 产出（活动）。',
        'rhetoric':'以「桥梁」隐喻沟通目的，以记忆场景作设计原型。',
        'closing':'落在情感沟通——社会创新的评价标准是人跟人的连接。'
    },
    narrNote='社会创新类自述：强调前期分析与在地记忆，产出是「事件」而非「物」。',
    desc=r['desc'],
    kw=['晒','大晒场','社区','社会创新','活动设计','市井'],
))

# a120 莲常·所愿（2024·刘莹、孙陈薇·刘毅、梁嘉、王时音）
r = BY['2398_61814']
E.append(W('a120','2024', r,
    type='文创产品 · 民俗祈福',
    typeCat='文创/衍生品', motif='信仰/神话/民间叙事',
    highlight='年轻人烧香拜佛的热梗 × 莲塘村榕树祈福的老传统：用「古与新的碰撞」把一次许愿做成可带走的产品。',
    concept='将当代年轻人烧香拜佛现象与莲塘村的榕树祈福结合，融入当下热梗产出与寺庙、佛祖等相关联的视觉及产品，运用古与新的碰撞给观众带来视觉冲击。',
    culture=['榕树祈福','寺庙民俗','青年烧香热梗','在地村落'],
    cultureNote='拜佛热梗的流行说明年轻人需要「低门槛的祈愿出口」。作品把它接到村口榕树的真实民俗上，让网络情绪落回具体的地方。',
    symbols=[
        {'src':'榕树祈福','way':'民俗挪用','out':'许愿产品'},
        {'src':'寺庙视觉符号','way':'造型挪用','out':'视觉体系'},
        {'src':'网络热梗','way':'概念转译','out':'年轻化表达'}
    ],
    transMethod=['造型挪用','概念转译','情绪转译'],
    presentation=['系列产品','视觉系统','展陈'],
    presCat='实物/产品',
    presNote='视觉与产品并行的文创组合。',
    narration='热梗 — 民俗 — 产品 — 冲击',
    narrMethod='背景—转译—应用',
    narrBreak={
        'opening':'并列两个时代背景：年轻人烧香现象与村落榕树祈福。',
        'structure':'现象（烧香热梗）× 在地民俗（榕树）→ 视觉与产品 → 观众反应。',
        'rhetoric':'「古与新的碰撞」是核心修辞，冲突即卖点。',
        'closing':'落在视觉冲击带来的传播力。'
    },
    narrNote='借势型文创的写法：把流行现象当「新民俗」处理，重心在视觉转译。',
    desc=r['desc'],
    kw=['莲常所愿','祈福','榕树','寺庙','热梗','文创'],
))

# a121 印记（2024·李汶蔚、何钰清·安娃、王柳庄）
r = BY['2398_61764']
E.append(W('a121','2024', r,
    type='数字文创 · 印章与手账',
    typeCat='文创/衍生品', motif='记忆/身份/情感',
    highlight='把「集章打卡」的时间轴反向做进文物：一款印章主题的时间规划 APP + 实体手账本，让逛博物馆变成攒印记。',
    concept='将古代文物与现代生活相融合，结合年轻人喜欢的集章形式，设计一款以印章为主题的时间规划 APP 和实体手账本，为用户创造独特而有趣的体验。',
    culture=['集章文化','文物数字化','手账','时间规划'],
    cultureNote='集章是年轻人自发的「文物打卡仪式」。作品没有再造一个导览 APP，而是把文物的「印」转成时间管理的「记」——文物成为生活的刻度。',
    symbols=[
        {'src':'文物纹样','way':'造型挪用','out':'印章图案'},
        {'src':'集章行为','way':'行为绑定','out':'打卡机制'},
        {'src':'手账本','way':'媒介转换','out':'数字+实体闭环'}
    ],
    transMethod=['造型挪用','行为绑定','媒介转换'],
    presentation=['APP 界面','实体手账','展板排版'],
    presCat='影像/交互/动态',
    presNote='数字产品与实体产品并行，图像展示界面与手账实物。',
    narration='文物 — 仪式 — 产品 — 日常',
    narrMethod='品牌—场景—消费',
    narrBreak={
        'opening':'给出融合公式：古代文物 × 现代生活。',
        'structure':'融合 → 机制（集章）→ 产品（APP+手账）→ 体验目标。',
        'rhetoric':'「独特而有趣的体验」收尾，产品型自述。',
        'closing':'行为机制（集章）是产品成立的关键。'
    },
    narrNote='机制驱动型文创：先有行为洞察（集章），再有产品形态。',
    desc=r['desc'],
    kw=['印记','文物','集章','印章','手账','APP','时间规划'],
))

# a122 抚（2023·沈安琪·梁嘉、王时音、秦臻）
r = BY['2098_50434']
E.append(W('a122','2023', r,
    type='产品 · 女性妊娠叙事',
    typeCat='产品设计', motif='女性与身体叙事',
    highlight='「妊娠纹·皂」：轻抚的动作既是使用方式也是共情方式——把妊娠这件私密的身体经验做成可被温柔对待的日常物。',
    concept='将女性视角下的妊娠感知体验经历重塑为以使用者为导向的产品，通过轻抚「妊娠纹·皂」时的行为感知，创造身体和情感上的连接，从而引发对于女性、妊娠的重新审视与反思。',
    culture=['妊娠经验','身体叙事','皂与轻抚','女性视角'],
    cultureNote='妊娠纹常被表述为「需要修复的瑕疵」。作品反转视角：用「抚」这个最温柔的动作去接触纹路，让身体痕迹从被遮蔽变成被珍视。',
    symbols=[
        {'src':'妊娠纹','way':'造型挪用','out':'皂体纹路'},
        {'src':'轻抚动作','way':'行为转译','out':'使用方式'},
        {'src':'身体连接','way':'情绪转译','out':'情感共鸣'}
    ],
    transMethod=['行为转译','情绪转译','概念转译'],
    presentation=['产品实物','使用场景','展板排版'],
    presCat='实物/产品',
    presNote='核心是产品与使用行为，图像以实物与场景为主。',
    narration='经验 — 物 — 行为 — 反思',
    narrMethod='人群—意象—体验',
    narrBreak={
        'opening':'限定视角：「女性视角下的妊娠感知体验」。',
        'structure':'经验重塑 → 产品（妊娠纹·皂）→ 行为（轻抚）→ 连接 → 反思。',
        'rhetoric':'「轻抚」一词贯穿，动作即理念。',
        'closing':'落在社会性议题：对女性与妊娠的重新审视。'
    },
    narrNote='情感设计型自述：以单一动作承载全部理念，克制而准确。',
    desc=r['desc'],
    kw=['抚','妊娠纹','皂','女性','身体','情感化设计'],
))

# a123 属性（2023·缪景怡、邹冱·张剑）
r = BY['2098_50244']
E.append(W('a123','2023', r,
    type='产品系列 · 材料感知',
    typeCat='产品设计', motif='物/材料/可持续',
    highlight='不研究材料「能做什么」，而研究材料「让人感到什么」：把物理属性背后的心理属性做成一件件小设计。',
    concept='本系列作品通过研究事物的属性并挖掘属性背后的感知来设计。材料的属性包括物理属性与心理属性，相比于对材料物理性能的研究和应用，「属性」系列作品更偏向于以感知为出发点的设计。',
    culture=['材料属性','心理感知','日常产品','张剑组方法论'],
    cultureNote='张剑组一贯的「感知设计」路径：从人对物的直觉感受出发，而非功能堆叠。属性是物与人之间的接口。',
    symbols=[
        {'src':'材料物理属性','way':'材料转译','out':'形态语言'},
        {'src':'心理属性','way':'概念转译','out':'感知体验'},
        {'src':'日常产品','way':'功能嫁接','out':'耳目一新的使用'}
    ],
    transMethod=['材料转译','概念转译'],
    presentation=['产品系列','展板排版'],
    presCat='实物/产品',
    presNote='系列化小产品，图集呈现各件形态与材质对比。',
    narration='属性 — 感知 — 形态 — 产品',
    narrMethod='材料—形态—感知',
    narrBreak={
        'opening':'先做概念界定：物理属性 vs 心理属性。',
        'structure':'界定 → 立场（偏心理感知）→ 系列产出。',
        'rhetoric':'「相比于…更偏向于…」的让步句式，立场鲜明。',
        'closing':'感知优先的设计宣言。'
    },
    narrNote='方法论型自述：先立概念再摊开系列，是研究型毕设的标准写法。',
    desc=r['desc'],
    kw=['属性','材料','感知','心理属性','系列','张剑'],
))

# a124 非遗幼儿益智玩具（2023·李隽杰·王柳庄、李健）
r = BY['2098_50514']
E.append(W('a124','2023', r,
    type='益智玩具 · 非遗启蒙',
    typeCat='游戏/桌游', motif='非遗与手工技艺',
    highlight='用「玩具化」的思路给幼儿做非遗启蒙：把非遗里适合孩子的部分转译成动手的益智玩具。',
    concept='以玩具化的思路对非物质文化遗产进行幼儿启蒙设计的探索，选取合适的非遗内容转译为幼儿益智玩具，让传统文化以可玩的方式进入童年。',
    culture=['非物质文化遗产','幼儿教育','益智玩具','文化传承'],
    cultureNote='非遗传承的难点在「孩子接不住」。作品不做知识灌输，而是筛选非遗中可动手、可游戏的部分，让传承从「看」变成「玩」。',
    symbols=[
        {'src':'非遗元素','way':'造型挪用','out':'玩具形态'},
        {'src':'幼儿行为','way':'功能嫁接','out':'益智玩法'},
        {'src':'文化传承','way':'概念转译','out':'启蒙价值'}
    ],
    transMethod=['造型挪用','功能嫁接','概念转译'],
    presentation=['玩具实物','使用场景','展板排版'],
    presCat='实物/产品',
    presNote='玩具系列实物呈现，附使用场景。',
    narration='非遗 — 转译 — 玩具 — 启蒙',
    narrMethod='背景—转译—应用',
    narrBreak={
        'opening':'大背景切入：非遗传承与设计创新。',
        'structure':'背景（传承共识）→ 思路（玩具化）→ 转译（选内容做玩具）→ 价值（启蒙）。',
        'rhetoric':'「以玩具化的思路」一句话立方法论。',
        'closing':'文化传承的教育价值。'
    },
    narrNote='教育型毕设的自述结构：共识背景 + 明确方法论 + 应用落点。',
    desc=r['desc'],
    kw=['非遗','益智玩具','幼儿','文化传承','启蒙'],
))

# a125 显隐（2023·邹冱、缪景怡·张剑）
r = BY['2098_50204']
E.append(W('a125','2023', r,
    type='产品系列 · 隐性感知显性化',
    typeCat='产品设计', motif='城市日常与市井文化',
    highlight='遥控器总丢在沙发缝、音响声像自然风、模糊的东西别样美——把生活里说不清的隐性感知，做成看得见的小设计。',
    concept='在产品中隐藏着不少细微的感知：遥控器与沙发的联系、音乐声与自然风的联想、模糊事物的别样美感。此系列通过简单轻松的设计，将生活中常见产品的隐性特质显性化，令人耳目一新。',
    culture=['隐性感知','日常之物','联想与通感','张剑组方法论'],
    cultureNote='显隐系列观察的是「物与人之间未被言明的联系」：小沙发遥控器、一片音响、光映磨砂袋。设计不发明新物，只把已有的默契摆上台面。',
    symbols=[
        {'src':'物与人的默契','way':'概念转译','out':'显性形态'},
        {'src':'自然联想','way':'情绪转译','out':'产品气质'},
        {'src':'模糊美感','way':'材料转译','out':'磨砂/光影'}
    ],
    transMethod=['概念转译','情绪转译','材料转译'],
    presentation=['产品系列','展板排版'],
    presCat='实物/产品',
    presNote='系列包含小沙发遥控器、一片音响、光映、多面孔时钟、圆鼓鼓胶水、俯视星空等多件。',
    narration='观察 — 显影 — 造型 — 产品',
    narrMethod='材料—形态—感知',
    narrBreak={
        'opening':'连用三个生活观察例证，节奏轻快。',
        'structure':'例证（遥控器/音响/模糊）→ 意图（隐性显性化）→ 手段（简单轻松的设计）→ 效果（耳目一新）。',
        'rhetoric':'排比举例 + 「显性化」的核心动词。',
        'closing':'「令人耳目一新」——感知设计的落点。'
    },
    narrNote='张剑组感知设计谱系的代表文本：观察先于设计，转译不露痕迹。',
    desc=r['desc'],
    kw=['显隐','遥控器','音响','感知','隐性','张剑','日常产品'],
))

# a126 叙事（2023·李晨潇·张剑）
r = BY['2098_50274']
E.append(W('a126','2023', r,
    type='产品叙事 · 情感体验',
    typeCat='产品设计', motif='信仰/神话/民间叙事',
    highlight='河灯与铃铛交融：把「祈愿」这件心理活动装进产品——产品叙事以情感体验为核心，先有故事后有物。',
    concept='产品叙事以情感体验为核心，注重人的主观体验和情感反应。相比于产品功能设计，更强调设计作品所传递的情感、故事和思想。河灯与铃铛交融，是祈愿者对神秘力量的寄托。',
    culture=['河灯','祈愿','产品叙事','情感体验'],
    cultureNote='河灯是给水的信，铃铛是给风的话。两种「发声的祈愿物」被放进同一件产品，叙事先于功能——这是产品叙事方法论的完整示范。',
    symbols=[
        {'src':'河灯','way':'造型挪用','out':'产品形态'},
        {'src':'铃铛','way':'媒介转换','out':'声音叙事'},
        {'src':'祈愿心理','way':'情绪转译','out':'情感寄托'}
    ],
    transMethod=['造型挪用','媒介转换','情绪转译'],
    presentation=['产品实物','叙事场景','展板排版'],
    presCat='实物/产品',
    presNote='产品与叙事场景并重。',
    narration='意象 — 故事 — 形态 — 情感',
    narrMethod='人群—意象—体验',
    narrBreak={
        'opening':'先给方法论定义：产品叙事 = 情感体验优先。',
        'structure':'定义 → 对比（vs 功能设计）→ 意象（河灯×铃铛）→ 情感落点。',
        'rhetoric':'「河灯与铃铛交融」意象化开场，先造境后说理。',
        'closing':'落在祈愿者与神秘力量的关系。'
    },
    narrNote='方法论 + 意象的双重自述：先声明「我是叙事设计」，再让意象自己说话。',
    desc=r['desc'],
    kw=['叙事','河灯','铃铛','祈愿','产品叙事','情感体验'],
))

# a127 猫用品艺术衍生设计 FitFactory（2023·王忠昊、彭颖慧、李宏宇·梁嘉、王时音、秦臻）
r = BY['2098_50354']
E.append(W('a127','2023', r,
    type='艺术衍生品牌 · 猫用品',
    typeCat='文创/衍生品', motif='当代媒介与流行文化',
    highlight='艺术史 × 猫：从 95 位艺术家与他们小猫的日常故事里，给养猫人做一套「像艺术家那样生活」的猫用品品牌。',
    concept='FitFactory 是一个猫用品艺术衍生品品牌，设计灵感来源于艺术史中 95 位知名艺术家与他们小猫的日常故事。品牌致力于让艺术融入养猫日常，使用户在养猫过程中体验艺术家的生活方式，透过小猫的视角发现艺术家内心柔软细腻的部分。',
    culture=['艺术史','猫与艺术家','IP 品牌','养猫日常'],
    cultureNote='「艺术家的猫」是天然的内容杠杆：既有艺术史的厚度，又有猫系流量的亲和。品牌把艺术故事装进猫抓板、食盆这些高频日常物里。',
    symbols=[
        {'src':'艺术家与猫的故事','way':'角色化','out':'产品系列'},
        {'src':'艺术史视觉','way':'造型挪用','out':'品牌视觉'},
        {'src':'养猫场景','way':'品牌叙事','out':'消费连接'}
    ],
    transMethod=['角色化','品牌叙事','造型挪用'],
    presentation=['产品系列','品牌视觉','展陈'],
    presCat='实物/产品',
    presNote='品牌化输出：产品+视觉+故事三线并行。',
    narration='故事 — 角色 — 产品 — 品牌',
    narrMethod='品牌—场景—消费',
    narrBreak={
        'opening':'直接给出品牌定义与灵感来源。',
        'structure':'品牌定位 → 内容资产（95 个艺术家与猫的故事）→ 体验目标（艺术的生活方式）→ 情感钩子（柔软细腻的部分）。',
        'rhetoric':'「透过小猫的视角」视角转换是点睛之笔。',
        'closing':'情绪价值收尾。'
    },
    narrNote='品牌型毕设的自述模板：定位、内容资产、体验、情绪四件套。',
    desc=r['desc'],
    kw=['FitFactory','猫用品','艺术衍生','品牌','艺术史','IP'],
))

# ---- a33 梦鼎富化：追加官方正文与图片 ----
md = BY['2398_61704']
existing_imgs = json.load(open('_a33_imgs.json')) if os.path.exists('_a33_imgs.json') else None

print('built entries:', len(E))
for e in E: print(' ', e['id'], e['title'], '| imgs', len(e['imgs']), '| video', bool(e.get('video')))
json.dump(E, open('works_sid.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(md, open('_a33_sid.json','w',encoding='utf-8'), ensure_ascii=False)
print('written works_sid.json + _a33_sid.json')
