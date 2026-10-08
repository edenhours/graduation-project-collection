import json, os, urllib.request, concurrent.futures as cf

d = json.load(open('works.json', encoding='utf-8'))
W = [w for w in d['works'] if not w['title'].startswith('图文编辑')]

# 修正标题/作者/系别
fix = {
    5:  {'title': '栖光者 LUMINFLAI', 'authors': '刘梦昊'},
    27: {'title': 'One Lastime', 'authors': '曹依蕊'},
    29: {'title': '万物生', 'authors': '叶栩扬'},
    28: {'title': '瓦猫', 'authors': '潘元元'},
}
for i, f in fix.items():
    if not W[i]['authors']:
        W[i]['authors'] = f['authors']
    W[i]['title'] = f['title']
for w in W:
    if not w['dep']:
        w['dep'] = '工业与交互设计系'

os.makedirs('images', exist_ok=True)
tasks = []
for wi, w in enumerate(W):
    for ii, url in enumerate(w['imgs']):
        tasks.append((f'w{wi:02d}_{ii:02d}.jpg', url))

HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
       'Referer': 'https://mp.weixin.qq.com/'}


def get(t):
    name, url = t
    p = os.path.join('images', name)
    if os.path.exists(p) and os.path.getsize(p) > 2000:
        return name, 'skip'
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers=HDR)
            data = urllib.request.urlopen(req, timeout=30).read()
            if len(data) > 2000:
                open(p, 'wb').write(data)
                return name, len(data)
        except Exception as e:
            err = str(e)
    return name, 'FAIL ' + err


ok = fail = 0
with cf.ThreadPoolExecutor(12) as ex:
    for name, r in ex.map(get, tasks):
        if isinstance(r, int):
            ok += 1
        elif r == 'skip':
            ok += 1
        else:
            fail += 1
            print('FAIL', name, r)
print('ok', ok, 'fail', fail, 'total', len(tasks))

json.dump({'works': W, 'intro': d['intro']}, open('works.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
