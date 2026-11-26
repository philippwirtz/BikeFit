// What-if simulator and the fit-calculations card (crank length, ankle, coordinates, aero).
import { $, h, icon, api, deg, mm, num0, toast } from "./util.js";
import { t, locale } from "./i18n.js";

const CRANKS = [150, 155, 160, 162.5, 165, 167.5, 170, 172.5, 175];
const nf = (digits) => new Intl.NumberFormat(locale(), { minimumFractionDigits: digits, maximumFractionDigits: digits });
const signed = (v, unit = "mm", digits = 0) => {
  if (v == null || !isFinite(v)) return "–";
  const r = Number(Math.abs(v).toFixed(digits));
  const sign = r === 0 ? "±" : v > 0 ? "+" : "−";
  return `${sign}${nf(digits).format(r)}${unit === "°" ? "°" : ` ${unit}`}`;
};

// ---------------------------------------------------------------- simulator
function slider(id, label, min, max, step, value, unit = "mm") {
  const out = h("output", { class: "num t-secondary", for: id }, signed(value, unit));
  const input = h("input", { type: "range", id, min, max, step, value: String(value) });
  input.addEventListener("input", () => (out.textContent = signed(Number(input.value), unit)));
  return { el: h("div", { class: "sim-slider" }, h("div", { class: "simulator-head" }, h("label", { class: "t-small", for: id }, label), out), input), input, out };
}

/** Knee-only simulator from the law of cosines, for fits without a stroke model. */
function simpleSimulator(d, box) {
  const b = d.biomech || {};
  const L1 = b.thigh_px, L2 = b.shank_px;
  const reach0 = Math.sqrt(L1 * L1 + L2 * L2 - 2 * L1 * L2 * Math.cos((d.metrics.knee_ext * Math.PI) / 180));
  const [lo, hi] = d.ranges.knee_ext;
  const s = slider("sim-range", t("Saddle height"), -20, 20, 1, Math.round(Math.max(-20, Math.min(20, b.saddle_adj_mm || 0))));
  const knee = h("div", { class: "readout-value" }, "–");
  const update = () => {
    const r = reach0 + Number(s.input.value) / b.mm_per_px;
    const c = Math.max(-1, Math.min(1, (L1 * L1 + L2 * L2 - r * r) / (2 * L1 * L2)));
    const k = (Math.acos(c) * 180) / Math.PI;
    knee.textContent = deg(k);
    knee.style.color = k >= lo && k <= hi ? "var(--color-ok)" : "";
  };
  s.input.addEventListener("input", update);
  box.replaceChildren(
    h("p", { class: "t-h3" }, t("Saddle height simulator")), s.el,
    h("div", { class: "simulator-out" },
      h("div", { class: "readout" }, h("div", { class: "readout-label" }, t("Knee at bottom")), knee),
      h("div", { class: "readout" }, h("div", { class: "readout-label" }, t("Target")), h("div", { class: "readout-value" }, `${lo}–${hi}°`))),
    h("p", { class: "t-caption", style: "margin-top: var(--s-2)" }, t("Law-of-cosines estimate from your measured thigh and shank. Move in 3–5 mm steps.")));
  update();
}

const SIM_ROWS = [
  ["knee_ext", "Knee at bottom"], ["knee_flex", "Knee at top"], ["hip_closed", "Hip angle at top"],
  ["torso", "Torso"], ["shoulder", "Shoulder"], ["kops_mm", "Knee vs pedal at 3 o'clock"],
];

