# -*- coding: utf-8 -*-
"""解析 sid 官网页的结构化数据块 -> sid_data.json"""
import re, json, glob, html as H

def field(s, cls):
    m = re.search(r'class="%s">\s*(.*?)\s*</div>' % cls, s, re.S)
    if not m: return ''
    t = re.sub(r'<[^>]+>', '', m.group(1))
    return H.unescape(t).strip()

def imgs_of(s, cls):
    out = []
    for m in re.finditer(r'class="%s"[^>]*>(.*?)</div>' % cls, s, re.S):
        for u in re.findall(r'src="(/__local[^"]+)"', m.group(1)):
            out.append('https://sid.gzarts.edu.cn' + H.unescape(u))
    return out

def video_of(s, cls):
    m = re.search(r'class="%s" path="([^"]+)"' % cls, s)
    return ('https://sid.gzarts.edu.cn/' + m.group(1)) if m else None

res = []
for fn in sorted(glob.glob('sid_*.html')):
    s = open(fn, encoding='utf-8').read()
    col = fn.replace('sid_', '').replace('.html', '')  # e.g. 2098_50204
    r = {
        'file': fn, 'col': col,
        'title': field(s, 'title'),
        'eng': field(s, 'english_title'),
        'authors': field(s, 'real_name'),
        'desc': field(s, 'descript'),
        'cls': field(s, 'classInSchool'),
        'teacher': field(s, 'teacher'),
        'recommend': field(s, 'is_recommend'),
        'thumb_count': field(s, 'thumb_count'),
        'imgs': (imgs_of(s, 'theme_image_url') + imgs_of(s, 'project_image_url')
                 + imgs_of(s, 'project_cover_url') + imgs_of(s, 'tutor_recommend_url')
                 + imgs_of(s, 'recommend_project_url')
                 + imgs_of(s, 'pc_main_video_image_url') + imgs_of(s, 'pc_sub_video_image_url')),
        'video_main': video_of(s, 'main_video_url'),
        'video_sub': video_of(s, 'sub_video_url'),
    }
    res.append(r)

json.dump(res, open('sid_data.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
for r in res:
    print(r['col'], '|', r['title'], '|', r['authors'], '| 师:', r['teacher'], '| 班:', r['cls'],
          '| 图', len(r['imgs']), '| 视频', r['video_main'] is not None, '| 正文', len(r['desc']))
