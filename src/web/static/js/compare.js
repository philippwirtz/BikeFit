// Comparing two fits: change table with a noise check, left/right reading, and a
// side-by-side player that keeps both riders at the same crank angle.
import { $, h, icon, api, deg, mm, dateFmt, toast, fix } from "./util.js";
import { t } from "./i18n.js";
import { poseAt, drawPose, fitCanvas, containRect } from "./overlay.js";

const half = (d, k) => {
  const ci = d.metric_detail?.[k]?.ci;
  return ci ? (ci[1] - ci[0]) / 2 : null;
};

/** Is a change bigger than measurement noise? Validated MDC first, else both fits' 95% CIs. */
export function noiseCheck(config, a, b, k) {
  const delta = a.metrics[k] - b.metrics[k];
  const mdc = config.validation?.metrics?.[k]?.mdc95;
  if (mdc) return { real: Math.abs(delta) > mdc, limit: mdc, source: "mdc" };
  const ha = half(a, k), hb = half(b, k);
  if (ha == null || hb == null) return { real: null, limit: null };
  const limit = Math.sqrt(ha * ha + hb * hb);
  return { real: Math.abs(delta) > limit, limit, source: "ci" };
}

const sideOf = (d) => d.extra?.side || d.track?.facing || null;

export function isLeftRight(a, b) {
  const sa = sideOf(a), sb = sideOf(b);
  return a.mode === "video" && b.mode === "video" && sa && sb && sa !== sb;
}

/** Table of changes (this fit `d` vs an earlier/other fit). */
export function compareTable(config, d, other) {
  const lr = isLeftRight(d, other);
  const colA = lr ? t(sideOf(other) === "left" ? "Left leg" : "Right leg") : t("Earlier");
  const colB = lr ? t(sideOf(d) === "left" ? "Left leg" : "Right leg") : t("This fit");
  const rows = Object.entries(config.metrics).map(([k, meta]) => {
    const a = d.metrics?.[k], b = other.metrics?.[k];
    if (!a || !b) return null;
    const [lo, hi] = d.ranges[k];
    const dist = (v) => (v < lo ? lo - v : v > hi ? v - hi : 0);
    const better = dist(a) < dist(b) - 0.5, worse = dist(a) > dist(b) + 0.5;
    const delta = a - b;
    const n = noiseCheck(config, d, other, k);
    const noise = n.real == null ? h("span", { class: "t-muted" }, "–")
      : n.real ? h("span", { class: "badge badge-ok" }, icon("circle-check"), t("Real"))
        : h("span", { class: "badge" }, icon("info"), t("Within noise (±{x}°)", { x: fix(n.limit) }));
    return h("tr", {},
      h("th", { scope: "row" }, meta.short),
      h("td", {}, deg(b)), h("td", {}, deg(a)),
      h("td", { class: lr ? "" : better ? "delta-good" : worse ? "delta-bad" : "" },
        `${delta > 0 ? "+" : ""}${fix(delta)}°`, lr ? "" : better ? ` · ${t("closer to target")}` : worse ? ` · ${t("further from target")}` : ""),
      h("td", {}, noise));
  }).filter(Boolean);
  const kopsA = d.biomech?.kops_mm, kopsB = other.biomech?.kops_mm;
  if (kopsA != null && kopsB != null) {
    rows.push(h("tr", {}, h("th", { scope: "row" }, t("Knee vs pedal at 3 o'clock")), h("td", {}, mm(kopsB, true)), h("td", {}, mm(kopsA, true)),
      h("td", {}, mm(kopsA - kopsB, true)), h("td", {}, h("span", { class: "t-muted" }, "–"))));
  }
  const scoreRow = lr ? null : h("tr", {}, h("th", { scope: "row" }, t("Fit score")), h("td", {}, other.score ?? "–"), h("td", {}, d.score ?? "–"),
    h("td", {}, d.score != null && other.score != null ? `${d.score - other.score > 0 ? "+" : ""}${d.score - other.score}` : "–"), h("td", {}));
  const usedMdc = Object.keys(config.metrics).some((k) => config.validation?.metrics?.[k]?.mdc95);
  return h("div", {},
    h("table", { class: "data-table compare-table" },
      h("thead", {}, h("tr", {}, h("th", { scope: "col" }, t("Angle")), h("th", { scope: "col" }, colA), h("th", { scope: "col" }, colB),
        h("th", { scope: "col" }, t("Difference")), h("th", { scope: "col" }, t("Beyond noise?")))),
      h("tbody", {}, scoreRow, rows)),
    h("p", { class: "t-caption", style: "margin-top: var(--s-2)" }, usedMdc
      ? t("“Real” means the change is larger than the smallest detectable change measured for this setup (MDC95).")
      : t("“Real” means the change is larger than both fits' 95% ranges combined. Film the same setup three times and run scripts/repeatability.py for a validated threshold.")));
}

