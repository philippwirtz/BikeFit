// Rider form: name, height, riding style, flexibility, discomfort and cranks as plain
// fields and buttons. Every change is saved and handed to the wizard through `onChange`.
import { $, h, icon, store } from "./util.js";

const PROFILE_ICONS = { road_endurance: "bike", road_race: "zap", tri_tt: "wind", mtb_gravel: "mountain", city: "bike" };
const CRANKS = [165, 170, 172.5, 175];

/** "178", "178 cm", "1.78 m" or 5'10" to centimetres, or null. */
function parseHeight(text) {
  const t = text.toLowerCase().replace(/[″"]/g, "in").replace(/[′’]/g, "'");
  let m = t.match(/(\d)\s*(?:'|ft|foot|feet)\s*(\d{1,2}(?:\.\d)?)?/);
  if (m) return Math.round((Number(m[1]) * 12 + Number(m[2] || 0)) * 2.54);
  m = t.match(/(\d(?:[.,]\d{1,2})?)\s*m\b/);
  if (m) return Math.round(Number(m[1].replace(",", ".")) * 100);
  m = t.match(/(\d{2,3}(?:[.,]\d)?)/);
  if (m) {
    const v = Number(m[1].replace(",", "."));
    return v < 3 ? Math.round(v * 100) : v;
  }
  return null;
}

/** A row of toggle buttons. `isOn(value)` says which are pressed; `onPick(value)` handles a click. */
function chipRow(items, isOn, onPick, { multi = false, label } = {}) {
  const row = h("div", { class: "chip-row", role: "group", "aria-label": label });
  const refresh = () => row.querySelectorAll("button").forEach((b, i) => b.setAttribute("aria-pressed", String(isOn(items[i].value))));
  row.replaceChildren(...items.map((c) => h("button", {
    type: "button", class: "quick-chip", title: c.help || null,
    onclick: () => { onPick(c.value); refresh(); },
  }, c.icon ? icon(c.icon, "icon icon-sm") : null, multi && !c.exclusive ? icon("check-bold", "icon icon-sm chip-tick") : null, c.label)));
  refresh();
  return row;
}

export function createIntake({ config, onChange }) {
  const defaults = () => ({ name: "", profile: config.default_profile, height: null, flexibility: "average", pains: [], crank: 172.5,
    inseam: null, weight: null, saddle: null, sta: null });
  let stored = {};
  try { stored = JSON.parse(store.get("intake", "{}")) || {}; } catch { stored = {}; }
  let answers = { ...defaults(), ...stored };
  if (!config.profiles[answers.profile]) answers.profile = config.default_profile;

  const save = () => {
    store.set("intake", JSON.stringify(answers));
    onChange?.(answers);
  };
  const set = (key, value) => { answers[key] = value; save(); };

  function field(label, control, hint) {
    return h("div", { class: "field" }, h("span", { class: "field-label" }, label), control, hint || null);
  }

  function render() {
    const heightHint = h("p", { class: "field-hint", "aria-live": "polite" }, "Lets us turn angles into millimetres. Optional.");
    const heightInput = h("input", {
      class: "input", id: "rider-height", type: "text", inputmode: "decimal", autocomplete: "off",
      placeholder: "178 cm or 5'10\"", value: answers.height ? String(answers.height) : "", "aria-label": "Height",
      oninput: (e) => {
        const text = e.target.value.trim();
        const cm = text ? parseHeight(text) : null;
        const bad = text && !(cm >= 100 && cm <= 230);
        e.target.setAttribute("aria-invalid", String(!!bad));
        heightHint.textContent = bad ? "That doesn't look like a height. Try 178 or 5'10\"." : cm ? `${cm} cm` : "Lets us turn angles into millimetres. Optional.";
        set("height", bad ? null : cm);
      },
    });
    const nameInput = h("input", {
      class: "input", id: "rider-name", type: "text", autocomplete: "given-name", maxlength: "40",
      placeholder: "Your first name (optional)", value: answers.name || "", "aria-label": "Name",
      oninput: (e) => set("name", e.target.value.trim().slice(0, 40)),
    });

    const flexHelp = h("p", { class: "field-hint" }, config.flexibility[answers.flexibility]?.help || "");
    const flex = chipRow(Object.entries(config.flexibility).map(([value, f]) => ({ value, label: f.label, help: f.help })),
      (v) => answers.flexibility === v,
      (v) => { set("flexibility", v); flexHelp.textContent = config.flexibility[v].help; },
      { label: "Flexibility" });

    const painNone = { value: "none", label: "Nothing hurts", exclusive: true };
    const pains = chipRow([...Object.entries(config.pains).map(([value, label]) => ({ value, label })), painNone],
      (v) => (v === "none" ? !answers.pains.length : answers.pains.includes(v)),
      (v) => set("pains", v === "none" ? [] : answers.pains.includes(v) ? answers.pains.filter((p) => p !== v) : [...answers.pains, v]),
      { multi: true, label: "Discomfort" });

    const crankHint = h("p", { class: "field-hint" }, "Stamped on the inside of the crank arm. Only the millimetre scale depends on it.");
    const crankInput = h("input", {
      class: "input", id: "rider-crank", type: "number", min: "150", max: "185", step: "0.5", inputmode: "decimal",
      value: String(answers.crank), "aria-label": "Crank length in millimetres",
      oninput: (e) => {
        const v = Number(e.target.value);
        const ok = v >= 150 && v <= 185;
        e.target.setAttribute("aria-invalid", String(!ok));
        crankHint.textContent = ok ? "Stamped on the inside of the crank arm. Only the millimetre scale depends on it." : "Crank lengths are between 150 and 185 mm.";
        if (ok) set("crank", v);
        crankChips.querySelectorAll("button").forEach((b, i) => b.setAttribute("aria-pressed", String(CRANKS[i] === answers.crank)));
      },
    });
    const crankChips = chipRow(CRANKS.map((value) => ({ value, label: `${value} mm` })),
      (v) => answers.crank === v,
      (v) => { crankInput.value = String(v); crankInput.setAttribute("aria-invalid", "false"); set("crank", v); },
      { label: "Crank length" });

    const profiles = chipRow(Object.entries(config.profiles).map(([value, p]) => ({ value, label: p.short, help: p.blurb, icon: PROFILE_ICONS[value] })),
      (v) => answers.profile === v,
      (v) => { set("profile", v); profileHelp.textContent = config.profiles[v].blurb; },
      { label: "Riding style" });
    const profileHelp = h("p", { class: "field-hint" }, config.profiles[answers.profile]?.blurb || "");

    const num = (key, label, min, max, step, unit, hint) => {
      const input = h("input", {
        class: "input", id: `rider-${key}`, type: "number", min: String(min), max: String(max), step: String(step), inputmode: "decimal",
        value: answers[key] ?? "", "aria-label": label,
        oninput: (e) => {
          const v = e.target.value === "" ? null : Number(e.target.value);
          const ok = v == null || (v >= min && v <= max);
          e.target.setAttribute("aria-invalid", String(!ok));
          set(key, ok ? v : null);
        },
      });
      return field(label, h("span", { class: "input-affix" }, input, h("span", { class: "affix" }, unit)), h("p", { class: "field-hint" }, hint));
    };
    const more = h("details", { class: "calc-more rider-more", open: answers.inseam || answers.weight || answers.saddle || answers.sta || null },
      h("summary", {}, icon("chevron-right"), "Body and bike details (optional)"),
      h("div", { class: "rider-grid" },
        num("inseam", "Inseam", 55, 110, 0.5, "cm", "Floor to crotch, barefoot. Adds the saddle-height formulas."),
        num("weight", "Weight", 30, 160, 0.5, "kg", "For the aero estimate."),
        num("saddle", "Saddle height now", 550, 950, 1, "mm", "BB centre to saddle top, along the seat tube."),
        num("sta", "Seat-tube angle", 65, 82, 0.5, "°", "From the frame geometry; 73° if unknown.")));

    $("#rider-form").replaceChildren(
      h("div", { class: "rider-grid" }, field("Name", nameInput), field("Height", heightInput, heightHint)),
      field("What kind of riding do you do?", profiles, profileHelp),
      field("How flexible are you? Stand with straight legs and reach for the floor.", flex, flexHelp),
      field("Does anything hurt or go numb when you ride?", pains),
      field("Crank length", h("div", { class: "rider-crank" }, crankChips, crankInput), crankHint),
      more);
  }

  return {
    /** Build the form when the step opens (once). */
    start() {
      if (!$("#rider-form").childElementCount) render();
    },
    restart() {
      answers = defaults();
      save();
      render();
    },
    /** Answers are always complete, so this just returns them. */
    finalize() { return answers; },
    get answers() { return answers; },
  };
}
