"""PDF report generation (fpdf2)."""
import os
from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from src import fit_profiles as fp
from src.i18n import t

STATUS_TXT = {'ok': 'In range', 'watch': 'Borderline', 'fix': 'Adjust', 'na': 'n/a'}
STATUS_RGB = {'ok': (22, 163, 74), 'watch': (217, 119, 6), 'fix': (220, 38, 38), 'na': (120, 120, 120)}
ACCENT = (35, 70, 216)       # brand cobalt #2346D8
INK = (20, 21, 27)           # graphite #14151B


def _latin(text):
    """Core PDF fonts are latin-1 only; map common unicode to safe equivalents."""
    repl = {'°': ' deg', '²': '2', '−': '-', '\u2014': '-', '–': '-', '’': "'", '‘': "'", '“': '"', '”': '"',
            '…': '...', '•': '-', '≈': '~', '×': 'x'}
    for a, b in repl.items():
        text = text.replace(a, b)
    return text.encode('latin-1', 'replace').decode('latin-1')


class BikeFitPDF(FPDF):
    lang = 'en'

    def header(self):
        self.set_fill_color(*INK)
        self.rect(0, 0, 210, 18, 'F')
        self.set_fill_color(*ACCENT)
        self.rect(0, 18, 210, 1.2, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 14)
        self.set_xy(10, 4)
        self.cell(0, 10, _latin(t(self.lang, 'BikeFit  |  Bike Fit Report')), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(6)

    def footer(self):
        self.set_y(-14)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 4, _latin(t(self.lang, 'BikeFit - open-source bike fitting')),
                  align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 4, _latin(t(self.lang, 'Page {n}  -  2D video estimate, not medical advice.', n=self.page_no())),
                  align='C')
        self.set_text_color(0, 0, 0)

    def section(self, title):
        self.ln(2)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(*ACCENT)
        self.cell(0, 8, _latin(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*ACCENT)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_text_color(0, 0, 0)
        self.ln(2)


def generate_fit_report(result, snapshot_paths, output_path=None, coach_text=None, rider_name="", lang='en'):
    """
    Build the PDF. Returns the PDF as bytes (and writes it to output_path if given).
    result: dict from engine.analyze_video / analyze_image.
    """
    loc = fp.localized(lang)
    prof = dict(fp.PROFILES[result['profile']], name=loc['profiles'][result['profile']]['name'])
    T = lambda text, **kw: t(lang, text, **kw)  # noqa: E731
    status_txt = {k: T(v) for k, v in STATUS_TXT.items()}
    pdf = BikeFitPDF()
    pdf.lang = lang
    pdf.set_auto_page_break(True, margin=18)
    pdf.add_page()

    # Summary line
    pdf.set_font('Helvetica', '', 10)
    who = T("Rider: {name}   |   ", name=rider_name) if rider_name else ""
    pdf.cell(0, 6, _latin(who + T("Style: {style}   |   {date}   |   Source: {src}", style=prof['name'],
                                  date=f"{datetime.now():%d.%m.%Y %H:%M}" if lang == 'de' else f"{datetime.now():%d %b %Y %H:%M}",
                                  src=T({'video': 'video', 'image': 'photo', 'frontal': 'front/rear video'}
                                        .get(result['mode'], result['mode'])))),
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    bio = result.get('biomech') or {}
    extras = []
    if bio.get('cadence_rpm'):
        extras.append(T("Cadence {c:.0f} rpm", c=bio['cadence_rpm']))
    if bio.get('cycles_detected'):
        extras.append(T("{n} pedal strokes modelled", n=bio['cycles_detected']))
    if (result.get('quality') or {}).get('grade'):
        extras.append(T("{g} capture quality", g=T(result['quality']['grade'].capitalize())))
    if extras:
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(90, 90, 90)
        pdf.cell(0, 5, _latin('   |   '.join(extras)), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
    if result.get('score') is not None:
        pdf.set_font('Helvetica', 'B', 22)
        sc = result['score']
        col = STATUS_RGB['ok'] if sc >= 80 else STATUS_RGB['watch'] if sc >= 55 else STATUS_RGB['fix']
        pdf.set_text_color(*col)
        pdf.cell(0, 12, _latin(T("Fit score: {s}/100", s=sc)), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)

    # Images
    pdf.section(T('Visual assessment'))
    order = [k for k in ('bdc', 'tdc', 'front', 'photo') if k in snapshot_paths]
    if len(order) == 1:
        pdf.image(snapshot_paths[order[0]], x=10, w=190)
    else:
        y = pdf.get_y()
        x_positions = [10, 105]
        row_h = 0
        for i, k in enumerate(order):
            col = i % 2
            if col == 0 and i > 0:
                y += row_h + 4
            info = pdf.image(snapshot_paths[k], x=x_positions[col], y=y, w=93)
            row_h = max(row_h if col else 0, info.rendered_height)
        pdf.set_y(y + row_h + 4)

    # Metrics table
    pdf.section(T('Measured angles'))
    widths = [64, 38, 40, 30]
    ranges = result.get('ranges') or prof['ranges']
    detail = result.get('metric_detail') or {}
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(236, 240, 252)
    for w, h in zip(widths, [T('Metric'), T('Value (95% range)'), T('Target range'), T('Status')]):
        pdf.cell(w, 8, _latin(h), border=1, align='C', fill=True)
    pdf.ln()
    pdf.set_font('Helvetica', '', 10)
    for k, meta in loc['metrics'].items():
        v = result['metrics'].get(k, 0)
        st = result['statuses'].get(k, 'na')
        lo, hi = ranges[k]
        ci = (detail.get(k) or {}).get('ci')
        val = f"{v:.1f} deg" + (f" +/-{(ci[1] - ci[0]) / 2:.1f}" if ci else "") if v else "-"
        pdf.cell(widths[0], 8, _latin(meta['label']), border=1)
        pdf.cell(widths[1], 8, val, border=1, align='C')
        pdf.cell(widths[2], 8, f"{lo:g}-{hi:g} deg", border=1, align='C')
        pdf.set_text_color(*STATUS_RGB[st])
        pdf.cell(widths[3], 8, _latin(status_txt[st]), border=1, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.ln()

    # Back & posture
    post = result.get('posture') or {}
    check = result.get('posture_check') or {}
    if post.get('available') or check.get('checks'):
        pdf.section(T('Back & posture'))
        if post.get('available'):
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(*STATUS_RGB[post['status']])
            bulge = f" ({post['bulge_mm']:.0f} mm)" if post.get('bulge_mm') else ''
            pdf.cell(0, 7, _latin(T("{label}: back curve {r:.1f}% of back length{bulge}, rounded in {p:.0f}% of frames",
                                    label=T(post['label']), r=post['roundness'], bulge=bulge,
                                    p=post['rounded_share'] * 100)),
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
            if 'posture' in snapshot_paths:
                if pdf.get_y() > 150:
                    pdf.add_page()
                pdf.image(snapshot_paths['posture'], x=10, w=190)
                pdf.ln(2)
            tm = post.get('timing')
            if tm:
                pdf.set_font('Helvetica', '', 9)
                pdf.set_text_color(90, 90, 90)
                pdf.cell(0, 5, _latin(T("Avg stroke {a:.2f} s   |   fastest stroke {fn} ({fd:.2f} s)   |   "
                                        "slowest stroke {sn} ({sd:.2f} s)   |   variation {cv:.0f}%",
                                        a=tm['avg'], fn=tm['fastest']['n'], fd=tm['fastest']['duration'],
                                        sn=tm['slowest']['n'], sd=tm['slowest']['duration'], cv=tm['cv_pct'])),
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_text_color(0, 0, 0)
        if check.get('checks'):
            pdf.ln(1)
            pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(0, 7, _latin(T("Posture score: {s}/100", s=check['score'])), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            for c in check['checks']:
                pdf.set_font('Helvetica', 'B', 9)
                pdf.set_text_color(*STATUS_RGB[c['status']])
                pdf.cell(38, 5.5, _latin(status_txt[c['status']]))
                pdf.set_text_color(0, 0, 0)
                pdf.cell(32, 5.5, _latin(c['label']))
                pdf.set_font('Helvetica', '', 9)
                pdf.multi_cell(0, 5.5, _latin(f"{c['value']} - {c['detail']}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Recommendations
    pdf.section(T('What to adjust (in this order)'))
    pdf.set_font('Helvetica', '', 10)
    if not result['recommendations']:
        pdf.multi_cell(0, 6, _latin(T("Everything measured is within range for this style. If you're comfortable, keep it!")))
    for i, r in enumerate(result['recommendations'], 1):
        pdf.set_font('Helvetica', 'B', 10)
        pdf.multi_cell(0, 6, _latin(f"{i}. {r['title']}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 5, _latin(r['detail']), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1)

    _calc_section(pdf, result, T)

    if result.get('warnings'):
        pdf.section(T('Capture quality notes'))
        pdf.set_font('Helvetica', 'I', 9)
        for w in result['warnings']:
            pdf.multi_cell(0, 5, _latin(f"- {w}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if coach_text:
        pdf.add_page()
        pdf.section(T('Coach notes'))
        pdf.set_font('Helvetica', '', 10)
        clean = coach_text.replace('**', '').replace('### ', '').replace('## ', '').replace('# ', '')
        pdf.multi_cell(0, 5.5, _latin(clean))

    data = bytes(pdf.output())
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, 'wb') as fh:
            fh.write(data)
    return data


def _calc_section(pdf, result, T):
    """Fit calculations: crank length, contact-point coordinates, ankle and aero estimate."""
    calc = result.get('calc') or {}
    lines = []
    crank = calc.get('crank') or {}
    if crank.get('suggest_mm'):
        sug = crank['suggest']
        lines.append(T("Crank length: {c:g} mm instead of {now:g} mm, with the saddle {dh:+.0f} mm, is predicted to give "
                       "a {hip:.0f}° hip angle and {kf:.0f}° knee bend at the top.", c=crank['suggest_mm'],
                       now=crank['current_mm'], dh=sug['saddle_mm'], hip=sug['hip_closed'], kf=sug['knee_flex']))
    if crank.get('tibia_rule_mm'):
        lines.append(T("Crank length by tibia length (41 %, Martin & Spirduso 2001, for peak power): {c:.0f} mm.",
                       c=crank['tibia_rule_mm']))
    co = calc.get('coords') or {}
    if co.get('hip_x') is not None:
        lines.append(T("Hip joint {x:.0f} mm behind and {y:.0f} mm above the bottom bracket.", x=-co['hip_x'], y=co['hip_y']))
    if co.get('hand_x') is not None:
        if co['hip_to_hand_drop'] >= 0:
            lines.append(T("Hands {x:.0f} mm ahead of the hip, {d:.0f} mm below it (drop).",
                           x=co['hip_to_hand_x'], d=co['hip_to_hand_drop']))
        else:
            lines.append(T("Hands {x:.0f} mm ahead of the hip, {d:.0f} mm above it.",
                           x=co['hip_to_hand_x'], d=-co['hip_to_hand_drop']))
    if co.get('saddle_target_mm'):
        lines.append(T("Saddle height (BB to saddle top): now {now:.0f} mm, target {tgt:.0f} mm.",
                       now=co['saddle_now_mm'], tgt=co['saddle_target_mm']))
        if abs(co['saddle_target_mm'] - co['saddle_now_mm']) > 5:
            lines.append(T("Reach it in 3–5 mm steps."))
    if co.get('lemond_mm'):
        lines.append(T("Inseam formulas: LeMond {l:.0f} mm, Hamley {h:.0f} mm (BB to saddle top). Static starting "
                       "points only.", l=co['lemond_mm'], h=co['hamley_mm']))
    an = calc.get('ankle') or {}
    if an.get('bdc') is not None:
        lines.append(T("Ankle at the bottom of the stroke: {b:+.0f}° (+ = toe down), range {r:.0f}° over the stroke.",
                       b=an['bdc'], r=an['range']))
    ae = calc.get('aero') or {}
    if ae.get('area_m2'):
        lines.append(T("Aero estimate: frontal area {a:.2f} m², about {p:.0f} W of air drag at {v:.0f} km/h; 5° lower "
                       "torso saves about {s:.0f} W. Rough estimate (Heil 2001, assumed Cd 0.7).",
                       a=ae['area_m2'], p=ae['power_w'], v=ae['speed_kmh'], s=ae['saving_w']))
    if not lines:
        return
    pdf.section(T('Fit calculations'))
    pdf.set_font('Helvetica', '', 10)
    for line in lines:
        pdf.multi_cell(0, 5.5, _latin(f"- {line}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
