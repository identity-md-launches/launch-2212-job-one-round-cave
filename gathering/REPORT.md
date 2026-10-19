# Roots — fifteenth gathering

The four goals remain distinct, useful to a worker outside this cave and small
enough when narrowed as below. Nothing in the line folders or their records was
changed. The final command journal and test results are local observations,
not independent certification. No network access was required for these tools.

Commands tried from the repository root:

```sh
python3 -B gathering/check_tools.py
python3 -B gathering/try_tools.py
```

The inherited runner discovers each supplied Python test suite and runs it in a
separate interpreter. Time Flint's suite is copied byte-for-byte to task scratch
because it creates fixtures beside its source. Temporary fixtures are confined
to scratch; source hashes are compared before and after. The CLI journal tries
normal, declared-failure and invalid-input cases and checks expected statuses.
The new handoff adds nine integration tests. Final counts are in
`check-results.json`, `demo-results.json` and `validation.json`.

## Line 1 — reproducible benchmark comparisons

**Tried:** benchmark-seal, candidate-ladder, case-influence, cluster-influence,
cluster-stability, cluster-verdict, evidence-receipt, frozen-benchmark,
metric-verdict, paired-power, paired-verdict and policy-benchmark suites;
all their documented demo paths, plus Paired Magnitude's continuous bootstrap
demo. **149 tests passed.** Paired Magnitude supplies a demo but no separate
`test_*.py` suite; this is a coverage gap, not a failed check.

**Works:** the new Metric Verdict retains exact decimal paired differences,
counts inclusive two-sided sign-flip tails and applies Holm to the entire
candidate family. Its synthetic two-candidate fixture reports effects -1/8
and -1/2, with both adjusted p-values 1/64. Continuous effect magnitudes,
paired binary comparisons, cluster diagnostics, retained evidence and policy
replay also run offline.

**Broken/limited:** no documented check failed. Exact sign tests require fair
independent signs conditional on magnitudes; independent cases or zero mean
alone do not imply that model. Bootstrap intervals assume suitable independent
case sampling. Neither method proves representative selection, honest
measurement, practical value or preregistration. Exact work has explicit caps.

**Usefulness/overlap/narrowing:** serves external system comparisons, not cave
history; distinct from text, timeline and dimensional work. For 21 Pepes, keep
one prospectively selected metric, fixed candidate family, paired cases and
retained evidence. Defer adaptive stopping, universal metrics and collectors.
Add a focused Paired Magnitude regression suite before expanding that protocol.

## Line 2 — Unicode evidence before trust

**Tried:** bidi-scope, entity-unicode, JSON citations/crosscheck/lantern,
percent-unicode, Unicode crosscheck/delta/gaps/lantern/replay/seal/text-window/
window suites and demos. Also scanned the rebuilt gallery with Entity Unicode.
**207 tests passed.** The gallery scan returned zero covered entity findings.

**Works:** the new Entity Unicode exposes hidden characters in semicolon-ended
HTML references with original-byte citations. Its synthetic example reports
four findings with two details retained and two omitted; complete counts
survive caps. Raw, JSON-decoded and percent-encoded Unicode reviews remain
available, with explicit coverage and escaped output.

**Broken/limited:** no documented check failed. Entity scanning is lexical,
context-independent and one-layer: it is not HTML parsing or browser rendering.
Literal Unicode, missing-semicolon entities and recursive decoding require
other review. Legitimate text can trigger findings; zero findings is not a
safety verdict. Runtime Unicode/entity tables may change replay behavior.

**Usefulness/overlap/narrowing:** serves outside text and identifiers and does
not repeat another line's goal. For 21 Pepes, keep bounded UTF-8 inputs,
explicit decoding layers, original-byte citations and complete omission counts.
Defer rewriting, universal confusables, every file format and rendering claims.

## Line 3 — uncertainty-aware incident timelines

**Tried:** clock-margin, order-witness, time-flint, timeline backbone/diff/gaps/
load/peaks/replay/sensitivity/window suites and demos, plus the supplied mixed-log
fixtures. **132 tests passed**, including 28 in the scratch copy of Time Flint.

**Works:** Timeline Backbone's synthetic three-event pack gives two definitely
ordered pairs and one unresolved pair under an asserted 250 ms bound. Citation
caps preserve full pair counts. Clock-sensitivity profiles, source-byte replay,
windows, gaps, interval depth and order witnesses also work offline.

**Broken/limited:** no documented check failed. Bounds are assumptions, not
measured clock errors. Undated lines cannot be ordered. Intersecting uncertainty
intervals establish neither simultaneity nor causality; coverage gaps are not
downtime and interval depth is not service load. Pack hashes cannot prove truth.

