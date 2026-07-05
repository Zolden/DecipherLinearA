# -*- coding: utf-8 -*-
"""Задача A: underdot-слой сомнительных чтений Янгера.

Источник: commentary.tar — каталог commentary/ репозитория
https://github.com/mwenge/lineara.xyz (commit eb9afc70104aed41dc740ebd05bf7e677fb48ffe,
2025-11-23). Это скрейп страниц Янгера «Linear A Texts in phonetic transcription»:
таблицы side.line | statement | logogram | no. | fraction, где сомнительные знаки
обёрнуты в <u>…</u> (underdot у Янгера), плюс инлайн-текст для не-табличных страниц.

ВАЖНО: в items/<ID>.html (сами страницы объектов) разметки сомнительности НЕТ
(все <ideogram> без атрибутов, U+0323 отсутствует) — проверено сканом всех 1720
файлов. Поэтому underdot-слой извлекается из commentary/, а не из items/.

Привязка страница→документ корпуса: имена файлов ненадёжны (пример: 16.html — это
HT116, а не HT16), поэтому кандидаты берутся по имени И по инвертированному индексу
редких слов, затем верифицируются выравниванием последовательностей токенов
(difflib.SequenceMatcher). Перенос underdot-флагов — только на сматченные токены.

Выход: underdots.tsv (doc_id, tok_index, kind, norm, позиции сомнительных знаков),
underdots_layer.pkl (dict (doc_id, tok_index) -> описание сомнения) и лог покрытия.
Замороженный corpus.pkl НЕ модифицируется.
"""
import re, sys, pickle, tarfile, difflib
from collections import defaultdict, Counter
from fractions import Fraction

sys.stdout.reconfigure(encoding='utf-8')

TAR = 'commentary.tar'

# ---------------------------------------------------------------- HTML → куски
TAG = re.compile(r'<[^>]+>')

def pieces_of(html):
    """Разбить HTML-фрагмент на куски (text, underdot_flag) с учётом <u> и <sub>.
    <sub>N</sub> приклеивается к предыдущему куску (PA<sub>3</sub> -> PA3)."""
    out = []   # [текст, флаг]
    depth_u = 0
    pos = 0
    for m in re.finditer(r'<(/?)(u|sub)\b[^>]*>|<[^>]+>', html, re.I):
        txt = html[pos:m.start()]
        if txt.strip():
            out.append([txt, depth_u > 0])
        pos = m.end()
        g = m.group(0).lower()
        if g.startswith('<u'): depth_u += 1
        elif g.startswith('</u'): depth_u = max(0, depth_u - 1)
        elif g.startswith('<sub'):
            m2 = re.compile(r'(.*?)</sub\s*>', re.S | re.I).match(html, m.end())
            if m2:
                sub = TAG.sub('', m2.group(1)).strip()
                if sub:
                    if out: out[-1][0] = out[-1][0].rstrip() + sub
                    else: out.append([sub, depth_u > 0])
                pos = m2.end()
    txt = html[pos:]
    if txt.strip(): out.append([txt, depth_u > 0])
    return [(t, f) for t, f in out]

# ------------------------------------------------------------- токены страницы
BRACES = re.compile(r'\{[^}]*\}')
# имена знаков Янгера -> номенклатура корпуса (Дурос/lineara.xyz)
SIGN_ALIAS = {
    'FIC': 'NI', '*123': 'AROM', '*303': 'CYP', '*180': 'HIDE',
    'OVISf': '*21F', 'OVISm': '*21M', 'CAPf': '*22F', 'CAPm': '*22M',
    'BOSf': '*23F', 'BOSm': '*23M',
}
def norm_sign(s):
    """Нормализация имени знака для сравнения Янгер ↔ корпус."""
    s = BRACES.sub('', s)
    s = s.replace('̣', '').replace('?', '')
    s = s.strip('[](). ')
    s = re.sub(r'\+\[\s*\]$', '', s)      # OLE+[] -> OLE
    s = re.sub(r'\+\[\s*\?\s*\]$', '', s)
    s = s.rstrip('+')
    if s in SIGN_ALIAS: return SIGN_ALIAS[s]
    if '+' in s:   # компаунды: алиасинг каждой части (*303+D -> CYP+D)
        parts = [SIGN_ALIAS.get(p, p) for p in s.split('+')]
        s = '+'.join(parts)
    if not s.startswith('*'):
        s = re.sub(r'(?<=[A-Z])[a-z]+$', '', s)  # VINa -> VIN
    return SIGN_ALIAS.get(s, s).strip('-')

