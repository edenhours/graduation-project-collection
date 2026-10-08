# -*- coding: utf-8 -*-
"""
为全部作品补充分类字段：
  motif        文化母题粗分类（单值）
  typeCat      作品类型粗分类（单值）
  presCat      呈现方式粗分类（单值）
  narrMethod   阐述方式粗分类（单值）
  transMethod  转译手法（数组，可多选）
"""
import json, os, re

JS = r"C:\Users\23515\Desktop\优秀毕设\data.js"
ws = json.load(open("works.json", encoding="utf-8"))

# ---------- 分类体系 ----------

# 作品类型粗分：从 type 字段取主语或关键词
def typeCat(w):
    t = w.get("type", "")
    if "首饰" in t: return "首饰/可穿戴"
    if "家具" in t or "家居" in t: return "家具/家居"
    if "潮玩" in t or "IP" in t: return "潮玩/IP/角色"
    if "桌游" in t or "游戏" in t: return "游戏/桌游"
    if "视频" in t or "影像" in t or "动画" in t or "数字叙事" in t: return "影像/内容"
    if "绘本" in t or "叙事设计" in t or "信息" in t: return "视觉/信息"
    if "品牌" in t and "设计" in t: return "视觉/信息"
    if "视觉" in t or "平面" in t: return "视觉/信息"
    if "文创" in t: return "文创/衍生品"
    if "灯具" in t or "餐具" in t or "器皿" in t: return "产品设计"
    if "乡村" in t or "乡建" in t or "研学" in t or "公共设施" in t or "服务" in t or "社会创新" in t or "参与式" in t: return "社会创新/服务"
    if "产品" in t or "感知" in t or "材料" in t: return "产品设计"
    if "思辨" in t or "装置" in t: return "思辨/装置"
    if "可持续" in t or "循环经济" in t or "再生" in t: return "文创/衍生品"
    return "其他"

# 文化母题粗分：从 culture、标题、关键词综合判断
def motif(w):
    text = " ".join([
        w.get("title",""), w.get("concept",""), w.get("cultureNote",""),
        " ".join(w.get("culture",[])), " ".join(w.get("kw",[]))
    ])
    rules = [
        ("当代媒介与流行文化", ["科创","创造者社群","DIY","纸飞机","折叠","试错","短视频","UP主","美妆博主","直播","手机","游戏","桌游","潮玩","IP","波普","机械复制","当代职场","打工人","躺平","表情包"]),
        ("女性与身体叙事", ["女性","她经济","仕女","簪花","首饰","婚礼","婚俗","妆容","身体","生育","母题"," pregnancy"]),
        ("非遗与手工技艺", ["非遗","大漆","髹","香云纱","飘色","粤剧","钩编","钩织","刺绣","织造","纸扎","灯彩","剪纸","泥塑","陶瓷","广彩","前童","行会","民俗"]),
        ("城市日常与市井文化", ["早茶","点心","红胶凳","广东省凳","市井","城市礼物","城市记忆","沙面","十三行","广府","广州","粤语","方言","叹茶","早茶"]),
        ("自然生态与地方景观", ["红树林","海洋","疍家","水文化","南沙","湿地","游牧","草原","生态","自然","桑基鱼塘","水乡","山水","植物","香云纱","薯莨"]),
        ("跨文化/海上丝路/外贸", ["海上丝绸之路","外销画","外销瓷","中西贸易","跨文化","远航","远航的种子","海丝","丝路","贸易"]),
        ("信仰/神话/民间叙事", ["神怪","民间信仰","神兽","龙","凤","麒麟","宗祠","祖先","祭祀","龙","神话","传说"]),
        ("社会议题与群体关怀", ["流浪猫","动物","公益","弱势群体","老龄化","孤独症","社会批判","异化","职场","打工人","参与式","社区","群体关怀"]),
        ("物/材料/可持续", ["余料","废料","再生","可持续","循环","材料","材质","海绵","萝卜","木材","香氛","嗅觉","触觉","感知"]),
        ("记忆/身份/情感", ["记忆","身份","情感","陪伴","治愈","疗愈","孤独","乡愁","归乡","华侨","个体记忆","家族","宗族"]),
        ("礼俗/节庆/仪式", ["春节","年味","年货","婚礼","婚俗","节庆","仪式","礼物","礼俗","提篮","茶盒","茶礼","敬茶"]),
        ("饮食文化", ["茶","早茶","点心","餐饮","食物","饮食","茶文化","茶点"]),
    ]
    scores = {}
    for cat, kws in rules:
        score = 0
        for kw in kws:
            score += text.count(kw)
        if score:
            scores[cat] = score
    if not scores:
        return "其他"
    # 取最高分；若非遗与城市日常冲突，非遗优先一点点
    best = max(scores, key=scores.get)
    # 手动修复：潮玩/IP/游戏类虽然可能带非遗元素，但媒介属性优先
    if any(k in text for k in ["潮玩","IP","游戏","桌游","短视频","表情包","UP主"]) and best not in ["当代媒介与流行文化"]:
        if scores.get("当代媒介与流行文化",0) > 0:
            best = "当代媒介与流行文化"
    return best

