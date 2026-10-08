import os, glob, json
from PIL import Image

os.makedirs('thumb', exist_ok=True)
meta = {}
for p in sorted(glob.glob('images/*.jpg')):
    name = os.path.basename(p)
    try:
        im = Image.open(p)
        im.load()
    except Exception as e:
        print('bad', p, e); continue
    w, h = im.size
    meta[name] = [w, h]
    tw = 900
    if w > tw:
        im = im.resize((tw, max(1, round(h * tw / w))), Image.LANCZOS)
    if im.mode in ('RGBA', 'P', 'LA'):
        bg = Image.new('RGB', im.size, (255, 255, 255))
        im = im.convert('RGBA')
        bg.paste(im, mask=im.split()[-1]); im = bg
    else:
        im = im.convert('RGB')
    im.save(os.path.join('thumb', name), 'JPEG', quality=82, optimize=True)
json.dump(meta, open('meta.json', 'w'))
print('done', len(meta))
print(round(sum(os.path.getsize(x) for x in glob.glob('thumb/*.jpg')) / 1e6, 1), 'MB thumbs')
