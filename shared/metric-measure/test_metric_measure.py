import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import metric_measure as glue


class MetricMeasureTests(unittest.TestCase):
    def run_analysis(self, raw=None, **kwargs):
        raw = glue.metric.demo() if raw is None else raw
        options = dict(measurement_unit='ms', display_unit='s', minimum='0.25 ms')
        options.update(kwargs)
        return glue.analyze(raw, hashlib.sha256(raw).hexdigest(), **options)

    def test_detectable_is_separate_from_observed_size(self):
        result = self.run_analysis()
        a, b = result['effects']
        self.assertEqual([a['mean_candidate_minus_baseline'], b['mean_candidate_minus_baseline']],
                         ['-0.000125', '-0.0005'])
        self.assertTrue(all(x['reject_zero_with_candidate_ahead'] for x in (a, b)))
        self.assertEqual([a['observed_mean_meets_minimum'], b['observed_mean_meets_minimum']], [False, True])
        self.assertEqual(result['evidence'], glue.metric.analyze(glue.metric.demo()))

    def test_exact_boundary_and_display_invariance(self):
        for display in ('s', 'ms', 'min', '2 ms'):
            result = self.run_analysis(display_unit=display, minimum='(1/8) * ms')
            self.assertTrue(result['effects'][0]['observed_mean_meets_minimum'])
        self.assertFalse(self.run_analysis(minimum='0.1250000001 ms')['effects'][0]['observed_mean_meets_minimum'])

    def test_rescaled_observations_preserve_evidence(self):
        # Exact decimal CSV in seconds, same physical effects as the ms fixture.
        raw = ('case,baseline,small_step,large_step\n' + ''.join(
            f'case-{i},0.010,0.009875,0.009500\n' for i in range(1, 9))).encode()
        result = self.run_analysis(raw, measurement_unit='s')
        original = self.run_analysis()
        self.assertEqual(result['effects'], original['effects'])
        self.assertEqual([x['holm_p'] for x in result['evidence']['candidates']],
                         [x['holm_p'] for x in original['evidence']['candidates']])

    def test_direction_and_baseline_advantage(self):
        higher = self.run_analysis(better='higher')
        self.assertTrue(all(x['reject'] for x in higher['evidence']['candidates']))
        self.assertTrue(all(not x['reject_zero_with_candidate_ahead'] for x in higher['effects']))
        raw = b'case,baseline,c\na,1,2\nb,1,2\n'
        result = self.run_analysis(raw, better='higher', minimum='1 ms')
        self.assertTrue(result['effects'][0]['observed_mean_meets_minimum'])
        self.assertFalse(result['effects'][0]['reject_zero_with_candidate_ahead'])

    def test_no_false_equivalence_for_ties(self):
        result = self.run_analysis(b'case,baseline,c\na,1,1\nb,1,1\n')
        self.assertEqual(result['effects'][0]['observed_improvement'], '0')
        self.assertFalse(result['effects'][0]['observed_mean_meets_minimum'])
        self.assertEqual(result['evidence']['candidates'][0]['raw_p'], {'numerator': 1, 'denominator': 1})

    def test_dimensions_scales_and_invalid_units(self):
        for changes in ({'minimum': '1 m'}, {'display_unit': 'B'}, {'minimum': '0 ms'},
                        {'minimum': '-1 ms'}, {'measurement_unit': '-ms'},
                        {'display_unit': '0 s'}, {'measurement_unit': 'ZTO'}):
            with self.subTest(changes=changes), self.assertRaises((ValueError, glue.units.UnitError)):
                self.run_analysis(**changes)

    def test_pins_and_invalid_csv(self):
        raw = glue.metric.demo()
        for pin in ('0'*64, None, 'A'*64):
            with self.assertRaises(ValueError):
                glue.analyze(raw, pin, 'ms', 's', '1 ms')
        for raw in (b'', b'case,baseline,c\na,1,NaN\nb,1,2\n', b'x'*(glue.metric.LIMIT+1)):
            with self.assertRaises(ValueError):
                self.run_analysis(raw)

    def test_original_engines_unchanged(self):
        here = Path(__file__).resolve().parent
        for item in json.loads((here/'provenance.json').read_text()):
            self.assertEqual(hashlib.sha256((here/item['copy']).read_bytes()).hexdigest(), item['sha256'])

    def test_actual_cli_and_portable_copy(self):
        here = Path(__file__).resolve().parent
        scratch = Path('test/scratch').resolve()
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as name:
            target = Path(name)/'tool'
            shutil.copytree(here, target, ignore=shutil.ignore_patterns('__pycache__'))
            command = [sys.executable, '-B', str(target/'metric_measure.py')]
            run = subprocess.run(command+['demo'], capture_output=True, cwd=name)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)['effects'], self.run_analysis()['effects'])
            raw = glue.metric.demo()
            args = ['analyze', '--expected-input-sha256', hashlib.sha256(raw).hexdigest(),
                    '--measurement-unit', 'ms', '--display-unit', 's', '--minimum', '0.25 ms']
            run = subprocess.run(command+args, input=raw, capture_output=True, cwd=name)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout), self.run_analysis())
            bad = subprocess.run(command+['analyze'], input=raw, capture_output=True, cwd=name)
            self.assertEqual(bad.returncode, 2)
            self.assertEqual(bad.stdout, b'')
            self.assertTrue(bad.stderr.isascii())


if __name__ == '__main__':
    unittest.main()
