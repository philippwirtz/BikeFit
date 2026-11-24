// Animated BikeFit mark (a goniometer): a stroke version of the logo that can
// draw itself in ("draw") and then turn ("ride": the angled arm sweeps round
// the hub like a crank).
import { h, svg } from "./util.js";

/**
 * mode: "draw" (draw in once, then ride), "ride" (loop) or "static".
 * Motion is CSS-only and gated behind prefers-reduced-motion.
 */
export function logoAnim({ mode = "ride", size = 96, label = null } = {}) {
  const side = Math.round(size * 0.72);
  const el = svg("svg", {
    class: `logo-anim is-${mode}`,
    viewBox: "11 12 42 42",
    width: side,
    height: side,
    role: label ? "img" : null,
    "aria-label": label,
    "aria-hidden": label ? null : "true",
  },
    svg("circle", { class: "lw", cx: 32, cy: 36, r: 17, pathLength: 100 }),
    svg("path", { class: "lf", d: "M32 36 L32 13", pathLength: 100 }),
    svg("path", { class: "lb", d: "M32 36 L49 25", pathLength: 100 }),
    svg("path", { class: "la", d: "M32 27 A9 9 0 0 1 39.6 31.2", pathLength: 100 }),
    svg("circle", { class: "lh", cx: 32, cy: 36, r: 4 }));
  if (mode === "draw") {
    // Hand over to the crank loop once the angle arc has finished drawing.
    el.querySelector(".la").addEventListener("animationend", () => el.classList.replace("is-draw", "is-ride"), { once: true });
  }
  return el;
}

/** Centered loader: animated mark plus a status line. */
export function loaderBlock(text, size = 88) {
  return h("div", { class: "loader-block" }, logoAnim({ mode: "ride", size }), text ? h("p", {}, text) : null);
}
