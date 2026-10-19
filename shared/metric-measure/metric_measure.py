#!/usr/bin/env python3
"""Join exact paired metric evidence to an explicitly dimensioned effect threshold."""
import argparse
from fractions import Fraction
import hashlib
import json
import sys

from engines import metric_verdict as metric
from engines import unit_flint as units


def analyze(raw, pin, measurement_unit, display_unit, minimum, better='lower', alpha='0.05'):
    if not isinstance(pin, str) or not metric.PIN.fullmatch(pin):
        raise ValueError('an independently retained lowercase SHA-256 is required')
    if hashlib.sha256(raw).hexdigest() != pin:
        raise ValueError('input SHA-256 mismatch')
    source = units.Parser(measurement_unit, target=True).parse()
    target = units.Parser(display_unit, target=True).parse()
    threshold = units.Parser(minimum).parse()
    if source.value <= 0 or target.value <= 0 or threshold.value <= 0:
        raise ValueError('measurement unit, display unit and minimum must have positive scales')
    if not source.dims == target.dims == threshold.dims:
        raise ValueError('measurement, display and minimum dimensions must match')
    evidence = metric.analyze(raw, alpha, better)
    rows = []
    for candidate in evidence['candidates']:
        effect = Fraction(**candidate['mean_candidate_minus_baseline']) * source.value
        improvement = -effect if better == 'lower' else effect
        # Keep arithmetic budgets on conversions as well as source quantities.
        converted = units.Parser.bounded(units.Quantity(effect / target.value, source.dims), 0)
        threshold_display = units.Parser.bounded(
            units.Quantity(threshold.value / target.value, source.dims), 0)
        rows.append({
            'candidate': candidate['candidate'],
            'mean_candidate_minus_baseline': units.exact_decimal(converted.value),
            'observed_improvement': units.exact_decimal(improvement / target.value),
            'minimum_improvement': units.exact_decimal(threshold_display.value),
            'display_unit': display_unit,
            'observed_mean_meets_minimum': improvement >= threshold.value,
            'reject_zero_with_candidate_ahead': candidate['reject_with_candidate_ahead'],
        })
    return {
        'schema': 'metric-measure/1',
        'measurement_unit': measurement_unit,
        'dimensions': units.dimensions(source.dims),
        'minimum_expression': minimum,
        'evidence': evidence,
        'effects': rows,
        'limitations': [
            'Threshold comparisons describe observed means; they are not tests or confidence bounds for the minimum effect.',
            'Rejecting zero and observing a mean above a minimum does not establish that the population effect exceeds that minimum.',
            'Units, metric direction, threshold, family and analysis must be declared before seeing outcomes; units are asserted, not measured.',
            'The exact sign-flip assumptions and workload limits in the embedded evidence still apply.',
            'A matching digest binds input bytes, not truth, authorship or preregistration time.',
        ],
    }


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('mode', choices=('demo', 'analyze'))
    cli.add_argument('--expected-input-sha256')
    cli.add_argument('--measurement-unit')
    cli.add_argument('--display-unit')
    cli.add_argument('--minimum')
    cli.add_argument('--better', choices=('lower', 'higher'), default='lower')
    cli.add_argument('--alpha', default='0.05')
    args = cli.parse_args(argv)
    try:
        if args.mode == 'demo':
            if any(x is not None for x in (args.expected_input_sha256, args.measurement_unit,
                                           args.display_unit, args.minimum)):
                raise ValueError('demo uses fixed synthetic inputs and units')
            raw = metric.demo()
            result = analyze(raw, hashlib.sha256(raw).hexdigest(), 'ms', 's', '0.25 ms',
                             args.better, args.alpha)
            result['fixture'] = 'synthetic latency data; no real performance measurement'
        else:
            if any(x is None for x in (args.expected_input_sha256, args.measurement_unit,
                                       args.display_unit, args.minimum)):
                raise ValueError('analyze requires a CSV digest, measurement/display units and minimum')
            raw = sys.stdin.buffer.read(metric.LIMIT + 1)
            if len(raw) > metric.LIMIT:
                raise ValueError('CSV exceeds 2 MiB')
            result = analyze(raw, args.expected_input_sha256, args.measurement_unit,
                             args.display_unit, args.minimum, args.better, args.alpha)
        print(json.dumps(result, ensure_ascii=True, allow_nan=False, sort_keys=True))
        return 0
    except (ValueError, units.UnitError, OSError) as exc:
        print('error: ' + ascii(str(exc)), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
