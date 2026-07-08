# Structure without Reading: a Reproducible Statistical Framework for Linear A

**Preprint v1.0 — 2026-07-06**
Repository: https://github.com/Zolden/DecipherLinearA — DOI: https://doi.org/10.5281/zenodo.21262275
(Full research log with all intermediate tests: `linear_a_full_report_v2.md`,
sections §0–§BL; every number regenerates under seed=42, PYTHONHASHSEED=0.)

## Abstract

We present a fully reproducible statistical framework for the undeciphered
Linear A script and report five families of permutation-controlled results.
(1) *Value transfer:* signs whose Linear B homomorphs are vowels show a
strong word-initial bias in Linear A (Mann-Whitney AUC=0.91, p=0.0005), and
final-sign alternations on shared stems share their consonant row above
chance (p=0.002 on the wide sample) — internal evidence that Linear B sound
values transfer to Linear A. (2) *Onomastics:* exact Linear A / Linear B
homographs are chance-level for two-sign words but exceed chance by an
order of magnitude for words of three or more signs (p<0.0001 for ≥4);
the excess concentrates in personal-name record slots and toponyms, and
replicates across two independent digitizations of the Linear B corpus.
Six personal-name candidates (da-i-pi-ta, i-ta-ja, ki-da-ro, pa-ra-ne,
ta-na-ti, i-ja-te) join three toponyms (pa-i-to, se-to-i-ja, su-ki-ri-ta)
as anchor words. (3) *Morphology:* suffix -JA and prefix A- survive
family-wise permutation control and replicate across independent archives;
-JA marks the non-administrative register (Fisher p=0.016 within shared
stems). A data-driven inventory of 34 two-sign "bimorphs" (elements attested
both free and bound) exceeds the positional null (19.8±3.6, p<0.001) and
splits cleanly by register. (4) *Document structure:* slot 2 of the
pan-Cretan libation formula is site-specific (p=0.012), with its
Palaikastro cluster (DI-KI-TE stem) coinciding with the later Greek cult
site of Zeus Diktaios; a validated slot-template engine (89% agreement with
expert readings) awaits the newly announced 119-sign Knossos ivory sceptre.
(5) *Metrology and typology:* grain is quantized on a pure binary fraction
grid (1/16, 100% coverage) versus a mixed duodecimal grid for oil and wine
(p=0.021); the word-shape profile of Linear A is incompatible with Greek,
Akkadian, Hurrian and Kartvelian profiles, while remaining candidates are
statistically inseparable. We also document, with equal prominence, the
regularities that failed testing — including the popular short-word
"identical word" lists, which our positional null fully explains.

## 1. Method

**Corpus.** We freeze a validated database of 1721 Linear A inscriptions
(parsed from the open lineara.xyz dataset, after GORILA, Younger and
Douros), with typed tokens (words as sign sequences, numbers as exact
fractions, damage flags). Validation against a hand-checked 52-document
sample: 44 exact, 3 fraction upgrades, 5 documented edition revisions,
0 unresolved. The frozen file is never edited; additions go through a
supplement mechanism. A separate machine-aligned layer records Younger's
underdot (uncertain-reading) marks: 717 marks in 345 documents; key results
are re-run on "reliable readings only" as a robustness check.

**Statistics.** Every claim is tested against an explicit null model:
label permutation, positional sign shuffling (preserving word lengths and
the positional frequencies of signs), or subset resampling; R=10,000
unless stated, seed=42. P-values are exploratory (no multiplicity
shopping); where a family of candidates is scanned, we additionally report
the family-wise "max-statistic" null. Paired and stem-matched designs are
preferred. Negative and retracted results are reported (§AF, §BG of the
research log).

**Comparison corpora.** Linear B: two independent digitizations — a
Wayback-archived scholarly transliteration site (4,275 tablets parsed) and
the open linearb.xyz dataset (5,832 documents; 4,791 word types) — plus
the public LiBER index (5,638 tablets) as a completeness benchmark.
Personal-name *record slots* are extracted structurally (word before
VIR/MUL/livestock/AES logograms; after pa-ro; first word of KN D/B/As/V/Ap
records; word+numeral in name-list series; word before GRA in land series).

## 2. Value transfer from Linear B

Pure-vowel signs (A, E, I, O, U by Linear B homomorphy) are word-initial
in 65.6% of lexicon occurrences versus 25.2% for CV signs (permutation
p=0.0025; AUC=0.91, p=0.0005; robust on tokens and on reliable-only
readings). Final-sign alternations on shared stems (STEM-x ~ STEM-y) share
the consonant row at 14.3% vs ~10% null on the strict morphological sample
(n=35, p≈0.09) and at 11.9% vs 9.4% (p=0.0018) on the wide sample, driven
by R/K/T rows. A leave-one-out calibration of the positional classifier on
known signs reaches 89% accuracy, licensing class verdicts for signs
without Linear B homomorphs: *301, *21F, *118, *49 pattern as CV-like;
*312, *333, *815 as V-like; the *4XX-VS series is identified as vessel
logograms (excluded from phonology). One anomaly is flagged: QA behaves
V-like (log10LR=+2.97) across eight sites.

## 3. The onomastic layer

Reading all fully-preserved Linear A lexicon words (618 types) through
Linear B values and matching them against the full Linear B lexicon yields
45 exact homographs. Stratified by length (positional null): two-sign
matches are at or below chance; three-sign matches are 8 observed vs 2.9
expected (p=0.0086); four-plus-sign matches are 3 vs 0.04 (p<0.0001).
Class-stratified (toponyms / name-series / secure Greek lexicon / other):
the excess sits exclusively in toponyms and name contexts; secure Greek
vocabulary contributes zero long matches. At the strictest level —
record-slot confirmation — six name candidates survive (p<0.0001 on
digitization A; independently re-found on digitization B, p=0.042 with a
narrower slot extractor). Behaviourally, the Knossos-series candidates
appear in Linear A as list entries with small integers (name-like), while
the Pylos-matching words (da-ma-te, i-ja-te, a-ro-te) are number-free and
vessel/stone-bound — a different phenomenon, honestly separated. The
picture "personal names survive, toponyms survive, local cult vocabulary
does not" (slot-2 words show no excess survival, p=0.52) is consistent
with language replacement over a continuous population.

