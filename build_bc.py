# -*- coding: utf-8 -*-
"""构建 raw6b(设计感知研究所2025) + raw6c(黄治权2026) 的筛选后作品。
   图像来源: 已下载的 cand6b/(102张) 与 cand6c/(81张)，按下标映射（不含肖像/展览现场/糖系列）。
   分析字段沿用 build_a 的启发式（无法读图，标注待深化）。
"""
import os, re, json, shutil
from PIL import Image

# 复用 build_a 的分类与条目构造（独立副本，避免触发其 __main__）
import importlib.util
spec = importlib.util.spec_from_file_location("build_a_mod", "build_a.py")
# 不执行 build_a 的 main：用 spec 仅读取函数不行（会跑 main）。改为就地复刻 classify。

def classify(title, desc):
    t = title + ' ' + desc
    if any(k in t for k in ['首饰','戒指','项链','耳环','手镯','佩戴','挂件']): tc='首饰/可穿戴'
    elif any(k in t for k in ['玩具','公仔','盲盒','角色','玩偶']): tc='潮玩/IP/角色'
    elif any(k in t for k in ['灯','收纳','存钱罐','花瓶','容器','文具','遥控器','音箱','镜子',
                              '教具','餐盘','水果盘','月饼盒','番茄酱','咸鸭蛋','壶','水杯','包',
                              '箱子','篮','罐','工具','支架','书架','钟','闹钟','手电']): tc='产品设计'
    elif any(k in t for k in ['文创','礼盒','年画','非遗','贺卡','包装']): tc='文创/衍生品'
    elif any(k in t for k in ['椅','桌','沙发','床','家具','架']): tc='家具/家居'
    else: tc='产品设计'
    if any(k in t for k in ['非遗','年画','木板年画','传统','民俗','节庆','中秋','礼']): mo='非遗与手工技艺'
    elif any(k in t for k in ['食物','食','糖','月饼','番茄','咸鸭蛋','饮食','甜','咖啡','茶','酒']): mo='饮食文化'
    elif any(k in t for k in ['儿童','幼儿','教具','教育','学习','启蒙','尺寸','认知']): mo='记忆/身份/情感'
    elif any(k in t for k in ['材料','木','金属','陶瓷','皮','硅胶','海绵','编织','织物','竹','玻璃','塑料','再生','余料']): mo='物/材料/可持续'
    elif any(k in t for k in ['城市','日常','市井','收纳','办公','家居','生活']): mo='城市日常与市井文化'
    else: mo='物/材料/可持续'
    pc='实物/产品'
    if any(k in t for k in ['非遗','年画','传统','文化','中秋','民俗']): nm='背景—转译—应用'
    elif any(k in t for k in ['材料','木','金属','陶瓷','皮','硅胶','海绵','编织','竹','玻璃','质感','触感','肌理']): nm='材料—形态—感知'
    elif any(k in t for k in ['儿童','幼儿','障碍','问题','收纳','不便','需求','痛']): nm='问题—机制—价值'
    elif any(k in t for k in ['情感','陪伴','记忆','亲密','治愈']): nm='人群—意象—体验'
    else: nm='材料—形态—感知'
    tm=[]
    if any(k in t for k in ['语义','符号','隐喻','指代']): tm.append('产品语义')
    if any(k in t for k in ['功能','可供','替代','转换']): tm.append('功能嫁接')
    if any(k in t for k in ['形态','造型','仿生','形状']): tm.append('形态转译')
    if any(k in t for k in ['材料','质感','肌理','触感']): tm.append('材料转译')
    if any(k in t for k in ['概念','理念','转译']): tm.append('概念转译')
    if any(k in t for k in ['行为','交互','使用','动作']): tm.append('行为绑定')
    if any(k in t for k in ['情绪','情感','治愈']): tm.append('情绪转译')
    if not tm: tm=['形态转译','概念转译']
    pres=['产品实物','使用场景图','细节特写']
    if '灯' in t or '光' in t: pres=['产品实物','光影效果','场景渲染图']
    if tc=='首饰/可穿戴': pres=['首饰实物','佩戴效果','材质特写']
    if tc=='文创/衍生品': pres=['文创实物','包装展示','应用情境']
    return dict(typeCat=tc, motif=mo, presCat=pc, narrMethod=nm, transMethod=tm, presentation=pres)

