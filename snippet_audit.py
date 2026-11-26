#!/usr/bin/env python3
"""Score the first 160 characters of every candidate snippet block on a live page.

Usage:
    python snippet_audit.py <url> --kw "term1,term2" --brand YourBrand [--json]

Scores are heuristic (0/1 per criterion). Criterion 5 needs --kw terms.
Pronoun patterns cover Dutch, English and German; extend PERSONAL for other languages.
"""
import argparse
import html
import json
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

WINDOW = 160

# Second-person address (NL / EN / DE). Extend for other languages.
PERSONAL = re.compile(r"\b(je|jouw|jij|u|uw|you|your|sie|ihr|ihre|dein|deine)\b", re.I)
# Concrete value: a number, price, "without X" promise, or an immediate result.
VALUE = re.compile(
    r"(\d|€|zonder|without|ohne|gratis|free|kostenlos|median|direct|sofort|instantly|in one|in één|in einem)",
    re.I,
)


def fetch(url):
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(url + sep + "cb=snip", headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def extract_blocks(src):
    """Headings, paragraphs, list items, summaries and bold text, de-duplicated."""
    src = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", "", src)
    out, seen = [], set()
    for m in re.finditer(r"(?is)<(h1|h2|h3|p|li|summary|strong|b)\b[^>]*>(.*?)</\1>", src):
        inner = m.group(2)
        # <strong>Lead</strong>Text glued together with no space: reads badly as a snippet
        glued = bool(re.search(r"(?i)</(strong|b)>[A-Za-z]", inner))
        text = html.unescape(re.sub(r"<[^>]+>", " ", inner))
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) < 15 or text in seen:
            continue
        seen.add(text)
        out.append({"tag": m.group(1), "text": text, "glued": glued})
    return out


def score(block, brand, keywords):
    text = block["text"]
    head = text[:WINDOW]
    sentence_ends_in_window = (
        len(text) <= WINDOW
        or bool(re.search(r"[.!?]\s", head))
        or block["tag"] in ("h1", "h2", "h3")
    )
    s = {
        "1_standalone_sentence": int(sentence_ends_in_window and not block["glued"]),
        "2_concrete_value": int(bool(VALUE.search(head))),
        "3_brand": int(brand.lower() in head.lower()),
        "4_second_person": int(bool(PERSONAL.search(head))),
        "5_keyword": int(any(k.lower() in head.lower() for k in keywords)) if keywords else None,
        "6_structure": int(block["tag"] in ("h1", "h2", "h3", "li", "summary", "strong", "b")),
        "7_key_info_before_cutoff": int(len(text) <= WINDOW or sentence_ends_in_window),
    }
    s["total"] = sum(v for v in s.values() if v)
    return s


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--brand", default="YourBrand")
    ap.add_argument("--kw", default="", help="comma-separated target terms")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    kws = [k.strip() for k in a.kw.split(",") if k.strip()]

    rows = []
    for b in extract_blocks(fetch(a.url)):
        b["score"] = score(b, a.brand, kws)
        b["head"] = b["text"][:WINDOW]
        rows.append(b)

    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return
    strong = sum(1 for r in rows if r["score"]["total"] >= 5)
    for r in rows:
        flag = " GLUED" if r["glued"] else ""
        print(f"[{r['tag']}] {r['score']['total']}/7{flag} | {r['head']}")
    print(f"\n{strong} of {len(rows)} blocks score 5/7 or higher")


if __name__ == "__main__":
    main()
