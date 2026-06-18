#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""أداة رفع الصور والفيديوهات لدروس التربية الإسلامية"""

import os, sys, json, shutil, subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
CONTENT = BASE / 'content'
INDEX = BASE / 'content-index.json'

LEVELS = {
    'رياض1': 'علوم رياضية (1)', 'رياض2': 'علوم رياضية (2)',
    'رياض3': 'علوم رياضية (3)', 'رياض4': 'علوم رياضية (4)',
    'رياض5': 'علوم رياضية (5)',
    'تج1': 'علوم تجريبية (1)',   'تج2': 'علوم تجريبية (2)',
    'تج3': 'علوم تجريبية (3)',
}

CATEGORIES = {
    'قران':    ['شطر1','شطر2','شطر3','شطر4','شطر5','شطر6'],
    'عقيدة':   ['ايمان_غيب','ايمان_علم','ايمان_فلسفة','ايمان_عمارة'],
    'اقتداء':  ['صلح_حديبية','رسول_مفاوض','عثمان_بذل','رسول_بيت'],
    'استجابة': ['زواج','طلاق','اطفال','اسرة'],
    'قسط':     ['امانة','صبر_يقين','عفة_حياء','توسط_بيئة'],
    'حكمة':    ['كفاءة','عفو','وقاية','سبعة'],
}

ALLOWED_EXTS = {'.jpg','.jpeg','.png','.gif','.webp','.mp4','.webm','.mov','.avi','.pdf'}

def load_index():
    if INDEX.exists():
        with open(INDEX, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'levels': {lv: {cat: {les: [] for les in lessons} for cat, lessons in CATEGORIES.items()} for lv in LEVELS}}

def save_index(idx):
    with open(INDEX, 'w', encoding='utf-8') as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)

def refresh_index():
    """Scan content folders and rebuild index."""
    idx = {'levels': {}}
    for lv in LEVELS:
        idx['levels'][lv] = {}
        for cat in CATEGORIES:
            idx['levels'][lv][cat] = {}
            for les in CATEGORIES[cat]:
                folder = CONTENT / lv / cat / les
                files = []
                if folder.exists():
                    files = sorted([f.name for f in folder.iterdir() if f.is_file() and f.suffix.lower() in ALLOWED_EXTS])
                idx['levels'][lv][cat][les] = files
    save_index(idx)
    return idx

def choose(msg, options, labels=None):
    print(f'\n{msg}')
    for i, (k, v) in enumerate(options, 1):
        label = labels[k] if labels and k in labels else v
        print(f'  {i}. {label}')
    while True:
        try:
            c = int(input('\nرقم اختيارك: ').strip())
            if 1 <= c <= len(options):
                return list(options.keys())[c-1]
        except ValueError:
            pass
        print('❌ رقم غير صحيح، حاول مرة أخرى')

def upload():
    print('\n' + '='*50)
    print('📤 أداة رفع محتوى الدروس')
    print('='*50)

    idx = load_index()

    lv = choose('اختر المستوى:', LEVELS, LEVELS)
    cat = choose('اختر القسم:', {k: k for k in CATEGORIES})

    lessons = CATEGORIES[cat]
    les_opts = {k: k for k in lessons}
    les = choose('اختر الدرس:', les_opts)

    folder = CONTENT / lv / cat / les
    folder.mkdir(parents=True, exist_ok=True)

    print(f'\n📂 المجلد المستهدف: {folder}')
    print('اسحب وأفلت الملفات في النافذة (أو اكتب المسارات مفصولة بفاصلة)')
    print('أو اكتب "quit" للخروج')
    print('الصيغ المدعومة: ' + ', '.join(ALLOWED_EXTS))

    while True:
        inp = input('\n📍 مسار الملف (أو quit): ').strip().strip('"').strip("'")
        if inp.lower() in ('quit', 'q', 'خروج'):
            break
        if not inp:
            continue

        src = Path(inp)
        if not src.exists():
            print(f'❌ الملف غير موجود: {inp}')
            continue
        if src.suffix.lower() not in ALLOWED_EXTS:
            print(f'❌ صيغة غير مدعومة: {src.suffix}')
            continue

        dst = folder / src.name
        shutil.copy2(src, dst)
        print(f'✅ تم رفع: {src.name}')

    print('\n🔄 تحديث فهرس المحتوى...')
    refresh_index()
    subprocess.run([sys.executable, str(BASE / 'build_index.py')], cwd=str(BASE))
    total = len([f for f in folder.iterdir() if f.is_file()])
    print(f'✅ تم التحديث. المجلد يحتوي على {total} ملف(ات).')

def show_all():
    print('\n📋 حالة المحتوى حسب المستوى والقسم:')
    idx = refresh_index()
    subprocess.run([sys.executable, str(BASE / 'build_index.py')], cwd=str(BASE))
    for lv in LEVELS:
        print(f'\n── {LEVELS[lv]} ──')
        for cat in CATEGORIES:
            total = 0
            for les in CATEGORIES[cat]:
                total += len(idx['levels'][lv][cat].get(les, []))
            status = '✅' if total > 0 else '📭'
            print(f'  {status} {cat}: {total} ملف(ات)')

def main():
    if not CONTENT.exists():
        print('⚠️  مجلد المحتوى غير موجود. شغّل build_folders.py أولاً.')
        return

    while True:
        print('\n' + '='*50)
        print('📤 أداة إدارة محتوى الدروس')
        print('='*50)
        print('1. 📤 رفع ملفات لدرس معين')
        print('2. 📋 عرض حالة المحتوى')
        print('3. 🔄 تحديث فهرس المحتوى')
        print('0. ❌ خروج')
        c = input('\nاختيارك: ').strip()
        if c == '1':    upload()
        elif c == '2':  show_all()
        elif c == '3':
            refresh_index()
            subprocess.run([sys.executable, str(BASE / 'build_index.py')], cwd=str(BASE))
            print('✅ تم تحديث الفهرس')
        elif c == '0':
            print('👋 السلام عليكم')
            break
        else:
            print('❌ اختيار غير صحيح')

if __name__ == '__main__':
    main()
