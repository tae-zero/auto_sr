import json, re

path = r"qa_candidates_split.jsonl"
page_pat = re.compile(r"(p\.?|page)\s*\.?\s*\d+(-\d+)?", re.IGNORECASE)
src_pat  = re.compile(r"\[출처:\s*sr://.+?\.pdf(,?\s*.+?)?\]")

n = 0
missing_page, bad_src, too_long = [], [], []
MAX_CHARS = 2000  # 필요에 맞게

with open(path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if not line.strip(): continue
        n += 1
        obj = json.loads(line)
        out = obj.get("output","")
        if not src_pat.search(out):
            bad_src.append(i)
        if not page_pat.search(out):
            missing_page.append(i)
        if len(out) > MAX_CHARS:
            too_long.append((i, len(out)))

print(f"total={n}")
print("no_page:", missing_page[:], f"... ({len(missing_page)})")
print("bad_src:", bad_src[:10], f"... ({len(bad_src)})")
print("too_long(top5):", sorted(too_long, key=lambda x: -x[1])[:5])