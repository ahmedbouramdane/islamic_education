import os, json

BASE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(BASE, 'content')

levels = ['رياض1', 'رياض2', 'رياض3', 'رياض4', 'رياض5', 'تج1', 'تج2', 'تج3']

categories = {
    'قران': ['شطر1', 'شطر2', 'شطر3', 'شطر4', 'شطر5', 'شطر6'],
    'عقيدة': ['ايمان_غيب', 'ايمان_علم', 'ايمان_فلسفة', 'ايمان_عمارة'],
    'اقتداء': ['صلح_حديبية', 'رسول_مفاوض', 'عثمان_بذل', 'رسول_بيت'],
    'استجابة': ['زواج', 'طلاق', 'اطفال', 'اسرة'],
    'قسط': ['امانة', 'صبر_يقين', 'عفة_حياء', 'توسط_بيئة'],
    'حكمة': ['كفاءة', 'عفو', 'وقاية', 'سبعة'],
}

index = {'levels': {}}

for lv in levels:
    index['levels'][lv] = {}
    for cat, lessons in categories.items():
        index['levels'][lv][cat] = {}
        for les in lessons:
            folder = os.path.join(CONTENT, lv, cat, les)
            os.makedirs(folder, exist_ok=True)
            index['levels'][lv][cat][les] = []

# JSON index (fallback for fetch)
with open(os.path.join(BASE, 'content-index.json'), 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

# JS index (primary, works with file://)
js = 'var __CONTENT_INDEX__ = ' + json.dumps(index, ensure_ascii=False) + ';\n'
with open(os.path.join(BASE, 'content-index.js'), 'w', encoding='utf-8') as f:
    f.write(js)

print(f'✅ تم إنشاء هيكل المجلدات وفهرس المحتوى')
print(f'📁 {len(levels)} مستويات × {sum(len(v) for v in categories.values())} درس = {len(levels) * sum(len(v) for v in categories.values())} مجلد درس')
print(f'📄 content-index.json')
print(f'📄 content-index.js')
