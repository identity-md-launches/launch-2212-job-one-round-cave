#!/usr/bin/env python3
"""Compare explicitly proposed input refinements using exact dimensional enclosures."""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
import sys

import interval_flint as interval


def width(result):
    return Fraction(result['base_upper']) - Fraction(result['base_lower'])


def evaluate(request):
    required = {'variables', 'expression', 'to', 'within', 'refinements'}
    if type(request) is not dict or set(request) != required:
        raise interval.IntervalError('request needs exactly variables, expression, to, within, refinements')
    original = {key: request[key] for key in required - {'refinements'}}
    baseline = interval.evaluate(original)
    refinements = request['refinements']
    if type(refinements) is not dict or not refinements:
        raise interval.IntervalError('refinements must be a nonempty object')
    # Validate every proposed domain before producing any comparisons.
    for name, pair in refinements.items():
        if name not in original['variables']:
            raise interval.IntervalError('refinement names an unknown input')
        before = interval.interval_pair(original['variables'][name])
        after = interval.interval_pair(pair)
        if before.dims != after.dims:
            raise interval.IntervalError('refinement dimensions differ from original input')
        if not before.lo <= after.lo <= after.hi <= before.hi:
            raise interval.IntervalError('refinement must be contained in original input')

    def scenario(changes):
        changed = dict(original)
        changed['variables'] = dict(original['variables'], **changes)
        result = interval.evaluate(changed)
        # Interval inclusion is essential; fail explicitly if the engine regresses.
        if not (Fraction(baseline['base_lower']) <= Fraction(result['base_lower'])
                <= Fraction(result['base_upper']) <= Fraction(baseline['base_upper'])):
            raise interval.IntervalError('refined enclosure escaped baseline')
        return {'result': result,
                'base_width': interval.engine.exact_decimal(width(result)),
                'base_width_reduction': interval.engine.exact_decimal(width(baseline) - width(result))}

    individual = []
    for name in sorted(refinements):
        item = scenario({name: refinements[name]})
        item['variable'] = name
        item['input'] = refinements[name]
        individual.append(item)
    individual.sort(key=lambda item: (-Fraction(item['base_width_reduction']), item['variable']))
    return {'expression': original['expression'], 'baseline': baseline,
            'baseline_base_width': interval.engine.exact_decimal(width(baseline)),
            'individual': individual, 'combined': scenario(refinements),
            'method': 'one proposed refinement at a time, then all together; exact interval enclosures',
            'interpretation': 'conditional on supplied narrower bounds; width reductions are not additive uncertainty contributions'}


def demo_request():
    return {'variables': {'distance': ['90 m', '110 m'], 'time': ['9 s', '11 s']},
            'expression': 'distance / time', 'to': 'm/s', 'within': ['9 m/s', '11 m/s'],
            'refinements': {'distance': ['99 m', '101 m'], 'time': ['9.9 s', '10.1 s']}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('demo', 'run'))
    args = parser.parse_args(argv)
    try:
        request = demo_request() if args.command == 'demo' else interval.decode(
            sys.stdin.buffer.read(interval.MAX_BYTES + 1))
        result = evaluate(request)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 1 if result['combined']['result'].get('within', {}).get('fully_within') is False else 0
    except (interval.IntervalError, interval.engine.UnitError, ZeroDivisionError) as exc:
        print(f'resolution-flint: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