export function renderSimulator(d, box) {
  const b = d.biomech || {};
  const canModel = d.mode === "video" && d.calc?.model;
  const canSimple = d.mode === "video" && b.mm_per_px && b.thigh_px && b.shank_px && d.metrics?.knee_ext;
  box.hidden = !(canModel || canSimple);
  if (!canModel) {
    if (canSimple) simpleSimulator(d, box);
    return;
  }
  const crankNow = Number(d.rider?.crank_mm || 172.5);
  const sl = {
    saddle: slider("sim-saddle", t("Saddle height"), -20, 20, 1, 0),
    setback: slider("sim-setback", t("Saddle setback (back = +)"), -20, 20, 1, 0),
    stem: slider("sim-stem", t("Stem length"), -30, 30, 5, 0),
    bar: slider("sim-bar", t("Bar height"), -30, 30, 5, 0),
  };
  const crank = h("select", { class: "select", id: "sim-crank" },
    [...new Set([...CRANKS, crankNow])].sort((a, c) => a - c).map((c) => h("option", { value: String(c), selected: c === crankNow }, `${c} mm`)));
  const body = h("tbody", {});
  const note = h("p", { class: "t-caption", style: "margin-top: var(--s-2)" });
  const presets = h("div", { class: "row sim-presets" });
  const reset = () => {
    Object.values(sl).forEach((s) => { s.input.value = "0"; s.input.dispatchEvent(new Event("input")); });
    crank.value = String(crankNow);
    run();
  };
  if (b.saddle_adj_mm) {
    presets.append(h("button", { class: "btn btn-ghost btn-sm", type: "button", onclick: () => {
      reset(); sl.saddle.input.value = String(Math.round(b.saddle_adj_mm)); sl.saddle.input.dispatchEvent(new Event("input")); run();
    } }, icon("sparkles", "icon icon-sm"), t("Suggested saddle height")));
  }
  const sug = d.calc?.crank?.suggest;
  if (sug) {
    presets.append(h("button", { class: "btn btn-ghost btn-sm", type: "button", onclick: () => {
      reset(); crank.value = String(sug.crank_mm); sl.saddle.input.value = String(Math.round(sug.saddle_mm));
      sl.saddle.input.dispatchEvent(new Event("input")); run();
    } }, icon("sparkles", "icon icon-sm"), t("Suggested cranks ({c} mm)", { c: sug.crank_mm })));
  }
  presets.append(h("button", { class: "btn btn-ghost btn-sm", type: "button", onclick: reset }, icon("rotate-ccw", "icon icon-sm"), t("Reset")));

  let timer = 0, seq = 0;
  async function run() {
    const my = ++seq;
    const body0 = { saddle_mm: Number(sl.saddle.input.value), setback_mm: Number(sl.setback.input.value),
      stem_mm: Number(sl.stem.input.value), bar_mm: Number(sl.bar.input.value), crank_mm: Number(crank.value) };
    let res;
    try {
      res = await api(`/api/sessions/${d.id}/whatif`, { method: "POST", body: JSON.stringify(body0) });
    } catch (err) {
      note.textContent = err.message;
      return;
    }
    if (my !== seq) return;
    body.replaceChildren(...SIM_ROWS.map(([k, label]) => {
      const p = res.pred[k];
      if (!p || p.now == null) return null;
      const isMm = k === "kops_mm";
      const rng = d.ranges?.[k];
      const inRange = rng && p.new >= rng[0] && p.new <= rng[1];
      const moved = Math.abs(p.delta) >= (isMm ? 1 : 0.3);
      return h("tr", {},
        h("th", { scope: "row" }, t(label)),
        h("td", {}, isMm ? mm(p.now, true) : deg(p.now)),
        h("td", { class: moved ? (rng ? (inRange ? "delta-good" : "delta-bad") : "") : "t-muted" },
          isMm ? mm(p.new, true) : deg(p.new), moved ? h("small", {}, ` (${signed(p.delta, isMm ? "mm" : "°", isMm ? 0 : 1)})`) : ""),
        h("td", { class: "t-muted" }, rng ? `${rng[0]}–${rng[1]}°` : "–"));
    }).filter(Boolean));
    const bits = [];
    if (!res.reachable) bits.push(t("The bars are out of reach with this change (arms fully stretched)."));
    if (res.aero_w != null && Math.abs(res.aero_w) >= 0.5) {
      bits.push(res.aero_w < 0 ? t("Aero: about {w} W less drag at 35 km/h (rough estimate).", { w: num0(-res.aero_w) })
        : t("Aero: about {w} W more drag at 35 km/h (rough estimate).", { w: num0(res.aero_w) }));
    }
    bits.push(t("Model of your measured stroke: thigh, shank and foot are rigid, the hands stay on the bars. Predictions are changes added to your measured angles."));
    note.textContent = bits.join(" ");
  }
  const schedule = () => { clearTimeout(timer); timer = setTimeout(run, 120); };
  Object.values(sl).forEach((s) => s.input.addEventListener("input", schedule));
  crank.addEventListener("change", run);

  box.replaceChildren(
    h("div", { class: "simulator-head" }, h("p", { class: "t-h3" }, t("What-if simulator")), h("span", { class: "t-caption" }, t("mm, + = higher / longer"))),
    h("div", { class: "sim-grid" }, sl.saddle.el, sl.setback.el, sl.stem.el, sl.bar.el,
      h("div", { class: "sim-slider" }, h("label", { class: "t-small", for: "sim-crank" }, t("Crank length")), crank)),
    presets,
    h("div", { class: "table-scroll" }, h("table", { class: "data-table sim-table" },
      h("thead", {}, h("tr", {}, h("th", { scope: "col" }, t("Angle")), h("th", { scope: "col" }, t("Now")), h("th", { scope: "col" }, t("Predicted")), h("th", { scope: "col" }, t("Target")))),
      body)),
    note);
  run();
}

