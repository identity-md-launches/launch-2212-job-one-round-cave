"""Independent enumeration, protocol boundaries, and offline CLI checks."""
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

import metric_verdict as mv


def brute(values):
    observed = abs(sum(values))
    totals = [abs(sum(s * v for s, v in zip(signs, values)))
              for signs in itertools.product((-1, 1), repeat=len(values))]
    return Fraction(sum(x >= observed for x in totals), len(totals))


class ExactTests(unittest.TestCase):
    def test_exhaustive_small_vectors(self):
        for n in range(2, 6):
            for values in itertools.product((-2, -1, 0, 1, 2), repeat=n):
                self.assertEqual(mv.sign_flip(values)[0], brute(values), values)

    def test_seeded_unequal_vectors(self):
        rng = random.Random(33)
        for _ in range(150):
            values = [rng.randint(-12, 12) for _ in range(rng.randint(2, 10))]
            p, count = mv.sign_flip(values)
            self.assertEqual(p, brute(values))
            self.assertEqual(p, mv.sign_flip([x * 100001 for x in values])[0])
            self.assertEqual(p, mv.sign_flip([-x for x in reversed(values)])[0])
            self.assertEqual(count['sign_assignments'], 2**sum(bool(x) for x in values))

    def test_conditional_null_calibration(self):
        magnitudes = [1, 1, 2, 3, 4, 5, 8]
        for threshold in (Fraction(1, 100), Fraction(1, 20), Fraction(1, 10), Fraction(1, 5)):
            rejects = 0
            for signs in itertools.product((-1, 1), repeat=len(magnitudes)):
                values = [s * x for s, x in zip(signs, magnitudes)]
                rejects += mv.sign_flip(values)[0] <= threshold
            self.assertLessEqual(Fraction(rejects, 2**len(magnitudes)), threshold)

    def test_precision_zero_and_inclusive_boundary(self):
        p, info = mv.sign_flip([1] * 200)
        self.assertEqual(p, Fraction(1, 2**199))
        self.assertEqual(info['sign_assignments'], 2**200)
        self.assertEqual(mv.sign_flip([0, 0])[0], 1)
        self.assertEqual(mv.sign_flip([1, -1, 0])[0], 1)
        # Exactly .03125, inclusive at the declared alpha.
        raw = b'case,baseline,candidate\n' + b''.join(f'{i},0,1\n'.encode() for i in range(6))
        yes = mv.analyze(raw, '0.03125', 'higher')['candidates'][0]
        no = mv.analyze(raw, '0.031249', 'higher')['candidates'][0]
        self.assertTrue(yes['reject'])
        self.assertFalse(no['reject'])
        self.assertTrue(yes['reject_with_candidate_ahead'])
        reversed_goal = mv.analyze(raw, '0.03125', 'lower')['candidates'][0]
        self.assertTrue(reversed_goal['reject'])
        self.assertFalse(reversed_goal['reject_with_candidate_ahead'])

    def test_holm_independent_stepdown_reference(self):
        rng = random.Random(10)
        for size in range(1, 17):
            for _ in range(30):
                pvalues = [Fraction(rng.randrange(65), 64) for _ in range(size)]
                adjusted = mv.holm(pvalues)
                for alpha in (Fraction(1, 20), Fraction(1, 10), Fraction(1, 5)):
                    rejected = set()
                    for rank, i in enumerate(sorted(range(size), key=lambda i: pvalues[i])):
                        if pvalues[i] > alpha / (size - rank):
                            break
                        rejected.add(i)
                    self.assertEqual({i for i, p in enumerate(adjusted) if p <= alpha}, rejected)
        self.assertEqual(mv.holm([Fraction(1, 100)] * 3), [Fraction(3, 100)] * 3)

    def test_decimal_exactness_and_family(self):
        self.assertEqual(mv.metric('0.1'), 100000)
        self.assertEqual(mv.metric('-0.000001'), -1)
        raw = b'case,baseline,a,b\nx,0.3,0.1,0.4\ny,0.3,0.2,0.5\n'
        result = mv.analyze(raw)
        self.assertEqual(result['family'], ['a', 'b'])
        self.assertEqual(result['candidates'][0]['mean_candidate_minus_baseline'],
                         {'numerator': -3, 'denominator': 20})
        self.assertEqual(result['candidates'][1]['mean_candidate_minus_baseline'],
                         {'numerator': 3, 'denominator': 20})
        demo = mv.analyze(mv.demo())
        for c in demo['candidates']:
            self.assertEqual(c['raw_p'], {'numerator': 1, 'denominator': 128})
            self.assertEqual(c['holm_p'], {'numerator': 1, 'denominator': 64})
            self.assertTrue(c['reject_with_candidate_ahead'])

    def test_csv_quoting_unicode_and_raw_digest(self):
        raw = '\ufeffcase,baseline,"fast, frog"\r\n"α,β",1.25,1.125\r\n"a""b",2,1.875\r\n'.encode()
        result = mv.analyze(raw)
        self.assertEqual(result['cases'], 2)
        self.assertEqual(result['family'], ['fast, frog'])
        self.assertEqual(result['input_sha256'], hashlib.sha256(raw).hexdigest())

    def test_bad_protocol_inputs(self):
        valid = b'case,baseline,a\nx,0,1\ny,0,2\n'
        for value in ('nan', 'NaN', 'inf', '1e3', '1_000', '01', '.1', '1.', ' 1',
                      '1 ', '0.0000001', '1000000000.000001', '99999999999', ''):
            with self.subTest(value=value), self.assertRaises(ValueError):
                mv.parse_csv(valid.replace(b'x,0,1', ('x,0,' + value).encode()))
        invalid = [b'', valid.replace(b'y,0,2\n', b''), valid + b'\n', valid + b'x,0,1\n',
                   valid.replace(b'y,0,2', b'y,0'), valid.replace(b'y,0,2', b'y,0,2,3'),
                   valid.replace(b'y,0,2', b' y,0,2'), valid.replace(b'y,0,2', b'y\x00,0,2'),
                   valid.replace(b'y,0,2', b'y,0,"2'), valid.replace(b'baseline,a', b'baseline,baseline'),
                   valid.replace(b'case,baseline,a', b'case,baseline'), b'\xff', b'x'*(mv.LIMIT+1)]
        for raw in invalid:
            with self.subTest(raw=raw[:100]), self.assertRaises(ValueError):
                mv.parse_csv(raw)
        for a in ('0', '0.200001', '0.0000001', 'nan', '1/20'):
            with self.assertRaises(ValueError):
                mv.analyze(valid, a)
        with self.assertRaises(ValueError):
            mv.analyze(valid, better='guess')

    def test_declared_limits(self):
        with self.assertRaises(ValueError):
            mv.sign_flip([10000, 10001])
        with self.assertRaises(ValueError):
            mv.sign_flip([1] * 199 + [19000])
        for values in ([True, 1], [1.0, 2], [1], [1] * 201):
            with self.assertRaises(ValueError):
                mv.sign_flip(values)
        for raw in (b'case,baseline,' + b','.join(f'a{i}'.encode() for i in range(17)),
                    b'case,baseline,a\n' + b''.join(f'{i},0,1\n'.encode() for i in range(201))):
            with self.assertRaises(ValueError):
                mv.parse_csv(raw)


