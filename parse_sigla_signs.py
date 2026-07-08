# -*- coding: utf-8 -*-
"""Этап 18 (§BV): SigLA — знаковый слой и кросс-валидация транскрипций.

Структура data (см. parse_sigla.py): OCaml Map, узел [l, key, Some(payload),
r, h]; payload = [метаданные(12), путь, СЛОВА(массив групп), (w,h),
ЗНАКИ(массив инстансов)]. Группа слова = [докссылка, список инстансов
(cons-ячейки), (строка, поз.), индекс]; инстанс = 8 полей, тип знака —
вложенная запись n=9 [префикс 'AB'/'A'/'B', номер, Some((чтение, _)), …].

Выход: sigla_signs.tsv (документ, слово, позиция, код, чтение) и сверка
с corpus.pkl: доля слов SigLA, находимых среди слов того же документа
корпуса (и обратно) — независимая кросс-валидация двух оцифровок
(GORILA-линия lineara.xyz против прорисовок Салгареллы).

Рук/писцов в слое данных SigLA НЕТ (в метаданных: размеры, период, URL) —
перезапуск §G на руках SigLA невозможен; фиксируем честно.
"""
import sys, re, struct, pickle
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

RAW = open('.sigla_cache.js', encoding='utf-8').read()

def js_var_bytes(name):
    m = re.search(r"var %s = '(.*?)';" % name, RAW, re.S)
    lit = m.group(1)
    inner = lit[1:-1]
    assert re.fullmatch(r'(?:\\\\\d{3})+', inner)
    return bytes(int(inner[i + 2:i + 5]) for i in range(0, len(inner), 5))

class Blk:
    __slots__ = ('tag', 'f')
    def __init__(self, tag):
        self.tag = tag
        self.f = []

def unmarshal(data):
    magic, dlen, nobj, _s32, _s64 = struct.unpack_from('>IIIII', data, 0)
    assert magic == 0x8495A6BE
    pos = [20]
    objs = []
    def u8():
        pos[0] += 1
        return data[pos[0] - 1]
    def rd(n):
        p = pos[0]; pos[0] += n
        return data[p:p + n]
    def u32():
        return struct.unpack('>I', rd(4))[0]
    root = Blk(-1)
    stack = [[root, 1]]
    while stack:
        if stack[-1][1] == 0:
            stack.pop(); continue
        stack[-1][1] -= 1
        cont = stack[-1][0]
        code = u8()
        if code >= 0x80:
            tag, sz = code & 0xF, (code >> 4) & 0x7
            b = Blk(tag)
            if sz:
                objs.append(b); stack.append([b, sz])
            cont.f.append(b)
        elif code >= 0x40:
            cont.f.append(code & 0x3F)
        elif code >= 0x20:
            s = rd(code & 0x1F); objs.append(s); cont.f.append(s)
        elif code == 0x00:
            cont.f.append(struct.unpack('>b', rd(1))[0])
        elif code == 0x01:
            cont.f.append(struct.unpack('>h', rd(2))[0])
        elif code == 0x02:
            cont.f.append(struct.unpack('>i', rd(4))[0])
        elif code == 0x04:
            cont.f.append(objs[len(objs) - u8()])
        elif code == 0x05:
            cont.f.append(objs[len(objs) - struct.unpack('>H', rd(2))[0]])
        elif code == 0x06:
            cont.f.append(objs[len(objs) - u32()])
        elif code == 0x08:
            hd = u32(); tag, sz = hd & 0xFF, hd >> 10
            b = Blk(tag)
            if sz:
                objs.append(b); stack.append([b, sz])
            cont.f.append(b)
        elif code == 0x09:
            s = rd(u8()); objs.append(s); cont.f.append(s)
        elif code == 0x0A:
            s = rd(u32()); objs.append(s); cont.f.append(s)
        elif code == 0x0C:
            v = struct.unpack('<d', rd(8))[0]; objs.append(v); cont.f.append(v)
        else:
            raise ValueError('код 0x%02x' % code)
    return root.f[0]

data_root = unmarshal(js_var_bytes('data'))

# --- обход Map: собрать (key, payload)
def iter_map(root):
    seen = set()
    st = [root]
    while st:
        x = st.pop()
        if not isinstance(x, Blk) or id(x) in seen:
            continue
        seen.add(id(x))
        if len(x.f) == 5 and isinstance(x.f[1], bytes) and \
           isinstance(x.f[2], Blk) and len(x.f[2].f) == 1 and \
           isinstance(x.f[2].f[0], Blk) and len(x.f[2].f[0].f) == 5:
            yield x.f[1].decode(), x.f[2].f[0]
        st.extend(c for c in x.f if isinstance(c, Blk))

def sign_entry(inst):
    """Инстанс n=8 → запись знака n=9 (f1.f0.f0), либо None."""
    try:
        e = inst.f[1].f[0].f[0]
        if isinstance(e, Blk) and len(e.f) == 9 and \
           isinstance(e.f[0], bytes) and isinstance(e.f[1], int):
            return e
    except (AttributeError, IndexError):
        pass
    return None