// ---------------------------------------------------------------- calculations card
const kv = (label, value, sub) => h("div", { class: "readout" }, h("div", { class: "readout-label" }, label), h("div", { class: "readout-value" }, value), sub ? h("div", { class: "t-caption" }, sub) : null);

function crankBlock(c) {
  if (!c?.rows?.length) return null;
  const rows = c.rows.map((r) => h("tr", { class: r.current ? "is-current" : r.crank_mm === c.suggest_mm ? "is-suggest" : "" },
    h("th", { scope: "row" }, `${r.crank_mm} mm`, r.current ? h("small", {}, ` · ${t("now")}`) : r.crank_mm === c.suggest_mm ? h("small", {}, ` · ${t("suggested")}`) : ""),
    h("td", {}, signed(r.saddle_mm)), h("td", {}, deg(r.hip_closed)), h("td", {}, deg(r.knee_flex))));
  const lines = [];
  if (c.suggest_mm) {
    lines.push(c.partial
      ? t("Shorter cranks help but don't fully open the hip: {c} mm is the best option here. Raise the bars too.", { c: c.suggest_mm })
      : t("{c} mm cranks (saddle {dh}) bring the hip and knee into range.", { c: c.suggest_mm, dh: signed(c.suggest.saddle_mm) }));
  } else {
    lines.push(t("Your current cranks don't close the hip or knee too far, so there's no reason to change them for fit."));
  }
  if (c.tibia_rule_mm) lines.push(t("By tibia length (41 %, Martin & Spirduso 2001): {c} mm. That rule is for peak sprint power; comfort and hip angle usually matter more.", { c: num0(c.tibia_rule_mm) }));
  return h("section", { class: "calc-block" },
    h("h3", { class: "t-small calc-title" }, t("Crank length")),
    h("p", { class: "t-small" }, lines[0]),
    h("div", { class: "table-scroll" }, h("table", { class: "data-table" },
      h("thead", {}, h("tr", {}, h("th", { scope: "col" }, t("Crank")), h("th", { scope: "col" }, t("Saddle")), h("th", { scope: "col" }, t("Hip at top")), h("th", { scope: "col" }, t("Knee at top")))),
      h("tbody", {}, rows))),
    h("p", { class: "t-caption" }, t("Saddle re-set so your knee extension stays as measured.")),
    lines[1] ? h("p", { class: "t-caption" }, lines[1]) : null);
}

function ankleBlock(a) {
  if (!a || a.bdc == null) return null;
  const verdict = a.bdc > 25 ? t("Strongly toe-down: check that the saddle isn't too high.")
    : a.bdc < -5 ? t("Heel drops below the pedal: this straightens the knee.")
      : a.bdc > 15 ? t("A little more toe-down than typical.") : t("Within the usual range.");
  return h("section", { class: "calc-block" },
    h("h3", { class: "t-small calc-title" }, t("Ankle")),
    h("div", { class: "kv" }, kv(t("At the bottom"), signed(a.bdc, "°"), t("+ = toe down, typical +5 to +15°")), kv(t("Range over the stroke"), deg(a.range, 0))),
    h("p", { class: "t-caption" }, verdict));
}

