# Linear A: a reproducible statistical framework
[![DOI](https://zenodo.org/badge/1291534873.svg)](https://doi.org/10.5281/zenodo.21262274)
### Kober-style combinatorics for an undeciphered Aegean script

This project analyses the Linear A corpus (Minoan Crete, ~1800–1450 BCE)
using **only combinatorics, arithmetic and permutation statistics** — no
decipherment claims, no translations. Every claim is of the form
"candidate", "class", or "consistent with", and every number in the report
is reproduced by a seeded script in this repository.

**Main document: [`linear_a_full_report_v2.md`](linear_a_full_report_v2.md)**
(sections §0–§DG; in Russian). The journal-style English
[preprint](preprint.md) (v1.4) condenses it; a popular-science summary is
available in [English](article_popular_en.md) and
[Russian](article_popular_ru.md). See also the [FAQ](FAQ.md).

## Headline results (all permutation-controlled, seed=42)

- **LB sound values transfer to LA**: signs that are vowels in Linear B
  behave positionally like vowels in Linear A (p≈0.0005); final-sign
  alternations share the consonant more often than chance (p≈0.002).
- **A toponym + personal-name layer survives into Greek Linear B archives**:
  exact homographs of length ≥3 are 11 observed vs ~2.4 expected
  (p<0.0001 for ≥4 signs); six candidates are confirmed in *name slots* of
  Knossos records (da-i-pi-ta, i-ta-ja, ki-da-ro, pa-ra-ne, ta-na-ti,
  i-ja-te; p<0.0001). Short-word "identical word" lists are shown to be
  statistical noise.
- **Calibrated morphology**: suffix **-JA** and prefix **A-** survive
  family-wise permutation control and replicate across independent archives
  (plus PI-); -JA marks the non-administrative register (p≈0.01–0.016).
- **A "geography slot" in the libation formula**: position 2 of the
  pan-Cretan formula is site-specific (p=0.012); its Palaikastro cluster
  (DI-KI-TE stem) sits exactly where Greek cult of Diktaian Zeus is later
  attested.
- **Commodity-dependent metrology**: grain is counted on a pure binary
  fraction grid (1/16 quantum, 100% coverage), oil/wine on a mixed
  duodecimal grid (Fisher p=0.021); people are counted in integers.
- **Typology**: word-shape profile of Linear A is incompatible with Greek
  (final -o: 4% vs 45%), Akkadian, Hurrian and Georgian profiles; the
  remaining candidate cluster (Etruscan/Anatolian/isolates) is not
  statistically separable at current sample sizes.
- **34 "bimorphs"** (two-sign elements living both as free words and inside
  longer words) vs 19.8±3.6 expected (p<0.001) — a first data-driven
  inventory of Linear A lexical elements, split cleanly by register
  (administrative A-DU vs cultic I-DA).

## Data

- `corpus.pkl` — frozen research database: 1721 inscriptions parsed into
  typed tokens, validated against a hand-checked mini-corpus (44 exact /
  3 fraction upgrades / 5 documented revisions / 0 unresolved). Derived
  from the tabulations of G. Douros and the editions GORILA (Godart &
  Olivier) and J. Younger, via the open dataset of
  [lineara.xyz](https://github.com/mwenge/lineara.xyz). See
  [`DATA_SOURCES.md`](DATA_SOURCES.md) for provenance, credits and takedown
  policy.
- `underdots.tsv` / `underdots_layer.pkl` — a layer of epigraphically
  uncertain sign readings (Younger's underdots), machine-aligned to the
  corpus (717 marks, 345 documents).
- `lb_lexicon.tsv`, `lb_name_slots.tsv` — Linear B comparison word lists
  (3694 types) and record-slot personal-name candidates (1641), derived
  from public scholarly transliterations (Killen & Olivier; Bennett) via
  archived pages of minoan.deaditerranean.com.
- `lb2_lexicon.tsv`, `lb2_name_slots.tsv` — an independent second
  digitization (4791 types; 1751 slot names) from the
  [linearb.xyz](https://github.com/mwenge/linearb.xyz) dataset, used for
  cross-replication.
- `sigla_docs.tsv` — document-level dating/metadata layer (687 corpus
  documents get an MM/LM period) extracted from the public data of
  [SigLA](https://sigla.phis.me) (Salgarella & Castellan) by our OCaml
  Marshal reader (`parse_sigla.py`).
- Raw third-party source files are **not redistributed** here; run
  `tools/fetch_sources.sh`, `tools/fetch_lbxyz.sh` and
  `tools/fetch_sigla.sh` to obtain them from the pinned upstream commits.

## Reproduce

Python 3.12 (uv), dependencies in `requirements.txt`:

```
uv venv .venv --python 3.12
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
PYTHONIOENCODING=utf-8 PYTHONHASHSEED=0 .venv/Scripts/python.exe validate_pkl.py   # expect 44/3/5/0
bash tools/stress_run.sh    # full battery; expect empty `git status --porcelain`
```

All scripts are seeded (`random.seed(42)`); additionally pin
`PYTHONHASHSEED=0`, otherwise rows with tied scores may print in a
different order (statistics are unaffected — verified by a clean-clone
stress test, report §BE).

## Method in one paragraph

Freeze the corpus; never edit it (additions go through
`corpus_supplement.py`). For every observed regularity, build an explicit
null model (label permutation, positional sign shuffle, subset resampling),
report R and an exploratory p-value, and state honestly whether the effect
survives. Negative results are reported with the same care as positive
ones; two of our own early claims were retracted by later tests (§AF, §BG).

## Citing / contact

Cite as: Zolden & Claude (2026). *Linear A: a reproducible statistical
framework.* v1.4. Zenodo. https://doi.org/10.5281/zenodo.21298882
(concept DOI for all versions: 10.5281/zenodo.21262274) — and please cite
the underlying editions (GORILA; Younger; Douros; lineara.xyz;
Killen & Olivier). Issues and questions: open a GitHub issue.
