# Counting What No One Can Read
### Notes from an open statistical investigation of Linear A

A century ago, clay tablets with two related scripts were found on Crete.
One — Linear B — was deciphered in 1952 and turned out to be the oldest
written Greek. The other — Linear A, the script of the Minoans who built
the palaces of Knossos fifteen centuries before Homer — remains
undeciphered. There is simply too little of it: every Linear A inscription
in the world would fit on about ten pages. And there is no Rosetta Stone.

So we took a different route: don't guess what words mean — **count**.
Test every apparent regularity against a simple question: *could this have
happened by chance?* — and answer it with an honest computational
experiment, shuffling signs thousands of times to see how often randomness
fakes the same pattern. Here is what came out.

**1. The Minoan "keyboard" is tuned correctly.** Linear A signs look like
Linear B signs, but for a century no one could prove they *sounded* the
same. We tested it from the inside, three independent ways. Vowel-signs
behave like vowels should in such a script (they cluster at word
beginnings). Word endings alternate keeping the consonant and swapping the
vowel — grammar, not chance. And if you read Linear A words with Linear B
values, Cretan town names emerge from the tablets. Chance would produce a
fraction of one such match; we observe them in excess with p < 0.001.

**2. Three Minoan words can be placed on a map.** PA-I-TO is Phaistos —
it appears in the account lists of Hagia Triada, the "accounting office"
of the Phaistos palace. SU-KI-RI-TA is Sybrita, stamped on a clay sealing
from Phaistos. SE-TO-I-JA is a town the Greeks later mentioned in their
own tablets; our stone with this word was found near Knossos.

**3. Minoan personal names hide inside Greek archives.** Greeks took over
Crete around 1450 BCE — but the people stayed. Comparing the two corpora
we found that short word matches are a statistical mirage (exactly as many
as chance predicts — which disqualifies most "identical word" lists
circulating online), while **long words match ten times more often than
chance**, and almost all of them sit in name slots of Greek records:
shepherds, workers, landholders. DA-I-PI-TA, for example, is written twice
in Minoan Zakros — and once, three centuries later, in a list of men at
Knossos. Six such names are now confirmed at the strictest level
(p < 0.0001).

**4. The language has its first confirmed grammar.** Not meanings —
functions. The suffix **-JA** moves a word from account books to sacred
stone vessels (the non-administrative register). The prefix **A-** is the
most robust marker in the language (family-wise p = 0.002), though its
function still escapes us. The two markers never combine on the same stem
— the language has rules we can see without understanding them.

**5. A "geography slot" was found in the Minoan libation prayer.** Stone
offering tables across Crete carry one six-part formula. Five parts are
identical everywhere. The second slot varies — and stones from the same
sanctuary share its words (p = 0.012). At Palaikastro that slot holds a
family of words on the stem DI-KI-TE — and Palaikastro is precisely where
Greeks later worshipped Zeus *Diktaios* for a thousand years. We found the
match between cult place and cult word purely statistically, without
reading a single line.

**6. Minoan bookkeeping is cracked — at least its arithmetic.** People are
counted in whole units (97% integers — a sanity check that our method
works). Grain divides only by halves down to 1/16 — a binary grid, like
ounces. Oil and wine use twelfths and forty-eighths — like dozens.
Different goods, different measuring systems, exactly like historical dry
vs liquid measures. If the Minoan unit matched the later Greek one, the
minimal grain portion was about 6 litres.

**7. We caught a scribe's error from 3,600 years ago.** On tablet HT 9a
the total misses the sum of entries by ¾. We checked every epigraphically
uncertain sign on the tablet: all clean. Every other mismatch in the
corpus is explained by damage — this one is not. Either the scribe erred,
or the document has a rule we don't yet understand.

**8. The Minoan language is definitively not Greek — now shown with
numbers.** The trick: Greek Linear B uses the same script, so any
difference is language, not writing. Greek words end in -o 45% of the
time; Minoan words — 4%. Minoan words are shorter, start with vowels less
often, and double their syllables twice as often (QA-QA-RU, SA-SA-RA).
What *is* it related to? The honest answer: measurably NOT Akkadian, NOT
Hurrian, NOT Kartvelian; the remaining candidates (Etruscan, Anatolian,
isolates) cannot be separated at current sample sizes — and anyone who
tells you otherwise is selling more than they know.

**9. We probably know the name of a Minoan goddess — and can watch it
decline.** The word (J)A-SA-SA-RA-ME appears on sacred stones across
Crete: ten distinct forms on ten sites — with prefixes A-/JA-, with tails
-ME/-MA-NA or bare, inside a longer compound from Poros. We cannot
translate it. But we can see the paradigm — like watching an unknown
language inflect "Madonna" across its cases.

**10. A first inventory of Minoan word-elements exists.** Thirty-four
two-sign elements live both as independent words and inside longer ones —
against ~20 expected by chance. They split neatly by register: A-DU heads
commodity lists (never on cult objects), I-DA lives on offering stones
across seven sites. This is what the building blocks of a language look
like before you can pronounce their meanings.

