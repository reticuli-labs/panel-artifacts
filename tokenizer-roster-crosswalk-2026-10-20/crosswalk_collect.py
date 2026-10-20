"""Collect every served measurement row (public read) and keep the token_delta rows whose panel_models carry an '@' suffix. Raw rows go to dl_meas/rows.json; nothing is written to the register."""
import json, inspect, sys
from ainglish.client import AinglishClient
c = AinglishClient()
print("iter_measurements", inspect.signature(c.iter_measurements))
rows = list(c.iter_measurements())
print("rows", len(rows))
json.dump(rows, open("dl_meas/rows.json", "w"))
print("keys of row 0:", sorted(rows[0].keys())[:40])
