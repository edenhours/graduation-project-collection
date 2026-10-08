s = open('C:/Users/23515/Desktop/优秀毕设/data.js', encoding='utf-8').read()
reps = [
    ('（依据标题 Pie vase 与形态转译手法推断）', ''),
    ('（依据标题“时间的影子”与形态转译手法推断）', ''),
    ('（据标题与transMethod推断）', ''),
]
for a, b in reps:
    s = s.replace(a, b)
open('C:/Users/23515/Desktop/优秀毕设/data.js', 'w', encoding='utf-8').write(s)
print('cleaned 3 annotations')
