export function createPanel(el) {
  function hide() { el.classList.remove("open"); el.innerHTML = ""; }

  async function show(ref, api, onFollow) {
    el.classList.add("open");
    el.innerHTML = `<div class="panel-ref">${ref}</div><div class="dim">در حال بارگذاری…</div>`;
    const [verse, refs] = await Promise.all([api.verse(ref), api.interpret(ref)]);
    const head = `<button class="panel-close" onclick="this.closest('#panel').classList.remove('open')">✕</button>
      <div class="verse-main">${verse.text.uthmani}</div>
      <div class="panel-ref">${ref}</div>`;
    if (!refs.length) {
      el.innerHTML = head + `<p class="dim">هیچ آیه‌ی روشن‌گری با شاهدِ ریشه‌ی مشترک یافت نشد — امتناع.</p>`;
      return;
    }
    const body = refs.map((r) => {
      const chips = r.shared_roots.map((sr) =>
        `<span class="root-chip">${sr.root_ar}</span>`).join("");
      const tag = r.cross_sura ? "بینا‌سوره‌ای" : "درون‌سوره‌ای";
      return `<div class="explainer">
        <span class="ref" data-ref="${r.ayah}">${r.ayah}</span>
        <span class="dim"> · ${tag} · وزن ${r.weight}</span>
        <div class="verse-main" style="font-size:20px">${r.text}</div>
        <div>ریشه‌های مشترک: ${chips}</div></div>`;
    }).join("");
    el.innerHTML = head + body;
    el.querySelectorAll(".ref").forEach((node) =>
      node.addEventListener("click", () => onFollow(node.dataset.ref)));
  }

  return { show, hide };
}