/** Plain-language reading of a left/right pair. */
export function leftRightNotes(config, d, other) {
  const notes = [];
  const k = "knee_ext";
  if (d.metrics?.[k] && other.metrics?.[k]) {
    const diff = Math.abs(d.metrics[k] - other.metrics[k]);
    const n = noiseCheck(config, d, other, k);
    if (n.real && diff >= 4) {
      const longer = d.metrics[k] > other.metrics[k] ? sideOf(d) : sideOf(other);
      notes.push(t("Knee extension differs by {x}° between legs: the {side} leg straightens more. Common causes are a leg-length difference, different cleat positions or a hip that drops to one side. Check cleats first; a leg-length difference should be measured before shimming.",
        { x: fix(diff), side: t(longer) }));
    } else {
      notes.push(t("Both legs extend alike at the bottom of the stroke (difference {x}°).", { x: fix(diff) }));
    }
  }
  const ka = d.biomech?.kops_mm, kb = other.biomech?.kops_mm;
  if (ka != null && kb != null && Math.abs(ka - kb) > 15) {
    notes.push(t("The knees sit {x} mm apart relative to the pedal at 3 o'clock: compare cleat fore-aft positions.", { x: Math.abs(ka - kb).toFixed(0) }));
  }
  if (d.backend && other.backend && d.backend !== other.backend) notes.push(t("The two clips used different pose engines, which adds a small offset."));
  return notes;
}

// ---------------------------------------------------------------- side by side
function strokeWindow(track) {
  // One full revolution from the middle of the clip: plays smoothly and avoids start-up frames
  const th = track.theta;
  if (!th) return null;
  const mid = Math.floor(th.length / 2);
  let acc = 0, prev = null;
  const idx = [];
  for (let i = mid; i < th.length && acc < 360; i++) {
    if (th[i] == null) continue;
    if (prev != null) { let d = th[i] - prev; if (d < -180) d += 360; if (d > 180) d -= 360; acc += Math.abs(d); }
    prev = th[i];
    idx.push(i);
  }
  return idx.length > 4 ? idx : null;
}

function timeAtCrank(track, win, phi) {
  let best = win[0], bd = 1e9;
  for (const i of win) {
    let d = Math.abs(track.theta[i] - phi) % 360;
    if (d > 180) d = 360 - d;
    if (d < bd) { bd = d; best = i; }
  }
  return track.t[best];
}

/** Pose in mm relative to the bottom bracket, so two riders can be overlaid. */
function bikeFrame(d, pose) {
  const tr = d.track, s = d.biomech?.mm_per_px;
  if (!tr?.crank || !s) return null;
  const [fw, fh] = tr.size;
  const fwd = tr.facing === "right" ? 1 : -1;
  const out = {};
  for (const [k, p] of Object.entries(pose.joints)) out[k] = [(p[0] * fw - tr.crank.cx * fw) * fwd * s, (tr.crank.cy * fh - p[1] * fh) * s];
  return out;
}

const OVERLAY_BONES = [["shoulder", "elbow"], ["elbow", "wrist"], ["shoulder", "hip"], ["hip", "knee"], ["knee", "ankle"], ["ankle", "toe"]];

function drawOverlay(canvas, poses, colors, phi) {
  const { ctx, width, height } = fitCanvas(canvas);
  ctx.clearRect(0, 0, width, height);
  // Bike frame: x -450..1000 mm, y -250..1300 mm
  const sx = width / 1450, sy = height / 1550, s = Math.min(sx, sy);
  const X = (x) => width / 2 + (x - 275) * s, Y = (y) => height - (y + 250) * s;
  ctx.strokeStyle = getComputedStyle(canvas).color;
  ctx.globalAlpha = 0.35;
  ctx.beginPath();
  ctx.arc(X(0), Y(0), 172.5 * s, 0, Math.PI * 2);
  ctx.stroke();
  ctx.globalAlpha = 1;
  poses.forEach((p, n) => {
    if (!p) return;
    ctx.strokeStyle = colors[n];
    ctx.lineWidth = 3;
    ctx.lineCap = "round";
    for (const [a, b] of OVERLAY_BONES) {
      if (!p[a] || !p[b]) continue;
      ctx.beginPath();
      ctx.moveTo(X(p[a][0]), Y(p[a][1]));
      ctx.lineTo(X(p[b][0]), Y(p[b][1]));
      ctx.stroke();
    }
  });
  ctx.fillStyle = getComputedStyle(canvas).color;
  ctx.font = `${12 * Math.min(2, window.devicePixelRatio || 1)}px system-ui`;
  ctx.fillText(`${t("Crank")} ${Math.round(phi)}°`, 8, 18 * Math.min(2, window.devicePixelRatio || 1));
}

