# Structure without Reading: a Reproducible Statistical Framework for Linear A

**Preprint v1.4 — 2026-07-10** (v1.3: 2026-07-09; v1.2/v1.1: 2026-07-08; v1.0: 2026-07-06)
Repository: https://github.com/Zolden/DecipherLinearA —
DOI (latest release): https://doi.org/10.5281/zenodo.21266454 (all versions: https://doi.org/10.5281/zenodo.21262274)
(Full research log with all intermediate tests: `linear_a_full_report_v2.md`,
sections §0–§DG; every number regenerates under seed=42, PYTHONHASHSEED=0.)
*New in v1.4 — after an independent external audit (report archived as
INPUT_FROM_SOL.md in the research repository):* the V/CV positional test
is confirmed by exhaustive enumeration (p=0.00049) and is our single
headline claim; the onomastic slot result is downgraded to *post-selected
discovery* (slots N6/N7 were added after diagnosing specific misses; the
two Linear B digitizations are overlapping transcriptions of one corpus,
Jaccard 0.652 — the honest pre-adaptation figure is 4 slot hits,
p≈0.0054); the grain-class family claim P=0.0003 is *retracted* (the unit
of independence is the physical tablet, not the tablet side; site-blocked
tablet-level KU-NI-SU gives p≈0.13) — the class stands as a coherent
exploratory grouping only; the second-position results (TE, SA-RA2) are
*admission-rule-sensitive* (family-significant only on the unfiltered
corpus; raw-only under the strict preservation filter), while KU-RO-final
and the formula-initial survive the strictest joint-permutation control
(family p=0.014 / 0.022). A hypotheses registry (`hypotheses.tsv`) now
assigns every main claim a status: CONFIRMED / EXPLORATORY /
POST-SELECTED / RETRACTED / PRE-REGISTERED.
*New in v1.3:* grain-class cascade (§4a — now see the v1.4 downgrades);
genre-dependence of positional openness (religious inversion, p=0.041,
§5); external convergences with the 2026 AURA volume (§7).
*New in v1.2:* three-slot record grammar; SigLA integration (dating
533/534; transcriptions 90%/86%); union onomastics (p=0.0004); the
final-vowel adaptation rule with sensitivity stated.
*New in v1.1:* anchor table; slot replication; operator grammar; *815
withdrawn.

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
replicates across two independent digitizations of the Linear B corpus
(union of digitizations: six slot-confirmed name candidates vs 0.93
expected, p=0.0004). Six personal-name candidates (da-i-pi-ta, i-ta-ja,
ki-da-ro, pa-ra-ne, ta-na-ti, i-ja-te) join three toponyms (pa-i-to,
se-to-i-ja, su-ki-ri-ta) as anchor words; a candidate adaptation rule —
Linear A finals in -u/-e/-a matching Linear B slot-name forms in -o —
survives permutation control in aggregate (p=0.0018). (3) *Morphology:* suffix -JA and prefix A- survive
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
the public LiBER index (5,638 tablets) as a completeness benchmark. For
Linear A itself we additionally unpacked the public data layer of the
SigLA palaeographic database (Salgarella & Castellan): 748 documents with
support type, site and period, and a sign-level layer (451 documents,
3,174 sign instances), via a purpose-built reader for its serialization
format.
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
*312 and *333 as V-like (a third V-like candidate, *815, was withdrawn in
v1.1: a concentration audit found all its occurrences in a single document,
so its profile may be one scribe's habit); the *4XX-VS series is identified
as vessel logograms (excluded from phonology). One anomaly is flagged: QA behaves
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
record-slot confirmation — six name candidates are slot-confirmed on the
union of our two Linear B transcription sources (6 vs 0.93 expected,
p=0.0004). *v1.4 status (audit): post-selected discovery.* Two of the
slot rules (N6/N7) were added after diagnosing specific missed candidates,
and the two sources are overlapping transcriptions of the same underlying
corpus (Jaccard 0.652), not independent archives; the honest
pre-adaptation figure is four slot-confirmed candidates at p≈0.0054. A
confirmatory version requires a held-out curated corpus (a DĀMOS export
is being requested). A consolidated anchor table (`anchors.tsv`) lists
all 11 anchor words with the full evidence chain and these caveats.

Beyond exact homographs, a *final-vowel adaptation rule* emerges: Linear A
words whose final sign changes only its vowel (same consonant row) match
Linear B slot-names 16 times vs 6.7 expected (p=0.0018), and 11 of the 16
variants end in Linear B -o (family-controlled over the five target
vowels, p=0.0147): di-de-ru ~ di-de-ro, qa-qa-ru ~ qa-qa-ro, pa-ja-re ~
pa-ja-ro, se-to-i-ja ~ se-to-i-jo, su-ki-ri-ta ~ su-ki-ri-to, etc. —
consistent with thematic (-o-stem) adaptation of Minoan names in Greek
administration. Two honest caveats: under a stricter exclusion regime the
name-stratum enrichment is borderline (9 vs 4.9, p=0.059) and the
names-vs-lexicon contrast is not significant (p=0.23); and final vowels
also alternate *within* Linear A (five internal pairs vs 1.75 expected,
p=0.037, e.g. ta-na-te ~ ta-na-ti), with a scattered vowel inventory —
which supports the adaptation reading of the -o pattern but shows the
final slot is not inert inside Minoan either.

## 4a. A commodity-word class through cascaded arbiters (downgraded in v1.4)

*v1.4 note (audit):* the family-wise claim below (P=0.0003) is retracted —
its hypergeometric unit was the tablet *side*, while HT 86a/b and HT 95a/b
are sides of two physical tablets, and all KU-NI-SU documents are from one
site; at the physical-tablet level with site blocking KU-NI-SU gives
p≈0.13, and the individually surviving items share the same tablets and
were data-selected. The class below therefore stands as a *coherent
exploratory grouping* (areal-word phonetics + list microstructure + clean
metrology), awaiting confirmation on new tablets.

Porting an areal-lexicon probe developed in our Etruscan sibling project
(230 Bronze-Age concepts × 7 deciphered languages; sound-class skeleton
matching), and replacing its gloss calibration — impossible for Linear A —
with a *distributional arbiter* (a commodity-domain candidate must
co-occur with its commodity logogram), yields a coherent grain class. The
pre-declared first test passed: KU-NI-SU matches Akkadian *kunāšu*
("emmer") skeleton-exactly, and its five documents carry the GRA logogram
three times vs 0.65 expected (p=0.015; wine-logogram control 0/5).
Exploratively, KI-RI-TA₂ (~ *krithē* "barley", GRA 2/2, p=0.0175) and
KI-RE-TA-NA (GRA 2/3, p=0.048) join it; family-wise, the probability of
three significant hits among twenty commodity checks *all landing in the
grain domain* is 0.0003. Two further arbiters agree: the numeral
environment of all four candidates is purely integer/binary (0% duodecimal
admixture, vs 5% in the GRA-document baseline and 9% in the oil baseline),
and tablet HT 86a shows the candidates as parallel list entries, each with
its own round number under GRA+ligature headings. Both roots are
long-standing loanword conjectures in the literature; the pipeline
reproduced them blind. Honest boundaries: the remaining list vocabulary of
HT 86/95 passes the same arbiter but on overlapping documents (a coherent
class, not independent confirmations); non-commodity domains fail their
arbiters (no positional or register concentration) — on Linear A the probe
works only where a material anchor (logograms, measures) exists. No row is
a translation; the claim is class membership. Behaviourally, the Knossos-series candidates
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

The operator vocabulary also has a *positional grammar*. Testing each
operator against a uniform within-document position null (367 documents
with ≥2 words; Westfall–Young family-wise control over 16 tests): the
total KU-RO is final far above chance (39% vs 8% initial, family-adjusted
p=0.008), while the header operator A-DU (67% initial, p=0.005) and the
libation-formula opening A-TA-I-*301-WA-JA (100% initial, p=0.0001) are
initial. The same polarity — deictic/header elements initial, predicate-like
elements final — was independently found in Etruscan by our sibling project
(github.com/Zolden/DecipherEtruscan), where the hypothesis originated;
Linear A confirmed it out-of-sample. Two honest nuances: TE is *not*
document-initial (it tags the word it follows), and KI-RO ("deficit"),
unlike KU-RO, shows no positional preference — consistent with a line-level
annotation rather than a closing total.

Extending the test to second and penultimate positions resolves the TE
nuance and suggests a three-slot record grammar: TE sits in *second*
position (54%), as does the account term SA-RA2 (56%; never first, never
last), while KU-RO occupies the closing block (69% of tokens in the last
two positions). *v1.4 status (audit):* under a single strict preservation
filter and a joint document-permutation null, the robust core is KU-RO
final (family p=0.014) and the formula opening initial (p=0.022); the
second-position excesses of TE and SA-RA2 are admission-rule-sensitive —
family-significant on the unfiltered corpus (p=0.007/0.004) but raw-only
under the strict filter (raw p=0.026/0.015, family ≈0.30/0.16) — and are
reported as raw signals. First position, by contrast, has an *open*
vocabulary: first-word repetition across documents is at chance (p=0.76),
and the words heading TE/SA-RA2 records split into commodity logograms
(SI, NI) and name-like hapaxes. The resulting schema —
[open topic] [second-position operator] … [closing total block] —
again has an Etruscan echo (turce "dedicated": 52% second position,
family-adjusted p=0.004, found there after our frame predicted it).
Genre modulates the schema: in the religious genre the polarity inverts
(the libation formula monopolizes first position while second position is
fully open — TTR Δ=−0.182, p=0.041, vs +0.075 in the administrative
genre), matching the genre-dependence independently found in Etruscan —
"slot openness" is a property of document genre, not of the language.

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

## 7. External validation layers

Unpacking SigLA's public data yielded two independent checks of our own
foundations. First, *dating*: SigLA carries per-document periods (726 of
748 documents), and the lineara.xyz source data carries a parallel
`context` field (1,388 of 1,721) — the two layers agree on the epoch
(MM vs LM) in 533 of 534 shared documents, with one conflict (KN Zf 13)
and 16 phase-level differences. A first diachronic test is nevertheless
blocked by the data themselves: period is almost functionally confounded
with site (Phaistos/Mallia = MM, Haghia Triada/Khania/Zakros = LM IB), so
no within-site contrast exists yet. Second, *transcriptions*: SigLA's
sign-level tracings, converted to our sign names, agree with our corpus on
90% of SigLA words and 84% of corpus words across 310 shared documents;
of 41 one-sign divergences checked against the raw source, all 41 confirm
our pipeline is faithful (two apparent failures were gloss renderings in
the source) — the residue is genuine editorial disagreement between the
GORILA line and the tracing line (systematically: QI vs *21F, and PA3
confused with JA/NU), catalogued in `divergences.tsv` for epigraphic
adjudication. A consolidated per-document dating layer (`dating.tsv`,
1,540 of 1,721 documents) merges both sources.

The 2026 AURA volume (*The Wor(l)ds of Linear A*, ASASA(RAME) 1) supplies
external convergences: Hogan's expert transaction classification of the
tablets (Entity/Transfer Lists) is the qualitative counterpart of our
record grammar, and of our six slot-confirmed name candidates five appear
in his machine-readable annotation — all five carrying his independently
assigned agent roles; Davis's survey reaches our morphotactic conclusion
(Minoan uses both prefixes and suffixes) on separate evidence, and his
index contains our internal alternation pair A-MI-DA-O/A-MI-DA-U.

## 8. What did not survive

Short-word Linear A ≡ Linear B lists (including most published
"identical word" collections) are fully explained by the positional null.
The HT 118 "transaction sign" pattern does not generalize (commodity
columns P=0.105; syllabograms P=0.052 with trivial hits). Scribal identity
does not explain spelling variants. An early "complementary distribution"
claim and the site-specificity of the formula opening were retracted after
stricter tests; the V-like verdict for the rare sign *815 was withdrawn in
v1.1 after a concentration audit (all occurrences in one document — a
lesson imported from the Etruscan sibling project, where a "special
grapheme" turned out to be a single monument's habit). Further honest
negatives from v1.2: the name-slot target does not constrain any unknown
sign (zero crossword hits even with the adaptation-rule-extended target),
and the weak Z-row candidacy of *306 is now contradicted by a weak
vowel-row vote from the name channel — its confidence is downgraded; a
suffix-pair complementarity test that separates stem classes in Etruscan
hits a power wall at Linear A's lexicon size (618 types); the
pre-declared a→o form of the adaptation rule was not confirmed — the
aggregate toward -o carries the signal; site-level "favourite finals"
vanish once operators are excluded (they were operator geography); and
the areal-lexicon probe fails outside commodity domains (ritual-domain
candidates show no register concentration; no action-domain candidate has
enough tokens) — its verdicts are confined to where material arbiters
exist. Substitution tournaments for unknown-sign values are
non-resolving at current corpus sizes (a weak repeated signal: *306
leading normalized row Z on both Linear B digitizations; *118 neighbours
and a single crossword vote converge on row R).

## 9. Reproducibility

A clean-clone stress test (fresh venv) reproduces every statistic; the
runner covers 85 script runs, with network-cache-dependent parsers listed
as deliberate exclusions in its header (their committed outputs are
regenerated deterministically from pinned caches). Following the external
audit, the pass criterion is an empty `git status --porcelain` (catching
new files as well as modified ones), and log writes are atomic
(temp-file + rename). With PYTHONHASHSEED=0 pinned, all canonical logs
reproduce byte-for-byte. Third-party inputs are not redistributed; pinned
fetch scripts (`tools/fetch_sources.sh`, `tools/fetch_lbxyz.sh`,
`tools/fetch_sigla.sh`) restore them byte-identically from upstream
commits (the SigLA fetch pins a SHA-256). A hypotheses registry
(`hypotheses.tsv`) tracks family, unit of observation, null universe,
selection history and current status for every main claim.

## 10. Outlook

Two datasets with known addresses would upgrade the framework from
"structure" toward "partial reading": the full edition of the Anetaki
sceptre (slot engine ready) and a complete curated Linear B corpus with
record contexts (the value tournament and the onomasticon scale directly);
inquiries to the Anetaki editors, the LiBER team and the SigLA authors
are out.
The SigLA integration performed for v1.2 shows the pattern such upgrades
follow: an external layer first cross-validates the foundations
(transcriptions, dating), then adds a new dimension of structure. The
divergence catalogue (QI/*21F, PA3) is a concrete, finite list an
epigrapher could adjudicate; the adaptation rule (-u/-e/-a ↔ -o) is a
concrete, finite prediction the Anetaki edition could test on fresh names.
In the best case — all anchors confirmed and extended — we estimate a
realistic ceiling of ~40–60 securely anchored words, several new sign
values, and a grammatically annotated libation formula: the state from
which Linear B's final assault was launched.

## Acknowledgements & data credits

GORILA (Godart & Olivier); J. Younger's Linear A texts; G. Douros's
tabulation; lineara.xyz and linearb.xyz open datasets (R. Mwenge);
Killen & Olivier's Knossos transliterations; LiBER (Del Freo &
Di Filippo); SigLA (Salgarella & Castellan); Kanta, Nakassis, Palaima &
Perna (Ariadne Suppl. 5). See DATA_SOURCES.md for the takedown policy.
All errors are ours.
