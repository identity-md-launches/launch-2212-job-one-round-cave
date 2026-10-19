# Timeline Backbone

Timeline Backbone verifies a Timeline Replay pack, then summarizes all pairwise
event order claims. Each event citation reports how many other events are
definitely before it, definitely after it, or unresolved because the two
half-open uncertainty intervals intersect. The result gives exact counts for
the whole pack, even when the displayed citation list is capped.

One command from the repository root shows it working offline:

```sh
python3 -B line-3/tools/timeline-backbone/backbone.py demo
```

Observed locally: the synthetic three-event pack replayed successfully. Two of
its three event pairs have a definite order and one remains unresolved under an
asserted ±250 ms clock bound. This is generated sample data, not a real incident
or a measurement of clock error.

Analyze a pack saved inside the current workspace:

```sh
python3 -B line-3/tools/timeline-backbone/backbone.py analyze path/to/pack.json --expect-sha256 TRUSTED_DIGEST
```

The optional digest must be independently retained if it is meant to detect
replacement of the pack. `--limit` caps displayed event citations from 0 to 200;
pair counts still cover every event. Source names, line numbers, line hashes and
interval bounds are citations; messages and embedded log bytes are not emitted.
Inputs are verified by the fixed Replay parser before analysis. The tool never
opens paths named by a pack, executes services or contacts the network.

Intervals are half-open: an end equal to another event's start establishes
definite order. Intersecting intervals mean the evidence does not establish an
order between the pair; they do not establish simultaneity, causality or event
truth. Omitted undated lines remain accounted for by Replay's verified summary,
but cannot be placed in this interval-order comparison. Clock bounds are analyst
assumptions, not measurements.

Python 3.10+ and the standard library only. The copied Replay verifier and parser
snapshot keep this folder independently runnable without network access or
installation.

```sh
python3 -B -m unittest discover -s line-3/tools/timeline-backbone -v
```

Observed: six focused tests passed for definite order, endpoint touching,
overlapping intervals, empty input, citation limits and the verified demo.
