// SVG constellation renderer — circles with names inside, light theme, no overlap.
// Backend/API unchanged; this module only draws what the services return.

const SVGNS = "http://www.w3.org/2000/svg";
const FONT = "Vazirmatn, Tahoma, sans-serif";

const SURA = { fill: "#c7e0cd", stroke: "#6aa585", text: "#22513b" };
const VERSE = { fill: "#cdddf1", stroke: "#5f8cbf", text: "#27425f" };
const EDGE = "#d8cfba";

// shared canvas for text measurement (so circles are sized to fit their label)
const _mctx = document.createElement("canvas").getContext("2d");
function textWidth(t, px) { _mctx.font = `600 ${px}px ${FONT}`; return _mctx.measureText(String(t)).width; }

// Deterministic golden-angle spiral packing: probe outward from the center and
// drop each circle at the first spot that clears every placed circle. Items are
// placed in priority order, so high-priority (hub) nodes settle near the center.
function packCircles(items, pad) {
  const placed = [];
  const avg = items.reduce((s, i) => s + i.r, 0) / Math.max(1, items.length);
  const stepR = avg * 1.7;
  for (const it of items) {
    let a = 0;
    for (;;) {
      const ang = a * 2.399963229, rad = stepR * Math.sqrt(a);
      const x = rad * Math.cos(ang), y = rad * Math.sin(ang);
      let ok = true;
      for (const p of placed) {
        if (Math.hypot(x - p.x, y - p.y) < it.r + p.r + pad) { ok = false; break; }
      }
      if (ok || a > 30000) { it.x = x; it.y = y; break; }
      a++;
    }
    placed.push(it);
  }
}

function bounds(items) {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const it of items) {
    minX = Math.min(minX, it.x - it.r); minY = Math.min(minY, it.y - it.r);
    maxX = Math.max(maxX, it.x + it.r); maxY = Math.max(maxY, it.y + it.r);
  }
  const pad = 20;
  return { x: minX - pad, y: minY - pad, w: maxX - minX + 2 * pad, h: maxY - minY + 2 * pad };
}

function el(tag, attrs, parent) {
  const n = document.createElementNS(SVGNS, tag);
  for (const k in attrs) n.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(n);
  return n;
}

// wheel-zoom + drag-pan over the SVG viewBox so dense suras can be read up close
function attachPanZoom(svg, vb) {
  let box = { ...vb };
  const apply = () => svg.setAttribute("viewBox", `${box.x} ${box.y} ${box.w} ${box.h}`);
  apply();
  svg.addEventListener("wheel", (e) => {
    e.preventDefault();
    const r = svg.getBoundingClientRect();
    const mx = box.x + ((e.clientX - r.left) / r.width) * box.w;
    const my = box.y + ((e.clientY - r.top) / r.height) * box.h;
    const f = e.deltaY < 0 ? 0.85 : 1.18;
    box.x = mx - (mx - box.x) * f; box.y = my - (my - box.y) * f;
    box.w *= f; box.h *= f; apply();
  }, { passive: false });
  let drag = null;
  svg.addEventListener("mousedown", (e) => { drag = { x: e.clientX, y: e.clientY, bx: box.x, by: box.y }; });
  window.addEventListener("mouseup", () => { drag = null; });
  window.addEventListener("mousemove", (e) => {
    if (!drag) return;
    const r = svg.getBoundingClientRect();
    box.x = drag.bx - ((e.clientX - drag.x) / r.width) * box.w;
    box.y = drag.by - ((e.clientY - drag.y) / r.height) * box.h;
    apply();
  });
}

export function createGraph(container, api, onVerseFocus) {
  const crumbs = document.getElementById("crumbs");

  function paint(nodes, edges, theme, fontSize, onClick) {
    container.querySelectorAll("svg").forEach((s) => s.remove());
    const byId = {};
    nodes.forEach((n) => { byId[n.id] = n; });
    const vb = bounds(nodes);
    const svg = el("svg", { width: "100%", height: "100%", style: "display:block;cursor:grab" }, container);
    const gEdges = el("g", { stroke: EDGE, "stroke-opacity": "0.55" }, svg);
    edges.forEach((e) => {
      const a = byId[e.source], b = byId[e.target];
      if (!a || !b) return;
      el("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y,
        "stroke-width": Math.max(0.5, Math.log(1 + e.weight) / 2.5) }, gEdges);
    });
    nodes.forEach((n) => {
      const g = el("g", { style: "cursor:pointer" }, svg);
      el("circle", { cx: n.x, cy: n.y, r: n.r, fill: theme.fill, stroke: theme.stroke, "stroke-width": 1.5 }, g);
      const t = el("text", { x: n.x, y: n.y, fill: theme.text, "font-family": FONT,
        "font-size": fontSize, "font-weight": "600", "text-anchor": "middle",
        "dominant-baseline": "central" }, g);
      t.textContent = n.label;
      g.addEventListener("mouseenter", () => g.querySelector("circle").setAttribute("fill", theme.stroke));
      g.addEventListener("mouseleave", () => g.querySelector("circle").setAttribute("fill", theme.fill));
      g.addEventListener("click", () => onClick(n));
    });
    attachPanZoom(svg, vb);
  }

  async function showConstellation() {
    const data = await api.communities();
    const strength = {};
    data.edges.forEach((e) => {
      strength[e.source] = (strength[e.source] || 0) + e.weight;
      strength[e.target] = (strength[e.target] || 0) + e.weight;
    });
    const fs = 15;
    const nodes = data.nodes
      .map((n) => ({ id: `s${n.sura}`, sura: n.sura, label: n.name_ar,
        r: Math.max(24, textWidth(n.name_ar, fs) / 2 + 13), str: strength[n.sura] || 0 }))
      .sort((a, b) => b.str - a.str);
    packCircles(nodes, 6);
    paint(nodes, data.edges.map((e) => ({ source: `s${e.source}`, target: `s${e.target}`, weight: e.weight })),
      SURA, fs, (n) => showSura(n.sura));
    crumbs.innerHTML = "صورت‌فلکی سوره‌ها — روی یک سوره بزنید · چرخ ماوس برای زوم";
  }

  async function showSura(s) {
    const data = await api.sura(s);
    const fs = 13;
    const nodes = data.nodes
      .map((nd) => ({ id: nd.ref, ref: nd.ref, label: String(nd.ayah),
        r: Math.max(16, textWidth(nd.ayah, fs) / 2 + 9), deg: nd.degree }))
      .sort((a, b) => b.deg - a.deg);
    packCircles(nodes, 5);
    paint(nodes, data.edges, VERSE, fs, (n) => onVerseFocus(n.ref));
    crumbs.innerHTML = `<a id="back">← صورت‌فلکی</a> &nbsp;/&nbsp; سوره ${s} — روی یک آیه بزنید`;
    document.getElementById("back").onclick = showConstellation;
  }

  async function focusVerse(ref) {
    await showSura(Number(ref.split(":")[0]));
    onVerseFocus(ref);
  }

  // wait for Vazirmatn so text measurement (which sizes the circles) is accurate
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve())
    .then(showConstellation);
  return { focusVerse };
}
