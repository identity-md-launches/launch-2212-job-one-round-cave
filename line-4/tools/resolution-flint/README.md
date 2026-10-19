# Resolution Flint

Compare proposed improvements to numerical input bounds before deciding which
measurement to resolve. This Python 3.10+ tool uses exact rational arithmetic
and explicit dimensions, entirely offline with the standard library. Copy this
whole folder to use it independently.

From the repository root, one command shows it working:

```sh
python3 -B line-4/tools/resolution-flint/resolution_flint.py demo
```

Observed locally: distance `[90,110] m` divided by time `[9,11] s` gives the
baseline enclosure `[90/11,110/9] m/s`. Proposed bounds `[99,101] m` and
`[9.9,10.1] s` are tested individually, then together. Together they give
`[990/101,1010/99] m/s`, fully inside the requested `[9,11] m/s` band; exit 0.
The baseline fails that band. These are hypothetical engineering inputs, not
measurements obtained by the tool. The worker selected this demonstration and
the comparison policy; no requester approval or external facts are implied.

For your own calculation, send a JSON request on stdin:

```sh
python3 -B line-4/tools/resolution-flint/resolution_flint.py run <<'JSON'
{"variables":{"distance":["90 m","110 m"],"time":["9 s","11 s"]},"expression":"distance / time","to":"m/s","within":["9 m/s","11 m/s"],"refinements":{"distance":["99 m","101 m"],"time":["9.9 s","10.1 s"]}}
JSON
```

Exactly those five top-level keys are required. `to` and `within` may be null.
Every refinement must name an existing input and give an inclusive two-element
interval of the same dimensions, completely contained in its original interval.
At least one refinement is required; you may refine only a subset of inputs.
An unchanged range or a point range is valid. Unit conversions are exact.
Quantities must be strings; JSON numbers, nonfinite constants, duplicate keys,
unknown names, extra keys, reversed bounds and dimension errors are rejected.

The baseline uses every original input range. Each `individual` row replaces
only its named input, keeping all others original. `combined` replaces all
proposed inputs together. Rows sort by exact base-unit width reduction,
descending, with names in ascending order for ties. Each row retains its
proposed bounds, full converted result, dimensions, base-unit width, exact
reduction, and optional containment/overlap check. Widths and reductions use
the result's **base unit**, not necessarily its display unit. A zero-width
baseline is supported without division by zero or percentage claims.

Exit 0 means the combined enclosure passes the optional inclusive `within`
check (or no check was requested). Exit 1 means that enclosure is not wholly
contained. Exit 2 means invalid input or a formula undefined on the original
domain; stdout is empty and stderr explains the error. A baseline denominator
including zero is refused even if proposed refinements would avoid zero.

This is a conditional comparison of enclosures, not a measurement service or
a guarantee that a refinement can be achieved. Narrower input bounds must be
justified separately. Reductions are not additive contributions, probabilities,
confidence, derivatives, optimal experiment choices, or actual attainable output
widths. Repeated variable dependencies can still make the enclosure loose:
`x-x` need not return a zero-width interval. Failing containment does not prove
a real value violates the band. Exact arithmetic cannot verify input truth or
the suitability of the formula. No coin, exchange rate, wallet or payment is
needed; ZTO/IMD prices are neither required nor invented.

Inherited bounds: 65,536 request bytes, at most 32 inputs, 4,096 expression
characters, 256 tokens, 32 nesting levels, integer powers from -12 to 12 and
2,048-bit endpoints. Work is at most 34 formula evaluations (baseline, up to
32 individual refinements, combined). Bounds remain exact; excessive values
fail explicitly. The tool reads only stdin and its own source dependencies,
with no network, environment, keys, configuration, or file-output operations.

Run the regression suite:

```sh
python3 -B -m unittest discover -s line-4/tools/resolution-flint -v
```

All ten tests passed locally, covering 200 seeded signed linear comparisons
against independent rational corner extrema, conversion, ranking/ties, unused
inputs, nonadditivity, dependency overestimation, point domains, subset/type/
schema errors, singularities, no input mutation and actual CLI statuses/streams.
These results are local evidence only. `engine.py` and `interval_flint.py` are
unchanged ordinary-file snapshots from the inherited Interval Flint folder;
no installed dependency, symlink to another tool, or network is needed.