def entry_code_reading(e):
    code = '%s%02d' % (e.f[0].decode(), e.f[1])
    reading = ''
    r = e.f[2]
    if isinstance(r, Blk) and r.f and isinstance(r.f[0], Blk) and \
       r.f[0].f and isinstance(r.f[0].f[0], bytes):
        reading = r.f[0].f[0].decode()
    return code, reading

rows = []
docs_signs = Counter()
for did, pl in iter_map(data_root):
    if len(pl.f) < 5 or not isinstance(pl.f[2], Blk):
        continue
    for g in pl.f[2].f:                    # массив групп-слов
        if not (isinstance(g, Blk) and len(g.f) == 4):
            continue
        line, wpos = -1, -1
        if isinstance(g.f[2], Blk) and len(g.f[2].f) == 2:
            line, wpos = g.f[2].f[0], g.f[2].f[1]
        widx = g.f[3] if isinstance(g.f[3], int) else -1
        seq = []
        node = g.f[1]
        while isinstance(node, Blk) and len(node.f) == 2:
            e = sign_entry(node.f[0]) if isinstance(node.f[0], Blk) else None
            if e is not None:
                seq.append(entry_code_reading(e))
            node = node.f[1]
        for k, (code, reading) in enumerate(seq):
            rows.append((did, widx, line, wpos, k, code, reading))
        if seq:
            docs_signs[did] += len(seq)

print(f'документов со словами-группами: {len(docs_signs)}; '
      f'инстансов знаков в словах: {len(rows)}')
with open('sigla_signs.tsv', 'w', encoding='utf-8') as f:
    f.write('doc\tword_idx\tline\twpos\tpos\tcode\treading\n')
    for r in sorted(rows):
        f.write('\t'.join(str(x) for x in r) + '\n')
print('sigla_signs.tsv записан')

# --- кросс-валидация с corpus.pkl
SUBSCRIPT = {56: 'PA3', 66: 'TA2', 76: 'RA2', 68: 'RO2', 79: 'ZU',
             118: '*118'}                  # 79: в таблице SigLA нет чтения
def code_to_our(code, reading):
    if code.startswith('AB'):
        n = int(code[2:])
        if n in SUBSCRIPT:                 # SigLA даёт «ra» для ra2 и т.п.
            return SUBSCRIPT[n]
        return reading.upper() if reading else None
    return '*' + code[1:].lstrip('0') if code[1:].lstrip('0') else None

sig_words = defaultdict(list)              # doc_norm -> [tuple знаков]
skipped = Counter()
for did in sorted(docs_signs):
    byw = defaultdict(dict)
    for d, widx, line, wpos, k, code, reading in rows:
        if d != did:
            continue
        byw[widx][k] = code_to_our(code, reading)
    for widx in sorted(byw):
        w = [byw[widx][k] for k in sorted(byw[widx])]
        if any(x is None for x in w):
            skipped[did] += 1
            continue
        if len(w) >= 2:
            sig_words[did.replace(' ', '')].append(tuple(w))

corpus = pickle.load(open('corpus.pkl', 'rb'))
cor_words = defaultdict(list)
for d in corpus:
    for k, v in d['toks']:
        if k == 'WORD' and v['syllabic'] and len(v['signs']) >= 2:
            cor_words[d['id']].append(tuple(v['signs']))

def sides(cid):
    out = [cid]
    if cid and cid[-1] in 'abcd':
        out.append(cid[:-1])
    return out

both = 0
tot_sig = 0
found = 0
tot_cor = 0
found_cor = 0
mism_sample = []
for did, ws in sorted(sig_words.items()):
    cands = {did} | {c for c in cor_words
                     if c == did or c.rstrip('abcd') == did}
    cws = [w for c in cands for w in cor_words.get(c, [])]
    if not cws:
        continue
    both += 1
    cset = set(cws)
    for w in ws:
        tot_sig += 1
        if w in cset:
            found += 1
        elif len(mism_sample) < 12:
            mism_sample.append((did, w))
    sset = set(ws)
    for w in cws:
        tot_cor += 1
        if w in sset:
            found_cor += 1

print(f'\nсверка: документов с обеих сторон: {both}')
print(f'слов SigLA (>=2 знаков): {tot_sig}; найдено в корпусе: {found} '
      f'({found / tot_sig:.0%})' if tot_sig else 'слов SigLA нет')
print(f'слов корпуса в тех же документах: {tot_cor}; найдено в SigLA: '
      f'{found_cor} ({found_cor / tot_cor:.0%})' if tot_cor else '')
print('примеры несовпадений (SigLA-слово, нет в корпусном документе):')
for did, w in mism_sample:
    print(f'   {did}: {"-".join(w)}')
print('''
Чтение: расхождения = сумма (а) реальных разночтений прорисовок против
GORILA-линии, (б) разной сегментации слов, (в) наших ограничений
(бинды/лакуны). Доли — честная верхняя граница разногласий, не оценка
ошибок какой-то одной стороны. Рук/писцов в данных SigLA нет.''')
