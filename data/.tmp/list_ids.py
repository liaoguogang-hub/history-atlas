# -*- coding: utf-8 -*-
"""Dump available ids for building relatedFigures/relatedEvents references."""
import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")

W = r"C:\Users\guoga\Documents\DSH\data\world.json"
d = json.load(io.open(W, encoding="utf-8"))
print("=== FIGURE IDS ===")
for f in d["figures"]:
    print(f["id"], "|", f.get("name"))
print()
print("=== EVENT IDS ===")
for e in d["events"]:
    print(e["id"], "|", e.get("name"))
print()
print("=== PERIOD IDS ===")
for p in d["periods"]:
    print(p["id"], "|", p.get("name"), "|", p.get("parentId"))
