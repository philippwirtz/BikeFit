"""
BikeFit Unit & Integration Test Suite.
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import core
from src import kinematics as kin
from src import fit_profiles as fp
from src import pose_backends as pb
from src import report
from src import coach
from src import posture


def test_calculate_angle():
    # 90 degree right angle: (0, 1) -> (0, 0) -> (1, 0)
    ang = core.calculate_angle([0, 1], [0, 0], [1, 0])
    assert abs(ang - 90.0) < 1e-4

    # Straight line 180 degrees: (-1, 0) -> (0, 0) -> (1, 0)
    ang180 = core.calculate_angle([-1, 0], [0, 0], [1, 0])
    assert abs(ang180 - 180.0) < 1e-4


def test_horizontal_angle_folding():
    # Facing right 45 deg slope
    ang_r = core.calculate_angle_horizontal([0, 0], [1, 1])
    assert abs(ang_r - 45.0) < 1e-4

    # Facing left equivalent slope (should be folded into 0-90 acute angle)
    ang_l = core.calculate_angle_horizontal([0, 0], [-1, 1])
    assert abs(ang_l - 45.0) < 1e-4


def test_circle_fit():
    # Known circle at (10, 20) with radius 5, plus one gross outlier the robust fit must ignore
    angles = np.linspace(0, 2 * np.pi, 48, endpoint=False)
    pts = np.column_stack([10 + 5 * np.cos(angles), 20 + 5 * np.sin(angles)])
    pts = np.vstack([pts, [[40.0, 40.0]]])
    fit = kin.fit_circle_robust(pts)
    assert fit is not None
    assert abs(fit['cx'] - 10.0) < 0.05 and abs(fit['cy'] - 20.0) < 0.05
    assert abs(fit['r'] - 5.0) < 0.05
    assert fit['coverage'] == 1.0


def test_crank_angle_convention():
    # Rider facing right: 12 o'clock = 0 deg, forward (3 o'clock) = 90, bottom = 180
    pts = np.array([[0, -1], [1, 0], [0, 1], [-1, 0]], float)
    th = kin.crank_angle(pts, 0, 0, fwd=1.0)
    assert np.allclose(th, [0, 90, 180, 270])
    # Facing left mirrors the forward direction
    assert np.allclose(kin.crank_angle(pts, 0, 0, fwd=-1.0), [0, 270, 180, 90])


def test_harmonic_fit_recovers_true_extremes_from_sparse_noisy_samples():
    # 20 strokes sampled at ~20 frames/stroke with jitter: no frame lands exactly on the peak
    rng = np.random.default_rng(0)
    theta = (np.arange(400) * 18.7) % 360
    truth = lambda t: 105 + 38 * np.cos(np.radians(t - 175)) + 4 * np.cos(np.radians(2 * (t - 175)))  # noqa: E731
    y = truth(theta) + rng.normal(0, 2.0, len(theta))
    fit = kin.harmonic_fit(theta, y)
    st = kin.curve_stats(fit['coef'])
    grid = np.arange(0, 360, 0.5)
    assert abs(st['max'] - truth(grid).max()) < 0.8
    assert abs(st['min'] - truth(grid).min()) < 0.8
    assert fit['r2'] > 0.98
    stroke = (np.arange(400) // 20).astype(int)
    ci = kin.bootstrap_ci(theta, y, stroke, lambda c: float(np.max(kin.eval_harmonic(c, kin.GRID))))
    assert ci[0] < st['max'] < ci[1] and ci[1] - ci[0] < 2.0


def test_viterbi_repairs_left_right_swaps():
    # Two limbs moving on opposite sides of a circle; the pose model swaps labels for 3 frames
    t = np.linspace(0, 4 * np.pi, 120)
    near = np.stack([np.column_stack([100 * np.cos(t), 100 * np.sin(t)])] * 2, axis=1)
    far = -near
    L, R = near.copy(), far.copy()
    L[50:53], R[50:53] = far[50:53], near[50:53]
    swapped = kin.viterbi_identity(L, R, scale=100.0)
    assert swapped[50:53].all() and swapped.sum() == 3


def test_personalized_ranges():
    base = fp.PROFILES['road_endurance']['ranges']
    ranges, notes = fp.personalize('road_endurance', 'limited', ['lower_back'])
    assert ranges['hip_closed'][0] == base['hip_closed'][0] + 8
    assert ranges['torso'][1] == base['torso'][1] + 8
    assert len(notes) == 2
    same, _ = fp.personalize('road_endurance')
    assert same == {k: tuple(v) for k, v in base.items()}


def test_fit_profiles_and_scoring():
    # Test optimal road endurance values
    metrics_optimal = {
        'knee_ext': 145.0,
        'knee_flex': 72.0,
        'hip_closed': 55.0,
        'torso': 50.0,
        'shoulder': 88.0,
        'elbow': 158.0,
    }
    score = fp.fit_score(metrics_optimal, 'road_endurance')
    assert score is not None and score >= 90

    # Test out of range saddle (low knee extension)
    metrics_low_saddle = dict(metrics_optimal, knee_ext=125.0)
    recs = fp.build_recommendations(metrics_low_saddle, 'road_endurance')
    assert any("Raise your saddle" in r['title'] for r in recs)


def test_pose_backends_available():
    avail = pb.available()
    assert 'mediapipe' in avail
    assert 'rtmpose' in avail
    assert 'yolo-pose' in avail


def test_yolo_foot_estimate():
    kp = {'right_knee': (100.0, 100.0, 0.9), 'right_ankle': (100.0, 200.0, 0.9)}
    pb.estimate_foot(kp, facing=1.0)
    assert kp['right_toe'][0] > kp['right_ankle'][0] > kp['right_heel'][0]
    pb.estimate_foot(kp, facing=-1.0)
    assert kp['right_toe'][0] < kp['right_ankle'][0] < kp['right_heel'][0]


def test_coach_notes():
    recs = [{'title': 'Raise saddle ~5 mm', 'detail': 'Low knee angle'}]
    text = coach.coach_notes(recs, 'Race road')
    assert "1. Raise saddle ~5 mm" in text and "Golden rule" in text
    assert "leave it alone" in coach.coach_notes([], 'Race road')


def test_pdf_generation_bytes():
    result = {
        'mode': 'video',
        'profile': 'road_endurance',
        'score': 85,
        'metrics': {'knee_ext': 146.0, 'torso': 48.0, 'shoulder': 88.0},
        'statuses': {'knee_ext': 'ok', 'torso': 'ok', 'shoulder': 'ok'},
        'recommendations': [{'title': 'Fit looks great', 'detail': 'All in range'}],
        'warnings': [],
    }
    pdf_bytes = report.generate_fit_report(result, snapshot_paths={})
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b'%PDF')


def _torso_mask(bulge_px):
    """Side-on torso (rider facing right): hip at (100, 300), shoulder at (400, 200)."""
    import cv2
    m = np.zeros((500, 600), np.float32)
    hip, sh = np.array([100., 300.]), np.array([400., 200.])
    n, L = posture.dorsal_normal(hip, sh, 'right')
    s = np.linspace(0, 1, 50)[:, None]
    back = hip + s * (sh - hip) + n * (40 + bulge_px * np.sin(np.pi * s))
    chest = hip + s * (sh - hip) - n * 40
    cv2.fillPoly(m, [np.vstack([back, chest[::-1]]).astype(np.int32)], 1.0)
    return m, hip, sh


def test_back_roundness_flat_vs_rounded():
    flat = posture.back_profile(*_torso_mask(0), 'right')
    hunched = posture.back_profile(*_torso_mask(30), 'right')
    assert flat is not None and hunched is not None
    assert posture.roundness_index(flat[1]) < posture.NEUTRAL_MAX
    assert posture.roundness_index(hunched[1]) >= posture.ROUNDED_MIN
    assert posture.verdict_for(posture.roundness_index(hunched[1])) == 'rounded'


def test_posture_summary_strokes_and_timing():
    mask, hip, sh = _torso_mask(30)
    prof = posture.back_profile(mask, hip, sh, 'right')
    times = np.arange(90) / 30.0
    stroke_id = np.repeat([0, 1, 2], 30)
    post = posture.summarize([prof] * 90, times, stroke_id, fps=30.0)
    assert post['verdict'] == 'rounded' and len(post['strokes']) == 3
    assert post['timing']['avg'] == 1.0
    assert posture.back_recommendation(post)['metric'] == 'back'


def test_analysis_video_panel_draws_progressively():
    from src import video_export
    mask, hip, sh = _torso_mask(30)
    prof = posture.back_profile(mask, hip, sh, 'right')
    times = np.arange(90) / 30.0
    tracks = {'hip': np.column_stack([np.zeros(90), 300 + 5 * np.sin(times * 9)]),
              'shoulder': np.column_stack([np.zeros(90), np.full(90, 200.0)])}
    post = posture.summarize([prof] * 90, times, np.repeat([0, 1, 2], 30), tracks, fps=30.0)
    panel = video_export._Panel(post, times[-1])
    early, _ = panel.draw(0.5)
    late, texts = panel.draw(2.9)
    assert early.shape == (video_export.OUT_H, video_export.PANEL_W, 3)
    assert (late != panel.base).sum() > (early != panel.base).sum()
    assert any('Stroke' in t[1] for t in texts)


# ---------------------------------------------------------------- front / rear view (beta)
def _front_kp(model_left_x, valgus_side=None, valgus_px=0.0, hip_gap=100.0):
    """Both legs seen from the front/back. valgus_side is the model's label ('left'|'right') whose
    knee is pushed toward the midline by valgus_px; model_left_x says where the model's 'left' hip is."""
    kp = {}
    mid = 300.0
    for side in ('left', 'right'):
        sign = 1 if (side == 'left') == (model_left_x > mid) else -1  # +1 = leg sits right of midline
        hx = mid + sign * hip_gap / 2
        kn = hx - sign * (valgus_px if side == valgus_side else 0.0)  # inward = toward the midline
        kp[f'{side}_hip'] = (hx, 200.0, 0.9)
        kp[f'{side}_knee'] = (kn, 300.0, 0.9)
        kp[f'{side}_ankle'] = (hx, 400.0, 0.9)
    return kp


