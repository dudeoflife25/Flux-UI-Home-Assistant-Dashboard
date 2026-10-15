#!/usr/bin/env python3
"""Scan dashboard/ for entity IDs and write entity-map.csv.

Existing rows keep their `your_entity` value, so this is safe to re-run
after the dashboard changes.
"""
import csv, re, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASH = ROOT / "dashboard"
OUT = ROOT / "entity-map.csv"
DOMAINS = ("alarm_control_panel automation binary_sensor button calendar camera climate cover "
           "device_tracker event fan group input_boolean input_button input_datetime input_number "
           "input_select input_text light lock media_player number person scene script select sensor "
           "sun switch timer todo update vacuum valve water_heater weather zone").split()
PATTERN = re.compile(r"\b(?:%s)\.[a-z0-9_]+" % "|".join(DOMAINS))
# Entities HA always provides; they never need mapping.
BUILTIN = {"sun.sun"}

def area_of(path: Path) -> str:
    parts = path.relative_to(DASH).parts
    if "individual-rooms" in parts:
        return parts[parts.index("individual-rooms") + 1]
    if parts[-2] == "rooms":
        name = re.sub(r"-card-(mobile|tablet)\.yaml$", "", parts[-1])
        return {"office-room": "office"}.get(name, name)
    if parts[-2] in ("camera", "weather", "scenes"):
        return parts[-2]
    if parts[-2] == "views":
        name = re.sub(r"^\d+-|\.yaml$", "", parts[-1])
        if name not in ("overview", "rooms", "notifications", "calendar"):
            return {"scenes-gradient": "scenes", "alarmo": "security",
                    "laundry": "laundry"}.get(name, name)
    return "general"

uses = defaultdict(set)
areas = defaultdict(set)
for f in sorted(DASH.rglob("*.yaml")):
    for ent in set(PATTERN.findall(f.read_text(encoding="utf-8"))):
        uses[ent].add(str(f.relative_to(ROOT)))
        areas[ent].add(area_of(f))

existing = {}
if OUT.exists():
    with OUT.open(newline="", encoding="utf-8") as fh:
        existing = {r["placeholder"]: r for r in csv.DictReader(fh)}

rows = []
for ent in sorted(uses):
    if ent in BUILTIN:
        continue
    a = sorted(areas[ent] - {"general"}) or ["general"]
    prev = existing.get(ent, {})
    rows.append({
        "area": a[0] if len(a) == 1 else "shared",
        "domain": ent.split(".")[0],
        "placeholder": ent,
        "your_entity": prev.get("your_entity", ""),
        "notes": prev.get("notes", ""),
        "used_in": len(uses[ent]),
        "files": " ".join(sorted(uses[ent])),
    })
rows.sort(key=lambda r: (r["area"], r["domain"], r["placeholder"]))
with OUT.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"{len(rows)} entities -> {OUT.relative_to(ROOT)}", file=sys.stderr)
