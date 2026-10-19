# Entity Unicode

Expose non-ASCII characters and controls hidden in HTML character references
before trusting copied text or identifiers. Python 3.10+; standard library only,
no installation, sibling imports, network, environment access, execution of
input, or rewriting of the selected file.

Run this one command from the repository root:

```sh
python3 -B line-2/tools/entity-unicode/entity_unicode.py --demo --max-details 2
```

Observed locally: **4 findings, 2 retained details, 2 omitted**, from 5 recognized
references. The synthetic example includes a Cyrillic i, a two-scalar named
entity, a zero-width space and a directional override. Ordinary `&amp;` is
recognized but not a finding. The demo exits 0 and is not an observed attack.

Review one explicitly selected, non-sensitive UTF-8 workspace file:

```sh
python3 -B line-2/tools/entity-unicode/entity_unicode.py --file dist/index.html
```

The existing gallery page and gathering report were reviewed locally: 70,793
and 7,530 bytes respectively, with zero covered findings. The engine's own
source has four findings in its explicitly synthetic demo bytes. Full reports,
hashes and runtime/table versions are in `line-2/round-34-real-review.json`.
These are observations about the selected bytes, not safety endorsements.

Every retained finding cites a zero-based, half-open original byte range and
SHA-256 of that exact source span, one-based LF-only line and byte column,
up to 80 original reference bytes, and up to 16 context bytes on each side in
hex. Long numeric references explicitly report omitted source-prefix bytes.
Every decoded scalar has a code point, Unicode name and category. Counts cover
the complete input even with `--max-details 0`. The full source SHA-256,
Python version, Unicode version and HTML entity-table digest support review
of runtime differences. Hashes establish neither authenticity nor authorship.

Coverage is lexical and deliberately narrow: exact, **semicolon-terminated**
HTML5 named references and decimal/hex numeric references whose decoded output
contains non-ASCII or ASCII controls, or is empty. Multi-scalar entities share
one source citation. HTML numeric rules may replace an out-of-range value or
surrogate with U+FFFD, remap a C1 value (128 becomes U+20AC), or remove a
disallowed control (1 becomes empty). The report gives what Python's HTML5
decoder produces, not a claim that the literal integer is that scalar.

No HTML parser or browser is run. References in comments, code blocks, scripts
and ordinary text are scanned equally; whether a browser interprets them
depends on context. Unknown names, missing semicolons and printable-ASCII
decodings are skipped. There is **one decoding layer**: `&amp;rlm;` is not
recursively turned into a directional mark. Literal Unicode, percent escapes,
JSON escapes, normalization and visual confusables need the other line tools.
Many references are legitimate. A finding requires interpretation; zero
findings does not establish safety or absence of deceptive Unicode.

Input must resolve to a regular file within the current working directory,
at most 2 MiB. The detail cap is 0–1000 (default 100). No recursive discovery.
Reports are printable ASCII JSON plus LF, with no raw terminal controls or
Unicode from input. This is terminal presentation, not HTML/Markdown
sanitization. Context is unredacted: select only files you may inspect.

Exit codes: **0** for demo or a file without findings, **1** for a file with
findings, **2** for input errors (empty stdout, escaped JSON error on stderr).

```sh
python3 -B -m unittest discover -s line-2/tools/entity-unicode -p 'test_*.py' -v
```

All **12 tests passed** locally. They cover every semicolon-terminated named
entity in the runtime table, numeric replacement/removal, multiscalar output,
exact CRLF/multibyte byte citations, 100 seeded offset cases, a full 2 MiB
input, huge numeric references, complete counts under caps, unknown/recursive
references, terminal presentation, symlink escape rejection, and copied
standalone CLI behavior. Generated test files remain in `test/scratch/`.
