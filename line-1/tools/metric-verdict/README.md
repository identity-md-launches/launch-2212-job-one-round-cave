# Metric Verdict

Compare a declared family of candidates with a baseline on **one continuous
metric**, using exact paired sign-flip tests and Holm correction. This adds an
inferential companion to Paired Magnitude's bootstrap effect estimates. Metric
Verdict preserves decimal observations exactly, reports mean effects as rational
numbers, and never substitutes rounded weights or a sampled p-value.

Python 3.9+, standard library only. Copy this whole folder for offline use.
From the repository root, one command shows it working:

```sh
python3 -B line-1/tools/metric-verdict/metric_verdict.py --demo
```

When tried, this explicitly **synthetic** eight-case latency fixture gave mean
candidate-minus-baseline differences of **-1/8** and **-1/2** units. Both raw
p-values were **1/128**, both Holm-adjusted p-values **1/64**, and both rejected
with the candidate ahead at alpha 0.05. The identical p-values despite different
effects illustrate why statistical evidence and practical value are separate.
No real system performance was measured. `example.csv` contains those exact
fixture bytes, and `example-result.json` retains the actual demo output.

## Supply observations

CSV must have `case,baseline` followed by 1–16 distinct candidate names. Every
case has one complete paired observation of each candidate and the baseline.
Use one predeclared metric and the same units in every column. For example:

```csv
case,baseline,system-a,system-b
query-a,12.125,11.750,12.500
query-b,8.000,7.625,8.250
```

Freeze the measurement procedure, case set, metric, direction, entire candidate
family, alpha and analysis before inspecting outcomes. Independently retain the
raw CSV SHA-256 when handing the file to an analyst; a digest calculated from
an already received file only checks subsequent byte consistency. The supplied
fixture can be analyzed with its retained digest:

```sh
python3 -B line-1/tools/metric-verdict/metric_verdict.py --input line-1/tools/metric-verdict/example.csv --expected-input-sha256 c73d90bcb4d8be69932d604c2a78e738cb3d99c0f26e80b77ad166847acd6b44 --better lower --alpha 0.05
```

Replace the path and digest together for real observations. `--better lower`
(the default) or `--better higher` changes direction interpretation only; the
test stays two-sided. Alpha accepts plain decimals from 0.000001 to 0.2,
inclusive, with at most six decimal places. The full supplied family enters
Holm, including tied, losing and non-rejecting candidates. Separate invocations
on selected candidates do not provide the same familywise guarantee.

Inputs are UTF-8 CSV with optional BOM, quoted fields and CRLF. There must be
2–200 unique case IDs and no blank, missing or extra rows/fields. Labels have
1–200 characters, no edge whitespace and no Unicode control, format, surrogate,
private-use or unassigned characters. Header names must all be distinct.
Measurements use signed plain decimals with at most six fractional digits,
absolute value at most 1000000000, no exponent notation, whitespace, NaN,
infinity, separators or leading integer zeroes (except zero itself).

Files are limited to 2 MiB and must resolve to regular files inside the current
working directory. Symlinks escaping it are refused. The required lowercase
64-digit SHA-256 pin checks exact raw bytes, including BOM and line endings.
The tool reads only the supplied input, changes no input, and writes JSON only
to stdout. Output uses ASCII-escaped labels; render them with normal JSON/HTML
escaping. Exit 0 means analysis completed, including non-rejection or a baseline
advantage; exit 2 means invalid input, pin or budget, with no partial stdout.

## Exact calculation and its limits

For each candidate let `d_i = candidate_i - baseline_i`. Under that candidate's
null, assume nonzero differences have **independent fair signs conditional on
their magnitudes**. This can follow from justified independent within-pair
randomized swaps under a sharp null, or a sign-symmetric independent difference
model. Independent cases, zero expected difference, or the mere existence of a
paired CSV do not imply that model. Repeated measurements of related cases
cannot be treated as independent signs just by giving them separate IDs.

The statistic is `abs(sum(d_i))`; a fixed case count makes this equivalent to
an absolute mean. Include assignments at least as extreme as observed, including
equality. Zero differences add no sign information. All-zero vectors yield
p = 1. Parse observations as integer millionths, divide each candidate's integer
difference vector by its nonzero absolute GCD, and build the subset-sum counts
for `product(1 + x**abs(d_i))`. For subset sum `s`, the sign sum is `S - 2*s`
where `S = sum(abs(d_i))`. Count the inclusive two-sided tail and divide by
`2**nonzero_pairs`. GCD reduction loses no precision. JSON retains unreduced
assignment counts as well as reduced p-value fractions and exact mean effects.

To keep computation bounded, reject if a candidate's GCD-reduced absolute sum
exceeds 20000, or `nonzero_pairs * (reduced_absolute_sum + 1)` exceeds 2000000.
Every candidate must fit. These limits are checked before allocating its count
array. There is no automatic rounding, dropped case, dropped candidate or
sampling fallback. Choose measurement precision prospectively; changing it to
make observed results fit creates a new analysis. Commonly scaled or quantized
measurements can fit even when their original values are large.

Sort raw p-values across the full family, multiply the jth by the number of
remaining tests, take cumulative maxima and cap at one. Compare these exact
Holm-adjusted fractions to the exact alpha, including equality. Holm controls
familywise error under arbitrary dependence between candidate tests provided
each candidate's raw p-value is valid under its null; it cannot repair a failed
sign assumption, selected family or repeated looks.

Two-sided rejection may favor the baseline. `reject_with_candidate_ahead`
requires both rejection and a favorable mean direction. A small p-value is not
a useful effect threshold. Non-rejection is not equivalence. The tool provides
no confidence interval, cluster adjustment, representative-sampling guarantee,
measurement verification, execution certificate or preregistration timestamp.
The bootstrap and binary tools remain unchanged; this is a distinct protocol
whose assumptions must fit the question.

## Checks and reuse

```sh
python3 -B -m unittest discover -s line-1/tools/metric-verdict -v
```

Ten tests passed locally. Checks include exhaustive sign enumeration of all
length-2–5 vectors over five integer values; 150 seeded unequal-magnitude vectors;
conditional-null calibration; 200-pair integer precision; inclusive rejection
boundaries; an independent Holm step-down reference; exact decimal effects;
UTF-8/BOM/quotes/CRLF; malformed input and workload limits; pins, escaping
symlinks, input immutability, and a copied-folder offline CLI. These local checks
are not independent statistical certification.

All runtime code is new, self-contained standard-library Python. No currency,
price, balance, pool, network, environment access, wallet, key, secret, signing,
sending, payment, posting or deployment is needed.
