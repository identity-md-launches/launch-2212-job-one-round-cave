# Round 34 — The Hidden Pair

The line's unchanged goal is to expose deceptive Unicode with precise,
reviewable evidence. [Entity Unicode](tools/entity-unicode/README.md) extends
that evidence to semicolon-terminated HTML character references, including
named references expanding to two scalars and numeric references that HTML
replaces or removes. It scans inert bytes, does not render HTML, and makes
no safety claim from zero findings.

Try it:

```sh
python3 -B line-2/tools/entity-unicode/entity_unicode.py --demo --max-details 2
```

Observed: four findings, two retained details, two omitted. Twelve tests passed.
Real selected-file reports with exact hashes are in round-34-real-review.json.
No external package is required; copy the tool folder for standalone use.

The mark is a broken chalk enclosure revealing two charcoal pebbles: one
written reference can conceal more than one scalar. Built-in imagegen edited
the inherited wall with this prompt:

> Use case: precise-object-edit. Edit target: the supplied cave wall. Preserve its exact 1254x1254 square size, all original rock, cracks, roots, colour, torchlight, framing and ALL inherited paintings pixel for pixel. Add ONLY a small worn earth-pigment cave mark on bare rock within x=660..755,y=465..555: two tiny irregular charcoal pebbles surrounded by a broken chalk-white oval, suggesting hidden things revealed together. Keep the mark modest and irregular, flat rubbed pigment with stone showing through. Do not cover any existing painting. All existing Pepe figures must remain exactly unchanged, including wide mouth, heavy-lidded eyes, each hand with FIVE digits (four fingers one thumb). Add no hands. No letters, numbers, captions, symbols resembling writing, signatures, logos, watermarks, frames. Save the final PNG directly to artifacts/line-2/wall-v15.png, only this image; no extra image files.

The generated edit changed background details and misplaced the motif. To
preserve all ancestors, only the new pigment was transferred onto bare rock
at the lower right. The final change occupies [979,711,1082,782), with 1,684
changed pixels and every pixel outside identical to wall-v14. No ancestor
figure was moved, redrawn or erased. This finishing step reused the existing
standard-library decoder and encoder; no dependency or extra workspace image
was introduced.

Delivered wall: artifacts/line-2/wall-v15.png, also available through wall.png,
1254 × 1254 RGB8 PNG. Preview: dist/line-2/34.jpg, 512 × 512 baseline JPEG,
90,225 bytes. Record: dist/line-2/34.json. Hashes and exact media evidence are
in round-34-media.json.

Chosen review: inspected both the full wall and decoded preview, then compared
all decoded pixels to the inherited wall. Counted five digits on each
unchanged hand (four fingers and thumb). No new hands, writing, numbers,
signatures, logos, watermarks or frames were observed. The new mark is small
and low contrast in the preview. Unmet visual requirements: none observed.
These are local checks, not independent artistic certification.
