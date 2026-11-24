"""
Agreement between the video angles and a reference method (goniometer, motion capture).

CSV with one row per comparison:

    metric,video,reference
    knee_ext,146.2,139.0
    knee_ext,149.0,141.5
    hip_closed,52.1,50.0

Instead of a video number you can give a session id in a 'fit' column; the metric is then read
from that fit:  metric,fit,reference

    python scripts/bland_altman.py measurements.csv [--plot out_dir]

Prints bias and 95 % limits of agreement per metric and, with --plot, writes one Bland-Altman
PNG per metric. A consistent bias (e.g. video reads ~8 deg higher than a static goniometer for the
knee) is expected and documented in docs/RESEARCH.md; wide limits are the real problem.
"""
import argparse
import csv
import os
import sys
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src import validation  # noqa: E402
from scripts.repeatability import load_result  # noqa: E402


def read_rows(path):
    pairs = defaultdict(lambda: ([], []))
    cache = {}
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            k = row['metric'].strip()
            if row.get('video'):
                v = float(row['video'])
            else:
                fit = row['fit'].strip()
                cache.setdefault(fit, load_result(fit))
                v = cache[fit]['metrics'].get(k)
            pairs[k][0].append(v)
            pairs[k][1].append(float(row['reference']))
    return pairs


def plot(metric, r, out_dir):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    ax.scatter(r['mean'], r['diff'], s=18, color='#3D63E6')
    for y, ls in ((r['bias'], '-'), (r['loa'][0], '--'), (r['loa'][1], '--')):
        ax.axhline(y, color='#444', linestyle=ls, linewidth=1)
    ax.set_xlabel('Mean of video and reference (°)')
    ax.set_ylabel('Video − reference (°)')
    ax.set_title(f"{metric}: bias {r['bias']:+.1f}°, LoA {r['loa'][0]:+.1f} to {r['loa'][1]:+.1f}° (n={r['n']})")
    fig.tight_layout()
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f'bland_altman_{metric}.png')
    fig.savefig(path)
    plt.close(fig)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('csv')
    ap.add_argument('--plot', metavar='DIR', help='write Bland-Altman plots here')
    args = ap.parse_args(argv)
    results = {}
    print(f"{'Metric':<12}{'n':>4}{'Bias':>8}{'LoA low':>10}{'LoA high':>10}")
    for k, (video, ref) in read_rows(args.csv).items():
        r = validation.bland_altman(video, ref)
        if not r:
            print(f"{k:<12} fewer than 3 pairs, skipped")
            continue
        results[k] = r
        print(f"{k:<12}{r['n']:>4}{r['bias']:>+7.1f}°{r['loa'][0]:>+9.1f}°{r['loa'][1]:>+9.1f}°")
        if args.plot:
            print('  ', plot(k, r, args.plot))
    return results


if __name__ == '__main__':
    main()
