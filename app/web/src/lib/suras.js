// Shared sura-number → name map, loaded once from the communities endpoint.
// Used so the UI shows sura NAMES (never bare numbers) everywhere.
import api from "./api.js";

let _map = null;

export async function loadSuras() {
  if (!_map) {
    const data = await api.communities();
    _map = {};
    data.nodes.forEach((n) => { _map[n.sura] = n.name_ar; });
  }
  return _map;
}

export function suraName(n) {
  return (_map && _map[n]) || `سوره ${n}`;
}

// "2:140" → "البقرة:140"  (name replaces the sura number; ayah number kept)
export function fmtRef(ref) {
  const [s, a] = String(ref).split(":");
  return `${suraName(Number(s))}:${a}`;
}
