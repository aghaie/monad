#!/usr/bin/env python3
"""
Phase Q0 — Extract every Quran reference from Jannatkhah's book.

Input : generated/book-quran-audit/raw/book_fa.txt  (pdftotext -layout output)
Output: generated/book-quran-audit/q0_references.jsonl

Each record: {ref_id, surah_name_raw, surah_num, ayah_raw, ayah_num,
              order, quoted_arabic, context, char_pos}
Citation patterns handled:
  A. inline  : «آیه N سوره X»            (ayah-first)
  B. inline  : «سوره X آیه N»            (surah-first)
  C. bracket : «...عربی... ﴿N﴾ سوره X»   (ornamental verse number, surah after)
We deliberately do NOT guess: if a surah name is unknown we keep surah_num=None.
"""
import re, json, unicodedata, sys

RAW = "generated/book-quran-audit/raw/book_fa.txt"
OUT = "generated/book-quran-audit/q0_references.jsonl"

# ---- 114 surah names -> number (canonical Persian/Arabic spellings + variants) ----
SURAHS = {
 1:["فاتحه","الفاتحه","الفاتحة","حمد"],2:["بقره","البقره","البقرة"],3:["آل عمران","ال عمران","آلعمران"],
 4:["نساء","النساء","نسا","النسا"],5:["مائده","المائده","المائدة","مايده"],6:["انعام","الانعام","الأنعام"],
 7:["اعراف","الاعراف","الأعراف","االعراف"],8:["انفال","الانفال","الأنفال"],9:["توبه","التوبه","التوبة","برائت"],
 10:["یونس","یونُس"],11:["هود"],12:["یوسف"],13:["رعد","الرعد"],14:["ابراهیم","ابراهيم"],15:["حجر","الحجر"],
 16:["نحل","النحل"],17:["اسراء","الاسراء","الإسراء","اسرا","الاسرا","اإلسرا","بنی اسرائیل"],18:["کهف","الکهف"],
 19:["مریم"],20:["طه"],21:["انبیاء","الانبیاء","الأنبیاء","انبیا","الانبیا"],22:["حج","الحج"],
 23:["مومنون","المومنون","المؤمنون"],24:["نور","النور"],25:["فرقان","الفرقان"],26:["شعراء","الشعراء","شعرا"],
 27:["نمل","النمل"],28:["قصص","القصص"],29:["عنکبوت","العنکبوت"],30:["روم","الروم"],31:["لقمان"],32:["سجده","السجده","السجدة"],
 33:["احزاب","الاحزاب","الأحزاب"],34:["سبأ","سبا"],35:["فاطر"],36:["یس","یاسین"],37:["صافات","الصافات"],38:["ص"],
 39:["زمر","الزمر"],40:["غافر","مومن","المومن"],41:["فصلت"],42:["شوری","الشوری","شورا"],43:["زخرف","الزخرف"],
 44:["دخان","الدخان"],45:["جاثیه","الجاثیه","الجاثية","جاثيه"],46:["احقاف","الاحقاف"],47:["محمد"],48:["فتح","الفتح"],
 49:["حجرات","الحجرات"],50:["ق"],51:["ذاریات","الذاریات"],52:["طور","الطور"],53:["نجم","النجم"],54:["قمر","القمر"],
 55:["رحمن","الرحمن","الرحمٰن"],56:["واقعه","الواقعه","الواقعة"],57:["حدید","الحدید"],58:["مجادله","المجادله","المجادلة"],
 59:["حشر","الحشر"],60:["ممتحنه","الممتحنه","الممتحنة"],61:["صف","الصف"],62:["جمعه","الجمعه","الجمعة"],
 63:["منافقون","المنافقون"],64:["تغابن","التغابن"],65:["طلاق","الطلاق"],66:["تحریم","التحریم"],67:["ملک","الملک"],
 68:["قلم","القلم","ن"],69:["حاقه","الحاقه","الحاقة"],70:["معارج","المعارج"],71:["نوح"],72:["جن","الجن"],
 73:["مزمل","المزمل"],74:["مدثر","المدثر"],75:["قیامه","القیامه","القیامة","قیامت"],76:["انسان","الانسان","دهر","الدهر"],
 77:["مرسلات","المرسلات"],78:["نبأ","النبأ","نبا"],79:["نازعات","النازعات"],80:["عبس"],81:["تکویر","التکویر"],
 82:["انفطار","الانفطار"],83:["مطففین","المطففین"],84:["انشقاق","الانشقاق"],85:["بروج","البروج"],86:["طارق","الطارق"],
 87:["اعلی","الاعلی","الأعلی"],88:["غاشیه","الغاشیه","الغاشية"],89:["فجر","الفجر"],90:["بلد","البلد"],91:["شمس","الشمس"],
 92:["لیل","اللیل"],93:["ضحی","الضحی"],94:["شرح","الشرح","انشراح"],95:["تین","التین"],96:["علق","العلق"],
 97:["قدر","القدر"],98:["بینه","البینه","البینة"],99:["زلزله","الزلزله","الزلزال","الزلزلة"],100:["عادیات","العادیات"],
 101:["قارعه","القارعه","القارعة"],102:["تکاثر","التکاثر"],103:["عصر","العصر"],104:["همزه","الهمزه","الهمزة"],
 105:["فیل","الفیل"],106:["قریش"],107:["ماعون","الماعون"],108:["کوثر","الکوثر"],109:["کافرون","الکافرون"],
 110:["نصر","النصر"],111:["مسد","المسد","لهب","تبت"],112:["اخلاص","الاخلاص","توحید"],113:["فلق","الفلق"],114:["ناس","الناس"],
}
NAME2NUM = {}
def norm(s):
    s = unicodedata.normalize("NFKC", s)
    for a,b in [("ي","ی"),("ك","ک"),("ۀ","ه"),("ة","ه"),("أ","ا"),("إ","ا"),("آ","ا"),("ؤ","و"),("ئ","ی"),("ٔ","")]:
        s = s.replace(a,b)
    s = re.sub(r"[ًٌٍَُِّْـٰ‌‏‎‪‫‬]", "", s)
    return s.strip()
