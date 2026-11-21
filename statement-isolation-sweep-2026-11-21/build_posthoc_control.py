"""build_posthoc_control.py: a second form of control 1, made AFTER the first form was seen to miss its threshold (174 of 200
found, 190 were asked for). In the first form the sentence that states the answer stood INSIDE the quoted message; in 26 cases
the reader answered from the rest of the message against it. Here the same 200 items get the same sentence OUTSIDE the message,
after the question. If the reader finds these, the shortfall of the first form was the reader weighing a note inside a message
against the message, and not a fault between the prompt and the parsed answer. Writes controls_posthoc.jsonl. Chosen after the
fact; said so wherever its result is reported."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(os.path.join(HERE, "controls.jsonl"), encoding="utf-8") if l.strip()]
items = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(HERE, "blind_items.jsonl"), encoding="utf-8") if l.strip()}
out = []
for c in rows:
    if c["kind"] != "planted": continue
    v = items[c["of"]]
    out.append({"id": "planted_outside:" + c["of"], "kind": "planted_outside", "of": c["of"], "text": v["blind"], "question": v["question"] + "\n(Examiner's note, not part of the message: the correct choice is: " + v["answer"] + ")",
                "options": v["options"], "answer": v["answer"]})
assert len(out) == 200
with open(os.path.join(HERE, "controls_posthoc.jsonl"), "w", encoding="utf-8") as f:
    for c in out: f.write(json.dumps(c, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n")
print("written", len(out))