def _flag_keys(view, model_left_x, valgus_side):
    from src import frontal
    rows = [frontal.frame_metrics(_front_kp(model_left_x, valgus_side, 40.0)) for _ in range(40)]
    return frontal.summarize(rows, view)


def test_frontal_valgus_is_attributed_to_the_right_leg_in_all_four_view_side_combinations():
    # Front view: the rider's left leg appears on the image right. Rear view: on the image left.
    for view, model_left_x in (('front', 400.0), ('rear', 200.0)):
        for side in ('left', 'right'):
            # The model labels follow the rider, so the rider's `side` is where the label says it is
            summ = _flag_keys(view, model_left_x, side)
            image_left_leg = (side == 'left') == (model_left_x < 300)
            expect_side = ('right' if view == 'front' else 'left') if image_left_leg else \
                ('left' if view == 'front' else 'right')
            flagged = [f for f in summ['flags'] if f['key'] == 'knee_in']
            assert len(flagged) == 1 and flagged[0]['side'] == expect_side, (view, side, summ['flags'])
            assert summ['knee'][expect_side]['medial_peak'] > 10
            assert not [f for f in summ['flags'] if f['key'] == 'knee_out']


def test_frontal_straight_legs_raise_no_flags_and_pelvis_rock_is_measured():
    from src import frontal
    rows = [frontal.frame_metrics(_front_kp(400.0)) for _ in range(40)]
    assert frontal.summarize(rows, 'front')['flags'] == []
    rocking = []
    for i in range(40):
        kp = _front_kp(400.0)
        kp['left_hip'] = (kp['left_hip'][0], 200.0 + 15 * np.sin(i / 3.0), 0.9)
        kp['right_hip'] = (kp['right_hip'][0], 200.0 - 15 * np.sin(i / 3.0), 0.9)
        rocking.append(frontal.frame_metrics(kp))
    summ = frontal.summarize(rocking, 'front')
    assert summ['pelvis_rock'] > frontal.PELVIS_FLAG_DEG and any(f['key'] == 'pelvis' for f in summ['flags'])


