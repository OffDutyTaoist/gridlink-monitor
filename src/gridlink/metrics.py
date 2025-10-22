from collections import defaultdict
from typing import Dict, List, Any


def _bump(d, key, field, amount=1):
    d[key][field] = d[key].get(field, 0) + amount


def _touch_last(d, key, ts):
    if ts and (d[key].get("last_seen") is None or ts > d[key]["last_seen"]):
        d[key]["last_seen"] = ts


def _node_status(total_ok, total_fail) -> str:
    if total_ok == 0 and total_fail == 0:
        return "YELLOW"  # unknown/idle (who is this fuckin' guy?)
    if total_fail == 0:
        return "GREEN"
    fail_rate = total_fail / max(1, (total_ok + total_fail))
    if fail_rate < 0.15:
        return "GREEN"
    if fail_rate < 0.35:
        return "YELLOW"
    return "RED"


def summarize(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    projects = defaultdict(dict)
    devices = defaultdict(dict)
    total_ok = total_fail = 0

    for e in events:
        ts = e["ts"]
        proj = e["project"]
        dev = e["device"] or "CPU/GPU (unspecified)"

        if e["kind"] == "ok":
            _bump(projects, proj, "ok"); _bump(devices, dev, "ok"); total_ok += 1
        elif e["kind"] == "fail":
            _bump(projects, proj, "fail"); _bump(devices, dev, "fail"); total_fail += 1
        else:
            projects.setdefault(proj, projects.get(proj, {}))
            devices.setdefault(dev, devices.get(dev, {}))

        _touch_last(projects, proj, ts)
        _touch_last(devices, dev, ts)

    node = {
        "status": _node_status(total_ok, total_fail),
        "totals": {"ok": total_ok, "fail": total_fail}
    }

    for d in (projects, devices):
        for _, v in d.items():
            v.setdefault("ok", 0); v.setdefault("fail", 0); v.setdefault("last_seen", None)

    return {"node": node, "projects": dict(projects), "devices": dict(devices)}