# 呈现方式粗分：取作品的主媒介，展板排版等通用呈现不作为一级分类
def presCat(w):
    ps = " ".join(w.get("presentation", []))
    if "视频" in ps or "影像" in ps or "交互" in ps or "界面" in ps or "游戏" in ps: return "影像/交互/动态"
    if "场域" in ps or "装置" in ps or "展陈" in ps or "空间" in ps or "橱窗" in ps: return "空间/装置/展陈"
    if "实物" in ps or "样机" in ps or "模型" in ps: return "实物/产品"
    if "渲染" in ps or "效果图" in ps or "概念渲染" in ps or "虚拟" in ps: return "渲染/模型"
    if "绘本" in ps or "插画" in ps or "信息图" in ps: return "视觉/信息"
    if "展板" in ps or "平面" in ps or "视觉" in ps or "品牌" in ps: return "平面/视觉/图像"
    return "其他"

# 阐述方式粗分：把59种 unique 结构归到 6-7 个共同模板
NARR_MAP = {
    # 问题—机制—价值
    "议题 — 机制 — 闭环":"问题—机制—价值",
    "观察 — 归纳 — 再设计":"问题—机制—价值",
    "洞察 — 机制 — 价值":"问题—机制—价值",
    "问题 — 手段 — 参与 — 目标":"问题—机制—价值",
    "对象 — 机制 — 双向价值":"问题—机制—价值",
    "发现 — 追问 — 方法 — 延展":"问题—机制—价值",
    "观察 — 机制 — 交付":"问题—机制—价值",
    "载体 — 问题 — 手段 — 双重价值":"问题—机制—价值",
    "定位 — 痛点 — 分层 — 结语":"问题—机制—价值",
    "困境 — 方案 — 体验 — 意义":"问题—机制—价值",
    # 人群—意象—体验
    "人群 — 意象 — 系统":"人群—意象—体验",
    "文化符号 — 功能嫁接 — 体验清单":"人群—意象—体验",
    "对象 — 需求 — 效果 — 意义":"人群—意象—体验",
    "设定 — 反差 — 共鸣":"人群—意象—体验",
    "意象 — 群体 — 升华":"人群—意象—体验",
    "意象 — 形态 — 场景":"人群—意象—体验",
    "关系 — 行为 — 空间":"人群—意象—体验",
    "对象 — 融合 — 方法 — 目标":"人群—意象—体验",
    "节奏 — 位移 — 流动":"人群—意象—体验",
    # 背景—转译—应用
    "背景 — 设定 — 核心句":"背景—转译—应用",
    "背景 — 蓝本 — 形式 — 延伸":"背景—转译—应用",
    "文献 — 视角 — 手法":"背景—转译—应用",
    "起源 — 媒介 — 体验 — 共鸣":"背景—转译—应用",
    "背景 — 载体 — 转译 — 双重目标":"背景—转译—应用",
    "传统 — 场景 — 迁移":"背景—转译—应用",
    "研究 — 提取 — 融入 — 目的":"背景—转译—应用",
    "研究基础 — 手法 — 用户 — 愿景":"背景—转译—应用",
    "回望 — 结构 — 手法 — 维度":"背景—转译—应用",
    "定位 — 提取 — 转译 — 理念":"背景—转译—应用",
    "线索 — 结构 — 转译 — 意义":"背景—转译—应用",
    "体系 — 实验 — 转化 — 应用":"背景—转译—应用",
    # 批判—重构—质询
    "破题 — 重构 — 分章":"批判—重构—质询",
    "概念先行 — 考据 — 平衡":"批判—重构—质询",
    "灵感 — 手法 — 反目标 — 质询":"批判—重构—质询",
    "反题 — 转译 — 平权":"批判—重构—质询",
    "残缺 — 立场 — 尊严":"批判—重构—质询",
    "人类中心主义批判":"批判—重构—质询",
    "价值重估 — 设定 — 意象":"批判—重构—质询",
    "拆字 — 对立 — 剥离 — 收束":"批判—重构—质询",
    "发现 — 隐喻 — 边界 — 多重价值":"批判—重构—质询",
    # 品牌—场景—消费
    "民俗 — 品牌 — 场景":"品牌—场景—消费",
    "母题 — 角色 — 消费":"品牌—场景—消费",
    "礼俗 — 提梁 — 携行":"品牌—场景—消费",
    "雅事 — 轻译 — 日常":"品牌—场景—消费",
    # 材料—形态—感知
    "体系 — 实验 — 转化 — 应用":"材料—形态—感知",
    "发现 — 追问 — 方法 — 延展":"材料—形态—感知",
    "意象 — 形态 — 场景":"材料—形态—感知",
    "关系 — 行为 — 空间":"材料—形态—感知",
    "节奏 — 位移 — 流动":"材料—形态—感知",
    "理论 — 现象 — 隐喻 — 疗效":"材料—形态—感知",
    "双作品 — 各自机制 — 共同疗效":"材料—形态—感知",
    "对象 — 机制 — 双向价值":"材料—形态—感知",
    "理念 — 依据 — 整合 — 状态":"材料—形态—感知",
    # 田野—叙事—在地
    "田野 — 图典 — 转译":"田野—叙事—在地",
    "神兽 — 寻踪 — 归巷":"田野—叙事—在地",
    "声韵 — 译形 — 把玩":"田野—叙事—在地",
    "民俗 — 品牌 — 场景":"田野—叙事—在地",
    # 媒介—角色—传播
    "形式 — 情节 — 视角 — 共鸣":"媒介—角色—传播",
    "设定 — 推演 — 揭示":"媒介—角色—传播",
    "议题 — 对位 — 手段 — 世界观":"媒介—角色—传播",
    "媒介 — 翻转 — 显影":"媒介—角色—传播",
    "语言 — 系统 — 参与":"媒介—角色—传播",
    "母题 — 角色 — 消费":"媒介—角色—传播",
    # 余料—再生
    "废料 — 随形 — 重生":"余料—再生",
    "余料 — 再造 — 闭环":"余料—再生",
    "碎料 — 拼合 — 再生":"余料—再生",
}