**11. The story is entering a new act.** In 2024 archaeologists published
the find of an ivory sceptre from Knossos carrying ~119 signs — the
longest Linear A text ever. The editors themselves compare its circular
layout to the libation-table formula we have already mapped slot by slot.
Our "slot engine" is validated (89% agreement with expert readings) and
waiting: the day the full transliteration appears, it runs in minutes.
Everything in this project — code, data tables, and every negative
result — is open and re-runs from scratch to the byte.

**12. Update (July 2026): the record turned out to have a syntax, and the
names a translation rule.** A new battery of tests showed that a Minoan
administrative record is a three-part formula: the first word says "of
whom or of what" (different nearly every time — a name or a commodity),
the second is a service tag from a closed list (TE or SA-RA2: 54–56% of
their occurrences sit exactly in second position, which chance does not
do), and the end belongs to the totals block with KU-RO. The very same
logic — "pointer, second-position particle, predicate at the end" — was
found independently in Etruscan inscriptions by our sibling project: two
unread languages, two scripts, one grammar of the document; and the
"openness" of the first slot proved to be a property of the *genre*, not
the language — a prediction that then held on the Minoan side too.
Comparing with the Mycenaean archives yielded a candidate "translation
rule" for Minoan names entering Greek records: Minoan finals in -u/-e/-a
correspond to Greek -o — the way Greek would later refit foreign names
with -os. And all our readings are now cross-checked against the
independent palaeographic database SigLA: 90% of words match sign for
sign, and the short list of divergences is published for the epigraphers
to settle.

**13. Second update: stress-tested.** The project went through an
independent audit by a different AI system — the best thing that ever
happened to it. The audit confirmed the headline result (vowels behave
like vowels — now recomputed by exhaustively enumerating all 2.9 million
permutations) but demanded the retraction of one loud family-wise
p-value (we had counted the two sides of one clay tablet as independent
documents) and downgraded a couple more. The answer became a new ritual:
freeze the hypothesis in a public commit BEFORE touching the data, run
once, publish whatever comes out. The first such test — on the
independent curated corpus of Mycenaean tablets, DĀMOS — confirmed the
name layer: six Minoan words sit in the name positions of Greek archives
where 0.7 were expected (p=0.0002), robust across three different null
models. The second pre-registered test failed and is published as
failed; the third passed (words on round sealings repeat across
sealings, exactly as names should). This is what honest statistics of a
dead language looks like: a registry of hypotheses with statuses instead
of a collection of lucky p-values.

The fourth frozen test passed too — and opened an unexpected door. In
the sheep ledgers of Knossos (already-readable Linear B, our proving
ground) the first word of a record rarely repeats across tablets while
the second repeats constantly: the shepherd is unique, the "curator" and
the place come from a short list. When we sorted the repeating first
words, seven of the top ten turned out to be the famous "collectors" of
Mycenaean scholarship — a class philologists took decades to establish.
Pure repetition statistics, knowing not a single meaning, rediscovered
it blind. The same profile on the Minoan tablets yields four
curator-class candidates at Haghia Triada — we still refuse to read
them, but the class is mapped. The source itself also survived an
external check: another GitHub user independently ran an arithmetic
audit of the corpus website and found silent number corrections; not one
of our headlines was touched — the anomalous tablet HT9a stays anomalous
under either reading of its total, and our parser, which reads numbers
from the glyphs, never inherited the site's display bug. Nine genres
across three traditions — Minoan, Mycenaean, Etruscan — now sit in one
table under one metric: the openness of the first position turns out to
be a property of the document's genre, not of its language.

Then the pipeline showed its character. The fifth frozen test failed —
instructively: we had compared word repetition across two series of very
different sizes, and repetition share grows with document count; the
design was crooked, and we said so in print. The sixth test — the same
question with document counts matched — passed with room to spare
(p=0.0044): the recipients of Knossos offering-oil repeat month after
month; the rite is cyclical, just like the Etruscan linen book in our
sibling project. Two failures out of six, both converted into passes by
honest error analysis — that is what a living method's scoreboard should
look like. And tablet arithmetic turned out to be three-storied: line →
section subtotal (KI-RO opens a "one each" census of persons, exact in
all three intact documents) → the grand total PO-TO-KU-RO, which folds
both faces of the clay tablet into one number (31+1+65=97, exactly).
The scribes counted in physical tablets — precisely the unit the audit
forced on us.

The moral: deciphering a dead script is not a lightning bolt of genius but
bookkeeping — thousands of small checks, nine out of ten returning an
honest "no". The remaining "yes"es accumulate. A century ago Linear A "could
not be read". Today it can be read aloud — but not yet understood. As
Ventris showed with Linear B, that is exactly the second-to-last step.

*All computations are reproducible: the corpus of 1721 inscriptions
(lineara.xyz, after GORILA and Younger), fixed random seeds, permutation
null models throughout. No translations were used or produced.*
