# Metric Measure

Line 1's Metric Verdict gives exact paired sign-flip evidence for one continuous
metric and a declared candidate family. Line 4's Unit Flint adds exact unit
conversion and a dimension-checked minimum observed improvement. This handoff
helps a benchmark worker distinguish detectable differences from changes large
enough to matter under a declared descriptive threshold.

Run from the repository root (Python 3.10+, standard library only):

```sh
python3 -B shared/metric-measure/metric_measure.py demo
```

Observed: the eight-case **synthetic** fixture has candidate-minus-baseline
effects of -0.125 ms and -0.5 ms, exactly -0.000125 s and -0.0005 s. Both
Holm-adjusted p-values are 1/64 and reject at 0.05 with lower being better.
Only the second observed improvement reaches the declared 0.25 ms minimum.
No real system was benchmarked. Units and the threshold are analyst assertions.

For your own explicitly selected non-sensitive CSV, retain its SHA-256
independently, then supply the bytes on stdin:

```sh
python3 -B shared/metric-measure/metric_measure.py analyze \
  --expected-input-sha256 c73d90bcb4d8be69932d604c2a78e738cb3d99c0f26e80b77ad166847acd6b44 \
  --measurement-unit ms --display-unit s --minimum '0.25 ms' \
  < line-1/tools/metric-verdict/example.csv
```

That command uses the shipped synthetic fixture. Replace its digest and input
together for real observations. Header: `case,baseline,candidate-a,candidate-b`;
2–200 distinct cases, 1–16 candidates, signed plain decimals with at most six
fractional digits, absolute value at most 10^9, at most 2 MiB. Measurement units
apply to **every** measurement column. `--better lower` is the default;
`--better higher` reverses favorable direction, retaining the two-sided tests.
`--alpha` defaults to 0.05. Minimum must be positive and have matching dimensions.
Units use Unit Flint's expression grammar: write `(1/8) * ms`, rather than
`1/8 ms` (which means inverse time). No currency units are invented.

Output embeds the complete original family analysis without dropping tied,
losing or non-rejecting candidates. Separate effect rows retain exact rational
or finite decimal conversions, inclusive observed-threshold comparisons and
the original zero-effect rejection flags. A completed analysis exits 0,
regardless of its conclusions. Invalid inputs exit 2, empty stdout and an
ASCII-escaped diagnostic. No files are written by the tool.

**Interpretation:** observing a mean above a minimum and rejecting zero does
not prove that the population effect exceeds that minimum. There is no test or
confidence bound for that practical threshold here. The sign-flip model requires
independent fair signs conditional on magnitudes under each null; independence
or zero mean alone is insufficient. Holm adjusts the full candidate family,
not repeated looks or selected metrics. Freeze metric, units, direction, cases,
family, alpha, threshold and analysis before seeing outcomes. Correlated cases,
unrepresentative samples, dishonest measurements and retrospective choices
remain outside these guarantees. Non-rejection is not equivalence.

Copy this entire folder anywhere for offline use. Two unmodified ordinary-file
engine copies and their original sources/hashes are in `provenance.json`.
Hashes bind bytes, not authenticity, authorship or preregistration time.
No network, environment, configuration, key, wallet, signing, payment or posting
is used. Input and output contain unredacted evidence labels; JSON escaping is
terminal presentation, not permission to render input as HTML.

```sh
python3 -B -m unittest discover -s shared/metric-measure -v
```

Nine tests cover exact unit and CSV rescaling, inclusive thresholds, higher/lower
direction, baseline advantage, ties, malformed inputs and dimensions, pins,
unchanged snapshots and a copied-folder CLI with successful and invalid inputs.
The original Metric Verdict suite separately tests its exact enumeration and
Holm calculation. These are local checks, not independent certification.
