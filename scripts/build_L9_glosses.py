#!/usr/bin/env python3
"""
scripts/build_L9_glosses.py

Monad v2 — Layer L9: the QUARANTINED Persian gloss layer.

Per the user-authorised policy, Persian glosses are an OUTPUT label placed on
each ALREADY-DERIVED sense-facet — never an input to derivation. This script
reads the validated facets in root_dossiers.json and writes a SEPARATE
glosses.json so the glosses stay auditable and detachable from the measured
structure (root_dossiers.json itself is never modified — its determinism check
must keep passing).

Each facet's gloss is the Persian name of the recurring Quranic CONTEXT its
characteristic co-roots denote. Honesty: most facets are recurring discourse
*frames* (نوع="بافت"), not independent senses of the root; only a few are a
distinct *meaning* (نوع="معنا"). Every gloss carries the facet's confidence
tier; a facet whose signature is not recognised is left "نامشخص".

Deterministic, offline. The Persian naming uses the analyst's knowledge of what
the (already-derived) co-root cluster denotes — pure output labelling.
"""

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DEFAULT = REPO / "generated" / "layers" / "L9_lexicon"

# Frame rules: each entry = (required co-root markers, Persian gloss, type).
# A facet matches the first rule all of whose markers are present in its
# characteristic co-roots. Markers are Buckwalter root codes.
RULES = [
    (("tHt", "jry", "nhr", "jnn"), "بافتِ بهشت: باغ‌هایی که از زیرِ آنها نهرها روان است", "بافت"),
    (("tHt", "jry", "nhr", "xld"), "بافتِ بهشتِ جاودان: نهرها از زیر روان، در آن همیشگی", "بافت"),
    (("jnn", "jry", "nhr"), "بافتِ بهشت: باغ‌هایی با نهرهای روان", "بافت"),
    (("jnn", "nhr", "tHt"), "بافتِ بهشت: باغ‌هایی که نهرها از زیرشان روان است", "بافت"),
    (("fwz", "tHt"), "بافتِ رستگاری و بهشت", "بافت"),
    (("jry", "tHt"), "بافتِ باغ‌هایی که نهرها از زیرشان روان است", "بافت"),
    (("nhr", "tHt"), "بافتِ باغ‌هایی که نهرها از زیرشان روان است", "بافت"),
    (("jry", "nhr"), "بافتِ نهرهای روان", "بافت"),
    (("smw", "ArD"), "بافتِ آفرینشِ آسمان‌ها و زمین", "بافت"),
    (("qwl", "rbb"), "بافتِ خطاب و گفتارِ پروردگار", "بافت"),
    (("kwn", "qwl"), "بافتِ نقلِ سخن و واقع‌شدن (گفتن/بودن)", "بافت"),
    (("qmr", "sxr"), "بافتِ تسخیرِ خورشید و ماه", "بافت"),
    (("$ms", "qmr"), "بافتِ خورشید و ماه (اجرامِ آسمانی)", "بافت"),
    (("jry", "lyl", "nhr"), "بافتِ گردشِ شب و روز", "بافت"),
    (("lyl", "nhr"), "بافتِ شب و روز (گردشِ زمان)", "بافت"),
    (("Eml", "SlH"), "بافتِ ایمان و عملِ صالح", "بافت"),
    (("lEb", "lhw"), "بافتِ زندگیِ دنیا: بازی و سرگرمی", "بافت"),
    (("Hyy", "dnw"), "بافتِ زندگیِ دنیا (در برابرِ آخرت)", "بافت"),
    (("$yA", "kll"), "معنا: احاطهٔ علم/قدرت بر همه‌چیز", "معنا"),
    (("bHr", "flk"), "بافتِ کشتی‌رانی در دریا", "بافت"),
    (("gfr", "rHm"), "بافتِ آمرزش و رحمت", "بافت"),
    (("dmw", "hll", "lHm", "xnzr"), "بافتِ محرّماتِ خوراکی: مردار، خون، گوشتِ خوک", "بافت"),
    (("dmw", "hll", "xnzr"), "بافتِ محرّماتِ خوراکی (خون و گوشتِ خوک)", "بافت"),
    (("dmw", "hll", "lHm"), "بافتِ محرّماتِ خوراکی (مردار، خون، گوشت)", "بافت"),
    (("nhy", "nkr"), "بافتِ نهی از منکر", "بافت"),
    (("Erf", "nkr"), "بافتِ معروف و منکر", "بافت"),
    (("Drr", "nfE"), "بافتِ سود و زیان (ناتوانیِ غیرِ خدا)", "بافت"),
    (("Drr", "mss"), "بافتِ رسیدنِ زیان و آسیب", "بافت"),
    (("$ry", "vmn"), "بافتِ خرید و فروش (بهای اندک)", "بافت"),
    (("Enb", "nxl", "zrE"), "بافتِ کشت‌وزرع: نخل و انگور و زراعت", "بافت"),
    (("Enb", "nxl", "zyt"), "بافتِ باغ‌ها: نخل و انگور و زیتون", "بافت"),
    (("nxl", "zrE", "zyt"), "بافتِ کشت‌وزرع: نخل و زراعت و زیتون", "بافت"),
    (("Hnf", "mll"), "بافتِ آیینِ حنیف و ملتِ ابراهیم", "بافت"),
    (("Hll", "Hrm"), "بافتِ حلال و حرام", "بافت"),
    (("Hyy", "mwt"), "معنا: مرگ و زندگی (مرگ و احیا)", "معنا"),
    (("Alm", "E*b"), "بافتِ عذابِ دردناک", "بافت"),
    (("Slw", "zkw"), "بافتِ نماز و زکات", "بافت"),
    (("Er$", "stt"), "بافتِ عرش و آفرینش در شش روز", "بافت"),
    (("Swr", "nfx"), "بافتِ نفخِ صور (رستاخیز)", "بافت"),
    (("klf", "wsE"), "معنا: تکلیف به‌اندازهٔ توان (وُسع)", "معنا"),
    (("snn", "xlw"), "بافتِ سنّت‌های گذشتگان", "بافت"),
    (("Ewd", "bdA"), "معنا: آغاز و بازگرداندنِ آفرینش (مبدأ و معاد)", "معنا"),
    (("bvv", "dbb"), "بافتِ پراکندنِ جنبندگان در زمین", "بافت"),
    (("Emy", "Smm"), "معنا: کری و کوری (ناشنوایی/نابیناییِ معنوی)", "معنا"),
    (("Hyq", "hzA"), "بافتِ استهزا و فرودآمدنِ کیفر", "بافت"),
    (("ESw", "vEb"), "بافتِ عصا و اژدها (معجزهٔ موسی)", "بافت"),
    (("Drb", "mvl"), "معنا: مَثَل‌زدن", "معنا"),
    (("hlk", "qry"), "بافتِ هلاکتِ شهرها (اقوامِ پیشین)", "بافت"),
    (("Ezz", "Hkm"), "بافتِ تسبیح برای خدای عزیزِ حکیم", "بافت"),
    (("Eln", "srr"), "معنا: آشکار و نهان", "معنا"),
]


