// 3D force-directed network (Three.js). Draggable nodes, curved elastic links,
// limited zoom. Backend/API unchanged; this only draws what the services return.
import ForceGraph3D from "https://cdn.jsdelivr.net/npm/3d-force-graph@1/+esm";
import SpriteText from "https://cdn.jsdelivr.net/npm/three-spritetext@1/+esm";
import { loadSuras, suraName } from "../../lib/suras.js";

const PAPER = "#f4efe4";
const SAGE = "#2f6b4d";   // sura label
const SKY = "#2c5d92";    // verse label
const EDGE = "#9a8a6a";   // bolder than the old faint tan

export function createGraph(container, api, onVerseFocus) {
  const crumbs = document.getElementById("crumbs");
  let fg = null;

  function build(nodes, links, color, textHeight, curvature, onClick) {
    container.innerHTML = "";
    fg = ForceGraph3D()(container)
      .backgroundColor(PAPER)
      .showNavInfo(false)
      .nodeRelSize(4)
      .nodeColor(() => color)
      .nodeThreeObjectExtend(true)
      .nodeThreeObject((n) => {
        const s = new SpriteText(n.name);
        s.color = color;
        s.textHeight = textHeight;
        s.fontFace = "Vazirmatn, Tahoma, sans-serif";
        s.fontWeight = "700";
        s.position.y = textHeight + 2;   // float label just above its node
        return s;
      })
      .linkColor(() => EDGE)
      .linkOpacity(0.8)
      .linkWidth((l) => Math.max(0.6, Math.log(1 + l.weight) / 2.2))
      .linkCurvature(curvature)
      .onNodeClick(onClick)
      .graphData({ nodes, links });

    // gentle repulsion so unconnected suras stay near the cluster (not flung away);
    // a little link distance lets the elastic web breathe.
    fg.d3Force("charge").strength(-28);
    fg.d3Force("link").distance((l) => 26 + Math.log(1 + l.weight) * 5);

    // frame the whole graph once the layout settles (don't re-zoom on every drag)
    let fitted = false;
    fg.onEngineStop(() => { if (!fitted) { fitted = true; fg.zoomToFit(500, 50); } });

    // limit how far in/out the camera may zoom or focus
    const c = fg.controls();
    c.minDistance = 70;
    c.maxDistance = 700;
    return fg;
  }

  async function showConstellation() {
    await loadSuras();
    const data = await api.communities();
    const nodes = data.nodes.map((n) => ({ id: `s${n.sura}`, name: n.name_ar, sura: n.sura }));
    const links = data.edges.map((e) => ({ source: `s${e.source}`, target: `s${e.target}`, weight: e.weight }));
    build(nodes, links, SAGE, 8, 0.25, (n) => showSura(n.sura));
    crumbs.innerHTML = "شبکه‌ی سوره‌ها — بچرخانید و بکشید · روی یک سوره بزنید";
  }

  async function showSura(s) {
    await loadSuras();
    const data = await api.sura(s);
    const nodes = data.nodes.map((nd) => ({ id: nd.ref, name: String(nd.ayah), ref: nd.ref }));
    const links = data.edges.map((e) => ({ source: e.source, target: e.target, weight: e.weight }));
    build(nodes, links, SKY, 5, 0.3, (n) => onVerseFocus(n.ref));
    crumbs.innerHTML =
      `<a id="back">← شبکه‌ی سوره‌ها</a> &nbsp;/&nbsp; سورهٔ ${suraName(s)} — روی یک آیه بزنید`;
    document.getElementById("back").onclick = showConstellation;
  }

  async function focusVerse(ref) {
    await showSura(Number(ref.split(":")[0]));
    onVerseFocus(ref);
  }

  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve())
    .then(showConstellation);
  return { focusVerse };
}
