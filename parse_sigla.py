# -*- coding: utf-8 -*-
"""Этап 17 (§BQ): SigLA (sigla.phis.me) — распаковка database.js.

Файл — две OCaml-Marshal-структуры (magic 8495a6be), сериализованные
js_of_ocaml в JS-строки с \\ddd-эскейпами (десятичными, по нотации OCaml):
`signs` (таблица знаков: код AB/A + номер, чтение, эталонные вхождения) и
`data` (документы: id, тип носителя, сайт, ПЕРИОД — датировки нет в
lineara.xyz — и знак-уровневые записи).

Здесь: полный итеративный ридер формата Marshal (малый заголовок; коды
малых/больших блоков, строк, целых, shared-ссылок, double) + извлечение
документного слоя → sigla_docs.tsv. Палеографический (знаковый) слой —
задача будущего этапа. Кэш .sigla_cache.js гитигнорен; восстановление —
tools/fetch_sigla.sh (sha256 фиксирован в скрипте и в логе).
"""
import sys, re, struct, hashlib
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

RAW = open('.sigla_cache.js', encoding='utf-8').read()
print('кэш: %d симв.; sha256: %s' % (
    len(RAW), hashlib.sha256(RAW.encode('utf-8')).hexdigest()))

def js_var_bytes(name):
    """var NAME = '"\\\\132\\\\149…"'; — JS-строка с OCaml-литералом внутри:
    каждый байт = \\ddd (десятичный, бэкслеш в JS удвоен), обёртка — '"'."""
    m = re.search(r"var %s = '(.*?)';" % name, RAW, re.S)
    lit = m.group(1)
    assert lit[0] == '"' and lit[-1] == '"', lit[:8]
    inner = lit[1:-1]
    assert re.fullmatch(r'(?:\\\\\d{3})+', inner), (
        'неожиданные эскейпы: %r' % re.sub(r'\\\\\d{3}', '', inner)[:40])
    return bytes(int(inner[i + 2:i + 5]) for i in range(0, len(inner), 5))

class Blk:
    __slots__ = ('tag', 'f')
    def __init__(self, tag):
        self.tag = tag
        self.f = []

