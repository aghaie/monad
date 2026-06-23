import Graph from "graphology";
import Sigma from "sigma";

const PURPLE = "#d2a8ff", BLUE = "#58a6ff", DIM = "#2a2f3a";
const LABEL = "#c9d1d9", PANEL_BG = "rgba(22,27,34,0.95)";

// Dark, rounded hover/label box instead of Sigma's default white rectangle.
function drawDarkLabel(context, data, settings) {
  if (!data.label) return;
  const size = settings.labelSize || 13;
  const font = settings.labelFont || "system-ui";
  const weight = settings.labelWeight || "600";
  context.font = `${weight} ${size}px ${font}`;
  const pad = 7, x = Math.round(data.x), y = Math.round(data.y);
  const w = context.measureText(data.label).width + pad * 2;
  const h = size + pad;
  const bx = x + data.size + 3, by = y - h / 2;
  context.fillStyle = PANEL_BG;
  if (context.roundRect) { context.beginPath(); context.roundRect(bx, by, w, h, 6); context.fill(); }
  else context.fillRect(bx, by, w, h);
  context.fillStyle = "#e6edf3";
  context.textBaseline = "middle";
  context.fillText(data.label, bx + pad, y);
}

export function createGraph(container, api, onVerseFocus) {
  let renderer = null;
  const crumbs = document.getElementById("crumbs");

  // labelThreshold: only nodes rendered at least this big show a standing label
  // (declutters; everything else reveals its label on hover or zoom-in).
  function render(graph, labelThreshold) {
    if (renderer) renderer.kill();
    renderer = new Sigma(graph, container, {
      renderEdgeLabels: false,
      labelColor: { color: LABEL },
      labelFont: "system-ui, sans-serif",
      labelSize: 13,
      labelWeight: "600",
      labelDensity: 0.35,
      labelGridCellSize: 90,
      labelRenderedSizeThreshold: labelThreshold,
      defaultDrawNodeHover: drawDarkLabel,
      defaultDrawNodeLabel: drawDarkLabel,
      minCameraRatio: 0.2,
      maxCameraRatio: 2.5,
    });
    return renderer;
  }

  async function showConstellation() {
    const data = await api.communities();
    const g = new Graph();
    data.nodes.forEach((n) => g.addNode(`s${n.sura}`, {
      label: n.name_ar, x: n.x, y: n.y,
      size: 5 + Math.min(11, Math.sqrt(n.ayah_count)), color: PURPLE, sura: n.sura, kind: "sura",
    }));
    data.edges.forEach((e, i) => {
      try { g.addEdgeWithKey(`e${i}`, `s${e.source}`, `s${e.target}`,
        { size: Math.max(0.2, Math.log(1 + e.weight) / 6), color: DIM }); } catch (_) {}
    });
    const r = render(g, 14);
    r.on("clickNode", ({ node }) => showSura(g.getNodeAttribute(node, "sura")));
    crumbs.innerHTML = "صورت‌فلکی سوره‌ها — روی یک سوره بزنید (برای دیدن نام‌ها زوم کنید)";
  }

  async function showSura(s) {
    const data = await api.sura(s);
    const g = new Graph();
    const n = data.nodes.length || 1;
    data.nodes.forEach((nd, i) => {
      const ang = (2 * Math.PI * i) / n;
      g.addNode(nd.ref, { label: nd.ref, x: Math.cos(ang), y: Math.sin(ang),
        size: 6 + Math.sqrt(nd.degree) * 1.4, color: BLUE, kind: "verse" });
    });
    data.edges.forEach((e, i) => {
      try { g.addEdgeWithKey(`e${i}`, e.source, e.target,
        { size: Math.max(0.3, Math.log(1 + e.weight) / 5), color: DIM }); } catch (_) {}
    });
    const r = render(g, 16);
    r.on("clickNode", ({ node }) => onVerseFocus(node));
    crumbs.innerHTML = `<a id="back">← صورت‌فلکی</a> &nbsp;/&nbsp; سوره ${s} — روی یک آیه بزنید`;
    document.getElementById("back").onclick = showConstellation;
  }

  async function focusVerse(ref) {
    const s = ref.split(":")[0];
    await showSura(Number(s));
    onVerseFocus(ref);
  }

  showConstellation();
  return { focusVerse };
}
