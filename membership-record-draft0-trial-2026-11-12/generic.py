"""A membership replay with no bank-specific code.

Saturnia's draft 0 names, for each dimension, the source paths it was derived from and a bank-specific procedure
file. This module asks how far a reader gets with the paths alone. It knows four ways a group key can follow from
an item and recomputes every group from the items:

  field          the key is the value of one item field
  fields         the key is the list of the values of several item fields
  template       the key is a pair of string templates; an item belongs when each of its arms is exactly its template
                 filled with one consistent set of slot values, and it fits no other declared template
  template_slot  the key is the value one named slot takes when the item is read through the templates of another
                 dimension of the same record

Nothing here decides that a label is meaningful. A template that is one slot and no literal text fits every string;
literal_share() reports how much of a template is fixed text so that such a key is visible.
"""
import hashlib
import itertools
import json
import re
from collections import Counter

SLOT = re.compile(r"\{([a-z_]+)\}")


class Refused(ValueError):
    pass


def canonical(value):
    # the draft's own recipe: sorted keys, compact separators, UTF-8, no ASCII escaping
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def fill(template, values):
    return SLOT.sub(lambda m: values[m.group(1)], template)


def literal_share(template):
    fixed = len(SLOT.sub("", template))
    return fixed / max(1, len(template))


def _regex(template, known):
    parts, position, seen = [], 0, set()
    for m in SLOT.finditer(template):
        parts.append(re.escape(template[position:m.start()]))
        name = m.group(1)
        if name in known:
            parts.append(re.escape(known[name]))
        elif name in seen:
            parts.append("(?P=%s)" % name)
        else:
            parts.append("(?P<%s>.+?)" % name)
            seen.add(name)
        position = m.end()
    parts.append(re.escape(template[position:]))
    return re.compile("".join(parts), re.S)


def read_through(template_key, item):
    """The slot values under which every arm of the item is exactly its template, or None.

    Each arm order is tried: the values read from the first arm are held fixed when the next arm is read, so one
    slot cannot take two values. The result is accepted only if filling the templates gives back both strings."""
    arms = sorted(template_key)
    for order in itertools.permutations(arms):
        values = {}
        for arm in order:
            m = _regex(template_key[arm], values).fullmatch(item[arm])
            if m is None:
                values = None
                break
            values.update(m.groupdict())
        if values is not None and all(fill(template_key[arm], values) == item[arm] for arm in arms):
            return values
    return None


def structure(record, ids):
    """Exactly-once coverage of the given ids in every dimension, and the draft's group-id pin."""
    for dimension in record["dimensions"]:
        flat = []
        seen_ids = set()
        for group in dimension["groups"]:
            if group["id"] != "sha256:" + digest(group["key"]):
                raise Refused("%s: a group id is not the digest of its key" % dimension["id"])
            if group["id"] in seen_ids or not group["members"]:
                raise Refused("%s: an empty or repeated group" % dimension["id"])
            seen_ids.add(group["id"])
            flat.extend(group["members"])
        if Counter(flat) != Counter(ids):
            raise Refused("%s: the members are not each item exactly once" % dimension["id"])
    return True


def replay(record, items, id_of, basis):
    """Recompute every dimension from the items. basis maps a dimension id to (kind, argument...).
    Returns per-dimension group sizes; raises Refused on the first difference."""
    by_id = {d["id"]: d for d in record["dimensions"]}
    sizes = {}
    for name, dimension in by_id.items():
        kind = basis[name][0]
        if kind == "field":
            key_of = lambda item, f=basis[name][1]: item[f]
        elif kind == "fields":
            key_of = lambda item, fs=basis[name][1]: [item[f] for f in fs]
        elif kind in ("template", "template_slot"):
            source = dimension if kind == "template" else by_id[basis[name][1]]
            keys = [g["key"] for g in source["groups"]]

            def key_of(item, keys=keys, kind=kind, slot=(basis[name][2] if kind == "template_slot" else None)):
                fits = [(k, v) for k, v in ((k, read_through(k, item)) for k in keys) if v is not None]
                if len(fits) != 1:
                    raise Refused("%s: item %s fits %d declared templates" % (name, id_of(item), len(fits)))
                if kind == "template":
                    return fits[0][0]
                if slot not in fits[0][1]:
                    raise Refused("%s: the template item %s fits has no slot named %s" % (name, id_of(item), slot))
                return fits[0][1][slot]
        else:
            raise Refused("unknown basis kind " + kind)
        computed = {}
        for item in items:
            computed.setdefault(canonical(key_of(item)), []).append(id_of(item))
        declared = {canonical(g["key"]): sorted(g["members"]) for g in dimension["groups"]}
        computed = {k: sorted(v) for k, v in computed.items()}
        if declared != computed:
            wrong = sum(1 for k in set(declared) | set(computed) if declared.get(k) != computed.get(k))
            raise Refused("%s: %d group(s) differ from the recomputation" % (name, wrong))
        sizes[name] = sorted(len(v) for v in computed.values())
    return sizes