export async function openSideBySide(a, b) {
  const dlg = $("#dlg-sbs");
  const fits = [b, a]; // earlier left, this fit right
  const wins = fits.map((f) => (f.track ? strokeWindow(f.track) : null));
  if (wins.some((w) => !w)) {
    toast(t("Side by side needs two side-view videos with a modelled pedal stroke."), { tone: "error" });
    return;
  }
  const panels = fits.map((f, n) => {
    const video = h("video", { muted: true, playsinline: true, preload: "auto", src: f.media_url });
    const img = h("img", { class: "stage-img", alt: "", hidden: true });
    const canvas = h("canvas", {});
    const label = isLeftRight(a, b) ? t(sideOf(f) === "left" ? "Left leg" : "Right leg") : n === 0 ? t("Earlier") : t("This fit");
    const el = h("figure", { class: "sbs-panel" }, h("div", { class: "stage sbs-stage" }, video, img, canvas),
      h("figcaption", { class: "t-small" }, h("strong", {}, label), ` · ${dateFmt(f.created)}`));
    const st = { f, video, img, canvas, el, frameMode: false, busy: false, want: null, time: 0 };
    video.addEventListener("error", () => {
      st.frameMode = true; video.hidden = true; img.hidden = false;
      st.busy = false; // the seek that was waiting on the video never finishes
      seek(st, st.want ?? st.time);
    }, { once: true });
    video.addEventListener("seeked", () => { st.busy = false; draw(st); if (st.want != null) seek(st, st.want); });
    const frameDone = () => { st.busy = false; draw(st); if (st.want != null) seek(st, st.want); };
    img.addEventListener("load", frameDone);
    img.addEventListener("error", frameDone);
    return st;
  });

  function draw(st) {
    const { ctx, width, height } = fitCanvas(st.canvas);
    ctx.clearRect(0, 0, width, height);
    const tr = st.f.track;
    drawPose(ctx, poseAt(tr, st.time), containRect(tr.size[0], tr.size[1], width, height), { crank: tr.crank });
  }
  function seek(st, time) {
    if (st.busy) { st.want = time; return; }
    st.want = null;
    st.busy = true;
    st.time = time;
    if (st.frameMode) st.img.src = `/api/sessions/${st.f.id}/frame?t=${time.toFixed(3)}&w=720`;
    else st.video.currentTime = time;
  }

  const overlay = h("canvas", { class: "sbs-overlay" });
  const canOverlay = fits.every((f) => f.track?.crank && f.biomech?.mm_per_px);
  const phiInput = h("input", { type: "range", min: "0", max: "359", step: "1", value: "180", "aria-label": t("Crank angle") });
  const playBtn = h("button", { class: "btn btn-secondary btn-sm", type: "button" }, icon("play", "icon icon-sm"), t("Play"));
  const colors = ["#9DB4FF", "#5CCFE0"];
  let phi = 180, raf = 0, playing = false, last = 0;

  const show = () => {
    phiInput.value = String(Math.round(phi));
    panels.forEach((p, n) => seek(p, timeAtCrank(p.f.track, wins[n], phi)));
    if (canOverlay) {
      const poses = panels.map((p, n) => bikeFrame(p.f, poseAt(p.f.track, timeAtCrank(p.f.track, wins[n], phi))));
      drawOverlay(overlay, poses, colors, phi);
    }
  };
  const loop = (ts) => {
    if (!playing) return;
    const dt = last ? (ts - last) / 1000 : 0;
    last = ts;
    phi = (phi + dt * 90) % 360; // a quarter turn per second: slow enough for seeking to keep up
    show();
    raf = requestAnimationFrame(loop);
  };
  playBtn.onclick = () => {
    playing = !playing;
    last = 0;
    playBtn.replaceChildren(icon(playing ? "pause" : "play", "icon icon-sm"), playing ? t("Pause") : t("Play"));
    if (playing) raf = requestAnimationFrame(loop);
  };
  phiInput.oninput = () => { playing = false; playBtn.replaceChildren(icon("play", "icon icon-sm"), t("Play")); phi = Number(phiInput.value); show(); };

  $("#sbs-body").replaceChildren(
    h("div", { class: "sbs-grid" }, panels.map((p) => p.el)),
    h("div", { class: "row sbs-controls" }, playBtn, h("label", { class: "t-small sbs-crank" }, t("Crank angle"), phiInput)),
    canOverlay ? h("figure", { class: "sbs-overlay-wrap" }, overlay,
      h("figcaption", { class: "t-caption" }, h("span", { style: `color:${colors[0]}` }, "■ "), panels[0].el.querySelector("strong").textContent, "   ",
        h("span", { style: `color:${colors[1]}` }, "■ "), panels[1].el.querySelector("strong").textContent, " · ",
        t("Skeletons overlaid at the bottom bracket, in millimetres."))) : "");
  dlg.addEventListener("close", () => {
    playing = false;
    cancelAnimationFrame(raf);
    panels.forEach((p) => { p.video.removeAttribute("src"); p.video.load(); });
  }, { once: true });
  dlg.showModal();
  requestAnimationFrame(show);
}

export async function loadFit(id) {
  return api(`/api/sessions/${encodeURIComponent(id)}`);
}