def build_entry(title, author, teacher, year, desc, img_names, new_id):
    cls = classify(title, desc)
    desc = re.sub(r'\s+', ' ', desc.strip())
    if not desc: desc='（原文未提供详细设计说明。）'
    e = {
        'id': new_id, 'year': year, 'title': title, 'authors': author or '（待补）',
        'teachers': teacher, 'type': cls['typeCat'], 'typeCat': cls['typeCat'],
        'motif': cls['motif'],
        'highlight': '《%s》：%s' % (title, desc[:60] + ('…' if len(desc) > 60 else '')),
        'concept': '以「%s」为题，围绕%s展开设计探索。' % (title, cls['motif']),
        'culture': [cls['motif']],
        'cultureNote': '文化坐标落在「%s」：从日常物件与材料出发，把生活经验转译为可触可感的产品语言。' % cls['motif'],
        'symbols': [],
        'transMethod': cls['transMethod'], 'presentation': cls['presentation'],
        'presCat': cls['presCat'],
        'presNote': '以实物为主，辅以场景与细节图，呈现从造型到使用的完整信息。',
        'narration': cls['narrMethod'], 'narrMethod': cls['narrMethod'],
        'narrBreak': {'opening':'以作品概念开篇，先点明设计对象与动机。',
                      'structure':'对象界定 → 材料/形态探索 → 功能/语义落地 → 使用情境呈现。',
                      'rhetoric':'以产品本体叙述为主，靠形态与功能说话。',
                      'closing':'落点在「让日常物件更好用 / 更有温度」。'},
        'narrNote': '典型的「材料—形态—感知」型产品叙述：把设计过程而非修辞作为说服主体。',
        'desc': desc, 'kw': list(dict.fromkeys(re.findall(r'[一-鿿]{2,4}', title)))[:6],
        'imgs': img_names
    }
    return e

def make_thumb(src, dst, tw=900):
    try:
        im = Image.open(src); im.load(); w,h = im.size
        if w > tw: im = im.resize((tw, max(1, round(h*tw/w))), Image.LANCZOS)
        if im.mode in ('RGBA','P','LA'):
            bg = Image.new('RGB', im.size, (255,255,255)); im = im.convert('RGBA')
            bg.paste(im, mask=im.split()[-1]); im = bg
        else: im = im.convert('RGB')
        im.save(dst, 'JPEG', quality=82, optimize=True); return True
    except Exception as e:
        print('thumb fail', src, e); return False

# ---- 文章 b：设计感知研究所 2025（张剑）。gi = 文章图像序号-1（cand6b 下标） ----
# 注意：陈澄(海绵显形&香氛) 与 张铭轩(印象的延展) 已在库(a20/a21)，属重复，已剔除。
# 仅保留库中没有的新作者：卢文羽、苏咏锶余若岩。
# (title, author, teacher, year, desc, [gi_start, gi_end 含])
B = [
 ("海绵花香器（砚）","卢文羽","张剑","2025",
  "海绵具有将液体气味蕴集起来的特性。使用时将方形海绵收束底部，顶面划痕因挤压形变形成如花瓣般的缝隙，整体呈现一朵盛开的花朵。",[56,64]),
 ("海绵墨砚","卢文羽","张剑","2025",
  "墨水倒在黑色海绵砚台上，随时间流逝被海绵吸收藏匿；使用时用毛笔轻压，墨迹便自然显现。",[65,68]),
 ("海绵存钱罐","卢文羽","张剑","2025",
  "黄色海绵多孔洞、常被用作隔音材料。海绵存钱罐内藏敲击装置，每投一枚硬币都会传出意料之外的响声，制造视觉与听觉的感官反差。",[69,72]),
 ("海绵水桶","卢文羽","张剑","2025",
  "这是一个海绵水桶。在菜地前装满水，拎起时水珠从底部不断滴落，掠过青菜，提桶缓步前行，一路浇灌菜地。",[73,75]),
 ("镭射片水面装置","苏咏锶 余若岩","张剑","2025",
  "通过机械控制使镭射片在空间中有序起伏，水面之上光彩夺目，水下倒影将美丽加倍；风的作用下镭射片如小生物般灵活起舞。",[93,101]),
]

