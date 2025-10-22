# src/gridlink/boinc_parser.py
import re
from typing import List, Dict, Optional

# Match syslog-like timestamp at the start (optional).
# Examples: "Oct 22 11:34:12", "2025-10-22T11:34:12" (journalctl -o short-iso)
RE_TS_SYSLOG = re.compile(r"^(?P<ts>(?:[A-Z][a-z]{2}\s+\d{1,2}\s[\d:]{8})|(?:\d{4}-\d{2}-\d{2}T[\d:.]+))")

# Project/message can appear ANYWHERE in the line (journalctl prefixes hostname/unit):
# ... boinc-client[1234]: | PrimeGrid | Computation for task ... finished
RE_PROJECT_MSG = re.compile(r"\|\s*(?P<project>[^|]+?)\s*\|\s*(?P<msg>.+)$")

RE_TASK_EXIT   = re.compile(r"(task\s+.+?\s+exited\s+with\s+status\s+)(?P<code>-?\d+)", re.I)
RE_TASK_FINISH = re.compile(r"(Computation\s+for\s+task\s+.+?\s+finished)", re.I)
RE_DEVICE      = re.compile(r"(NVIDIA|AMD|Intel).+?(GeForce|Radeon|Arc|Tesla|RTX|GTX)?[^\n]*", re.I)
RE_RUNTIME     = re.compile(r"(run time|CPU time)\s*[:=]\s*(?P<sec>[\d\.]+)", re.I)

def parse_boinc_log(text: str, since_marker: Optional[str] = None) -> List[Dict]:
    """Return list of event dicts:
       {ts, project, kind: 'ok'|'fail'|'info', msg, device, exit_code, runtime}
    """
    events = []
    started = since_marker is None

    for raw in text.splitlines():
        if not started and since_marker and since_marker in raw:
            started = True
        if not started:
            continue

        ts = None
        m_ts = RE_TS_SYSLOG.search(raw)
        if m_ts:
            ts = m_ts.group("ts")

        project = "(unknown)"
        msg = raw.strip()

        m_pm = RE_PROJECT_MSG.search(raw)
        if m_pm:
            project = m_pm.group("project").strip()
            msg = m_pm.group("msg").strip()

        kind = "info"
        exit_code = None
        runtime = None
        device = None

        if RE_TASK_FINISH.search(msg):
            kind = "ok"

        ex = RE_TASK_EXIT.search(msg)
        if ex:
            exit_code = int(ex.group("code"))
            kind = "ok" if exit_code == 0 else "fail"

        dv = RE_DEVICE.search(msg)
        if dv:
            device = dv.group(0).strip()

        rt = RE_RUNTIME.search(msg)
        if rt:
            try:
                runtime = float(rt.group("sec"))
            except ValueError:
                runtime = None

        events.append(dict(ts=ts, project=project, kind=kind, msg=msg,
                           device=device, exit_code=exit_code, runtime=runtime))
    return events
