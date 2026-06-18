#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, sys, re
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from server.config import LEVELS, CATEGORIES, CAT_LABELS, LESSON_LABELS, ALLOWED_EXTS, ALLOWED_STR

BASE = Path(__file__).resolve().parent.parent
CONTENT = BASE / 'content'
INDEX_JSON = BASE / 'content-index.json'
INDEX_JS = BASE / 'content-index.js'

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

def read_students(folder):
    sp = folder / 'students.txt'
    if sp.exists():
        with open(sp, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return ''

def write_index(idx):
    with open(INDEX_JSON, 'w', encoding='utf-8') as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)
    js = 'var __CONTENT_INDEX__ = ' + json.dumps(idx, ensure_ascii=False) + ';\n'
    with open(INDEX_JS, 'w', encoding='utf-8') as f:
        f.write(js)

def refresh():
    idx = {'levels': {}, 'students': {}}
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
                idx['students'][lv][cat][les] = read_students(folder)
    write_index(idx)
    return idx

def next_filename(folder, ext):
    exist = set()
    for f in folder.iterdir():
        m = re.match(r'lesson(\d+)', f.stem)
        if m:
            exist.add(int(m.group(1)))
    n = 1
    while n in exist:
        n += 1
    return f'lesson{n}{ext}'

# ── Routes ──
@app.route('/site/')
@app.route('/site/<path:filename>')
def student_site(filename=''):
    if not filename:
        return send_from_directory(str(BASE), 'index.html')
    return send_from_directory(str(BASE), filename)

@app.route('/')
def dashboard():
    return render_template('upload.html',
        title='📤 رفع محتوى الدروس',
        levels=LEVELS, cats=CATEGORIES,
        clab=CAT_LABELS, llab=LESSON_LABELS,
        allowed=ALLOWED_STR, accept=','.join(ALLOWED_EXTS),
        exts=list(ALLOWED_EXTS))

@app.route('/api/files/<level>/<cat>/<les>')
def api_files(level, cat, les):
    folder = CONTENT / level / cat / les
    files = []
    if folder.exists():
        files = sorted([
            f.name for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in ALLOWED_EXTS
        ])
    return jsonify({'files': files})

@app.route('/api/upload', methods=['POST'])
def api_upload():
    level = request.form.get('level')
    cat = request.form.get('cat')
    les = request.form.get('les')
    if not all([level, cat, les]):
        return jsonify({'ok': False, 'error': 'بيانات ناقصة'})
    folder = CONTENT / level / cat / les
    folder.mkdir(parents=True, exist_ok=True)
    count = 0
    names = []
    for f in request.files.getlist('files'):
        if f.filename:
            ext = Path(f.filename).suffix.lower()
            if ext in ALLOWED_EXTS:
                name = next_filename(folder, ext)
                f.save(str(folder / name))
                count += 1
                names.append(name)
    refresh()
    return jsonify({'ok': True, 'count': count, 'names': names})

@app.route('/api/delete/<level>/<cat>/<les>/<path:filename>', methods=['DELETE'])
def api_delete(level, cat, les, filename):
    fp = CONTENT / level / cat / les / filename
    if fp.exists() and fp.is_file():
        fp.unlink()
        refresh()
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'error': 'الملف غير موجود'})

@app.route('/api/students/<level>/<cat>/<les>')
def api_students(level, cat, les):
    folder = CONTENT / level / cat / les
    return jsonify({'text': read_students(folder)})

@app.route('/api/students/<level>/<cat>/<les>', methods=['POST'])
def api_students_save(level, cat, les):
    data = request.get_json(force=True)
    text = data.get('text', '')
    folder = CONTENT / level / cat / les
    folder.mkdir(parents=True, exist_ok=True)
    sp = folder / 'students.txt'
    if text.strip():
        with open(sp, 'w', encoding='utf-8') as f:
            f.write(text.strip())
    elif sp.exists():
        sp.unlink()
    refresh()
    return jsonify({'ok': True})

@app.route('/content/<path:subpath>')
def serve_content(subpath):
    return send_from_directory(str(CONTENT), subpath)

if __name__ == '__main__':
    if not CONTENT.exists():
        print('⚠️  شغّل build_folders.py أولاً')
        sys.exit(1)
    refresh()
    print('=' * 50)
    print('  📤 لوحة الرفع:  http://127.0.0.1:5000/')
    print('=' * 50)
    print('  📖 الموقع الرئيسي: http://127.0.0.1:5000/site/')
    print('  أو افتح index.html مباشرة')
    print('=' * 50)
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