def narrMethod(w):
    n = w.get("narration", "")
    return NARR_MAP.get(n, "其他")

# 转译手法：多选
def transMethod(w):
    text = " ".join([
        w.get("title",""), w.get("concept",""), w.get("cultureNote",""),
        w.get("type",""), w.get("narration",""), w.get("narrNote",""),
        " ".join(w.get("culture",[])), " ".join(w.get("kw",[])),
        " ".join(s.get("way","") for s in w.get("symbols",[]))
    ])
    methods = []
    # 四大工具系列（参考用户提供的工具分类）
    # 造型挪用：强调对既有造型/形态/符号的借用与变形
    if any(k in text for k in ["造型挪用","仿生","拟人","造型化","形体","轮廓","形态化","变形","挪用","拼贴","复制","挪用","异化","卡通化","几何化","抽象"]):
        methods.append("造型挪用")
    # 行为绑定：把文化行为、仪式、使用方式转译为设计触发点
    if any(k in text for k in ["行为绑定","行为","动作","姿态","仪式","使用方式","互动","参与","仪式化","可供性","手势","操作流程","使用场景","婚俗","茶礼","早茶","叹茶","祈福","游嬉","行走","寻踪","共创"]):
        methods.append("行为绑定")
    # 品牌叙事：以品牌/IP/角色/传播/消费场景为核心的叙事
    if any(k in text for k in ["品牌叙事","品牌","IP","潮玩","角色","世界观","传播","内容","频道","博主","UP主","文创产品","衍生品","消费市场","情绪价值","产品延伸","故事化传播","城市礼物","伴手礼"]):
        methods.append("品牌叙事")
    # 产品语义：用产品的功能、象征、隐喻承载意义
    if any(k in text for k in ["产品语义","功能嫁接","功能语义","象征","隐喻","转喻","语义","产品再设计","日常物","省凳","可供性","预期","惯性"]):
        methods.append("产品语义")
    # 维度
    if any(k in text for k in ["材料","材质","木料","金属","陶","瓷","漆","织物","海绵","软胶","硅胶","木材","石","玻璃","质感"]):
        methods.append("材料转译")
    if any(k in text for k in ["色彩","配色","色调","低饱和","色谱","五色","矿物颜料","颜色","色"]):
        methods.append("色彩转译")
    if any(k in text for k in ["形态","造型","几何","抽象","具象","轮廓","形体","结构","模块化","参数化"]):
        methods.append("形态转译")
    if any(k in text for k in ["情绪","情感","治愈","疗愈","陪伴","解压","幽默","氛围","心情","情绪价值"]):
        methods.append("情绪转译")
    if any(k in text for k in ["概念","观念","批判","思辨","隐喻","反讽","异化","话语","符号"]):
        methods.append("概念转译")
    if any(k in text for k in ["行为","动作","姿态","使用","仪式","互动","参与","手势","操作流程"]):
        methods.append("行为转译")
    # 媒介与视觉
    if any(k in text for k in ["视觉化","视觉转移","视觉转译","图像","插画","影像","视频","动态化","媒介转换","短视频","美妆博主","UP主"]):
        methods.append("视觉转移")
    if any(k in text for k in ["角色","IP","博主","拟人","人格","花灵","神兽","仕女"]):
        methods.append("角色化")
    if any(k in text for k in ["功能嫁接","功能","可用","使用"]):
        methods.append("功能嫁接")
    # 去重并排序
    methods = sorted(set(methods))
    # 兜底：至少给一个
    if not methods:
        methods = ["概念转译"]
    # 避免过于宽泛，最多保留 5 个
    return methods[:5]

