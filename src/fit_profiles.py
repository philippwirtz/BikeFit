"""
Riding-style reference ranges and plain-language fit recommendations.

Ranges are commonly cited dynamic bike-fit guidelines (side-view, 2D). They are
starting points, not medical advice. Comfort and injury history always win.

Sources behind the road/TT/gravel ranges (angles here are inner angles, so knee
extension 140-150 deg is the same thing as "knee flexion 30-40 deg at the bottom"):
- Holmes method (knee at BDC, avg knee ~36 +/- 7 deg, elbow ~19 +/- 8 deg):
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9219349/
- Angles measured while pedalling on video read ~8 deg higher than static goniometer
  values, which is why the dynamic knee zone is 30-40 and not the static 25-35:
  https://pubmed.ncbi.nlm.nih.gov/24499342/
- Hip angle at the top (shoulder-hip-knee): fitter's reference of ~55-65 deg on a road
  bike (Burt, 2014, "Bike Fit"). Lower for aggressive/TT, higher for upright bikes.
- Practitioner cross-check for torso, shoulder and hip:
  https://www.bikefitadviser.com/blog/not-basic-bike-fit-part-3-bike-fit-joint-angles
The city profile has no published source and is marked "estimate". See docs/RESEARCH.md.
"""
from src.i18n import t

# Degrees of knee angle change per mm of saddle height is roughly 0.35-0.45
# for most riders, i.e. ~2.5 mm of saddle per degree of knee extension.
MM_PER_KNEE_DEGREE = 2.5
MAX_SINGLE_SADDLE_CHANGE_MM = 15
# Foot angle at the bottom of the stroke (+ = toe down vs the shank-perpendicular). Burt (2014) gives
# 5-15 deg plantarflexion as a static starting point; flags sit well outside that window.
PLANTAR_HIGH_DEG = 25.0
PLANTAR_LOW_DEG = -5.0
HIP_SWAY_FLAG_MM = 25.0  # heuristic: fore-aft hip travel per stroke

METRICS = {
    "knee_ext": {
        "label": "Knee extension (bottom of stroke)",
        "short": "Knee extension",
        "explain": "How straight your leg gets at the bottom of the pedal stroke. "
                   "Mostly controlled by saddle height.",
    },
    "knee_flex": {
        "label": "Knee bend (top of stroke)",
        "short": "Knee bend at top",
        "explain": "How bent your knee is at the top of the stroke. Too small = knee "
                   "is cramped (saddle low/forward or cranks too long).",
    },
    "hip_closed": {
        "label": "Hip angle (most closed)",
        "short": "Hip angle at top",
        "explain": "Angle between torso and thigh at the top of the stroke. Too closed "
                   "chokes breathing and power; too open is less aero.",
    },
    "torso": {
        "label": "Torso angle (vs. horizontal)",
        "short": "Torso",
        "explain": "How low your back is. Lower = more aero, higher = more comfortable. "
                   "Mostly controlled by handlebar height and reach.",
    },
    "shoulder": {
        "label": "Shoulder angle (arm vs. torso)",
        "short": "Shoulder",
        "explain": "Angle between upper arm and torso. Tells you if the bars are too "
                   "close (small) or too far (large).",
    },
    "elbow": {
        "label": "Elbow bend",
        "short": "Elbow",
        "explain": "A slight bend absorbs road buzz. Locked-out elbows usually mean "
                   "the reach is too long.",
    },
}

