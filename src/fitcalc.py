"""
Fit calculations built on the measured pedal stroke.

Everything here works on a *bike frame* in millimetres:
origin at the bottom bracket (BB), x forward, y up. The model is built from the
stored per-frame track of a side-view fit, so it also works for fits saved by
older versions and for the bundled demo.

What-if model
-------------
The rider is reduced to a planar linkage that is driven by the crank:

* hip (H), shoulder (S) and hand (W) are fixed points (their stroke means),
* the foot is rigid relative to the pedal: ankle(theta) = pedal(theta) + offset(theta),
  where offset is the measured ankle - ball-of-foot vector, Fourier-fitted on crank angle,
* thigh and shank are rigid links, so the knee follows from two-link inverse kinematics,
* the torso length and the shoulder-hand distance are rigid (elbow bend unchanged), so a moved
  hip or hand moves the shoulder to the intersection of those two circles.

A setting change moves H (saddle height along the seat tube, setback), the pedal circle (crank
length) or W (stem length, bar height). Predictions are reported as the measured value plus the
model's *change*, so the model's own bias against the measurement cancels out.
Sources for the reference formulas are in docs/RESEARCH.md.
"""
import math

import numpy as np

from src import kinematics as kin

DEFAULT_SEAT_TUBE_DEG = 73.0
CRANK_CHOICES = (150.0, 155.0, 160.0, 162.5, 165.0, 167.5, 170.0, 172.5, 175.0)
LEMOND_FACTOR = 0.883          # BB centre -> saddle top along the seat tube, x inseam
HAMLEY_FACTOR = 1.09           # pedal axle (crank in line with seat tube) -> saddle top, x inseam
TIBIA_CRANK_FRACTION = 0.41    # Martin & Spirduso (2001): optimal crank = 41 % of tibia length
MIN_SUGGEST_CRANK = 160.0      # shortest crank the app suggests on its own
MIN_PARTIAL_GAIN_DEG = 2.0     # a crank change must open the hip at least this much to be worth suggesting
AIR_DENSITY = 1.204            # kg/m^3, 20 degC at sea level
DRAG_COEFF = 0.7               # assumed Cd for rider + bike (Cd x A_p ~ 0.25 m^2 for a TT rider)
AERO_SPEED_KMH = 35.0


# --------------------------------------------------------------------------- #
# Model building
# --------------------------------------------------------------------------- #
def _arr(track, name):
    a = track['joints'].get(name)
    if a is None:
        return None
    fw, fh = track['size']
    return np.array([[np.nan, np.nan] if p is None else [p[0] * fw, p[1] * fh] for p in a], float)


def build_model(res):
    """Rider linkage in mm from a stored side-view result, or None when it can't be built."""
    if res.get('mode') != 'video':
        return None
    track, bio = res.get('track') or {}, res.get('biomech') or {}
    crank, s = track.get('crank'), bio.get('mm_per_px')
    if not (crank and s and track.get('theta') and bio.get('thigh_px') and bio.get('shank_px')):
        return None
    fw, fh = track['size']
    fwd = 1.0 if track.get('facing') == 'right' else -1.0
    cx, cy = crank['cx'] * fw, crank['cy'] * fh
    theta = np.array([np.nan if v is None else v for v in track['theta']], float)

    def to_bike(p):
        return np.column_stack([(p[:, 0] - cx) * fwd * s, (cy - p[:, 1]) * s])

    pts = {}
    for j in ('hip', 'shoulder', 'wrist', 'elbow', 'ankle', 'ball', 'knee'):
        a = _arr(track, j)
        if a is None:
            return None
        pts[j] = to_bike(a)

    def mean_pt(name):
        p = pts[name][np.isfinite(pts[name]).all(axis=1)]
        return np.median(p, axis=0) if len(p) > 10 else None

    H, S, W, E = (mean_pt(j) for j in ('hip', 'shoulder', 'wrist', 'elbow'))
    if H is None or S is None:
        return None
    off = pts['ankle'] - pts['ball']
    fx, fy = kin.harmonic_fit(theta, off[:, 0]), kin.harmonic_fit(theta, off[:, 1])
    # The hip rocks through the stroke (lowest near the bottom), which matters for knee extension
    hx, hy = kin.harmonic_fit(theta, pts['hip'][:, 0]), kin.harmonic_fit(theta, pts['hip'][:, 1])
    if not (fx and fy and hx and hy):
        return None
    hx, hy = np.array(hx['coef']), np.array(hy['coef'])
    hx[0] = hy[0] = 0.0  # periodic part only; the mean is H
    crank_mm = float((res.get('rider') or {}).get('crank_mm') or 172.5)
    m = {
        'H': H.tolist(), 'S': S.tolist(), 'W': None if W is None else W.tolist(),
        'E': None if E is None else E.tolist(),
        'L1': float(bio['thigh_px'] * s), 'L2': float(bio['shank_px'] * s),
        'crank_mm': crank_mm, 'off_x': fx['coef'].tolist(), 'off_y': fy['coef'].tolist(),
        'hip_x': hx.tolist(), 'hip_y': hy.tolist(),
    }
    m['torso_len'] = float(np.linalg.norm(S - H))
    m['arm_reach'] = None if W is None else float(np.linalg.norm(S - W))
    _calibrate_legs(m, res)
    return m


