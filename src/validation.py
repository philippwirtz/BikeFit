"""
Measurement-quality statistics: repeatability (ICC, SEM, MDC) and agreement (Bland-Altman).

* Repeatability: film the same rider several times without changing the bike. The spread between
  those repeats is the measurement noise. SEM = within-rider SD; MDC95 = 1.96 * sqrt(2) * SEM is the
  smallest change between two fits that is unlikely to be noise (Weir 2005).
  With several riders, ICC(2,1) (two-way random, absolute agreement; Shrout & Fleiss 1979) says how
  well the method separates riders.
* Agreement: compare the video angle with a reference (goniometer, motion capture) on the same
  pedal strokes. Bias = mean difference, limits of agreement = bias +/- 1.96 SD (Bland & Altman 1986).

Results written to assets/validation.json are picked up by the app: the compare view then uses the
MDC instead of the per-fit confidence intervals to decide whether a change is real.
"""
import json
import math
import os

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VALIDATION_PATH = os.path.join(ROOT, 'assets', 'validation.json')
METRIC_KEYS = ('knee_ext', 'knee_flex', 'hip_closed', 'torso', 'shoulder', 'elbow')


def load(path=VALIDATION_PATH):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def icc_2_1(table):
    """
    ICC(2,1) for an n_subjects x k_repeats table (no missing values).
    Returns None with fewer than 2 subjects or 2 repeats.
    """
    x = np.asarray(table, float)
    if x.ndim != 2 or x.shape[0] < 2 or x.shape[1] < 2 or not np.isfinite(x).all():
        return None
    n, k = x.shape
    grand = x.mean()
    ssr = k * np.sum((x.mean(axis=1) - grand) ** 2)
    ssc = n * np.sum((x.mean(axis=0) - grand) ** 2)
    sst = np.sum((x - grand) ** 2)
    sse = sst - ssr - ssc
    msr, msc, mse = ssr / (n - 1), ssc / (k - 1), sse / ((n - 1) * (k - 1))
    den = msr + (k - 1) * mse + k * (msc - mse) / n
    return float((msr - mse) / den) if den > 0 else None


def repeatability(groups):
    """
    groups: {subject: [value, value, ...]} repeated measurements of one metric per rider.
    Returns SEM (pooled within-rider SD), MDC95, the number of repeats and, with 2+ riders, ICC(2,1).
    """
    groups = {s: [float(v) for v in vs if v is not None and math.isfinite(float(v))] for s, vs in groups.items()}
    groups = {s: vs for s, vs in groups.items() if len(vs) >= 2}
    if not groups:
        return None
    ss = sum(np.sum((np.array(v) - np.mean(v)) ** 2) for v in groups.values())
    dof = sum(len(v) - 1 for v in groups.values())
    sem = math.sqrt(ss / dof) if dof else None
    out = {'sem': sem, 'mdc95': 1.96 * math.sqrt(2) * sem if sem is not None else None,
           'riders': len(groups), 'repeats': sum(len(v) for v in groups.values())}
    k = min(len(v) for v in groups.values())
    if len(groups) >= 2:
        out['icc'] = icc_2_1([v[:k] for v in groups.values()])
    return out


def bland_altman(video, reference):
    """Bias and 95% limits of agreement of video minus reference."""
    a, b = np.asarray(video, float), np.asarray(reference, float)
    ok = np.isfinite(a) & np.isfinite(b)
    d = a[ok] - b[ok]
    if len(d) < 3:
        return None
    bias, sd = float(d.mean()), float(d.std(ddof=1))
    return {'n': int(len(d)), 'bias': bias, 'sd': sd, 'loa': [bias - 1.96 * sd, bias + 1.96 * sd],
            'mean': ((a[ok] + b[ok]) / 2).tolist(), 'diff': d.tolist()}


def change_is_real(delta, half_ci_a=None, half_ci_b=None, mdc=None):
    """
    True when a change between two fits is larger than measurement noise.
    Prefers a validated MDC; otherwise combines the two fits' 95% CI half-widths.
    Returns None when there is nothing to judge it against.
    """
    if mdc:
        return abs(delta) > mdc
    if half_ci_a is None or half_ci_b is None:
        return None
    return abs(delta) > math.sqrt(half_ci_a ** 2 + half_ci_b ** 2)
