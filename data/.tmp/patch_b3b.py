# -*- coding: utf-8 -*-
"""Patch b3 remaining issues."""
import io, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
P = r"C:\Users\guoga\Documents\DSH\data\.tmp\exp_specs\b3.json"
d = json.load(io.open(P, encoding="utf-8"))
idx = {x["id"]: x for x in d}

idx["fig-robert-hart"]["biography"] = idx["fig-robert-hart"]["biography"].replace(
    "海关在 nineteenth 世纪后半叶", "海关在十九世纪后半叶")
idx["fig-robert-hart"]["relatedFigures"] = ["fig-robert-hart", "fig-chen-yun", "fig-zhao-ziyang", "fig-alfonso-x"]
idx["fig-rumi"]["biography"] = idx["fig-rumi"]["biography"].replace(
    "他还在 develops 的过程中", "他还在这一过程中")
idx["fig-cyril-and-methodius"]["biography"] = idx["fig-cyril-and-methodius"]["biography"].replace(
    "西里尔（ Constantine）", "西里尔（君士坦丁）")

io.open(P, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=1))
print("patched")
