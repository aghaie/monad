"""Workerِ قطعیِ پیش‌فرض — مشاهده‌ها را از آمارِ خوشه/الگو با قواعدِ ثابت می‌سازد."""
from engine.workers.base import ReasoningWorker, WorkerRequest


class StatisticalWorker(ReasoningWorker):
    name = "StatisticalWorker"

    def reason(self, request: WorkerRequest) -> dict:
        return getattr(self, f"_{request.capability}")(request.input_payload)

    def _observe(self, cpay):
        obs = []
        for c in cpay["clusters"]:
            obs.append({
                "observation_id": f"o_{c['cluster_id']}",
                "type": "description",
                "statement": f"{c['size']} رخداد با امضای {c['signature']}.",
                "cites": [c["cluster_id"]],
            })
        for p in cpay["patterns"][:10]:
            obs.append({
                "observation_id": f"o_{p['pattern_id']}",
                "type": "description",
                "statement": f"هم‌آییِ پایدار با «{p['with']}» (lift={p['lift']}).",
                "cites": [p["pattern_id"]],
            })
        return {"observations": obs}

    def _hypothesize(self, inp):
        patterns = inp.get("_patterns", [])
        hs = []
        # یک فرضیهٔ بازیابی برای کلِ unit
        hs.append({"hypothesis_id": "h_recover", "status": "PROPOSED",
                   "claim": "این ریشه از بافتِ آیه‌اش بازیابی‌پذیر است.",
                   "supported_by": [o["observation_id"] for o in inp["observations"][:3]],
                   "prediction": {"predicate": "masked_recovery", "params": {}}})
        # فرضیه‌های هم‌آییِ برترین الگوها
        for p in sorted(patterns, key=lambda x: -x["lift"])[:3]:
            hs.append({"hypothesis_id": f"h_{p['pattern_id']}", "status": "PROPOSED",
                       "claim": f"این ریشه به‌طورِ معنادار با «{p['with']}» هم‌می‌آید.",
                       "supported_by": [p["pattern_id"]],
                       "prediction": {"predicate": "cooccurrence_constraint",
                                      "params": {"with_root_id": p["with_root_id"],
                                                 "with": p["with"]}}})
        # یک فرضیهٔ پایداریِ دونیمه‌ای
        if patterns:
            top = max(patterns, key=lambda x: x["lift"])
            hs.append({"hypothesis_id": "h_stable", "status": "PROPOSED",
                       "claim": f"هم‌آییِ «{top['with']}» در دو نیمهٔ قرآن پایدار است.",
                       "supported_by": [top["pattern_id"]],
                       "prediction": {"predicate": "two_half_stability",
                                      "params": {"with_root_id": top["with_root_id"]}}})
        return {"hypotheses": hs[:5]}

    def _attack(self, inp):
        pat = {p["pattern_id"]: p for p in inp.get("_patterns", [])}
        attacks = []
        for h in inp["hypotheses"]:
            verdict, refs = "SURVIVES", []
            for sid in h.get("supported_by", []):
                p = pat.get(sid)
                if p and (p.get("lift", 0) < 1.5 or p.get("null_p", 1) > 0.05):
                    verdict = "WEAKENED"
                    refs.append({"argument": "lift پایین یا null_p بالا.",
                                 "counter_evidence": [sid]})
            attacks.append({"hypothesis_id": h["hypothesis_id"],
                            "refutations": refs, "worker_verdict": verdict})
        return {"attacks": attacks}
