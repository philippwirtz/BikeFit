"""Stroke model, crank length, inseam and aero maths, measurement statistics and translations."""
import json
import os
import re
import string
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import fitcalc as fc, fit_profiles as fp, validation  # noqa: E402
from src.i18n import t  # noqa: E402
from src.locale_de import DE  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), '..')
DEMO = os.path.join(ROOT, 'assets', 'demo', 'result.json')


@pytest.fixture(scope='module')
def demo():
    with open(DEMO, encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(scope='module')
def model(demo):
    return fc.build_model(demo)


def test_model_reproduces_the_measured_knee_curve(demo, model):
    assert model['calibrated'] and model['calib_rms'] < 6
    base = fc.simulate(model)
    assert abs(base['knee_ext'] - demo['metrics']['knee_ext']) < 2
    assert abs(base['knee_flex'] - demo['metrics']['knee_flex']) < 2


def test_saddle_and_crank_changes_move_the_knee_the_right_way(demo, model):
    up = fc.what_if(demo, model, saddle_mm=10)['pred']
    # Roughly 0.35-0.55 deg per mm of saddle (fitter's rule of thumb is ~0.4)
    assert 3.0 < up['knee_ext']['delta'] < 6.5
    assert up['knee_flex']['delta'] > 0
    short = fc.what_if(demo, model, crank_mm=165)['pred']
    assert short['knee_ext']['delta'] < 0 and short['knee_flex']['delta'] > 0 and short['hip_closed']['delta'] > 0
    assert fc.what_if(demo, model, bar_mm=20)['pred']['torso']['delta'] > 0


def test_saddle_solver_hits_the_target(model):
    dh = fc.saddle_for_knee_ext(model, 3.0)
    assert dh is not None and dh > 0
    assert abs(fc.simulate(model, saddle_mm=dh)['knee_ext'] - fc.simulate(model)['knee_ext'] - 3.0) < 0.05


def test_crank_options_keep_extension_and_suggest_only_when_needed(demo, model):
    ranges, _ = fp.personalize('tri_tt')
    out = fc.crank_options(demo, ranges, model)
    assert out['suggest_mm'] is None  # demo hip and knee are in range
    for r in out['rows']:
        assert abs(fc.simulate(model, saddle_mm=r['saddle_mm'], crank_mm=r['crank_mm'])['knee_ext']
                   - fc.simulate(model)['knee_ext']) < 0.1
    cramped = dict(demo, metrics=dict(demo['metrics'], knee_flex=60.0))  # knee closes too far at the top
    sug = fc.crank_options(cramped, ranges, model)
    assert sug['suggest_mm'] and fc.MIN_SUGGEST_CRANK <= sug['suggest_mm'] < 172.5


def test_inseam_and_aero_formulas():
    s = fc.inseam_saddle(86, 172.5)
    assert s['lemond_mm'] == pytest.approx(759.4, abs=0.1)
    assert s['hamley_mm'] == pytest.approx(937.4 - 172.5, abs=0.1)
    a = fc.aero_estimate(75, 15)
    assert 0.25 < a['area_m2'] < 0.45 and a['saving_w'] > 0 and not a['extrapolated']
    assert fc.aero_estimate(75, 45)['extrapolated']


def test_ankle_profile(demo):
    a = fc.ankle_profile(demo)
    assert a is not None and -20 < a['bdc'] < 40 and a['range'] > 5


def test_ankle_cross_check_flags_toe_down_compensation():
    m = {'knee_ext': 146.0, 'knee_flex': 70, 'hip_closed': 55, 'torso': 50, 'shoulder': 88, 'elbow': 155}
    titles = [r['title'] for r in fp.build_recommendations(m, 'road_endurance', {'plantar_bdc': 32.0})]
    assert any('Toes point down' in x for x in titles)
    assert not any('Toes' in r['title'] for r in fp.build_recommendations(m, 'road_endurance', {'plantar_bdc': 10.0}))


def test_repeatability_and_agreement_statistics():
    r = validation.repeatability({'a': [145, 146, 144], 'b': [150, 151, 152], 'c': [140, 139, 141]})
    assert r['sem'] == pytest.approx(1.0)
    assert r['mdc95'] == pytest.approx(1.96 * np.sqrt(2))
    assert r['icc'] > 0.9
    ba = validation.bland_altman([140, 142, 145, 150], [132, 135, 137, 141])
    assert ba['bias'] == pytest.approx(8.0) and ba['loa'][0] < ba['bias'] < ba['loa'][1]
    assert validation.change_is_real(3.0, mdc=2.8) and not validation.change_is_real(1.2, 1.0, 1.0)


def _python_templates():
    out = set()
    for path in ('src/fit_profiles.py', 'src/posture.py', 'src/frontal.py', 'src/coach.py', 'src/report.py',
                 'src/engine.py'):
        src = open(os.path.join(ROOT, path), encoding='utf-8').read()
        for m in re.finditer(r'\bt\((?:lang|self\.lang), ((?:"(?:[^"\\]|\\.)*"\s*)+)', src):
            out.add(''.join(re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))).replace("\\'", "'"))
    return out


def test_every_server_text_has_a_german_translation_with_the_same_placeholders():
    names = lambda s: {f[1] for f in string.Formatter().parse(s) if f[1]}  # noqa: E731
    missing = [k for k in _python_templates() if k not in DE]
    assert not missing, missing
    assert all(names(k) == names(v) for k, v in DE.items())
    assert t('de', '{v:.1f}% curve', v=13.7) == '13,7 % Wölbung'
