import hashlib
from html.entities import html5
import html
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

import entity_unicode as engine


class EntityTests(unittest.TestCase):
    def test_demo(self):
        report = engine.scan(engine.DEMO, 2)
        self.assertEqual(report['finding_count'], 4)
        self.assertEqual(report['recognized_references'], 5)
        self.assertEqual(report['omitted_details'], 2)
        self.assertEqual(report['details'][0]['decoded_scalars'][0]['codepoint'], 'U+0456')

    def test_exact_multibyte_crlf_citations(self):
        data = 'é\r\nx=&rlm;\u2028&#x456;'.encode()
        details = engine.scan(data)['details']
        for detail, ref in zip(details, [b'&rlm;', b'&#x456;']):
            lo, hi = detail['source_byte_range']
            self.assertEqual(data[lo:hi], ref)
            self.assertEqual(detail['source_span_sha256'], hashlib.sha256(ref).hexdigest())
            self.assertEqual(detail['source_line'], 2)
            self.assertEqual(detail['source_byte_column'], lo - data.rfind(b'\n', 0, lo))

    def test_every_named_reference_against_stdlib(self):
        for name, decoded in html5.items():
            if not name.endswith(';'):
                continue
            raw = ('&' + name).encode('ascii')
            self.assertEqual(engine.decode_reference(raw), decoded)
            report = engine.scan(raw)
            expected = not decoded or any(not 0x20 <= ord(c) <= 0x7e for c in decoded)
            self.assertEqual(report['finding_count'], int(expected), name)

    def test_multi_scalar(self):
        report = engine.scan(b'&NotEqualTilde;')
        self.assertEqual([x['codepoint'] for x in report['details'][0]['decoded_scalars']],
                         ['U+2242', 'U+0338'])

    def test_html_numeric_rules(self):
        for raw in [b'&#0;', b'&#xD800;', b'&#1114112;', b'&#128;',
                    b'&#13;', b'&#9;', b'&#1;', b'&#x10FFFF;', b'&#X202e;']:
            self.assertEqual(engine.decode_reference(raw), html.unescape(raw.decode()))
        self.assertEqual(engine.scan(b'&#1;')['details'][0]['kind'], 'empty-decoding')
        self.assertEqual(engine.scan(b'&#128;')['details'][0]['decoded_scalars'][0]['codepoint'], 'U+20AC')

    def test_large_numeric_without_int_limit(self):
        self.assertEqual(engine.decode_reference(b'&#' + b'0' * 10000 + b'8238;'), '\u202e')
        self.assertEqual(engine.decode_reference(b'&#' + b'9' * 10000 + b';'), '\ufffd')
        d = engine.scan(b'&#' + b'9' * 10000 + b';')['details'][0]
        self.assertEqual(len(d['source_reference_prefix']), 80)
        self.assertEqual(d['source_reference_omitted_bytes'], 9923)

    def test_scope_and_no_recursion(self):
        data = b'&madeup; &notARealEntity; &rlm &#x202e &amp;rlm; &#65; &#32;'
        report = engine.scan(data)
        self.assertEqual(report['finding_count'], 0)
        self.assertEqual(report['recognized_references'], 3)

    def test_counts_without_retention(self):
        report = engine.scan(b'&rlm;' * 10000, 0)
        self.assertEqual(report['finding_count'], 10000)
        self.assertEqual(report['omitted_details'], 10000)
        self.assertEqual(report['details'], [])

    def test_independent_generated_offsets(self):
        rng = random.Random(345)
        for _ in range(100):
            data, expected = bytearray(), []
            for _ in range(20):
                data.extend(rng.choice(['é', '\r\n', '\u2028', 'abc']).encode())
                lo = len(data)
                ref = rng.choice([b'&rlm;', b'&#8238;', b'&NotEqualTilde;'])
                data.extend(ref)
                expected.append((lo, len(data)))
            report = engine.scan(bytes(data))
            self.assertEqual([tuple(x['source_byte_range']) for x in report['details']], expected)
            for d in report['details']:
                lo = d['source_byte_range'][0]
                self.assertEqual(d['source_line'], data[:lo].count(b'\n') + 1)

    def test_bounds(self):
        self.assertEqual(engine.scan(b'a' * engine.MAX_BYTES)['finding_count'], 0)
        for data, cap in [(b'a' * (engine.MAX_BYTES+1), 1), (b'\xff', 1),
                          (b'', -1), (b'', 1001), (b'', True)]:
            with self.assertRaises(ValueError):
                engine.scan(data, cap)

    def test_terminal_safe_output(self):
        report = engine.scan(b'\x1b[31m &NewLine; &Tab; &#8238;')
        output = json.dumps(report, ensure_ascii=True, indent=2)
        self.assertTrue(all(32 <= ord(c) <= 126 or c == '\n' for c in output))

    def test_cli_and_selected_paths(self):
        script = Path(engine.__file__).resolve()
        scratch = Path('test/scratch')
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temp:
            temp = Path(temp).resolve()
            (temp/'selected.txt').write_bytes(b'&rlm;')
            (temp/'plain.txt').write_bytes(b'&amp;')
            (temp/'invalid.txt').write_bytes(b'\xff')
            # Copy proves this folder's engine needs no sibling packages.
            copied = temp/'entity_unicode.py'
            copied.write_bytes(script.read_bytes())
            for args, code in [(['--demo'], 0), (['--file','selected.txt'], 1),
                               (['--file','plain.txt'], 0), (['--file','invalid.txt'], 2),
                               (['--file','.'], 2), (['--file','missing'], 2),
                               (['--file','../outside'], 2),
                               (['--demo','--max-details','-1'], 2)]:
                result = subprocess.run([sys.executable, '-B', str(copied), *args],
                                        cwd=temp, capture_output=True)
                self.assertEqual(result.returncode, code, result.stderr)
                if code == 2:
                    self.assertEqual(result.stdout, b'')
                    json.loads(result.stderr)
                else:
                    json.loads(result.stdout)
            (temp/'escape').symlink_to(script)
            result = subprocess.run([sys.executable, '-B', str(copied), '--file', 'escape'],
                                    cwd=temp, capture_output=True)
            self.assertEqual(result.returncode, 2)


if __name__ == '__main__':
    unittest.main()