# 手工修正表（覆盖规则判断）
OVERRIDE = {
    "a00": {"motif":"社会议题与群体关怀", "typeCat":"社会创新/服务", "presCat":"平面/视觉/图像", "narrMethod":"问题—机制—价值", "transMethod":["行为绑定","产品语义","品牌叙事"]},
    "a08": {"motif":"跨文化/海上丝路/外贸", "typeCat":"影像/内容", "presCat":"影像/交互/动态", "narrMethod":"媒介—角色—传播", "transMethod":["视觉转移","角色化","品牌叙事","媒介转换"]},
    "a18": {"motif":"非遗与手工技艺", "typeCat":"影像/内容", "presCat":"空间/装置/展陈", "narrMethod":"背景—转译—应用", "transMethod":["视觉转移","媒介转换","概念转译"]},
    "a42": {"motif":"当代媒介与流行文化", "typeCat":"思辨/装置", "presCat":"空间/装置/展陈", "narrMethod":"批判—重构—质询", "transMethod":["概念转译","产品语义","视觉转移"]},
    "a43": {"motif":"自然生态与地方景观", "typeCat":"首饰/可穿戴", "presCat":"实物/产品", "narrMethod":"背景—转译—应用", "transMethod":["造型挪用","材料转译","概念转译"]},
    "a51": {"motif":"社会议题与群体关怀", "typeCat":"思辨/装置", "presCat":"空间/装置/展陈", "narrMethod":"批判—重构—质询", "transMethod":["概念转译","视觉转移","产品语义"]},
}