PROFILES = {
    "road_endurance": {
        "short": "Endurance road",
        "name": "Road: endurance / comfort",
        "emoji": "🚲",
        "blurb": "Sportives, long rides, commuting. Comfort first.",
        "ranges": {
            "knee_ext": (140, 150),
            "knee_flex": (65, 80),
            "hip_closed": (50, 65),
            "torso": (45, 55),
            "shoulder": (80, 95),
            "elbow": (150, 165),
        },
    },
    "road_race": {
        "short": "Race road",
        "name": "Road: race / aggressive",
        "emoji": "🏁",
        "blurb": "Racing, crits, fast group rides. Lower and longer.",
        "ranges": {
            "knee_ext": (140, 150),
            "knee_flex": (65, 80),
            "hip_closed": (45, 55),
            "torso": (35, 45),
            "shoulder": (85, 100),
            "elbow": (150, 165),
        },
    },
    "tri_tt": {
        "short": "Triathlon / TT",
        "name": "Triathlon / Time trial",
        "emoji": "⏱️",
        "blurb": "Aero bars, long steady efforts. Aero but sustainable.",
        "ranges": {
            "knee_ext": (140, 150),
            "knee_flex": (65, 80),
            "hip_closed": (40, 55),
            "torso": (10, 28),
            "shoulder": (80, 100),
            "elbow": (85, 115),
        },
    },
    "mtb_gravel": {
        "short": "Gravel / MTB",
        "name": "MTB / Gravel",
        "emoji": "⛰️",
        "blurb": "Off-road control, more upright, wider bars.",
        "ranges": {
            "knee_ext": (138, 148),
            "knee_flex": (65, 80),
            "hip_closed": (55, 70),
            "torso": (45, 60),
            "shoulder": (75, 90),
            "elbow": (140, 160),
        },
    },
    "city": {
        "short": "City / hybrid",
        "name": "City / hybrid / commuter",
        "emoji": "🚲",
        "blurb": "Commuting and casual riding. Upright and relaxed.",
        # Estimates: no published dynamic ranges exist for upright bikes. Treat as rough guidance.
        "estimate": True,
        "ranges": {
            "knee_ext": (138, 150),
            "knee_flex": (65, 85),
            "hip_closed": (65, 85),
            "torso": (55, 75),
            "shoulder": (60, 85),
            "elbow": (150, 170),
        },
    },
}

DEFAULT_PROFILE = "road_endurance"

FLEXIBILITY = {
    "limited": {"label": "Limited", "help": "Can't touch toes with straight legs"},
    "average": {"label": "Average", "help": "Fingertips reach toes"},
    "flexible": {"label": "Flexible", "help": "Palms reach the floor"},
}

PAINS = {
    "knee_front": "Front of knee",
    "knee_back": "Back of knee",
    "lower_back": "Lower back",
    "neck_shoulders": "Neck & shoulders",
    "hands": "Hands or wrists",
    "saddle": "Saddle discomfort",
}


def personalize(profile_key, flexibility="average", pains=(), lang="en"):
    """
    Shift the discipline's target ranges for the rider (MyVeloFit-style).

    Less flexible riders need a more open hip and a more upright torso; pain
    points bias the window toward the side that unloads the sore area.
    Returns (ranges, notes) where notes explain each shift.
    """
    ranges = {k: list(v) for k, v in PROFILES[profile_key]["ranges"].items()}
    notes = []

    def shift(key, lo=0, hi=0):
        ranges[key][0] += lo
        ranges[key][1] += hi

    if flexibility == "limited":
        shift("hip_closed", 5, 5)
        shift("torso", 5, 5)
        notes.append(t(lang, "Limited flexibility: hip and torso targets opened by 5°."))
    elif flexibility == "flexible":
        shift("hip_closed", -3, -3)
        shift("torso", -3, -3)
        notes.append(t(lang, "Good flexibility: hip and torso targets lowered by 3°."))

    pains = set(pains or ())
    if "knee_front" in pains:
        shift("knee_ext", 2, 0)
        shift("knee_flex", 3, 0)
        notes.append(t(lang, "Front-of-knee pain: favour a slightly higher saddle (less knee bend)."))
    if "knee_back" in pains:
        shift("knee_ext", 0, -3)
        notes.append(t(lang, "Back-of-knee pain: avoid over-extension at the bottom of the stroke."))
    if "lower_back" in pains:
        shift("hip_closed", 3, 3)
        shift("torso", 3, 3)
        notes.append(t(lang, "Lower-back pain: hip and torso targets opened by 3°."))
    if "neck_shoulders" in pains or "hands" in pains:
        shift("shoulder", 0, -5)
        shift("torso", 2, 2)
        notes.append(t(lang, "Neck, shoulder or hand pain: shorter reach and a slightly higher front end."))

    if PROFILES[profile_key].get("estimate"):
        notes.append(t(lang, "These targets are estimates: no published dynamic ranges exist for this riding style."))

    for k, v in ranges.items():
        if v[0] > v[1]:
            v[0] = v[1]
    return {k: tuple(v) for k, v in ranges.items()}, notes


def status_for(value, rng, tolerance=3.0):
    """Return 'ok', 'watch' (just outside) or 'fix' (clearly outside)."""
    if value is None or value <= 0:
        return "na"
    lo, hi = rng
    if lo <= value <= hi:
        return "ok"
    dist = lo - value if value < lo else value - hi
    return "watch" if dist <= tolerance else "fix"


def _mid(rng):
    return (rng[0] + rng[1]) / 2.0


def _rec(lang, priority, metric, title, detail, **kw):
    return {"priority": priority, "metric": metric, "title": t(lang, title, **kw), "detail": t(lang, detail, **kw)}