def test_frontal_side_on_clip_is_detected_and_missing_joints_are_skipped():
    from src import frontal
    row = frontal.frame_metrics(_front_kp(400.0, hip_gap=5.0))
    assert row['hip_sep'] < frontal.SIDE_ON_RATIO
    kp = _front_kp(400.0)
    kp['left_knee'] = (300.0, 300.0, 0.1)
    assert frontal.frame_metrics(kp) is None
    assert frontal.summarize([None] * 100, 'front') is None


def test_frontal_result_survives_rescore_and_pdf():
    from src import engine, frontal
    summ = _flag_keys('front', 400.0, 'left')
    res = {'mode': 'frontal', 'profile': 'road_endurance', 'profile_name': 'x', 'metrics': {k: 0.0 for k in fp.METRICS},
           'statuses': {k: 'na' for k in fp.METRICS}, 'ranges': {}, 'score': None, 'warnings': [],
           'recommendations': frontal.recommendations(summ), 'frontal': summ, 'posture': None}
    before = list(res['recommendations'])
    engine.score_result(res, 'city')
    assert res['profile'] == 'city' and res['recommendations'] == before and before
    assert report.generate_fit_report(res, snapshot_paths={}).startswith(b'%PDF')


def test_city_profile_and_frame_size_rule():
    assert 'city' in fp.PROFILES and fp.PROFILES['city'].get('estimate')
    base = {'knee_ext': 145.0, 'knee_flex': 72.0, 'hip_closed': 55.0, 'torso': 50.0, 'shoulder': 88.0, 'elbow': 158.0}
    titles = lambda m, **x: [r['title'] for r in fp.build_recommendations(m, 'road_endurance', x)]  # noqa: E731
    assert not any('too long' in t or 'too short' in t for t in titles(base))
    assert any('too long' in t for t in titles(dict(base, shoulder=105.0, elbow=175.0)))
    assert any('too short' in t for t in titles(dict(base, shoulder=70.0, hip_closed=40.0)))
    assert not any('too long' in t for t in titles(dict(base, shoulder=105.0)))  # one reading alone isn't enough
    assert any('ahead of' in t for t in titles(base, kops_mm=45.0))
    assert not any('ahead of' in t for t in fp.build_recommendations(base, 'tri_tt', {'kops_mm': 45.0}))