def norm_word_corpus(norm):
    """Ключ слова корпуса для выравнивания."""
    signs = [norm_sign(x) for x in norm.split('-')]
    return '-'.join(x for x in signs if x).replace('+', '-')

WORDCH = re.compile(r'^[A-Za-z0-9*+\[\]{}̣?._-]+$')

def parse_statement(pieces):
    """Куски ячейки statement/logogram → список слов [(signs, doubts, raw)].
    Знаки внутри слова разделены '-', слова — пробелами или •."""
    # склеиваем куски в последовательность символов с флагами, затем режем
    chars = []
    for t, f in pieces:
        t = t.replace('•', ' • ')
        for ch in t:
            chars.append((ch, f))
    words = []
    cur_sign, cur_flag, cur_word = '', False, []
    def end_sign():
        nonlocal cur_sign, cur_flag
        s = cur_sign.strip()
        if s and s not in ('•', '[', ']', '(', ')') and not s.islower():
            cur_word.append((s, cur_flag))          # islower: supra/mutila/vest…
        cur_sign, cur_flag = '', False
    def end_word():
        nonlocal cur_word
        end_sign()
        if cur_word:
            words.append(cur_word)
        cur_word = []
    i = 0
    while i < len(chars):
        ch, f = chars[i]
        if ch in '[]':
            i += 1            # эпиграфические скобки прозрачны: QA-[ ]-PU -> QA-PU
            continue
        if ch == '-':
            end_sign()
        elif ch.isspace() or ch == '•':
            # пробел заканчивает слово, если следующий непробельный не '-'
            # и текущий знак не пуст (иначе 'U </u> -TA-RO' разорвётся)
            j = i
            while j < len(chars) and (chars[j][0].isspace() or chars[j][0] == '•'):
                j += 1
            nxt = chars[j][0] if j < len(chars) else ''
            prv_dash = cur_sign == '' and cur_word  # только что был '-'
            if nxt == '-' or prv_dash:
                pass                       # продолжение того же слова
            elif cur_sign.strip().endswith(('*', '+')):
                pass                       # 'VIR+* 307', '* 324-DI-RA': компаунд ждёт номер
            elif nxt.isdigit() and cur_sign and cur_sign[-1].isalpha() and not cur_word:
                pass                       # 'RA 2' -> RA2 (подстрочный без <sub>)
            else:
                end_word()
            i = j - 1
        else:
            cur_sign += ch
            cur_flag = cur_flag or f
        i += 1
    end_word()
    # склейка компаундов, разорванных пробелами: 'QA' '+' '+PU' -> 'QA+PU'
    merged = []
    glue = False
    for w in words:
        raw0 = w[0][0]
        if raw0.strip() == '+':
            glue = True
            rest = w[1:]
            if rest and merged:
                s0, f0 = merged[-1][-1]
                merged[-1][-1] = (s0 + '+' + rest[0][0].lstrip('+'), f0 or rest[0][1])
                merged[-1].extend(rest[1:])
                glue = False
            continue
        if (glue or raw0.startswith('+')) and merged:
            s0, f0 = merged[-1][-1]
            merged[-1][-1] = (s0 + '+' + raw0.lstrip('+'), f0 or w[0][1])
            merged[-1] = merged[-1] + list(w[1:])
            glue = False
            continue
        glue = False
        merged.append(list(w))
    out = []
    for w in merged:
        signs = [norm_sign(s) for s, _ in w]
        doubts = [f for s, f in w]
        keep = [(s, d) for s, d in zip(signs, doubts) if s]
        if keep:
            out.append(([s for s, _ in keep], [d for _, d in keep],
                        '-'.join(s for s, _ in w)))
    return out

def parse_number(pieces):
    """Ячейка no.: цифровые куски конкатенируются ('1 <u>5</u>' -> 15, часть под
    сомнением). Возвращает (int|None, doubt_any) или None."""
    digits, doubt = '', False
    for t, f in pieces:
        for run in re.findall(r'\d+', t):
            digits += run
            doubt = doubt or f
    if not digits: return None
    return int(digits), doubt

FRACL = re.compile(r'^[A-Z]{1,2}\d?$')   # J, E, DD, L2…
def parse_fraction(pieces):
    """Ячейка fraction: буквенные коды Янгера (J, E, F, K, DD…). -> (n_letters, doubt_any)"""
    n, doubt = 0, False
    for t, f in pieces:
        for tok in t.split():
            tok = tok.strip('[]().')
            if FRACL.match(tok):
                n += 1
                doubt = doubt or f
    return n, doubt