def build_recommendations(metrics, profile_key, extra=None, ranges=None, lang="en"):
    """
    metrics: dict with keys from METRICS (degrees). Missing / 0 values are skipped.
    extra:   optional dict e.g. {'torso_range': deg, 'mode': 'video'|'image'}
    Returns an ordered list of dicts: {priority, title, detail, metric}
      priority 1 = do this first (saddle height), 3 = nice to have.
    """
    extra = extra or {}
    ranges = ranges or PROFILES[profile_key]["ranges"]
    recs = []
    R = lambda *a, **kw: recs.append(_rec(lang, *a, **kw))  # noqa: E731

    def get(k):
        v = metrics.get(k)
        return v if v is not None and v > 0 else None

    # 1. Saddle height: always the first thing to get right.
    ke = get("knee_ext")
    if ke is not None:
        lo, hi = ranges["knee_ext"]
        geo = extra.get("saddle_adj_mm")
        if ke < lo:
            mm = abs(geo) if geo else (_mid(ranges["knee_ext"]) - ke) * MM_PER_KNEE_DEGREE
            mm = min(max(mm, 2), MAX_SINGLE_SADDLE_CHANGE_MM)
            R(1, "knee_ext", "Raise your saddle ~{mm:.0f} mm",
              "Your knee only opens to {ke:.0f}° at the bottom (target {lo}–{hi}°). "
              "A low saddle overloads the front of the knee and wastes power. "
              "Raise it in 3–5 mm steps and re-test.", mm=mm, ke=ke, lo=lo, hi=hi)
        elif ke > hi:
            mm = abs(geo) if geo else (ke - _mid(ranges["knee_ext"])) * MM_PER_KNEE_DEGREE
            mm = min(max(mm, 2), MAX_SINGLE_SADDLE_CHANGE_MM)
            R(1, "knee_ext", "Lower your saddle ~{mm:.0f} mm",
              "Your knee opens to {ke:.0f}° at the bottom (target {lo}–{hi}°). "
              "Over-extension often causes hip rocking and pain behind the knee. "
              "Lower it in 3–5 mm steps and re-test.", mm=mm, ke=ke, lo=lo, hi=hi)

    # 1b. Ankle cross-check: toe-down pedalling can hide a saddle that is too high,
    #     a dropped heel makes a fine saddle read as too high.
    pf = extra.get("plantar_bdc")
    if pf is not None and ke is not None:
        lo, hi = ranges["knee_ext"]
        if pf > PLANTAR_HIGH_DEG and ke >= lo - 3:
            R(2, "knee_ext", "Toes point down hard at the bottom: saddle may be high",
              "Your foot is {pf:.0f}° toe-down at the bottom of the stroke (typical 5–15°). Pointing the toes "
              "reaches for a pedal that is too far away, so the knee angle ({ke:.0f}°) can look fine while the "
              "saddle is too high. Lower the saddle 3–5 mm and re-test: if the toes level out and the knee stays "
              "in range, keep it.", pf=pf, ke=ke)
        elif pf < PLANTAR_LOW_DEG and ke > hi:
            R(3, "knee_ext", "Your heel drops at the bottom of the stroke",
              "Your foot is {pfa:.0f}° heel-down at the bottom. A dropped heel straightens the knee, so part of "
              "the over-extension ({ke:.0f}°) is pedalling style rather than saddle height. Lower the saddle in "
              "small steps and re-check the ankle with each step.", pfa=abs(pf), ke=ke)

    # 2. Knee at top of stroke (only meaningful once saddle height is sane).
    kf = get("knee_flex")
    if kf is not None and (ke is None or ranges["knee_ext"][0] - 3 <= ke <= ranges["knee_ext"][1] + 3):
        lo, hi = ranges["knee_flex"]
        if kf < lo - 3:
            crank = extra.get("crank_suggest_mm")
            if crank:
                R(2, "knee_flex", "Knee is cramped at the top of the stroke",
                  "Knee closes to {kf:.0f}° (target {lo}–{hi}°). The stroke model predicts {crank:g} mm cranks "
                  "would open it, with the saddle raised by the difference. Sliding the saddle back a few mm "
                  "also helps.", kf=kf, lo=lo, hi=hi, crank=crank)
            else:
                R(2, "knee_flex", "Knee is cramped at the top of the stroke",
                  "Knee closes to {kf:.0f}° (target {lo}–{hi}°). Consider sliding the saddle "
                  "back a few mm or trying shorter cranks (e.g. 165–170 mm).", kf=kf, lo=lo, hi=hi)

    # 3. Hip angle.
    hc = get("hip_closed")
    if hc is not None:
        lo, hi = ranges["hip_closed"]
        if hc < lo - 2:
            crank = extra.get("crank_suggest_mm")
            if crank:
                R(2, "hip_closed", "Open up your hip angle",
                  "Your hip closes to {hc:.0f}° (target {lo}–{hi}°). Raise the bars (spacers / stem flip) or try "
                  "{crank:g} mm cranks: the stroke model predicts about {gain:.0f}° more hip angle with them "
                  "(raise the saddle {dh:.0f} mm at the same time).",
                  hc=hc, lo=lo, hi=hi, crank=crank, gain=extra.get("crank_hip_gain") or 0,
                  dh=extra.get("crank_saddle_mm") or 0)
            else:
                R(2, "hip_closed", "Open up your hip angle",
                  "Your hip closes to {hc:.0f}° (target {lo}–{hi}°). Try raising the bars "
                  "(spacers / stem flip), shorter cranks, or (on a tri bike) moving the "
                  "saddle slightly forward.", hc=hc, lo=lo, hi=hi)
        elif hc > hi + 5:
            R(3, "hip_closed", "You have room to get lower",
              "Hip angle of {hc:.0f}° is more open than needed for this style "
              "(target {lo}–{hi}°). If you want more speed, drop the bars gradually.", hc=hc, lo=lo, hi=hi)

    # 4. Torso / bar height.
    to = get("torso")
    if to is not None:
        lo, hi = ranges["torso"]
        aero = extra.get("aero")
        if to > hi + 3:
            if aero and aero.get("saving_w"):
                R(3, "torso", "Position is more upright than typical for this style",
                  "Torso at {to:.0f}° (typical {lo}–{hi}°). Fine if comfort is the goal; otherwise lower the bars "
                  "5–10 mm at a time. Rough estimate: 5° lower saves about {w:.0f} W at {v:.0f} km/h.",
                  to=to, lo=lo, hi=hi, w=aero["saving_w"], v=aero["speed_kmh"])
            else:
                R(3, "torso", "Position is more upright than typical for this style",
                  "Torso at {to:.0f}° (typical {lo}–{hi}°). Fine if comfort is the goal; "
                  "otherwise lower the bars 5–10 mm at a time.", to=to, lo=lo, hi=hi)
        elif to < lo - 3:
            R(2, "torso", "Position is very low: check it's sustainable",
              "Torso at {to:.0f}° (typical {lo}–{hi}°). If you feel neck/back strain or "
              "can't hold it for long, raise the bars slightly.", to=to, lo=lo, hi=hi)

    # Frame size: only when two independent readings agree, so one noisy angle can't blame the bike.
    # When it fires it replaces the single-angle reach and elbow items below, which say the same thing.
    sh, el, hc = get("shoulder"), get("elbow"), get("hip_closed")
    long_cockpit = sh is not None and el is not None and sh > ranges["shoulder"][1] + 3 \
        and el > ranges["elbow"][1] + 5
    short_cockpit = sh is not None and hc is not None and sh < ranges["shoulder"][0] - 3 \
        and hc < ranges["hip_closed"][0] - 2

    # 5. Reach (shoulder angle).
    if sh is not None and not (long_cockpit or short_cockpit):
        lo, hi = ranges["shoulder"]
        if sh < lo - 3:
            R(2, "shoulder", "Reach looks short",
              "Shoulder angle {sh:.0f}° (target {lo}–{hi}°). You may feel cramped. "
              "A 10 mm longer stem (or extending aerobar pads forward) is a common fix.", sh=sh, lo=lo, hi=hi)
        elif sh > hi + 3:
            R(2, "shoulder", "Reach looks long",
              "Shoulder angle {sh:.0f}° (target {lo}–{hi}°). Stretching for the bars loads "
              "the neck and shoulders. Try a 10 mm shorter stem or move pads back.", sh=sh, lo=lo, hi=hi)

    # 6. Elbows.
    if el is not None and not long_cockpit:
        lo, hi = ranges["elbow"]
        if el > hi + 5:
            R(3, "elbow", "Soften your elbows",
              "Elbows are nearly locked ({el:.0f}°). Keep a slight bend to absorb bumps; "
              "if you can't, reach is probably too long.", el=el)

    # 7. Hip rock (video only, from the crank-phase model).
    rock = extra.get("hip_rock_mm")
    if rock is not None and rock > 18 and (ke is None or ke >= ranges["knee_ext"][0]):
        R(2, "knee_ext", "Hips rock on the saddle",
          "Your hips move about {rock:.0f} mm up and down each stroke. More than ~15 mm "
          "usually means the saddle is a touch high or the cleats are too far forward.", rock=rock)

    # 7a. Hip sway: sliding fore-aft on the saddle each stroke (heuristic, no published threshold).
    sway = extra.get("hip_sway_mm")
    if sway is not None and sway > HIP_SWAY_FLAG_MM:
        R(3, None, "You slide forward and back on the saddle",
          "Your hips shift about {sway:.0f} mm fore-aft each stroke. Riders usually creep forward when the "
          "reach is long or the saddle nose tilts down, and back when the saddle is low. Check saddle tilt "
          "(start level) and reach. This flag is a heuristic, not a published limit.", sway=sway)

    # 7b. Frame size (readings computed above).
    if long_cockpit or short_cockpit:
        if long_cockpit:
            R(2, "shoulder", "The bike may be too long for you",
              "Shoulder and elbow angles both point the same way. Adjust the stem first, and if that isn't "
              "enough consider a shorter stem, or a smaller frame if the stem is already short.")
        else:
            R(2, "shoulder", "The bike may be too short for you",
              "Shoulder and hip angles both point the same way. Adjust the stem first, and if that isn't "
              "enough consider a longer stem, or a larger frame if the stem is already long.")

    # 7c. KOPS (knee over pedal spindle at 3 o'clock). A reference point, not a rule.
    kops = extra.get("kops_mm")
    if kops is not None and abs(kops) > 30 and profile_key != "tri_tt":  # tri bikes sit the knee well forward on purpose
        if kops > 0:
            R(3, None, "Knee is {k:.0f} mm ahead of the pedal axle at 3 o'clock",
              "A knee roughly above the pedal axle is a common starting point, but riders differ. "
              "If you have knee pain, try moving the saddle back a few mm and re-test. Saddle height comes first.",
              k=abs(kops))
        else:
            R(3, None, "Knee is {k:.0f} mm behind the pedal axle at 3 o'clock",
              "A knee roughly above the pedal axle is a common starting point, but riders differ. "
              "If you have knee pain, try moving the saddle forward a few mm and re-test. Saddle height comes first.",
              k=abs(kops))

    # 8. Pain-specific guidance.
    pains = set(extra.get("pains") or ())
    if "saddle" in pains:
        R(3, None, "Check saddle tilt and width",
          "Saddle discomfort is often tilt (start level, then 1–2° nose down) or a saddle "
          "too narrow for your sit bones, rather than height.")
    if "knee_front" in pains or "knee_back" in pains:
        R(3, None, "Check cleat position",
          "Knee pain that persists with a good saddle height often comes from cleat "
          "rotation or fore-aft position. Ball of the foot over the pedal spindle is the start point.")

    # 9. Stability (video only).
    tr = extra.get("torso_range")
    if tr is not None and tr > 10:
        R(2, "torso", "Upper body is moving a lot",
          "Your torso angle varies by {tr:.0f}° while pedalling. Rocking usually means the "
          "saddle is too high, or you're filming during a very hard effort.", tr=tr)

    recs.sort(key=lambda r: r["priority"])
    return recs


