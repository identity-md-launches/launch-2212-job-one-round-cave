#!/usr/bin/env python3
"""Cite Unicode concealed by semicolon-terminated HTML character references."""
import argparse
from collections import Counter
import hashlib
import html
from html.entities import html5
import json
from pathlib import Path
import re
import stat
import sys
import unicodedata

MAX_BYTES = 2 * 1024 * 1024
REFERENCE = re.compile(rb'&(?:#[xX][0-9a-fA-F]+|#[0-9]+|[A-Za-z][A-Za-z0-9]*);')
DEMO = b'owner=adm&#x456;n\nlabel=&NotEqualTilde; gap=&ZeroWidthSpace; bidi=&#8238; normal=&amp;'


def decode_reference(raw):
    """One lexical reference, no recursion or partial named matches."""
    text = raw.decode('ascii')
    if not text.startswith('&#'):
        return html5.get(text[1:])
    hexadecimal = text[2:3].lower() == 'x'
    digits = text[3:-1] if hexadecimal else text[2:-1]
    significant = digits.lstrip('0') or '0'
    # Avoid int's digit limit and unbounded bignum conversion. All values above
    # this bound decode to U+FFFD under HTML rules, regardless of their length.
    if len(significant) > (6 if hexadecimal else 7):
        return '\ufffd'
    canonical = '&#' + ('x' if hexadecimal else '') + significant + ';'
    return html.unescape(canonical)


def scan(data, max_details=100):
    if not isinstance(data, bytes) or len(data) > MAX_BYTES:
        raise ValueError('input must be bytes of at most 2 MiB')
    if type(max_details) is not int or not 0 <= max_details <= 1000:
        raise ValueError('max_details must be an integer from 0 to 1000')
    data.decode('utf-8', 'strict')
    details, categories = [], Counter()
    recognized = findings = 0
    line, line_start, previous = 1, 0, 0
    for match in REFERENCE.finditer(data):
        lo, hi = match.span()
        # Advance coordinates once over each byte, including skipped references.
        line += data.count(b'\n', previous, lo)
        last_lf = data.rfind(b'\n', previous, lo)
        if last_lf >= 0:
            line_start = last_lf + 1
        previous = lo
        decoded = decode_reference(match.group())
        if decoded is None:
            continue
        recognized += 1
        if decoded and all(0x20 <= ord(c) <= 0x7e for c in decoded):
            continue
        findings += 1
        kind = 'empty-decoding' if not decoded else 'non-ascii-or-control'
        categories[kind] += 1
        if len(details) >= max_details:
            continue
        raw = match.group()
        details.append({
            'source_byte_range': [lo, hi],
            'source_line': line, 'source_byte_column': lo - line_start + 1,
            'source_span_sha256': hashlib.sha256(raw).hexdigest(),
            'source_reference_prefix': raw[:80].decode('ascii'),
            'source_reference_bytes': len(raw),
            'source_reference_omitted_bytes': max(0, len(raw) - 80),
            'source_before_hex': data[max(0, lo-16):lo].hex(),
            'source_after_hex': data[hi:hi+16].hex(),
            'kind': kind,
            'decoded_scalars': [
                {'codepoint': f'U+{ord(c):04X}',
                 'name': unicodedata.name(c, 'UNNAMED'),
                 'category': unicodedata.category(c)} for c in decoded],
        })
    return {
        'schema_version': 1, 'tool': 'entity-unicode/1',
        'source_sha256': hashlib.sha256(data).hexdigest(), 'source_bytes': len(data),
        'unicode_version': unicodedata.unidata_version,
        'python_version': list(sys.version_info[:3]),
        'entity_table_sha256': hashlib.sha256(json.dumps(html5, sort_keys=True,
            ensure_ascii=True, separators=(',', ':')).encode('ascii')).hexdigest(),
        'analysis_complete': True, 'recognized_references': recognized,
        'finding_count': findings, 'counts_by_kind': dict(sorted(categories.items())),
        'detail_cap': max_details, 'retained_details': len(details),
        'omitted_details': findings - len(details), 'details': details,
        'coverage': 'Exact semicolon-terminated HTML5 named or decimal/hex numeric references decoding to non-ASCII, controls, or empty text.',
        'limitations': [
            'Lexical review only: no HTML context, rendering, script execution or browser safety claim.',
            'No semicolonless, recursive, percent, JSON or literal Unicode analysis.',
            'Numeric references use Python HTML5 replacement/removal rules; decoded scalars are not necessarily the written numeric value.',
            'References can be legitimate; unknown names and printable-ASCII decodings are not findings.',
            'Coordinates use original UTF-8 bytes, zero-based half-open ranges and one-based LF-only lines/byte columns.',
            'Output is ASCII JSON for terminal review, not HTML sanitization; source snippets are unredacted.',
            'Zero findings does not establish safety. Hashes identify bytes, not authorship or authenticity.',
        ],
    }


def read_selected(path):
    selected = Path(path).resolve(strict=True)
    if not selected.is_relative_to(Path.cwd().resolve()):
        raise ValueError('file must resolve within the current working directory')
    if not stat.S_ISREG(selected.stat().st_mode):
        raise ValueError('input must be a regular file')
    with selected.open('rb') as handle:
        data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError('input exceeds 2 MiB')
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--demo', action='store_true')
    group.add_argument('--file', type=Path)
    parser.add_argument('--max-details', type=int, default=100)
    args = parser.parse_args(argv)
    try:
        report = scan(DEMO if args.demo else read_selected(args.file), args.max_details)
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 2
    report['source_kind'] = 'synthetic-demo' if args.demo else 'selected-file'
    print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True))
    return 0 if args.demo or not report['finding_count'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