# --------------------------------------------------------------- страница → потоки
SIDE = re.compile(r'^([a-z]{0,2})\s*[.·]?\s*(\d|$)')

def parse_page(html):
    """Вернуть dict side -> список токенов
    токен WORD: ('W', key, signs, doubts, raw); NUM: ('N', key, int, doubt)."""
    streams = defaultdict(list)
    tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.S | re.I)
    consumed_spans = []
    for tm in re.finditer(r'<table[^>]*>.*?</table>', html, re.S | re.I):
        consumed_spans.append(tm.span())
    header_labels = None
    side = ''
    for tbl in tables:
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbl, re.S | re.I)
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S | re.I)
            if not cells: continue
            texts = [TAG.sub(' ', c) for c in cells]
            plain = [re.sub(r'\s+', ' ', t).strip() for t in texts]
            if 'side.line' in plain or ('statement' in plain and 'logogram' in plain):
                header_labels = [re.sub(r'[^a-z.]', '', p.lower()) for p in plain]
                continue
            labels = header_labels
            if labels is None or len(labels) < 2:
                labels = ['side.line', 'statement', 'logogram', 'no.', 'fraction']
            # side.line
            sl = plain[0] if plain else ''
            m = SIDE.match(sl)
            if m and sl:
                if m.group(1): side = m.group(1)
            row_toks = []
            pend_num = None   # [int|None, doubt] ждёт возможной дроби
            HARD_FRAC = {'J', 'F', 'H', 'K', 'W', 'X', 'Y', 'B', 'DD', 'EE', 'JE'}
            SOFT_FRAC = {'E', 'L'}   # реальные знаки; дробь — только сразу после числа
            def flush_num():
                nonlocal pend_num
                if pend_num is not None:
                    iv, dv = pend_num
                    key = str(iv) if iv is not None else 'F'
                    row_toks.append(('N', key, iv, dv))
                pend_num = None
            def add_frac(doubt):
                nonlocal pend_num
                if pend_num is None:
                    pend_num = [None, False]   # дробь без целой части -> группа 'F'
                pend_num[1] = pend_num[1] or doubt
            for idx in range(1, len(cells)):
                lab = labels[idx] if idx < len(labels) else 'logo'
                pieces = pieces_of(cells[idx])
                if not pieces: continue
                if lab.startswith(('statement', 'logogram', 'logo')):
                    for signs, doubts, raw in parse_statement(pieces):
                        key = '-'.join(signs).replace('+', '-')
                        if len(signs) == 1 and (
                                signs[0] in HARD_FRAC or
                                (signs[0] in SOFT_FRAC and pend_num is not None)):
                            add_frac(doubts[0])
                            continue
                        if key and WORDCH.match(key.replace('-', '')) is None:
                            continue
                        if key:
                            flush_num()
                            row_toks.append(('W', key, signs, doubts, raw))
                elif lab.startswith(('no', 'number')):
                    flush_num()
                    pn = parse_number(pieces)
                    if pn is not None: pend_num = list(pn)
                    nfr, fd = parse_fraction(pieces)   # буквы дробей в той же ячейке
                    if nfr: add_frac(fd)
                elif lab.startswith('fraction'):
                    nfr, fd = parse_fraction(pieces)
                    if nfr: add_frac(fd)
                    if pend_num is not None: flush_num()
                else:
                    flush_num()
            flush_num()
            streams[side].extend(row_toks)
    # инлайн-текст вне таблиц (Za-страницы и шапки): только если таблиц нет
    if not tables:
        body = re.sub(r'Commentary\s*©.*', '', html, flags=re.S)
        pieces = pieces_of(body)
        # выкинуть служебные строки: имя, скобки музея, GORILA
        toks = []
        for signs, doubts, raw in parse_statement(pieces):
            key = '-'.join(signs)
            # слова: только с ≥1 валидным слоговым знаком; отсечь болтовню
            if all(re.match(r'^[A-Z]{1,2}\d?$|^\*\d+[A-Za-z]*$|^[A-Z]+\+[A-Z0-9*]+$', s)
                   for s in signs) and (len(signs) >= 2 or key in ('KU-RO',)):
                toks.append(('W', key, signs, doubts, raw))
        streams[''] = toks
    return streams