def _calibrate_legs(m, res):
    """
    Pick effective thigh and shank lengths so the model's knee curve matches the measured one.

    Median segment lengths from 2D video are slightly off (foreshortening, joint-centre offsets), and
    near full extension a small length error moves the knee angle a lot. Matching the measured curve
    keeps the model's sensitivity (degrees per mm of saddle) realistic.
    """
    curves = (res.get('stroke') or {}).get('curves') or {}
    knee, grid = curves.get('knee'), curves.get('theta')
    if not knee or not grid:
        m['calibrated'] = False
        return
    knee, idx = np.asarray(knee, float), np.round(np.asarray(grid)).astype(int) % 360
    L1, L2 = m['L1'], m['L2']
    best = (np.inf, 1.0, 1.0)
    for a in np.linspace(0.9, 1.1, 21):
        for b in np.linspace(0.9, 1.1, 21):
            m['L1'], m['L2'] = L1 * a, L2 * b
            k = _leg(m)[0][idx]
            err = float(np.mean((k - knee) ** 2))
            if err < best[0]:
                best = (err, a, b)
    m['L1'], m['L2'] = L1 * best[1], L2 * best[2]
    m['calibrated'] = True
    m['calib_rms'] = math.sqrt(best[0])


# --------------------------------------------------------------------------- #
# Forward kinematics
# --------------------------------------------------------------------------- #
def _angle(a, b, c):
    """Inner angle at b, degrees (vectorised over rows)."""
    v1, v2 = np.asarray(a) - np.asarray(b), np.asarray(c) - np.asarray(b)
    cos = np.sum(v1 * v2, axis=-1) / (np.linalg.norm(v1, axis=-1) * np.linalg.norm(v2, axis=-1))
    return np.degrees(np.arccos(np.clip(cos, -1, 1)))