def _pedalling_front_kp(i, splay=6.0):
    """Both legs from the front; every few frames a thigh points at the camera (very short in the image)."""
    kp = {}
    for side, hx, sign in (('left', 350.0, 1), ('right', 250.0, -1)):
        drop = 10.0 if (i + (0 if side == 'left' else 5)) % 10 < 3 else 100.0  # foreshortened ~30% of the time
        kp[f'{side}_hip'] = (hx, 200.0, 0.9)
        kp[f'{side}_knee'] = (hx - sign * splay, 200.0 + drop, 0.9)  # splay toward the midline
        kp[f'{side}_ankle'] = (hx, 400.0, 0.9)
    return kp


def test_frontal_ignores_frames_where_the_thigh_points_at_the_camera(monkeypatch):
    from src import frontal
    rows = [frontal.frame_metrics(_pedalling_front_kp(i)) for i in range(100)]
    assert frontal.summarize(rows, 'front')['flags'] == []
    monkeypatch.setattr(frontal, 'MIN_THIGH_FRACTION', 0.0)  # without the filter the same clip is flagged
    assert any(f['key'] == 'knee_in' for f in frontal.summarize(rows, 'front')['flags'])


def test_frontal_one_sided_drift_is_reported_once():
    summ = _flag_keys('front', 400.0, 'left')
    assert [f['key'] for f in summ['flags']] == ['knee_in']


def test_frame_size_rule_replaces_the_single_reach_and_elbow_items():
    base = {'knee_ext': 145.0, 'knee_flex': 72.0, 'hip_closed': 55.0, 'torso': 50.0, 'shoulder': 88.0, 'elbow': 158.0}
    titles = [r['title'] for r in fp.build_recommendations(dict(base, shoulder=105.0, elbow=175.0), 'road_endurance')]
    assert any('too long' in t for t in titles)
    assert not any('Reach looks' in t or 'Soften' in t for t in titles)
    assert any('Reach looks long' in r['title'] for r in
               fp.build_recommendations(dict(base, shoulder=105.0), 'road_endurance'))


def test_estimated_profile_says_so():
    assert any('estimates' in n for n in fp.personalize('city')[1])
    assert not any('estimates' in n for n in fp.personalize('road_endurance')[1])