# --------------------------------------------------------------- корпус
def corpus_stream(doc):
    """Поток ключей корпуса: WORD → ключ слова, NUM-группа → ключ числа."""
    toks = []
    cur = None  # [значение, doubt, индексы]
    def flush():
        nonlocal cur
        if cur is not None:
            v, idxs = cur
            iv = int(v) if v == int(v) else int(v)  # floor для Fraction
            key = str(iv) if v >= 1 else 'F'
            toks.append(('N', key, idxs))
            cur = None
    for i, (k, v) in enumerate(doc['toks']):
        if k == 'WORD':
            flush()
            toks.append(('W', norm_word_corpus(v['norm']), i))
        elif k == 'NUM':
            if cur is None: cur = [Fraction(0), []]
            cur[0] += v['val']; cur[1].append(i)
        else:
            flush()
    flush()
    return toks

def match_score(page_keys, doc_keys):
    sm = difflib.SequenceMatcher(a=page_keys, b=doc_keys, autojunk=False)
    return sm

# --------------------------------------------------------------- основной проход
def main():
    corpus = pickle.load(open('corpus.pkl', 'rb'))
    docs = {d['id']: d for d in corpus}
    doc_streams = {d['id']: corpus_stream(d) for d in corpus}

    # инвертированный индекс: ключ слова (len>=2 знаков) -> документы
    inv = defaultdict(set)
    for did, st in doc_streams.items():
        for t in st:
            if t[0] == 'W' and '-' in t[1]:
                inv[t[1]].add(did)

    t = tarfile.open(TAR)
    layer = {}          # (doc_id, tok_index) -> dict
    page_report = []
    n_pages = n_matched_pages = 0
    for m in sorted(t.getmembers(), key=lambda x: x.name):
        if not m.name.endswith('.html'): continue
        n_pages += 1
        name = m.name[:-5]
        html = t.extractfile(m).read().decode('utf-8', 'replace')
        streams = parse_page(html)
        base = re.sub(r'\.html$', '', name)
        page_roots = set()   # корни doc_id, найденные другими сторонами этой страницы
        sides_sorted = sorted(streams.items(), key=lambda kv: kv[0])
        # fallback: если в корпусе документ без буквы стороны — склеить все стороны
        if len(streams) > 1:
            merged = []
            for s, tk in sides_sorted: merged.extend(tk)
            sides_sorted.append(('*merged*', merged))
        matched_sides = set()
        for side, toks in sides_sorted:
            if not toks: continue
            if side == '*merged*' and matched_sides: continue  # стороны уже привязаны
            if side == '*merged*': side = ''
            wkeys = [tt[1] for tt in toks if tt[0] == 'W' and '-' in tt[1]]
            # кандидаты по имени
            cands = set()
            for suff in ('', side, 'a', 'b', 'c', 'd', 'e'):
                for pre in ('', 'HT'):
                    cid = pre + base + suff
                    if cid in docs: cands.add(cid)
            # нормализация скобок/регистров: APZa3 -> APZa<3>, HT154A -> HT154a
            for did in docs:
                dn = did.replace('<', '').replace('>', '')
                if dn.lower() == (base + side).lower() or dn.lower() == base.lower():
                    cands.add(did)
            # корни от уже привязанных сторон той же страницы
            for root in page_roots:
                for suff in ('', side, 'a', 'b'):
                    if root + suff in docs: cands.add(root + suff)
            # кандидаты по содержимому: редкие слова целиком, частые — топом
            cnt = Counter()
            for w in wkeys:
                dfw = len(inv.get(w, ()))
                for did in inv.get(w, ()):
                    if dfw <= 40: cands.add(did)
                    cnt[did] += 1.0 / max(dfw, 1)
            cands |= {did for did, c in cnt.most_common(15)}
            page_keys = [tt[1] for tt in toks]
            scored = []
            for did in cands:
                st = doc_streams[did]
                doc_keys = [x[1] for x in st]
                sm = difflib.SequenceMatcher(a=page_keys, b=doc_keys, autojunk=False)
                matched = sum(bl.size for bl in sm.get_matching_blocks())
                scored.append((sm.ratio(), matched, did, sm))
            scored.sort(key=lambda x: (-x[0], -x[1]))
            best = best_sm = None; best_ratio = 0.0; matched = 0
            if scored:
                best_ratio, matched, best, best_sm = scored[0]
            # верификация + защита от неоднозначности
            ok = False
            if best is not None:
                small = len(doc_streams[best]) <= 3
                # какие ключи сматчены (для требования «есть многознаковое слово»)
                mk = []
                for bl in best_sm.get_matching_blocks():
                    mk.extend(page_keys[bl.a:bl.a + bl.size])
                has_word = any(('-' in k or '+' in k) for k in mk)
                cover = matched / max(1, len(doc_streams[best]))
                ok = (matched >= 2 and best_ratio >= 0.45) or \
                     (matched >= 2 and cover >= 0.6 and has_word) or \
                     (small and matched >= 1 and best_ratio >= 0.4)
                if ok and len(scored) > 1 and best_ratio < 0.6:
                    r2, m2, d2, _ = scored[1]
                    root1 = best.rstrip('abcde'); root2 = d2.rstrip('abcde')
                    if best_ratio - r2 < 0.05 and root1 != root2:
                        ok = False   # два разных документа почти одинаково похожи
            n_doubt = sum(1 for tt in toks
                          if (tt[0] == 'W' and any(tt[3])) or (tt[0] == 'N' and tt[3]))
            page_report.append((name, side, len(toks), best, round(best_ratio, 3), ok, n_doubt))
            if not ok: continue
            n_matched_pages += 1
            matched_sides.add(side)
            page_roots.add(re.sub(r'[a-e]$', '', best))
            st = doc_streams[best]
            for bl in best_sm.get_matching_blocks():
                for k in range(bl.size):
                    pt = toks[bl.a + k]; ct = st[bl.b + k]
                    if pt[0] == 'W' and ct[0] == 'W':
                        _, key, signs, doubts, raw = pt
                        if not any(doubts): continue
                        ci = ct[2]
                        cs = docs[best]['toks'][ci][1]['signs']
                        ent = layer.setdefault((best, ci), {
                            'kind': 'WORD', 'norm': docs[best]['toks'][ci][1]['norm'],
                            'sign_doubt': [False] * len(cs), 'whole': False,
                            'src': name + ('.' + side if side else '')})
                        if len(cs) == len(doubts):
                            for si, dq in enumerate(doubts):
                                if dq: ent['sign_doubt'][si] = True
                        else:
                            ent['whole'] = True
                    elif pt[0] == 'N' and ct[0] == 'N':
                        _, key, iv, dq = pt
                        if not dq: continue
                        for ci in ct[2]:
                            layer.setdefault((best, ci), {
                                'kind': 'NUM', 'norm': str(docs[best]['toks'][ci][1]['val']),
                                'sign_doubt': None, 'whole': True,
                                'src': name + ('.' + side if side else '')})

    # ---------- выгрузка
    with open('underdots.tsv', 'w', encoding='utf-8') as f:
        f.write('doc_id\ttok_index\tkind\tnorm\tdoubt_positions\tsource_page\n')
        for (did, ci), ent in sorted(layer.items()):
            pos = 'ALL' if ent['whole'] else ','.join(
                str(i) for i, x in enumerate(ent['sign_doubt']) if x)
            f.write(f'{did}\t{ci}\t{ent["kind"]}\t{ent["norm"]}\t{pos}\t{ent["src"]}\n')
    pickle.dump(layer, open('underdots_layer.pkl', 'wb'))

    docs_hit = len({k[0] for k in layer})
    print(f'страниц commentary: {n_pages}; сматчено потоков: {n_matched_pages}')
    print(f'underdot-записей: {len(layer)} (WORD: '
          f'{sum(1 for v in layer.values() if v["kind"]=="WORD")}, NUM: '
          f'{sum(1 for v in layer.values() if v["kind"]=="NUM")}) в {docs_hit} документах')
    bad = [p for p in page_report if not p[5] and p[2] >= 3]
    print(f'непривязанных потоков с >=3 токенами: {len(bad)}')
    lost = [p for p in page_report if not p[5] and p[6] > 0]
    print(f'потоков с underdot-метками, оставшихся без привязки: {len(lost)} '
          f'(underdot-токенов в них: {sum(p[6] for p in lost)})')
    for p in lost[:25]: print('  LOST', p)
    # известные проверки
    for probe in [('HT9a',), ('HT118',), ('HT116a',)]:
        did = probe[0]
        ents = [(ci, v) for (d, ci), v in layer.items() if d == did]
        print(f'--- {did}: {len(ents)} underdot-токенов')
        for ci, v in sorted(ents):
            print('   ', ci, v['kind'], v['norm'],
                  'ALL' if v['whole'] else [i for i, x in enumerate(v['sign_doubt']) if x])

if __name__ == '__main__':
    main()