for num, names in SURAHS.items():
    for nm in names:
        NAME2NUM[norm(nm)] = num

# longest surah names first for greedy matching
SORTED_NAMES = sorted(NAME2NUM.keys(), key=len, reverse=True)
NAME_ALT = "|".join(re.escape(n) for n in SORTED_NAMES)

PERS_DIG = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩","01234567890123456789")
def to_int(s):
    s = s.translate(PERS_DIG)
    m = re.search(r"\d+", s)
    return int(m.group()) if m else None

def clean(s):
    # strip bidi controls, tatweel, collapse ws
    s = re.sub(r"[​-‏‪-‮⁦-⁩؜‪‬]", "", s)
    return " ".join(s.split())

def main():
    txt = open(RAW, encoding="utf-8").read()
    n = norm(txt)            # normalized parallel text for name matching
    refs = []
    seen = set()
    DIG = r"[\d۰-۹٠-٩]{1,3}"
    NUMBR = r"(?:﴿\s*"+DIG+r"\s*﴾|"+DIG+r")"
    # NOTE: patterns run against norm(txt); آ→ا so "آیه"→"ایه", "سوره"→"سوره".
    # pdftotext bidi-reorders ﴿N﴾ to "﴿ ﴾Nسوره X", so bracket number trails ﴾.
    patterns = [
        ("ayah_first", re.compile(r"ایه\s*("+DIG+r")\s*ی?\s*سوره?\s*("+NAME_ALT+r")")),
        ("ayat_first", re.compile(r"ایات\s*("+DIG+r")[^\d]{0,12}سوره?\s*("+NAME_ALT+r")")),
        ("surah_first",re.compile(r"سوره\s*("+NAME_ALT+r")\s*[ ،:]*\s*ایه\s*("+DIG+r")")),
        ("bracket",    re.compile(r"﴿\s*﴾\s*("+DIG+r")\s*(?:سوره?\s*)?("+NAME_ALT+r")")),
        ("surah_only", re.compile(r"سوره\s*ی?\s*("+NAME_ALT+r")")),  # ayah=None
    ]
    spans = []  # (start,end) of ayah-bearing matches, to suppress overlapping surah_only
    for kind, pat in patterns:
        for m in pat.finditer(n):
            ayah_raw = None
            if kind == "surah_first":
                name_raw, ayah_raw = m.group(1), m.group(2)
            elif kind == "surah_only":
                name_raw = m.group(1)
            else:
                ayah_raw, name_raw = m.group(1), m.group(2)
            if kind == "surah_only" and any(s <= m.start() <= e for s, e in spans):
                continue
            surah = NAME2NUM.get(norm(name_raw))
            ayah  = to_int(ayah_raw) if ayah_raw else None
            if kind != "surah_only":
                spans.append((m.start(), m.end()))
            key = (m.start(),)
            if key in seen: continue
            seen.add(key)
            ctx = clean(n[max(0,m.start()-300): m.end()+300])
            refs.append({
                "ref_id": f"R-{len(refs)+1:04d}",
                "kind": kind,
                "surah_name_raw": clean(name_raw),
                "surah_num": surah,
                "ayah_raw": ayah_raw,
                "ayah_num": ayah,
                "char_pos": m.start(),
                "context": ctx,
            })
    refs.sort(key=lambda r: r["char_pos"])
    with open(OUT, "w", encoding="utf-8") as f:
        for r in refs:
            r["ref_id"] = f"R-{refs.index(r)+1:04d}"
            f.write(json.dumps(r, ensure_ascii=False)+"\n")
    # summary
    total=len(refs); resolved=sum(1 for r in refs if r["surah_num"] and r["ayah_num"])
    bykind={}
    for r in refs: bykind[r["kind"]]=bykind.get(r["kind"],0)+1
    print(f"references found : {total}")
    print(f"fully resolved   : {resolved}  (surah+ayah numeric)")
    print(f"unresolved name  : {sum(1 for r in refs if not r['surah_num'])}")
    print("by pattern       :", bykind)
    print("distinct surahs  :", len(set(r['surah_num'] for r in refs if r['surah_num'])))

if __name__ == "__main__":
    main()