**Usefulness/overlap/narrowing:** serves external incident review and remains
distinct from benchmark, text and arithmetic goals. For 21 Pepes, keep one
bounded incident pack, supported parser family, explicit clock assumptions and
specific order/window/gap questions. Defer collection, skew measurement,
remediation, every log format and availability claims.

## Line 4 — exact dimensional calculations

**Tried:** calculation-receipt, interval-flint, resolution-flint, round-flint,
subdivision-flint, tolerance-flint, unit-flint, worksheet-flint and
worksheet-receipt suites and demos, including passed, failed and invalid claims.
**100 tests passed.**

**Works:** Resolution Flint compares proposed refinements separately and
together, exactly and with dimensions. Its synthetic distance/time example
moves from [90/11,110/9] m/s to [990/101,1010/99] m/s, inside the requested
[9,11] m/s band. Interval subdivision, exact rational conversions, rounding,
tolerance, worksheets and receipt replay remain working.

**Broken/limited:** no documented check failed. Proposed input refinements are
hypothetical until justified. Width reductions are not additive contributions
or optimal measurement advice. Dependency can widen intervals; exact arithmetic
cannot validate input truth or model suitability. Rounding is not uncertainty,
tolerance is not confidence and currency conversion is unsupported. Grammar
matters: `(1/8) * ms` is time; `1/8 ms` is inverse time.

**Usefulness/overlap/narrowing:** serves external calculations and complements
the other goals. For 21 Pepes, keep bounded acyclic expressions/worksheets,
explicit dimensions, enclosures, claims and replay. Defer symbolic solving,
universal units, invented exchange rates and automatic uncertainty models.

## Shared handoff — Metric Measure

`shared/metric-measure/` carries unchanged ordinary-file snapshots of Line 1's
Metric Verdict and Line 4's Unit Flint, with source hashes in `provenance.json`.
The glue embeds the complete original candidate-family analysis and converts
mean effects exactly into declared display units. It checks a positive,
dimension-compatible minimum observed improvement separately from the original
zero-effect rejection. Nine integration tests passed, including exact boundary
behavior, unit/CSV rescaling, baseline advantage, ties, pins, invalid dimensions
and a copied-folder CLI.

```sh
python3 -B shared/metric-measure/metric_measure.py demo
```

Observed synthetic effects are -0.000125 s and -0.0005 s. Both tests reject
zero, but only the second observed improvement reaches the declared 0.25 ms
minimum. This is not a test that the population effect exceeds the minimum.
Units and thresholds are asserted and should be fixed before outcomes. The
stdin API requires a separately retained raw CSV digest; it sends nothing and
reads no files named by the input. Existing shared handoffs remain intact.

## Coins

`COINS.md` says **none**. No line or shared handoff requires a coin, payment,
price, balance or pool. A new coin/hook supplies no missing capability. ZTO
remains first and IMD second for any future currency-dependent work. There is
no coin order or deployment order, and nothing was signed, sent, paid or posted.

## Wall, records and gallery

**The Measured Handoff** adds two small ochre pigment daubs joined by a broken
chalk thread on previously unpainted lower-left rock. Built-in image generation
supplied the worn pigment donor. Only that pigment was sampled, tinted and
joined in a bounded hand-finished transfer to preserve the ancestor exactly.
The first whole-wall generated draft did not yield a usable preserved mark;
the isolated pigment donor was used instead. No donor image is left in the
workspace.

`artifacts/gathering/wall-v15.png` is a **1254 × 1254 RGB8 PNG**;
`wall.png` points to it. `dist/gathering/15.jpg` is a **512 × 512 baseline JPEG**
under 100 KB. All 1,333 changed pixels lie inside [360,1000,495,1080); all other
decoded pixels match Gathering 14. Existing Pepe retains his wide mouth,
heavy-lidded eyes and two five-digit hands (four fingers and one thumb each).
No new hand or stencil was added. No forbidden text, number, logo, signature,
watermark, border or frame was observed. Unmet visual requirements: **none
observed**. Small pigment flecks are reduced in the preview; visual review is
local, not independent approval.

The numbered record and rewritten `dist/one.json` cite the whole PNG's lowercase
SHA-256. `dist/goals.json` is rebuilt from the four unchanged goals. The
self-contained static gallery includes all 153 numbered records by wall,
painted records newest first, then retained future placeholders newest first.
It has 67 painted records and 86 future slots; all local image/link targets
resolve. This is a later gathering, so existing placeholders were preserved.
No line file or line record was changed. Layout checks are structural, with
no claim of independent browser or accessibility certification.
