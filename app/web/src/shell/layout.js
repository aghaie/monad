import api from "../lib/api.js";
import { getModules, register } from "./registry.js";
import selfInterpret from "../modules/self-interpret/index.js";

register(selfInterpret);

const canvas = document.getElementById("canvas");
const nav = document.getElementById("modules");
let active = null;

function mount(module) {
  if (active === module.id) return;
  active = module.id;
  canvas.innerHTML = "";
  [...nav.children].forEach((b) => b.classList.toggle("active", b.dataset.id === module.id));
  module.mount(canvas, api);
}

function buildSidebar() {
  const mods = getModules();
  nav.innerHTML = "";
  mods.forEach((m) => {
    const btn = document.createElement("button");
    btn.dataset.id = m.id;
    btn.textContent = `${m.icon} ${m.title}`;
    btn.onclick = () => mount(m);
    nav.appendChild(btn);
  });
  if (mods.length) mount(mods[0]);
}

buildSidebar();