def fit_score(metrics, profile_key, ranges=None):
    """0-100 score: share of metrics in range, with partial credit for 'watch'."""
    ranges = ranges or PROFILES[profile_key]["ranges"]
    weights = {"knee_ext": 3, "knee_flex": 1, "hip_closed": 2, "torso": 1, "shoulder": 1.5, "elbow": 0.5}
    total = got = 0.0
    for k, w in weights.items():
        s = status_for(metrics.get(k), ranges[k])
        if s == "na":
            continue
        total += w
        got += w * {"ok": 1.0, "watch": 0.6, "fix": 0.15}[s]
    if total == 0:
        return None
    return int(round(100 * got / total))


def localized(lang):
    """METRICS, PROFILES, FLEXIBILITY and PAINS with their user-facing text translated."""
    tr = lambda d, keys: {k: (t(lang, v) if k in keys and isinstance(v, str) else v) for k, v in d.items()}  # noqa: E731
    return {
        "metrics": {k: tr(v, ("label", "short", "explain")) for k, v in METRICS.items()},
        "profiles": {k: tr(v, ("short", "name", "blurb")) for k, v in PROFILES.items()},
        "flexibility": {k: tr(v, ("label", "help")) for k, v in FLEXIBILITY.items()},
        "pains": {k: t(lang, v) for k, v in PAINS.items()},
    }
