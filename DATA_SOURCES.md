# Data sources, credits and takedown policy

This project stands on the shoulders of the scholars who edited and
digitized the Aegean corpora. Nothing here would exist without them.

## Linear A

- **Editions**: L. Godart & J.-P. Olivier, *Recueil des inscriptions en
  linéaire A* (GORILA I–V); J. G. Younger, *Linear A Texts in phonetic
  transcription* (web edition, with underdot uncertainty marks);
  G. Douros, tabulated Linear A corpus.
- **Digital source**: the open repository
  [mwenge/lineara.xyz](https://github.com/mwenge/lineara.xyz)
  (commit `eb9afc70`, 2025-11-23), which compiles the above.
- **What we ship**: `corpus.pkl` — our parsed, validated and frozen
  research database (typed tokens, numbers as exact fractions, damage
  flags), plus `underdots.tsv`/`underdots_layer.pkl` — our machine
  alignment of Younger's uncertainty marks. These are derived analytical
  databases with our own structure and corrections (documented in the
  report, §0/§A).
- **What we do NOT ship**: verbatim copies of upstream files
  (`LinearAInscriptions.js` → corpus_raw.json, `items_image_map.js`,
  the scraped `commentary/` pages). Run `tools/fetch_sources.sh` to obtain
  them from the pinned upstream commit if you want to rebuild the
  underdot layer from scratch.

## Linear B

- **Editions**: J. T. Killen & J.-P. Olivier, *The Knossos Tablets* (5th
  ed.); E. L. Bennett et al. (Pylos); scholarly transliterations as
  published on minoan.deaditerranean.com (site now offline; pages
  retrieved via the Internet Archive Wayback Machine).
- **What we ship**: `lb_lexicon.tsv` (word-frequency list, 3694 types) and
  `lb_name_slots.tsv` (words in personal-name record slots) — derived
  word-level indexes with per-series attribution.
- `liber_tablets_index.json` — the public tablet index (IDs, sites,
  findspots, dating) of [LiBER](https://liber.cnr.it) (M. Del Freo &
  F. Di Filippo, CNR), saved as a completeness benchmark. Transliterations
  are NOT included.
- `lb2_lexicon.tsv` / `lb2_name_slots.tsv` — word-level indexes derived
  from the open [linearb.xyz](https://github.com/mwenge/linearb.xyz)
  dataset (R. Mwenge), used as an independent second digitization. The
  raw source file is not redistributed; `tools/fetch_lbxyz.sh` restores
  it from the pinned upstream commit.

## SigLA (Linear A palaeography and dating)

- **Source**: [SigLA](https://sigla.phis.me) — *The signs of Linear A: a
  palaeographical database* by Ester Salgarella (text) & Simon Castellan
  (engine). Dataset and drawings are published under **CC BY-NC-SA 4.0**
  (per the SigLA site); our derived metadata index is non-commercial,
  attributed, and shared under compatible terms. The raw data layer
  (`database.js`) is fetched — not redistributed — by
  `tools/fetch_sigla.sh` into a gitignored cache (SHA-256 pinned in the
  script).
- **What we ship**: `sigla_docs.tsv` — a document-level metadata index
  (inscription ID, support type, site, period, source URL) extracted by
  `parse_sigla.py`, used solely to add a dating layer to our corpus.
  Sign tracings and palaeographic content are NOT included. Please cite
  SigLA (Salgarella & Castellan) whenever this layer is used.

## Reference lists

Cretan toponyms and ethnica follow standard Mycenaean scholarship
(Documents in Mycenaean Greek; McArthur). Swadesh comparison lists come
from Wiktionary appendices; Etruscan/Anatolian lemmas from Wiktionary
category APIs; the Pre-Greek substrate sample from the corresponding
Wikipedia article. The Anetaki sceptre facts follow Kanta, Nakassis,
Palaima & Perna, *Ariadne* Suppl. 5 (2024/2025), open access.

## Policy

We believe shipping derived, attributed research databases for
verification purposes is fair scholarly use. If you are a rights holder
of any underlying edition and disagree, open an issue or contact the
maintainer — we will promptly adjust or remove the material in question.
