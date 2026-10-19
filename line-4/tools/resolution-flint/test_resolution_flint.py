import copy
from fractions import Fraction as F
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

import resolution_flint as tool


class ResolutionTests(unittest.TestCase):
    def test_demo(self):
        request = tool.demo_request()
        saved = copy.deepcopy(request)
        result = tool.evaluate(request)
        self.assertEqual(request, saved)
        self.assertFalse(result['baseline']['within']['fully_within'])
        self.assertTrue(result['combined']['result']['within']['fully_within'])
        self.assertEqual(F(result['combined']['result']['base_lower']), F(990, 101))
        self.assertEqual(F(result['combined']['result']['base_upper']), F(1010, 99))
        self.assertEqual([row['variable'] for row in result['individual']], ['time', 'distance'])

    def test_subset_leaves_other_inputs_unchanged(self):
        request = {'variables': {'x': ['-8 m', '-4 m'], 'y': ['-4 s', '-2 s']},
                   'expression': 'x / y', 'to': 'cm/s', 'within': None,
                   'refinements': {'x': ['-600 cm', '-500 cm']}}
        result = tool.evaluate(request)
        self.assertEqual(len(result['individual']), 1)
        self.assertEqual(result['individual'][0]['result'], result['combined']['result'])
        self.assertEqual(result['combined']['result']['lower'], '125')
        self.assertEqual(result['combined']['result']['upper'], '300')

    def test_independent_linear_oracle(self):
        rng = random.Random(3204)
        for _ in range(200):
            a, b = rng.randint(-20, 20), rng.randint(-20, 20)
            lx, ly = rng.randint(-100, 100), rng.randint(-100, 100)
            ux, uy = lx + rng.randint(2, 50), ly + rng.randint(2, 50)
            inputs = {'x': [f'{lx} m', f'{ux} m'], 'y': [f'{ly} m', f'{uy} m']}
            refined = {'x': [f'{lx+1} m', f'{ux-1} m'], 'y': [f'{ly+1} m', f'{uy-1} m']}
            request = {'variables': inputs, 'expression': f'({a}) * x + ({b}) * y',
                       'to': 'cm', 'within': None, 'refinements': refined}
            result = tool.evaluate(request)
            def oracle(x, y):
                corners = [a*i+b*j for i in x for j in y]
                return min(corners), max(corners)
            base_lo, base_hi = oracle([lx, ux], [ly, uy])
            all_lo, all_hi = oracle([lx+1, ux-1], [ly+1, uy-1])
            combined = result['combined']['result']
            self.assertEqual((F(combined['base_lower']), F(combined['base_upper'])), (all_lo, all_hi))
            self.assertEqual(F(combined['lower']), all_lo*100)
            for row in result['individual']:
                x = [lx+1, ux-1] if row['variable'] == 'x' else [lx, ux]
                y = [ly+1, uy-1] if row['variable'] == 'y' else [ly, uy]
                lo, hi = oracle(x, y)
                self.assertEqual(F(row['base_width_reduction']), (base_hi-base_lo)-(hi-lo))

    def test_ranking_ties_and_unused_input(self):
        request = {'variables': {'x': ['0 m', '10 m'], 'y': ['0 m', '10 m'], 'z': ['1 s', '2 s']},
                   'expression': 'x + y', 'to': None, 'within': None,
                   'refinements': {'z': ['1 s', '1 s'], 'y': ['2 m', '8 m'], 'x': ['2 m', '8 m']}}
        rows = tool.evaluate(request)['individual']
        self.assertEqual([r['variable'] for r in rows], ['x', 'y', 'z'])
        self.assertEqual([r['base_width_reduction'] for r in rows], ['4', '4', '0'])

    def test_nonadditive_and_dependency(self):
        request = {'variables': {'x': ['0 m', '2 m'], 'y': ['0 m', '2 m']},
                   'expression': 'x * y', 'to': None, 'within': None,
                   'refinements': {'x': ['1 m', '1 m'], 'y': ['1 m', '1 m']}}
        result = tool.evaluate(request)
        self.assertEqual(result['combined']['base_width_reduction'], '4')
        self.assertEqual(sum(F(r['base_width_reduction']) for r in result['individual']), 4)
        # A different interior range demonstrates non-additivity explicitly.
        request['refinements'] = {'x': ['0 m', '1 m'], 'y': ['0 m', '1 m']}
        result = tool.evaluate(request)
        self.assertEqual(result['combined']['base_width_reduction'], '3')
        self.assertEqual(sum(F(r['base_width_reduction']) for r in result['individual']), 4)
        request['expression'] = 'x - x'
        result = tool.evaluate(request)
        self.assertEqual(result['combined']['base_width'], '2')  # actual x-x is zero

    def test_units_and_point_baseline(self):
        request = {'variables': {'x': ['1 m', '1 m']}, 'expression': 'x', 'to': 'cm',
                   'within': ['1 m', '1 m'], 'refinements': {'x': ['100 cm', '100 cm']}}
        result = tool.evaluate(request)
        self.assertEqual(result['baseline_base_width'], '0')
        self.assertEqual(result['combined']['result']['lower'], '100')

    def test_bad_refinements(self):
        for changes in [{}, [], {'unknown': ['1 m', '2 m']},
                        {'distance': ['89 m', '100 m']}, {'distance': ['100 m', '111 m']},
                        {'distance': ['100 m', '99 m']}, {'distance': ['99 s', '101 s']},
                        {'distance': ['99 m']}, {'distance': [99, '101 m']}]:
            request = tool.demo_request()
            request['refinements'] = changes
            with self.assertRaises((tool.interval.IntervalError, tool.interval.engine.UnitError)):
                tool.evaluate(request)

    def test_baseline_singularity_not_hidden(self):
        request = tool.demo_request()
        request['variables']['time'] = ['-1 s', '1 s']
        request['refinements']['time'] = ['0.5 s', '1 s']
        with self.assertRaises(tool.interval.engine.UnitError):
            tool.evaluate(request)

    def test_strict_json_and_schema(self):
        for data in [b'{"x":1}', b'{"x":"1","x":"2"}', b'NaN', b'\xff', b' '*65537]:
            with self.assertRaises(tool.interval.IntervalError):
                tool.interval.decode(data)
        for request in [None, [], {}, dict(tool.demo_request(), extra='no')]:
            with self.assertRaises(tool.interval.IntervalError):
                tool.evaluate(request)

    def test_cli(self):
        script = str(Path(__file__).with_name('resolution_flint.py'))
        demo = subprocess.run([sys.executable, '-B', script, 'demo'], capture_output=True)
        self.assertEqual(demo.returncode, 0, demo.stderr)
        self.assertEqual(demo.stderr, b'')
        json.loads(demo.stdout)
        request = tool.demo_request()
        request['within'] = ['0 m/s', '1 m/s']
        failed = subprocess.run([sys.executable, '-B', script, 'run'], input=json.dumps(request).encode(), capture_output=True)
        self.assertEqual(failed.returncode, 1, failed.stderr)
        self.assertEqual(failed.stderr, b'')
        invalid = subprocess.run([sys.executable, '-B', script, 'run'], input=b'{}', capture_output=True)
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(invalid.stdout, b'')
        self.assertIn(b'resolution-flint:', invalid.stderr)


if __name__ == '__main__':
    unittest.main()
