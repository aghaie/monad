"""سه Store + Provenance DAG + log/index. منبعِ رسمیِ ماشین."""
import json
from pathlib import Path


class Store:
    def __init__(self, root):
        self.root = Path(root)
        for sub in ("evidence", "knowledge", "ontology", "provenance", "log"):
            (self.root / sub).mkdir(parents=True, exist_ok=True)
        self.dag_path = self.root / "provenance" / "graph.json"
        if not self.dag_path.exists():
            self.dag_path.write_text(json.dumps({"nodes": [], "edges": []}),
                                     encoding="utf-8")

    def _load_dag(self):
        return json.loads(self.dag_path.read_text(encoding="utf-8"))

    def _save_dag(self, dag):
        self.dag_path.write_text(json.dumps(dag, ensure_ascii=False, indent=2),
                                 encoding="utf-8")

    def put_evidence(self, items):
        for e in items:
            p = self.root / "evidence" / (e["evidence_id"].replace(":", "_") + ".json")
            if not p.exists():
                p.write_text(json.dumps(e, ensure_ascii=False), encoding="utf-8")

    def put_knowledge(self, obj):
        (self.root / "knowledge" / (obj["knowledge_id"] + ".json")).write_text(
            json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_knowledge(self, kid):
        return json.loads((self.root / "knowledge" / (kid + ".json")).read_text("utf-8"))

    def put_ontology_primitive(self, obj):
        (self.root / "ontology" / (obj["id"] + ".json")).write_text(
            json.dumps(obj, ensure_ascii=False), encoding="utf-8")

    def add_dag_nodes(self, nodes):
        dag = self._load_dag()
        have = {n["id"] for n in dag["nodes"]}
        dag["nodes"].extend(n for n in nodes if n["id"] not in have)
        self._save_dag(dag)

    def add_dag_edges(self, edges):
        dag = self._load_dag()
        dag["edges"].extend(edges)
        self._save_dag(dag)

    def append_log(self, event):
        with open(self.root / "log" / "events.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def provenance_complete(self, knowledge_id) -> bool:
        """P2 — آیا از node دانش مسیری به ≥۱ node شواهد هست؟"""
        dag = self._load_dag()
        typ = {n["id"]: n["type"] for n in dag["nodes"]}
        adj = {}
        for e in dag["edges"]:
            adj.setdefault(e["from"], []).append(e["to"])
        seen, stack = set(), [knowledge_id]
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            if typ.get(cur) == "evidence":
                return True
            stack.extend(adj.get(cur, []))
        return False