# ---- 文章 c：黄治权 2026（张剑）。排除糖系列；gi = 文章图像序号-1 ----
C = [
 ("水管盆景A","黄治权","张剑","2026",
  "利用可随意弯折的水管替代盆景枝干，让自然生长的形态转变为可被人为塑造的路径，使用者随手插入拾得的植物即可造型。",[24,28]),
 ("水管盆景B","黄治权","张剑","2026",
  "水管盆景的另一种形态，延续以水管重构枝干、将生长交还使用者的设计思路。",[29,34]),
 ("PVC透明花瓶","黄治权","张剑","2026",
  "将印有喜爱鲜花图案的透明PVC片插入扁平花瓶内，无需水源、无需修剪，轻轻一插即可根据心情轻松更换。",[35,36]),
 ("油画棒盒","黄治权","张剑","2026",
  "用手指按压油棒末端，油棒便像跷跷板一样被抬升到一定高度，让取用油棒变得轻松有趣。",[37,42]),
 ("亲肤硅胶皮尺","黄治权","张剑","2026",
  "一款由亲肤硅胶制成的皮尺，与被测量者皮肤轻轻接触时带来柔软舒适的体验，减少测量身体时的尴尬。",[43,46]),
 ("疯马皮软尺","黄治权","张剑","2026",
  "利用疯马皮的留痕特性制作软尺，指尖划过表面会留下清晰痕迹；随时间推移皮面愈发温润光亮，让每次测量都充满情感温度。",[47,50]),
 ("颜料包装（花状尖头）","黄治权","张剑","2026",
  "颜料管上仅标注颜色名称，开启盖子时花状尖头带出最真实的颜料色，引导人们关注颜料本身而非印刷色卡。",[51,54]),
 ("招财猫存钱罐","黄治权","张剑","2026",
  "当存钱罐变成一只招财猫，摆动的猫爪晃动着对金钱的渴望；钱币坠入猫爪发出清脆声响，储蓄成为一种愉悦仪式。",[55,59]),
 ("钱币吸铁石","黄治权","张剑","2026",
  "将吸铁石做成圆润、表面闪烁金属光泽如钱币的形态，让人不自觉想把钱币随手一放，重新定义存钱的容器。",[60,64]),
 ("硅胶蟾蜍印章","黄治权","张剑","2026",
  "一款柔软富弹性的硅胶印章，表面看似普通趴在桌面，掀起时底部蟾蜍图案显现，带来俏皮的反转趣味。",[65,70]),
 ("水洗纸表盘吊牌","黄治权","张剑","2026",
  "将吊牌重构为时尚单品：选用水洗纸为基底，中间嵌入圆角表盘，悬挂于衣物时如怀表垂坠，以摇晃韵律彰显品牌态度。",[71,73]),
 ("夜光苍耳（遛狗）","黄治权","张剑","2026",
  "把苍耳涂成夜光样式，装进糖果罐般的透明瓶中；出门遛狗时贴在狗狗身上，夜晚草丛里便蹦跳晃动，趣味新奇。",[74,78]),
 ("香水卡片","黄治权","张剑","2026",
  "当硬纹纸卡片的符号进入香水瓶，便自然让人想要带走它；卡片通过简单卡槽结构与瓶身连接，可压印品牌名增加时尚感。",[79,80]),
]

# ---- 映射图像并写入 ----
def map_imgs(cand_dir, gi_range):
    files = sorted(os.listdir(cand_dir))
    out = []
    for gi in range(gi_range[0], gi_range[1]+1):
        if gi < len(files): out.append(os.path.join(cand_dir, files[gi]))
    return out

cand6b = 'cand6b'; cand6c = 'cand6c'
art_img = 'art_images'; art_thumb = 'art_thumb'
os.makedirs(art_img, exist_ok=True); os.makedirs(art_thumb, exist_ok=True)

# 起始 id
data = open('data.js', encoding='utf-8').read()
ids = [int(x) for x in re.findall(r'"id":\s*"a(\d+)"', data)]
start = max(ids) + 1
print('start id a%02d' % start)

entries = []
seq = 0
for title, author, teacher, year, desc, rg in B + C:
    src = cand6b if year == '2025' else cand6c
    srcs = map_imgs(src, rg)
    if not srcs:
        print('  WARN no imgs', title); continue
    new_id = 'a%02d' % (start + seq); seq += 1
    img_names = []
    for k, sp in enumerate(srcs):
        ext = os.path.splitext(sp)[1]
        name = '%s_%02d%s' % (new_id, k, ext)
        dst = os.path.join(art_img, name)
        if not os.path.exists(dst): shutil.copy(sp, dst)
        tdst = os.path.join(art_thumb, name)
        if not os.path.exists(tdst): make_thumb(dst, tdst)
        img_names.append(name)
    entries.append(build_entry(title, author, teacher, year, desc, img_names, new_id))

print('built', len(entries), 'b/c entries')
json.dump(entries, open('works_bc.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
for e in entries:
    print(' ', e['id'], e['year'], '|', e['title'], '|', e['authors'], '| imgs', len(e['imgs']))
