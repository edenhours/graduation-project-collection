# 只保留艺术设计系（原文「艺术设计系」段落）的 5 件作品，抽出到 art_images / art_thumb
import os, glob, json, shutil

d = json.load(open('works.json', encoding='utf-8'))
art = [w for w in d['works'] if w['dep'] == '艺术设计系']
print('艺术设计系作品数:', len(art))
for w in art:
    print(' -', w['title'], '|', w['authors'], '|', w['teachers'], '| imgs', len(w['imgs']))

meta = json.load(open('meta.json'))
newmeta = {}
pairs = []
for ai, w in enumerate(art):
    wi = d['works'].index(w)
    for ii in range(len(w['imgs'])):
        pairs.append((f'w{wi:02d}_{ii:02d}.jpg', f'a{ai:02d}_{ii:02d}.jpg'))

for sub, out in (('images', 'art_images'), ('thumb', 'art_thumb')):
    os.makedirs(out, exist_ok=True)
    for src, dst in pairs:
        s = os.path.join(sub, src)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(out, dst))
        if src in meta:
            newmeta[dst] = meta[src]

json.dump(newmeta, open('meta.json', 'w'))
json.dump(art, open('art.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('art_images:', len(glob.glob('art_images/*.jpg')), 'art_thumb:', len(glob.glob('art_thumb/*.jpg')))