## 4. Morphology without readings

Paradigm support with positional-null calibration identifies suffix -JA
(9 stems, p=0.004, family-wise p_max=0.031) and prefix A- (14 stems,
p=0.002, p_max=0.002); both replicate in independent archive splits, as
does prefix PI-. Functionally, -JA forms of the same stems shift from
tablets to religious stone objects (Fisher p=0.016 / p=0.010); A- has no
detected function yet (all paired tests null) — and A- and -JA never
co-occur on one stem (0/23). A combined prefix+stem+suffix segmentation
finds 199 paradigm stems vs 149.8±7.8 expected (p<0.001). The best
paradigm in the corpus is the theonym-candidate SA-SA-RA: ten forms across
ten sites (A-/JA-/∅ × -ME/-MA-NA/∅ × core variant *802 × one compound).
Thirty-four "bimorphs" (two-sign elements attested both free and inside
longer words) exceed the null (p<0.001); they split by register
(administrative A-DU — heads commodity lists, 0/10 religious contexts;
cultic I-DA — 71% religious, seven sites) and do not concatenate with each
other: Linear A words are [prefix] + core + [suffix], not element chains.

## 5. Document structure: registers, formula, operators

An operator registry quantifies the service vocabulary: TE (58 tokens,
9 sites, 62% headers, almost never with numbers), totals KU-RO /
PO-TO-KU-RO / KI-RO (arithmetic verified; one real anomaly, HT 9a at −3/4,
survives all damage checks), the administrative header operator A-DU and
its cultic mirror I-DA, and the formula finalizer SI-RU-TE (7 tokens,
5 sites, 100% religious, 71% final position) — a cultic mirror of KU-RO.
The pan-Cretan libation formula parses into six slots; slots 3–6 are
invariant across the island, while slot 2 is site-specific (exact-word
Δ=+0.065, p=0.012; stem-level Δ=+0.105, p=0.024). The slot-2 inventory
reads as a gazetteer of local cult designations; its Palaikastro cluster
(A-/JA-DI-KI-TE(-TE) with the productive second element (DU-)PU2-RE)
coincides geographically with the later sanctuary of Zeus Diktaios — the
vowel mismatch with Greek di-ka-ta is stated, not explained away. A
slot-template engine validated at 89% word-level agreement against expert
readings stands ready for the 119-sign Anetaki ivory sceptre (Kanta,
Nakassis, Palaima & Perna 2025), whose ring layout the editors themselves
compare to a libation table.

## 6. Metrology and typology

People are counted in integers (97%); grain values are covered 100% by a
1/16 binary quantum; oil, wine and CYP use a mixed grid (1/12 covers ~95%;
CYP modal value is 1/2); the grain/oil contrast is significant (Fisher
p=0.021). Fraction-sign values agree with the independent "updating note"
reassessment (J=1/2, E=1/4, F=1/8, K=1/16, B=1/5, D=1/3). Typologically —
using Mycenaean Greek in the *same script* as the control — Linear A
differs on all six word-shape metrics (notably final -o: 4% vs 45%) and,
in a crude phonological projection, is measurably unlike Akkadian, Hurrian
and Georgian, while the remaining cluster (Sumerian, Etruscan, Anatolian,
Basque) is not separable at current sample sizes; Etruscan shows a
suggestive final-vowel parallel (o-poor, a-rich) at n=234.

## 7. What did not survive

Short-word Linear A ≡ Linear B lists (including most published
"identical word" collections) are fully explained by the positional null.
The HT 118 "transaction sign" pattern does not generalize (commodity
columns P=0.105; syllabograms P=0.052 with trivial hits). Scribal identity
does not explain spelling variants. An early "complementary distribution"
claim and the site-specificity of the formula opening were retracted after
stricter tests. Substitution tournaments for unknown-sign values are
non-resolving at current corpus sizes (a weak repeated signal: *306
leading normalized row Z on both Linear B digitizations; *118 neighbours
and a single crossword vote converge on row R).

## 8. Reproducibility

A clean-clone stress test (fresh venv, 47 scripts) reproduces every
statistic; with PYTHONHASHSEED=0 pinned, all canonical logs reproduce
byte-for-byte (empty `git diff`). The only nondeterminism ever found —
tie-break ordering under unpinned hash seeds — is documented and fixed in
the run protocol.

## 9. Outlook

Two datasets with known addresses would upgrade the framework from
"structure" toward "partial reading": the full edition of the Anetaki
sceptre (slot engine ready) and a complete curated Linear B corpus with
record contexts (the value tournament and the onomasticon scale directly).
In the best case — all anchors confirmed and extended — we estimate a
realistic ceiling of ~40–60 securely anchored words, several new sign
values, and a grammatically annotated libation formula: the state from
which Linear B's final assault was launched.

## Acknowledgements & data credits

GORILA (Godart & Olivier); J. Younger's Linear A texts; G. Douros's
tabulation; lineara.xyz and linearb.xyz open datasets (R. Mwenge);
Killen & Olivier's Knossos transliterations; LiBER (Del Freo &
Di Filippo); Kanta, Nakassis, Palaima & Perna (Ariadne Suppl. 5). See
DATA_SOURCES.md for the takedown policy. All errors are ours.
