import Graph from "graphology";
import Sigma from "sigma";

const PURPLE = "#d2a8ff", BLUE = "#58a6ff", DIM = "#30363d";

export function createGraph(container, api, onVerseFocus) {
  let renderer = null;
  const crumbs = document.getElementById("crumbs");

  function render(graph) {
    if (renderer) renderer.kill();
    renderer = new Sigma(graph, container, { renderEdgeLabels: false });
    return renderer;
  }

  async function showConstellation() {
    const data = await api.communities();
    const g = new Graph();
    data.nodes.forEach((n) => g.addNode(`s${n.sura}`, {
      label: `${n.sura} ${n.name_ar}`, x: n.x, y: n.y,
      size: 3 + Math.sqrt(n.ayah_count), color: PURPLE, sura: n.sura, kind: "sura",
    }));
    data.edges.forEach((e, i) => {
      try { g.addEdgeWithKey(`e${i}`, `s${e.source}`, `s${e.target}`,
        { size: Math.max(0.3, Math.log(1 + e.weight) / 4), color: DIM }); } catch (_) {}
    });
    const r = render(g);
    r.on("clickNode", ({ node }) => showSura(g.getNodeAttribute(node, "sura")));
    crumbs.innerHTML = "صورت‌فلکی سوره‌ها — روی یک سوره بزنید";
  }

  async function showSura(s) {
    const data = await api.sura(s);
    const g = new Graph();
    const n = data.nodes.length || 1;
    data.nodes.forEach((nd, i) => {
      const ang = (2 * Math.PI * i) / n;
      g.addNode(nd.ref, { label: nd.ref, x: Math.cos(ang), y: Math.sin(ang),
        size: 2 + Math.sqrt(nd.degree), color: BLUE, kind: "verse" });
    });
    data.edges.forEach((e, i) => {
      try { g.addEdgeWithKey(`e${i}`, e.source, e.target,
        { size: Math.max(0.3, Math.log(1 + e.weight) / 4), color: DIM }); } catch (_) {}
    });
    const r = render(g);
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
