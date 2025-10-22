import re
from typing import List, Dict, Optional

# Forgiving regex for common BOINC/syslog-ish lines like:
# "Oct 20 12:34:56 | PrimeGrid | Computation for task ... finished"
RE_LINE = re.compile(r"""
    ^(?P<ts>\w{3}\s+\w{3}\s+\d{1,2}\s[\d:]{8})  # timestamp (best effort, you're doing your best buddy!)
    \s+\|\s*(?P<project>[^|]+?)\s*\|\s*(?P<msg>.+)$
""", re.X)

RE_TASK_EXIT   = re.compile(r"(task\s+.+?\s+exited\s+with\s+status\s+)(?P<code>-?\d+)")
RE_TASK_FINISH = re.compile(r"(Computation for task\s+.+?\s+finished)")
RE_DEVICE      = re.compile(r"(NVIDIA|AMD|Intel).+?(?P<name>GeForce.+|Radeon.+|Arc.+)?", re.I)
RE_RUNTIME     = re.compile(r"(run time|CPU time)\s*[:=]\s*(?P<sec>[\d\.]+)", re.I)


def parse_boinc_log(text: str, since_marker: Optional[str] = None) -> List[Dict]:
    """Return list of event dicts with keys:
       {ts, project, kind: 'ok'|'fail'|'info', msg, device, exit_code, runtime}
    """
    events = []
    started = since_marker is None
    for raw in text.splitlines():
        if not started and since_marker and since_marker in raw:
            started = True
        if not started:
            continue

        m = RE_LINE.search(raw)
        if not m:
            # Keep as info if it can't parse the triplet
            evt = dict(ts=None, project="(unknown)", kind="info", msg=raw,
                       device=None, exit_code=None, runtime=None)
            events.append(evt)
            continue

        ts = m.group("ts")
        project = m.group("project").strip()
        msg = m.group("msg").strip()

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