for w in ws:
    oid = w["id"]
    w["typeCat"] = typeCat(w)
    w["motif"] = motif(w)
    w["presCat"] = presCat(w)
    w["narrMethod"] = narrMethod(w)
    w["transMethod"] = transMethod(w)
    if oid in OVERRIDE:
        for k, v in OVERRIDE[oid].items():
            w[k] = v

# ---------- 写回 data.js，保持原格式 ----------

ORDER = [
    "id","year","title","sub","authors","teachers","topic","type","typeCat",
    "motif","highlight","concept","culture","cultureNote","symbols","transMethod",
    "presentation","presCat","presNote","narration","narrMethod","narrBreak",
    "narrNote","desc","kw","imgs","video"
]

def fmt(v, indent=4):
    sp = " " * indent
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        if not v: return "[]"
        # 字符串数组单行
        if all(isinstance(x, str) for x in v):
            return "[" + ", ".join(json.dumps(x, ensure_ascii=False) for x in v) + "]"
        # 对象数组换行
        return "[\n" + ",\n".join(sp + "    " + fmt(x, indent+4) for x in v) + "\n" + sp + "]"
    if isinstance(v, dict):
        return "{\n" + ",\n".join(sp + "    " + json.dumps(k, ensure_ascii=False) + ": " + fmt(v[k], indent+4) for k in v) + "\n" + sp + "}"
    return json.dumps(v, ensure_ascii=False)

def obj_lines(w, indent=4):
    sp = " " * indent
    lines = []
    for k in ORDER:
        if k not in w:
            continue
        lines.append(sp + json.dumps(k, ensure_ascii=False) + ": " + fmt(w[k], indent))
    return "{\n" + ",\n".join(lines) + "\n" + sp + "}"

meta = {
    "source": "广州美术学院艺术设计系 优秀毕业设计作品档案（2022 / 2024 / 2025 / 2026 届 部分优秀作品）",
    "dept": "艺术设计系",
    "theme": "趋近完美",
    "updated": "2026-09-09",
    "note": "本页仅收录原文「艺术设计系」段落下的作品。分析维度新增文化母题、作品类型、呈现方式、阐述方式、转译手法等粗分类，便于筛选与知识沉淀。"
}

out = "window.ART_DATA = {\n  meta: " + fmt(meta, 2) + ",\n  works: [\n" + ",\n".join(obj_lines(w, 2) for w in ws) + "\n  ]\n};\n"

# backup
if os.path.exists(JS):
    open(JS + ".bak", "w", encoding="utf-8").write(open(JS, encoding="utf-8").read())
open(JS, "w", encoding="utf-8").write(out)

print("done, works:", len(ws))
for k in ["typeCat","motif","presCat","narrMethod"]:
    cnt = {}
    for w in ws:
        v = w.get(k,"")
        cnt[v] = cnt.get(v,0)+1
    print("\n",k)
    for v,n in sorted(cnt.items(), key=lambda x:-x[1]):
        print(f"  {n:2d} {v}")
print("\ntransMethod top")
cnt={}
for w in ws:
    for t in w.get("transMethod",[]): cnt[t]=cnt.get(t,0)+1
for v,n in sorted(cnt.items(), key=lambda x:-x[1]):
    print(f"  {n:2d} {v}")