class CLITests(unittest.TestCase):
    def test_standalone_pins_errors_and_immutability(self):
        # All temporary files stay within the workspace's expressly allowed scratch area.
        scratch = Path('test/scratch/metric-verdict')
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            directory = Path(directory).resolve()
            tool = directory / 'metric_verdict.py'
            shutil.copyfile(Path(mv.__file__), tool)
            data = directory / 'input.csv'
            data.write_bytes(mv.demo())
            pin = hashlib.sha256(data.read_bytes()).hexdigest()
            def run(*args):
                return subprocess.run([sys.executable, '-B', str(tool), *args], cwd=directory,
                                      capture_output=True, text=True, timeout=20)
            good = run('--input', str(data), '--expected-input-sha256', pin)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertEqual(json.loads(good.stdout), mv.analyze(mv.demo()))
            self.assertEqual(run('--input', str(data), '--expected-input-sha256', pin).stdout,
                             good.stdout)
            demo = run('--demo')
            self.assertEqual(demo.returncode, 0, demo.stderr)
            self.assertIn('synthetic', json.loads(demo.stdout)['fixture'])
            for args in (('--input', str(data)),
                         ('--input', str(data), '--expected-input-sha256', 'a'*64),
                         ('--demo', '--alpha', 'nan'),
                         ('--demo', '--expected-input-sha256', pin)):
                bad = run(*args)
                self.assertEqual(bad.returncode, 2)
                self.assertEqual(bad.stdout, '')
                self.assertTrue(bad.stderr)
            self.assertEqual(data.read_bytes(), mv.demo())
            # A symlink that resolves outside the CLI working directory must be refused.
            external = Path('line-1/GOAL.md').resolve()
            link = directory / 'escape.csv'
            link.symlink_to(external)
            bad = run('--input', str(link), '--expected-input-sha256', pin)
            self.assertEqual(bad.returncode, 2)
            self.assertEqual(bad.stdout, '')


if __name__ == '__main__':
    unittest.main()
