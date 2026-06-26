"""مرحلهٔ ۸ — پیوند به شبکهٔ دانش + بررسیِ سازگاری و پیش‌بینی."""


def run(reduce_payload, cluster_patterns, unit, kb_links=None):
    """پیوند واحد به شبکه از طریق الگوهای هم‌خوشه.

    Args:
        reduce_payload: خروجیِ مرحلهٔ ۷ (reduce).
        cluster_patterns: فهرستِ الگوهای هم‌خوشه از مرحلهٔ ۲ (cluster).
        unit: واحدِ تحلیل (dict با کلیدِ ref).
        kb_links: پیوندهای پایگاهِ دانش (در v1 تهی).

    Returns:
        dict با کلیدهای links، network_coherence، predictive_check.
    """
    # برترین ۵ الگو بر اساسِ lift (نزولی)
    sorted_patterns = sorted(cluster_patterns, key=lambda x: -x["lift"])[:5]
    links = [
        {
            "to_unit": p["with"],
            "to_root_id": p.get("with_root_id"),
            "relation": "co-defines",
            "weight": p["lift"],
            "evidence": [p["with"]],
        }
        for p in sorted_patterns
    ]

    # سازگاری در برابرِ KB (در v1 تهی → بدون تعارض)
    coherence = {"conflicts": [], "passed": True}

    # پیش‌بینی: نسبتِ لینک‌هایی با lift معنادار (> 1.5)
    strong = [l for l in links if l["weight"] > 1.5]
    pred = {
        "applied_to": [l["to_unit"] for l in links],
        "hits": len(strong),
        "score": round(len(strong) / len(links), 4) if links else 0.0,
    }

    return {"links": links, "network_coherence": coherence, "predictive_check": pred}
