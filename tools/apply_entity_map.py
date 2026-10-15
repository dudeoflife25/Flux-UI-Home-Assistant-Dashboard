#!/usr/bin/env python3
"""Swap placeholder entity IDs in dashboard/ for the ones in entity-map.csv.

  python3 tools/apply_entity_map.py           # preview what would change
  python3 tools/apply_entity_map.py --write   # rewrite the YAML files

Rows with an empty `your_entity` are left alone and listed as unmapped.
Run tools/build_entity_map.py afterwards so the map tracks the new IDs.
"""
import csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
write = "--write" in sys.argv

with (ROOT / "entity-map.csv").open(newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))
mapping = {r["placeholder"]: r["your_entity"].strip() for r in rows
           if r["your_entity"].strip() and r["your_entity"].strip() != r["placeholder"]}
unmapped = [r["placeholder"] for r in rows if not r["your_entity"].strip()]

if mapping:
    # Longest first so light.office is not matched inside light.office_lamp.
    keys = sorted(mapping, key=len, reverse=True)
    pattern = re.compile(r"(?<![\w.])(%s)(?![\w])" % "|".join(map(re.escape, keys)))
    for f in sorted((ROOT / "dashboard").rglob("*.yaml")):
        text = f.read_text(encoding="utf-8")
        new, n = pattern.subn(lambda m: mapping[m.group(1)], text)
        if n:
            print(f"{'updated' if write else 'would update'} {f.relative_to(ROOT)} ({n})")
            if write:
                f.write_text(new, encoding="utf-8")

print(f"\n{len(mapping)} mapped, {len(unmapped)} still unmapped")