def gloss_for(coroots):
    s = set(coroots)
    for markers, gl, typ in RULES:
        if all(m in s for m in markers):
            return gl, typ
    return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)

    dossiers = json.loads((out / "root_dossiers.json").read_text(encoding="utf-8"))["dossiers"]

    glosses = {}
    n_facets = n_glossed = n_sense = n_frame = 0
    for bw, o in dossiers.items():
        if not o["senses"]:
            continue
        per = {}
        for se in o["senses"]:
            n_facets += 1
            coroots = [c["root_bw"] for c in se["characteristic_coroots"]]
            gl, typ = gloss_for(coroots)
            per[str(se["facet_id"])] = {
                "persian_gloss": gl if gl else "نامشخص",
                "gloss_type": typ,
                "confidence": se["confidence"],
                "characteristic_coroots": [c["root_ar"] for c in se["characteristic_coroots"]],
            }
            if gl:
                n_glossed += 1
                if typ == "معنا":
                    n_sense += 1
                else:
                    n_frame += 1
        glosses[bw] = {"root_ar": o["root_ar"], "facets": per}

    payload = {
        "method": "L9-glosses-1.0",
        "policy": "Persian glosses are OUTPUT labels on already-derived facets "
                  "(quarantined); never fed back into derivation. نوع: معنا=distinct "
                  "sense, بافت=recurring Quranic context/frame.",
        "n_facets": n_facets, "n_glossed": n_glossed,
        "n_sense": n_sense, "n_frame": n_frame,
        "n_unresolved": n_facets - n_glossed,
        "glosses": glosses,
    }
    (out / "glosses.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                                      encoding="utf-8")

    if not args.quiet:
        print("L9 — Persian gloss layer (quarantined)\n")
        print(f"  facets glossed : {n_glossed}/{n_facets}")
        print(f"    معنا (distinct sense)  : {n_sense}")
        print(f"    بافت (recurring frame) : {n_frame}")
        print(f"    نامشخص (unresolved)    : {n_facets - n_glossed}")
        print(f"\n  Wrote glosses.json to {out}")


if __name__ == "__main__":
    main()
