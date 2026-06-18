#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
CONTENT = BASE / 'content'
INDEX_JSON = BASE / 'content-index.json'
INDEX_JS = BASE / 'content-index.js'

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

def read_students(folder):
    sp = folder / 'students.txt'
    if sp.exists():
        with open(sp, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return ''

def build():
    idx = {'levels': {}, 'students': {}}
    total_students = 0
    for lv in LEVELS:
        idx['levels'][lv] = {}
        idx['students'][lv] = {}
        for cat in CATEGORIES:
            idx['levels'][lv][cat] = {}
            idx['students'][lv][cat] = {}
            for les in CATEGORIES[cat]:
                folder = CONTENT / lv / cat / les
                files = []
                if folder.exists():
                    files = sorted([
                        f.name for f in folder.iterdir()
                        if f.is_file() and f.suffix.lower() in ALLOWED_EXTS
                    ])
                idx['levels'][lv][cat][les] = files
                students = read_students(folder)
                idx['students'][lv][cat][les] = students
                total_students += len(students)

    with open(INDEX_JSON, 'w', encoding='utf-8') as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)

    js = 'var __CONTENT_INDEX__ = ' + json.dumps(idx, ensure_ascii=False) + ';\n'
    with open(INDEX_JS, 'w', encoding='utf-8') as f:
        f.write(js)

    total = sum(len(v) for lv in idx['levels'].values() for c in lv.values() for v in c.values())
    print(f'✅ تم بناء فهرس المحتوى: {total} ملف دراسي + {total_students} اسم طالب')
    print(f'📄 {INDEX_JSON}')
    print(f'📄 {INDEX_JS}')

if __name__ == '__main__':
    if not CONTENT.exists():
        print('⚠️ مجلد المحتوى غير موجود. أنشئه أولاً.')
        sys.exit(1)
    build()
