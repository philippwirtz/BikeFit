"""
Front / rear view checks (frontal plane). BETA and report-only: these produce soft hints,
never a fit score, because no frontal clip has been validated against this code yet.

Definitions (all in degrees, image x to the right, y down):
- Knee deviation (a 2D FPPA): the angle between the thigh (hip->knee) and the shank
  (knee->ankle) in the image. Positive = knee drifts toward the midline (valgus),
  negative = outward (varus). "Toward the midline" is decided per frame from the hip
  positions, so it works for both front and rear views.
- Knee tracking value per leg: the 5th/95th percentile of that series (a robust peak).
- Pelvic rock: peak-to-peak (95th - 5th percentile) of the hip-line tilt from horizontal.
- Symmetry: |median knee deviation of the left leg - that of the right leg|.

Flag thresholds sit at the top of the healthy range, not near the mean, because healthy
riders already show real frontal movement and 2D measurement noise is ~3 deg (smallest
detectable difference ~7.5-9 deg). See docs/RESEARCH.md for the sources.
"""
import numpy as np

CONF_MIN = 0.35
KNEE_FLAG_DEG = 10.0
PELVIS_FLAG_DEG = 12.0
SYMMETRY_FLAG_DEG = 9.0
MIN_FRAMES = 30
MIN_THIGH_FRACTION = 0.6  # of the leg's 90th-percentile thigh length in the image
SIDE_ON_RATIO = 0.25  # hip separation / thigh length; below this the clip is side-on, not front/rear

_LEG_JOINTS = ('hip', 'knee', 'ankle')


def _lean(v):
    """Angle of a vector from straight down, in degrees (+ = toward image right)."""
    return np.degrees(np.arctan2(v[0], v[1]))


def frame_metrics(kp):
    """One frame's metrics from {name: (x, y, conf)}, or None when a needed joint is missing."""
    need = [f'{s}_{j}' for s in ('left', 'right') for j in _LEG_JOINTS]
    if any(k not in kp or kp[k][2] < CONF_MIN for k in need):
        return None
    # Name legs by image position, not by the model's left/right label (which can flip).
    a, b = sorted(('left', 'right'), key=lambda s: kp[f'{s}_hip'][0])
    out, thigh = {}, []
    for name, side, medial in (('img_left', a, 1.0), ('img_right', b, -1.0)):
        hip, knee, ankle = (np.asarray(kp[f'{side}_{j}'][:2], float) for j in _LEG_JOINTS)
        out[name] = medial * (_lean(knee - hip) - _lean(ankle - knee))
        thigh.append(np.linalg.norm(knee - hip))
        out[name + '_len'] = float(thigh[-1])
    ha, hb = np.asarray(kp[f'{a}_hip'][:2], float), np.asarray(kp[f'{b}_hip'][:2], float)
    out['tilt'] = float(np.degrees(np.arctan2(hb[1] - ha[1], hb[0] - ha[0])))
    out['hip_sep'] = float(abs(hb[0] - ha[0]) / max(np.mean(thigh), 1e-6))
    return out


def _side_names(view):
    """Image-left/right leg -> the rider's anatomical side. A front view mirrors the rider."""
    return ('right', 'left') if view == 'front' else ('left', 'right')


def summarize(rows, view):
    """Aggregate per-frame metrics into readings and soft flags. None if too little data."""
    rows = [r for r in rows if r]
    if len(rows) < MIN_FRAMES:
        return None
    col = lambda k: np.array([r[k] for r in rows])  # noqa: E731
    left_name, right_name = _side_names(view)
    knee = {}
    for key, side in (('img_left', left_name), ('img_right', right_name)):
        # Near the top of the stroke the thigh points at the camera and its image line is a few pixels of
        # noise, so its angle is meaningless. Judge the knee only while the thigh is clearly visible.
        length = col(key + '_len')
        dev = col(key)[length >= MIN_THIGH_FRACTION * np.percentile(length, 90)]
        if len(dev) < MIN_FRAMES:
            return None
        knee[side] = {'median': float(np.median(dev)), 'medial_peak': float(np.percentile(dev, 95)),
                      'lateral_peak': float(-np.percentile(dev, 5))}
    tilt = col('tilt')
    rock = float(np.percentile(tilt, 95) - np.percentile(tilt, 5))
    symmetry = abs(knee['left']['median'] - knee['right']['median'])

    flags = []
    for side, k in knee.items():
        if k['medial_peak'] > KNEE_FLAG_DEG:
            flags.append({'key': 'knee_in', 'side': side, 'title': f"Your {side} knee drifts inward",
                          'detail': f"It moves up to {k['medial_peak']:.0f}° toward the frame midline "
                                    "(flag at 10°). Check cleat rotation and wedges, foot support, and stance width."})
        if k['lateral_peak'] > KNEE_FLAG_DEG:
            flags.append({'key': 'knee_out', 'side': side, 'title': f"Your {side} knee drifts outward",
                          'detail': f"It moves up to {k['lateral_peak']:.0f}° away from the midline "
                                    "(flag at 10°). Check cleat rotation, stance width and pedal spacers."})
    if symmetry > SYMMETRY_FLAG_DEG and not flags:  # a one-sided drift already explains the difference
        flags.append({'key': 'asymmetry', 'side': None, 'title': "Your legs track differently",
                      'detail': f"The two knees differ by {symmetry:.0f}° (flag at 9°). Compare cleat set-up "
                                "left and right, and consider a leg-length or flexibility difference."})
    if rock > PELVIS_FLAG_DEG:
        flags.append({'key': 'pelvis', 'side': None, 'title': "Your pelvis rocks side to side",
                      'detail': f"The hip line tilts {rock:.0f}° peak to peak (flag at 12°). "
                                "A saddle that is a little high or too narrow is the usual cause."})
    return {'view': view, 'frames': len(rows), 'knee': knee, 'pelvis_rock': rock, 'symmetry': float(symmetry),
            'hip_sep_ratio': float(np.median(col('hip_sep'))), 'flags': flags,
            'thresholds': {'knee': KNEE_FLAG_DEG, 'pelvis': PELVIS_FLAG_DEG, 'symmetry': SYMMETRY_FLAG_DEG}}


def recommendations(summary):
    """Flags as plan items (priority 3: hints only), always marked beta."""
    return [{'priority': 3, 'metric': None, 'title': f"{f['title']} (beta)", 'detail': f['detail']}
            for f in summary['flags']]