def unmarshal(data):
    """Итеративный ридер OCaml Marshal (intern.c), малый формат."""
    magic, dlen, nobj, _s32, _s64 = struct.unpack_from('>IIIII', data, 0)
    assert magic == 0x8495A6BE, hex(magic)
    assert len(data) == 20 + dlen, (len(data), dlen)
    pos = [20]
    objs = []

    def u8():
        pos[0] += 1
        return data[pos[0] - 1]

    def rd(n):
        p = pos[0]
        pos[0] += n
        return data[p:p + n]

    def s16():
        return struct.unpack('>h', rd(2))[0]

    def u32():
        return struct.unpack('>I', rd(4))[0]

    root = Blk(-1)
    stack = [[root, 1]]                      # [контейнер, осталось полей]
    while stack:
        if stack[-1][1] == 0:
            stack.pop()
            continue
        stack[-1][1] -= 1
        cont = stack[-1][0]
        code = u8()
        if code >= 0x80:                     # малый блок
            tag, sz = code & 0xF, (code >> 4) & 0x7
            b = Blk(tag)
            if sz:
                objs.append(b)
                stack.append([b, sz])
            cont.f.append(b)
        elif code >= 0x40:                   # малое целое
            cont.f.append(code & 0x3F)
        elif code >= 0x20:                   # малая строка
            s = rd(code & 0x1F)
            objs.append(s)
            cont.f.append(s)
        elif code == 0x00:                   # INT8
            cont.f.append(struct.unpack('>b', rd(1))[0])
        elif code == 0x01:                   # INT16
            cont.f.append(s16())
        elif code == 0x02:                   # INT32
            cont.f.append(struct.unpack('>i', rd(4))[0])
        elif code == 0x03:                   # INT64
            cont.f.append(struct.unpack('>q', rd(8))[0])
        elif code == 0x04:                   # SHARED8
            cont.f.append(objs[len(objs) - u8()])
        elif code == 0x05:                   # SHARED16
            cont.f.append(objs[len(objs) - struct.unpack('>H', rd(2))[0]])
        elif code == 0x06:                   # SHARED32
            cont.f.append(objs[len(objs) - u32()])
        elif code == 0x08:                   # BLOCK32
            hd = u32()
            tag, sz = hd & 0xFF, hd >> 10
            b = Blk(tag)
            if sz:
                objs.append(b)
                stack.append([b, sz])
            cont.f.append(b)
        elif code == 0x09:                   # STRING8
            s = rd(u8())
            objs.append(s)
            cont.f.append(s)
        elif code == 0x0A:                   # STRING32
            s = rd(u32())
            objs.append(s)
            cont.f.append(s)
        elif code == 0x0C:                   # DOUBLE_LITTLE
            v = struct.unpack('<d', rd(8))[0]
            objs.append(v)
            cont.f.append(v)
        elif code == 0x0B:                   # DOUBLE_BIG
            v = struct.unpack('>d', rd(8))[0]
            objs.append(v)
            cont.f.append(v)
        elif code in (0x0E, 0x0D):           # DOUBLE_ARRAY8
            n = u8()
            fmt = '<' if code == 0x0E else '>'
            v = list(struct.unpack(fmt + 'd' * n, rd(8 * n)))
            objs.append(v)
            cont.f.append(v)
        elif code in (0x07, 0x0F):           # DOUBLE_ARRAY32
            n = u32()
            fmt = '<' if code == 0x07 else '>'
            v = list(struct.unpack(fmt + 'd' * n, rd(8 * n)))
            objs.append(v)
            cont.f.append(v)
        elif code in (0x12, 0x19, 0x18):     # CUSTOM(_FIXED/_LEN)
            ident = b''
            while True:
                c = u8()
                if c == 0:
                    break
                ident += bytes([c])
            if code == 0x18:
                rd(12)                       # size32(u32)+size64(u64)
            if ident == b'_j':
                v = struct.unpack('>q', rd(8))[0]
            elif ident == b'_i':
                v = struct.unpack('>i', rd(4))[0]
            elif ident == b'_n':
                v = struct.unpack('>q', rd(8))[0]
            else:
                raise ValueError('custom %r' % ident)
            objs.append(v)
            cont.f.append(v)
        else:
            raise ValueError('код 0x%02x @%d' % (code, pos[0] - 1))
    print('  объектов: %d (заявлено %d), байт прочитано %d/%d'
          % (len(objs), nobj, pos[0] - 20, dlen))
    return root.f[0]

# ---------- распаковка обеих переменных
signs_root = None
data_root = None
for nm in ('signs', 'data'):
    b = js_var_bytes(nm)
    print('%s: %d байт' % (nm, len(b)))
    v = unmarshal(b)
    if nm == 'signs':
        signs_root = v
    else:
        data_root = v

# ---------- обход
def iter_blocks(root):
    seen = set()                 # shared-подструктуры обходим один раз
    st = [root]
    while st:
        x = st.pop()
        if isinstance(x, Blk) and id(x) not in seen:
            seen.add(id(x))
            yield x
            st.extend(c for c in x.f if isinstance(c, Blk))

def dstr(b):
    """Прямые строковые поля (+ разворачивание option-обёрток размера 1)."""
    out = []
    for c in b.f:
        if isinstance(c, bytes):
            out.append(c.decode('utf-8', 'replace'))
        elif isinstance(c, Blk) and len(c.f) == 1 and isinstance(c.f[0], bytes):
            out.append(c.f[0].decode('utf-8', 'replace'))
    return out

DOCID = re.compile(r'^[A-Z]{2,4}\s?(?:[A-Za-z]{1,3}\s?)?\d+[a-z]{0,2}$')
PERIOD = re.compile(r'^(EM|MM|LM|MH|LH)\b')

