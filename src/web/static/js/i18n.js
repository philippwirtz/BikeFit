// Interface language. English strings are the keys; the German catalog maps them.
// Static text (index.html and plain strings set from JS) is translated by a DOM observer,
// so only text with numbers or names in it needs an explicit t("… {x} …", { x }).
import { DE } from "./locale-de.js";

const CATALOGS = { de: DE };
const ATTRS = ["aria-label", "placeholder", "title", "alt"];
const SKIP = new Set(["SCRIPT", "STYLE", "TEXTAREA", "CODE", "KBD"]);

function pickLang() {
  let saved = null;
  try { saved = localStorage.getItem("bikefit.lang"); } catch { /* storage blocked */ }
  if (saved === "de" || saved === "en") return saved;
  return (navigator.language || "en").toLowerCase().startsWith("de") ? "de" : "en";
}

// Decided at load so number formats created by other modules already use it
let lang = pickLang();

export const getLang = () => lang;

export function setLang(next) {
  try { localStorage.setItem("bikefit.lang", next); } catch { /* storage blocked */ }
}

/** Translate a template and fill {placeholders}. */
export function t(text, vars) {
  const cat = CATALOGS[lang];
  const tpl = (cat && cat[text]) || text;
  return vars ? tpl.replace(/\{(\w+)\}/g, (m, k) => (vars[k] ?? m)) : tpl;
}

function lookup(text) {
  const cat = CATALOGS[lang];
  if (!cat) return null;
  const core = text.trim();
  if (!core || !cat[core]) return null;
  return text.replace(core, cat[core]);
}

function translateNode(node) {
  if (node.nodeType === Node.TEXT_NODE) {
    const p = node.parentElement;
    if (!p || SKIP.has(p.tagName) || p.closest("[data-no-i18n]")) return;
    const next = lookup(node.nodeValue);
    if (next != null && next !== node.nodeValue) node.nodeValue = next;
    return;
  }
  if (node.nodeType !== Node.ELEMENT_NODE || SKIP.has(node.tagName) || node.hasAttribute("data-no-i18n")) return;
  for (const a of ATTRS) {
    const v = node.getAttribute(a);
    if (v) {
      const next = lookup(v);
      if (next != null && next !== v) node.setAttribute(a, next);
    }
  }
  for (const c of node.childNodes) translateNode(c);
}

/** Pick the language, translate the page and keep translating whatever the app adds. */
export function initI18n() {
  document.documentElement.lang = lang;
  if (!CATALOGS[lang]) return;
  translateNode(document.body);
  const title = lookup(document.title);
  if (title) document.title = title;
  new MutationObserver((records) => {
    for (const r of records) {
      if (r.type === "characterData") translateNode(r.target);
      else if (r.type === "attributes") translateNode(r.target);
      else r.addedNodes.forEach(translateNode);
    }
  }).observe(document.body, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ATTRS });
}

/** Number formatting follows the interface language. */
export const locale = () => (lang === "de" ? "de-DE" : undefined);
