"""
Repeatability of the video measurement (SEM, MDC95 and, with several riders, ICC).

Film each rider 3+ times without touching the bike (re-mount the camera between clips),
analyse every clip in the app, then run:

    python scripts/repeatability.py --rider anna 20261124-101500-ab12cd 20261124-102100-ef34gh ... \
                                    --rider ben  20261124-110000-... ...  [--write]

Arguments are session ids (folders under output/sessions) or paths to result.json files.
--write stores the result in assets/validation.json, which the compare view then uses.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src import validation  # noqa: E402

SESSIONS = os.path.join(validation.ROOT, 'output', 'sessions')


def load_result(ref):
    path = ref if ref.endswith('.json') else os.path.join(SESSIONS, ref, 'result.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--rider', nargs='+', action='append', metavar=('NAME', 'FIT'), required=True,
                    help='rider name followed by the fits filmed without changes')
    ap.add_argument('--write', action='store_true', help='save to assets/validation.json')
    args = ap.parse_args(argv)

    data = {name: [load_result(r) for r in refs] for name, *refs in args.rider}
    engines = {d.get('backend') for fits in data.values() for d in fits}
    out = {'created': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'engines': sorted(e for e in engines if e),
           'metrics': {}}
    print(f"{'Metric':<12}{'SEM':>7}{'MDC95':>8}{'ICC':>7}  riders/fits")
    for k in validation.METRIC_KEYS:
        groups = {name: [d['metrics'].get(k) or None for d in fits] for name, fits in data.items()}
        r = validation.repeatability(groups)
        if not r:
            continue
        out['metrics'][k] = r
        icc = f"{r['icc']:.2f}" if r.get('icc') is not None else '–'
        print(f"{k:<12}{r['sem']:>6.1f}°{r['mdc95']:>7.1f}°{icc:>7}  {r['riders']}/{r['repeats']}")
    if len(engines) > 1:
        print("Warning: these fits used different pose engines; repeat with one engine.")
    if args.write:
        with open(validation.VALIDATION_PATH, 'w', encoding='utf-8') as f:
            json.dump(out, f, indent=2)
        print(f"Saved to {validation.VALIDATION_PATH}")
    return out


if __name__ == '__main__':
    main()
