"""
Result-shape contract. app.js (renderSide), report.py and the web app's rescore/_summary all read the same
top-level fields, so every analysis mode must provide them. Run this after adding a mode.
"""
import json
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import engine, report  # noqa: E402
from src import pose_backends as pb  # noqa: E402

REQUIRED = ('mode', 'profile', 'profile_name', 'metrics', 'statuses', 'ranges', 'score', 'recommendations',
            'warnings', 'snapshots', 'quality', 'biomech')
DEMO = os.path.join(os.path.dirname(__file__), '..', 'assets', 'demo', 'result.json')


class _FakeFrontDetector:
    """Both legs seen from the front; the left knee drifts inward on every frame."""

    def __init__(self, *a, **k):
        pass

    def process(self, frame, ts_ms=0):
        kp = {}
        for side, hx in (('left', 350.0), ('right', 250.0)):
            inward = 45.0 if side == 'left' else 0.0
            kp[f'{side}_hip'] = (hx, 200.0, 0.9)
            kp[f'{side}_knee'] = (hx + (-inward if hx > 300 else inward), 300.0, 0.9)
            kp[f'{side}_ankle'] = (hx, 400.0, 0.9)
        return kp

    def close(self):
        pass


def _blank_video(path, frames=90, fps=30):
    out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (640, 480))
    for _ in range(frames):
        out.write(np.zeros((480, 640, 3), np.uint8))
    out.release()


def _check(res):
    missing = [k for k in REQUIRED if k not in res]
    assert not missing, f"{res.get('mode')} result lacks {missing}"
    assert set(res['statuses']) == set(res['metrics']) and set(res['metrics']) <= set(res['ranges'])
    assert all({'priority', 'title', 'detail'} <= set(r) for r in res['recommendations'])
    assert all('title' in s for s in res['snapshots'].values())


def _scored_twice(res, profile='city'):
    engine.score_result(res, profile)
    _check(res)
    assert res['profile'] == profile
    pdf = report.generate_fit_report({**res, 'snapshots': {}}, snapshot_paths={})
    assert pdf.startswith(b'%PDF')


def test_stored_demo_fit_meets_the_contract_and_rescores():
    with open(DEMO, encoding='utf-8') as f:
        res = json.load(f)
    _check(res)
    _scored_twice(res)


def test_frontal_pipeline_end_to_end_with_a_fake_detector(tmp_path, monkeypatch):
    monkeypatch.setattr(pb, 'make_backend', lambda *a, **k: _FakeFrontDetector())
    monkeypatch.setattr(engine, 'resolve_backend', lambda b: 'mediapipe')
    path = str(tmp_path / 'front.mp4')
    _blank_video(path)
    res = engine.analyze_frontal(path, view='front')
    _check(res)
    assert res['mode'] == 'frontal' and res['score'] is None
    assert res['snapshots']['frontal']['jpg']
    # Image-right leg in a front view is the rider's left leg
    flagged = [f for f in res['frontal']['flags'] if f['key'] == 'knee_in']
    assert len(flagged) == 1 and flagged[0]['side'] == 'left'
    before = list(res['recommendations'])
    _scored_twice(res)
    assert res['recommendations'] == before


def test_frontal_rejects_a_clip_without_visible_legs(tmp_path, monkeypatch):
    class Empty(_FakeFrontDetector):
        def process(self, frame, ts_ms=0):
            return None

    monkeypatch.setattr(pb, 'make_backend', lambda *a, **k: Empty())
    monkeypatch.setattr(engine, 'resolve_backend', lambda b: 'mediapipe')
    path = str(tmp_path / 'empty.mp4')
    _blank_video(path)
    try:
        engine.analyze_frontal(path, view='rear')
    except engine.AnalysisError as e:
        assert 'legs' in str(e)
    else:
        raise AssertionError("expected AnalysisError")


def test_video_results_carry_the_fit_calculations():
    with open(DEMO, encoding='utf-8') as f:
        res = json.load(f)
    engine.score_result(res, 'tri_tt')
    calc = res['calc']
    assert calc['model'] and calc['crank']['rows'] and calc['ankle'] is not None
    assert {'hip_x', 'hip_y'} <= set(calc['coords'])


def test_api_localizes_and_answers_what_if():
    from fastapi.testclient import TestClient
    from src.web.app import app
    c = TestClient(app)
    de = c.get('/api/sessions/demo?lang=de').json()
    en = c.get('/api/sessions/demo').json()
    assert de['recommendations'] and de['recommendations'][0]['title'] != en['recommendations'][0]['title']
    assert de['coach']['text'].startswith('Positionsübersicht')
    w = c.post('/api/sessions/demo/whatif', json={'saddle_mm': 10}).json()
    assert w['pred']['knee_ext']['delta'] > 0
    assert c.get('/api/config?lang=de').json()['profiles']['city']['short'] == 'City / Trekking'
    assert c.get('/api/sessions/demo/report.pdf?lang=de').content.startswith(b'%PDF')
