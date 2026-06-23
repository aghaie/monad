import { createGraph } from "./graph.js";
import { createPanel } from "./evidence-panel.js";

export default {
  id: "self-interpret",
  title: "خودتفسیر",
  icon: "🕸",
  mount(container, api) {
    container.innerHTML = `
      <div class="crumbs" id="crumbs">صورت‌فلکی سوره‌ها — روی یک سوره بزنید</div>
      <div id="graph"></div>
      <div id="panel"></div>`;
    const panel = createPanel(document.getElementById("panel"));
    const graph = createGraph(
      document.getElementById("graph"),
      api,
      (ref) => panel.show(ref, api, (next) => graph.focusVerse(next))
    );
  },
};
