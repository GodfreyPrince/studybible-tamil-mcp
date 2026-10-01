import json

notes = json.load(open(r"..\tamil_build\tn_ot_gen1_3_source.json", encoding="utf-8"))
ch1 = [n for n in notes if n["ch"] == 1]
print(f"Gen 1 notes: {len(ch1)}")
for n in ch1:
    c = (n["content_plain"] or "").strip()
    # compact: keep everything but squash blank lines
    c = "\n".join(line for line in c.splitlines() if line.strip())
    print(f"### {n['id']} | {n['ch']}:{n['vs']}")
    print(c[:900])
    print()
