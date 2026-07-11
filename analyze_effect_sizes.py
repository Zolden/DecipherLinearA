# -*- coding: utf-8 -*-
"""Этап 34 (§DR): размеры эффектов и доверительные интервалы для главных
результатов (требование аудита №7: не только p).

Для MC-тестов: p = (b+1)/(R+1), 95% CI Клоппера–Пирсона по b из R;
стандартизованный эффект Z = (obs − μ₀)/σ₀ и обогащение obs/μ₀.
Числа — из канонических логов (ссылки в таблице); скрипт детерминирован.
"""
import sys
from scipy.stats import beta

sys.stdout.reconfigure(encoding='utf-8')

def cp_ci(b, R, level=0.95):
    a = (1 - level) / 2
    lo = beta.ppf(a, b + 1, R - b) if b >= 0 else 0.0
    hi = beta.ppf(1 - a, b + 2, R - b - 1) if b < R else 1.0
    return lo, hi

# (метка, obs, mu0, sd0, b, R, источник)
ROWS = [
    ('V/CV AUC=0.910 (точное перечисление)', None, None, None, 1401, 2869684,
     '§D + аудит: p=0.00049 точное'),
    ('Ономастикон DĀMOS (§DH, первичная)', 6, 0.68, 0.82, 1, 10000,
     'onomasticon_damos.log'),
    ('  устойчивость: Null-LP', 6, 0.74, 0.85, 1, 10000,
     'onomasticon_nulls.log'),
    ('  устойчивость: Null-MK', 6, 1.16, 1.07, 11, 10000,
     'onomasticon_nulls.log'),
    ('Пломбы №3: повторяемость (§DN)', 0.385, 0.129, 0.073, 24, 10000,
     'roundels2.log'),
    ('to-so-de предпоследний (§DP)', 40, 9.07, None, 0, 10000,
     'lb_record_syntax.log (p̃сем)'),
    ('KU-RO финал, строгий (§DF)', 12, 5.40, None, 13, 10000,
     'record_syntax2.log (p̃сем=0.0143)'),
    ('Формула-инициаль, строгий (§DF)', 6, 2.06, None, 21, 10000,
     'record_syntax2.log (p̃сем=0.0217)'),
]

print(f'{"тест":<42}{"эффект":>14}{"Z":>7}{"p":>9}'
      f'{"95% CI p":>20}')
for label, obs, mu, sd, b, R, src in ROWS:
    if obs is not None and mu:
        enr = f'×{obs / mu:.1f}'
        z = f'{(obs - mu) / sd:.1f}' if sd else '—'
    else:
        enr = '—'
        z = '—'
    p = (b + 1) / (R + 1)
    lo, hi = cp_ci(b, R)
    print(f'{label:<42}{enr:>14}{z:>7}{p:>9.5f}'
          f'   [{lo:.5f}, {hi:.5f}]')
    print(f'{"":<42}источник: {src}')
print('''
Чтение: CI — Клоппера–Пирсона по числу превышений b из R перестановок
(для точного перечисления V/CV интервал вырожден в точное значение);
Z и обогащение — где доступны μ₀/σ₀ из логов. p разведочные, кроме
предрегистрированных (§DH, §DN) и точного V/CV.''')