# знаковая таблица (для лога): блоки [префикс 'AB'/'A'/'B', номер, ..., чтение]
grid = {}
for b in iter_blocks(signs_root):
    ss = b.f
    if (len(ss) >= 2 and isinstance(ss[0], bytes) and
            ss[0] in (b'AB', b'A', b'B') and isinstance(ss[1], int)):
        strs = dstr(b)
        reading = next((s for s in strs[1:]
                        if re.fullmatch(r'[a-z]{1,3}\d?\*?', s)), '')
        grid['%s%02d' % (ss[0].decode(), ss[1])] = reading
ab = [(k, v) for k, v in sorted(grid.items()) if k.startswith('AB') and v]
print('\nзнаковая таблица: %d кодов (AB с чтением: %d); примеры: %s'
      % (len(grid), len(ab), ab[:8]))

# документы: поля классифицируем по СОДЕРЖАНИЮ (позиции ненадёжны:
# опциональные поля пропускаются)
SITES = {'Haghia Triada', 'Khania', 'Phaistos', 'Zakros', 'Knossos',
         'Mallia', 'Arkhanes', 'Thera', 'Kea', 'Tylissos', 'Petras',
         'Palaikastro', 'Gournia', 'Myrtos-Pyrgos', 'Pyrgos', 'Kato Zakros',
         'Akrotiri', 'Ayia Irini', 'Phylakopi', 'Kophinas', 'Kythera',
         'Iouktas', 'Syme', 'Vrysinas', 'Troullos', 'Kardamoutsa',
         'Mount Iouktas', 'Psychro', 'Larani', 'Prassa', 'Apodoulou',
         'Sitia', 'Samothrace', 'Mochlos', 'Papoura', 'Nerokourou',
         'Armenoi', 'Khamalevri', 'Sklavokambos', 'Tel Haror', 'Miletus',
         'Palaiokastro', 'GOURNIA', 'Psykhro', 'Mycenae', 'Melos',
         'Haghios Stephanos'}
HEX6 = re.compile(r'^[0-9a-f]{6}$')
docs = {}
unclass = Counter()
for b in iter_blocks(data_root):
    ss = dstr(b)
    ids = [s for s in ss if DOCID.match(s) and not PERIOD.match(s)]
    if not ids:
        continue
    did = ids[0]
    site = next((s for s in ss if s in SITES), '')
    per = next((s for s in ss if PERIOD.match(s)), '')
    url = next((s for s in ss if s.startswith('http')), '')
    rest = [s for s in ss if s not in (did, site, per, url)
            and not HEX6.match(s) and not DOCID.match(s)]
    kind = rest[0] if rest else ''
    for s in rest[1:]:
        unclass[s] += 1
    rec = (did, kind, site, per, url)
    if did not in docs or sum(bool(x) for x in rec) > \
            sum(bool(x) for x in docs[did]):
        docs[did] = rec

kinds = Counter(r[1] for r in docs.values())
periods = Counter(r[3] for r in docs.values())
sites_c = Counter(r[2] for r in docs.values())
print('\nдокументов: %d; с периодом: %d; с сайтом: %d'
      % (len(docs), sum(1 for r in docs.values() if r[3]),
         sum(1 for r in docs.values() if r[2])))
print('типы носителей:', kinds.most_common(12))
print('сайты:', sites_c.most_common(12))
print('периоды:', periods.most_common(16))
print('неклассифицированные строки (top):', unclass.most_common(10))

with open('sigla_docs.tsv', 'w', encoding='utf-8') as f:
    f.write('id\tid_norm\tkind\tsite\tperiod\turl\n')
    for did in sorted(docs):
        d, k, s, p, u = docs[did]
        f.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (d, d.replace(' ', ''), k, s, p, u))
print('sigla_docs.tsv записан')