def _circle_meet(p0, r0, p1, r1):
    """Upper intersection of two circles (higher y), or the closest point when they don't meet."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = float(np.linalg.norm(p1 - p0))
    if d < 1e-6:
        return p0 + [0, r0], False
    if d > r0 + r1 or d < abs(r0 - r1):
        return p0 + (p1 - p0) / d * r0, False
    a = (r0 ** 2 - r1 ** 2 + d ** 2) / (2 * d)
    h = math.sqrt(max(r0 ** 2 - a ** 2, 0.0))
    mid = p0 + a * (p1 - p0) / d
    perp = np.array([-(p1 - p0)[1], (p1 - p0)[0]]) / d
    c1, c2 = mid + h * perp, mid - h * perp
    return (c1 if c1[1] >= c2[1] else c2), True


def _leg(m, H=None, crank_mm=None):
    """Knee angle (deg) and knee position over the crank grid for a hip position H (stroke mean)."""
    crank = float(crank_mm or m['crank_mm'])
    H = np.array(m['H'] if H is None else H, float)
    th = kin.GRID
    rad = np.radians(th)
    hip = H + np.column_stack([kin.eval_harmonic(np.array(m['hip_x']), th),
                               kin.eval_harmonic(np.array(m['hip_y']), th)])
    pedal = np.column_stack([crank * np.sin(rad), crank * np.cos(rad)])
    ankle = pedal + np.column_stack([kin.eval_harmonic(np.array(m['off_x']), th),
                                     kin.eval_harmonic(np.array(m['off_y']), th)])
    L1, L2 = m['L1'], m['L2']
    v = ankle - hip
    d = np.linalg.norm(v, axis=1)
    dc = np.clip(d, abs(L1 - L2) + 1e-6, L1 + L2 - 1e-6)
    knee = np.degrees(np.arccos(np.clip((L1 ** 2 + L2 ** 2 - dc ** 2) / (2 * L1 * L2), -1, 1)))
    knee[d >= L1 + L2] = 180.0
    phi = np.arccos(np.clip((L1 ** 2 + dc ** 2 - L2 ** 2) / (2 * L1 * dc), -1, 1))
    u = v / d[:, None]
    # Rotate the hip->ankle direction towards the front of the bike to place the knee
    rot = lambda ang: np.column_stack([u[:, 0] * np.cos(ang) - u[:, 1] * np.sin(ang),  # noqa: E731
                                       u[:, 0] * np.sin(ang) + u[:, 1] * np.cos(ang)])
    k1, k2 = hip + L1 * rot(phi), hip + L1 * rot(-phi)
    K = np.where((k1[:, 0] >= k2[:, 0])[:, None], k1, k2)
    return knee, K, pedal, crank, hip


def simulate(m, saddle_mm=0.0, setback_mm=0.0, crank_mm=None, stem_mm=0.0, bar_mm=0.0,
             seat_tube_deg=DEFAULT_SEAT_TUBE_DEG):
    """
    Model angles for one set-up. saddle_mm raises the saddle along the seat tube, setback_mm moves it
    back, stem_mm lengthens the reach to the bars, bar_mm raises the bars.
    """
    a = math.radians(seat_tube_deg)
    H = np.array(m['H']) + saddle_mm * np.array([-math.cos(a), math.sin(a)]) + [-setback_mm, 0.0]
    knee, K, pedal, crank, hip_pts = _leg(m, H, crank_mm)

    S, reachable = np.array(m['S']), True
    W = None
    if m.get('W') is not None:
        W = np.array(m['W']) + [stem_mm, bar_mm]
        S, reachable = _circle_meet(H, m['torso_len'], W, m['arm_reach'])
    else:
        S = H + (np.array(m['S']) - np.array(m['H']))
    hip = _angle(S + (hip_pts - H), hip_pts, K)  # the upper body rides along with the hip
    tv = S - H
    out = {
        'knee_ext': float(knee.max()), 'knee_flex': float(knee.min()),
        'hip_closed': float(hip.min()), 'hip_open': float(hip.max()),
        'torso': float(math.degrees(math.atan2(abs(tv[1]), abs(tv[0])))),
        'kops_mm': float(K[90, 0] - pedal[90, 0]),
        'hip': H.tolist(), 'shoulder': S.tolist(), 'hand': None if W is None else W.tolist(),
        'reachable': bool(reachable), 'crank_mm': crank,
    }
    if W is not None:
        out['shoulder_open'] = float(_angle(H, S, W))  # torso vs shoulder->hand line
    return out


def what_if(res, m=None, **change):
    """Predicted metrics for a set-up change: measured value + modelled change."""
    m = m or build_model(res)
    if m is None:
        return None
    sta = (res.get('rider') or {}).get('seat_tube_deg') or DEFAULT_SEAT_TUBE_DEG
    base, new = simulate(m, seat_tube_deg=sta), simulate(m, seat_tube_deg=sta, **change)
    metrics = res.get('metrics') or {}
    bio = res.get('biomech') or {}
    pred = {}
    for k in ('knee_ext', 'knee_flex', 'hip_closed', 'torso'):
        meas = metrics.get(k)
        pred[k] = {'now': meas, 'new': (meas + new[k] - base[k]) if meas else None, 'delta': new[k] - base[k]}
    if metrics.get('shoulder') and 'shoulder_open' in base:
        d = new['shoulder_open'] - base['shoulder_open']
        pred['shoulder'] = {'now': metrics['shoulder'], 'new': metrics['shoulder'] + d, 'delta': d}
    kops = bio.get('kops_mm')
    pred['kops_mm'] = {'now': kops, 'new': None if kops is None else kops + new['kops_mm'] - base['kops_mm'],
                       'delta': new['kops_mm'] - base['kops_mm']}
    return {'pred': pred, 'reachable': new['reachable'], 'change': change,
            'model_bias': {k: base[k] - metrics[k] for k in ('knee_ext', 'knee_flex', 'hip_closed')
                           if metrics.get(k)}}


def saddle_for_knee_ext(m, target_delta, crank_mm=None, setback_mm=0.0, sta=DEFAULT_SEAT_TUBE_DEG):
    """Saddle change (mm) that shifts peak knee extension by target_delta degrees (bisection)."""
    base = simulate(m, crank_mm=crank_mm, setback_mm=setback_mm, seat_tube_deg=sta)['knee_ext']
    ref = simulate(m, seat_tube_deg=sta)['knee_ext'] + target_delta
    lo, hi = -60.0, 60.0
    f = lambda x: simulate(m, saddle_mm=x, crank_mm=crank_mm, setback_mm=setback_mm,  # noqa: E731
                           seat_tube_deg=sta)['knee_ext'] - ref
    if f(lo) > 0 or f(hi) < 0:
        return None
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    del base
    return (lo + hi) / 2


# --------------------------------------------------------------------------- #
# Crank length
# --------------------------------------------------------------------------- #
def crank_options(res, ranges, m=None):
    """
    Effect of each common crank length with the saddle re-set so knee extension stays as measured.
    Returns rows plus a suggestion when the current crank closes the hip or knee too far.
    """
    m = m or build_model(res)
    if m is None:
        return None
    sta = (res.get('rider') or {}).get('seat_tube_deg') or DEFAULT_SEAT_TUBE_DEG
    metrics = res.get('metrics') or {}
    base = simulate(m, seat_tube_deg=sta)
    rows = []
    for c in CRANK_CHOICES:
        dh = saddle_for_knee_ext(m, 0.0, crank_mm=c, sta=sta)
        if dh is None:
            continue
        s = simulate(m, saddle_mm=dh, crank_mm=c, seat_tube_deg=sta)
        rows.append({'crank_mm': c, 'saddle_mm': dh,
                     'hip_closed': metrics.get('hip_closed', 0) + s['hip_closed'] - base['hip_closed'],
                     'knee_flex': metrics.get('knee_flex', 0) + s['knee_flex'] - base['knee_flex'],
                     'current': abs(c - m['crank_mm']) < 0.1})
    out = {'rows': rows, 'current_mm': m['crank_mm'], 'suggest_mm': None}
    shank = (res.get('biomech') or {}).get('shank_mm')
    if shank and 330 <= shank <= 470:  # outside this the video scale is off, so the rule would mislead
        out['tibia_rule_mm'] = TIBIA_CRANK_FRACTION * shank
    hc, kf = metrics.get('hip_closed'), metrics.get('knee_flex')
    if not (hc and kf and rows):
        return out
    hlo, klo = ranges['hip_closed'][0], ranges['knee_flex'][0]
    if hc >= hlo - 2 and kf >= klo - 3:
        return out
    # Only lengths that are easy to buy and not a drastic jump from the current crank
    shorter = sorted((r for r in rows if MIN_SUGGEST_CRANK <= r['crank_mm'] < m['crank_mm'] - 0.1),
                     key=lambda r: -r['crank_mm'])
    for r in shorter:  # the smallest reduction that brings both into range
        if r['hip_closed'] >= hlo - 2 and r['knee_flex'] >= klo - 3:
            out['suggest_mm'] = r['crank_mm']
            out['suggest'] = r
            break
    else:
        if shorter:
            best = shorter[-1]
            gain = best['hip_closed'] - hc
            if gain >= MIN_PARTIAL_GAIN_DEG:
                out['suggest_mm'] = best['crank_mm']
                out['suggest'] = best
                out['partial'] = True
    return out


# --------------------------------------------------------------------------- #
# Inseam formulas, fit coordinates, aero
# --------------------------------------------------------------------------- #
def inseam_saddle(inseam_cm, crank_mm=172.5):
    """Static starting points for saddle height (mm, BB centre to saddle top along the seat tube)."""
    if not inseam_cm:
        return None
    ins = inseam_cm * 10.0
    return {'lemond_mm': LEMOND_FACTOR * ins,
            'hamley_mm': HAMLEY_FACTOR * ins - crank_mm,  # their pedal-to-saddle length minus the crank
            'inseam_mm': ins}


def fit_coordinates(res, m=None):
    """Rider contact-point coordinates in mm relative to the BB, for moving a position to another bike."""
    m = m or build_model(res)
    if m is None:
        return None
    H, S = m['H'], m['S']
    out = {'hip_x': H[0], 'hip_y': H[1], 'hip_dist': math.hypot(*H), 'shoulder_x': S[0], 'shoulder_y': S[1]}
    if m.get('W') is not None:
        W = m['W']
        out.update(hand_x=W[0], hand_y=W[1], hip_to_hand_x=W[0] - H[0], hip_to_hand_drop=H[1] - W[1])
    rider = res.get('rider') or {}
    adj = (res.get('biomech') or {}).get('saddle_adj_mm')
    if rider.get('saddle_height_mm'):
        out['saddle_now_mm'] = rider['saddle_height_mm']
        out['saddle_target_mm'] = rider['saddle_height_mm'] + (adj or 0.0)
    ins = inseam_saddle(rider.get('inseam_cm'), rider.get('crank_mm') or 172.5)
    if ins:
        out.update(ins)
    return out


def frontal_area(mass_kg, torso_deg, seat_tube_deg=DEFAULT_SEAT_TUBE_DEG):
    """Projected frontal area (m^2) of the rider, Heil (2001): fitted for trunk angles 5-25 deg."""
    if not mass_kg or not torso_deg or torso_deg <= 0:
        return None
    return 0.00433 * seat_tube_deg ** 0.172 * max(torso_deg, 1.0) ** 0.0965 * mass_kg ** 0.762


def aero_estimate(mass_kg, torso_deg, speed_kmh=AERO_SPEED_KMH, seat_tube_deg=DEFAULT_SEAT_TUBE_DEG):
    """Rough aero power at a speed and the saving per 5 deg lower torso. Bike frontal area not included."""
    a = frontal_area(mass_kg, torso_deg, seat_tube_deg)
    if a is None:
        return None
    v = speed_kmh / 3.6
    p = 0.5 * AIR_DENSITY * DRAG_COEFF * a * v ** 3
    lower = max(torso_deg - 5.0, 1.0)
    a2 = frontal_area(mass_kg, lower, seat_tube_deg)
    p2 = 0.5 * AIR_DENSITY * DRAG_COEFF * a2 * v ** 3
    return {'area_m2': a, 'cda_m2': DRAG_COEFF * a, 'speed_kmh': speed_kmh, 'power_w': p,
            'lower_torso_deg': lower, 'saving_w': p - p2, 'saving_pct': 100 * (1 - a2 / a),
            'extrapolated': not (5 <= torso_deg <= 25)}


def aero_for_torso(mass_kg, torso_now, torso_new, speed_kmh=AERO_SPEED_KMH):
    """Aero power change (W) between two torso angles; + = more power needed."""
    a0, a1 = frontal_area(mass_kg, torso_now), frontal_area(mass_kg, torso_new)
    if a0 is None or a1 is None:
        return None
    v = speed_kmh / 3.6
    return 0.5 * AIR_DENSITY * DRAG_COEFF * (a1 - a0) * v ** 3


# --------------------------------------------------------------------------- #
# Ankle
# --------------------------------------------------------------------------- #
def ankle_profile(res):
    """
    Plantarflexion over the stroke from the stored track: angle between shank and the heel->toe line,
    minus 90 (0 = foot at right angles to the shank, + = toe down). Returns value at peak knee
    extension and the stroke range, or None without heel/toe points.
    """
    track = res.get('track') or {}
    if res.get('mode') != 'video' or not track.get('theta') or res.get('backend') == 'yolo-pose':
        return None
    pts = {j: _arr(track, j) for j in ('knee', 'ankle', 'heel', 'toe')}
    if any(v is None for v in pts.values()):
        return None
    v1, v2 = pts['knee'] - pts['ankle'], pts['toe'] - pts['heel']
    with np.errstate(invalid='ignore', divide='ignore'):
        cos = np.sum(v1 * v2, axis=1) / (np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1))
    pf = np.degrees(np.arccos(np.clip(cos, -1, 1))) - 90.0
    theta = np.array([np.nan if v is None else v for v in track['theta']], float)
    f = kin.harmonic_fit(theta, pf)
    if not f or f['r2'] < 0.3:
        return None
    curve = kin.eval_harmonic(f['coef'], kin.GRID)
    at = ((res.get('stroke') or {}).get('events') or {}).get('knee_ext_at', 180.0)
    return {'bdc': float(curve[int(round(at)) % 360]), 'max': float(curve.max()), 'min': float(curve.min()),
            'range': float(np.ptp(curve)), 'resid_sd': f['resid_sd'],
            'curve': [round(float(v), 2) for v in curve[::5]]}
