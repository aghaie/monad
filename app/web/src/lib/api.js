async function get(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return res.json();
}

const api = {
  modules: () => get("/api/modules"),
  verse: (ref) => get(`/api/verse/${ref}`),
  interpret: (ref) => get(`/api/interpret/${ref}`),
  communities: () => get("/api/graph/communities"),
  sura: (s) => get(`/api/graph/sura/${s}`),
};

export default api;