function coordBlock(c) {
  if (!c) return null;
  const items = [];
  if (c.hip_x != null) items.push(kv(t("Hip behind BB"), mm(-c.hip_x)), kv(t("Hip above BB"), mm(c.hip_y)));
  if (c.hip_to_hand_x != null) {
    items.push(kv(t("Hands ahead of hip"), mm(c.hip_to_hand_x)),
      kv(c.hip_to_hand_drop >= 0 ? t("Hands below hip") : t("Hands above hip"), mm(Math.abs(c.hip_to_hand_drop))));
  }
  if (c.saddle_target_mm != null) {
    const big = Math.abs(c.saddle_target_mm - c.saddle_now_mm) > 5;
    items.push(kv(t("Saddle height now"), mm(c.saddle_now_mm)),
      kv(t("Saddle height target"), mm(c.saddle_target_mm), big ? t("Reach it in 3–5 mm steps.") : null));
  }
  if (c.lemond_mm) items.push(kv(t("LeMond (0.883 × inseam)"), mm(c.lemond_mm)), kv(t("Hamley (109 % inseam − crank)"), mm(c.hamley_mm)));
  if (!items.length) return null;
  return h("section", { class: "calc-block" },
    h("h3", { class: "t-small calc-title" }, t("Fit coordinates")),
    h("div", { class: "kv" }, items),
    h("p", { class: "t-caption" }, t("Joint positions relative to the bottom bracket, from the video. Use them to set up another bike the same way. Saddle heights are measured from the BB centre to the top of the saddle; the inseam formulas are static starting points only.")));
}

function aeroBlock(a) {
  if (!a) return null;
  return h("section", { class: "calc-block" },
    h("h3", { class: "t-small calc-title" }, t("Aero estimate")),
    h("div", { class: "kv" }, kv(t("Frontal area"), `${nf(2).format(a.area_m2)} m²`),
      kv(t("Air drag at {v} km/h", { v: num0(a.speed_kmh) }), `${num0(a.power_w)} W`),
      kv(t("Torso 5° lower"), t("−{w} W", { w: num0(a.saving_w) }))),
    h("p", { class: "t-caption" }, a.extrapolated
      ? t("Rough estimate (Heil 2001, Cd 0.7 assumed). Your torso angle is outside the 5–25° the formula was fitted on, so treat it as a trend only.")
      : t("Rough estimate (Heil 2001, Cd 0.7 assumed, bike not included).")));
}

function detailsForm(d, onSave) {
  const r = d.rider || {};
  const f = (id, label, value, min, max, step, unit) => h("label", { class: "field" }, h("span", { class: "field-label" }, label),
    h("span", { class: "input-affix" }, h("input", { class: "input", id, type: "number", min, max, step, inputmode: "decimal", value: value ?? "" }), h("span", { class: "affix" }, unit)));
  const form = h("form", { class: "calc-details" },
    h("div", { class: "rider-grid" },
      f("cd-inseam", t("Inseam"), r.inseam_cm, 55, 110, 0.5, "cm"),
      f("cd-weight", t("Weight"), r.weight_kg, 30, 160, 0.5, "kg"),
      f("cd-saddle", t("Saddle height now"), r.saddle_height_mm, 550, 950, 1, "mm"),
      f("cd-sta", t("Seat-tube angle"), r.seat_tube_deg, 65, 82, 0.5, "°")),
    h("div", { class: "row" }, h("button", { class: "btn btn-secondary btn-sm", type: "submit" }, t("Update calculations"))));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const val = (id) => { const v = $(`#${id}`, form).value; return v === "" ? null : Number(v); };
    onSave({ inseam_cm: val("cd-inseam"), weight_kg: val("cd-weight"), saddle_height_mm: val("cd-saddle"), seat_tube_deg: val("cd-sta") });
  });
  return h("details", { class: "calc-more", open: !(r.inseam_cm || r.weight_kg || r.saddle_height_mm) || null },
    h("summary", {}, icon("chevron-right"), t("Add body and bike details")),
    h("p", { class: "t-caption" }, t("Optional. Inseam adds the saddle-height formulas, weight the aero estimate, your measured saddle height a target in mm, and the seat-tube angle sharpens the simulator (default 73°).")),
    form);
}

export function renderCalc(d, card, onRescore) {
  const c = d.calc;
  card.hidden = d.mode !== "video" || !c;
  if (card.hidden) return;
  const blocks = [crankBlock(c.crank), ankleBlock(c.ankle), coordBlock(c.coords), aeroBlock(c.aero)].filter(Boolean);
  const body = $("#calc-body", card);
  body.replaceChildren(...blocks,
    blocks.length ? "" : h("p", { class: "t-small t-muted" }, t("These calculations need a side-view video with a millimetre scale.")),
    detailsForm(d, async (rider) => {
      try {
        await onRescore(rider);
        toast(t("Calculations updated."), { tone: "success" });
      } catch (err) {
        toast(err.message, { tone: "error" });
      }
    }));
}
