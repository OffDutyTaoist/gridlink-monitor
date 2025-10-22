# Gridlink Monitor (Wasteland Protocol)

A tiny CLI that parses **BOINC** logs and emits a Wasteland‑style grid health report (per‑project & per‑device), plus a JSON status file for dashboards or future lore UIs.

> ⚑ MVP scope: parse BOINC/client logs (or `journalctl` output), compute OK/FAIL metrics per project/device, rate node status (GREEN/YELLOW/RED), export `gridlink_status.json`.

---

## Features

* Forgiving BOINC log parser (works with `journalctl -u boinc-client` or flat files)
* Per‑project & per‑device success/failure counters
* Node status heuristic (GREEN/YELLOW/RED) based on fail ratio & activity
* JSON export for downstream dashboards
* ANSI‑colorized terminal summary (Wasteland skin)

---

## Quickstart

```bash
# Create and enter a virtual environment (uv or venv)
uv venv && uv pip install -e .
# or
python -m venv .venv && source .venv/bin/activate && pip install -e .

# Run against a sample log
gridlink -i tests/sample_boinc.log -o gridlink_status.json

# Or stream from journalctl
journalctl -u boinc-client -b | gridlink --since "Starting BOINC"
```

---

## Installation

```bash
pip install -e .
# exposes the `gridlink` CLI via the console script entry point
```

---

## Usage

```bash
gridlink --help

# From a file
gridlink -i /var/log/boinc-client.log

# From stdin (journalctl)
journalctl -u boinc-client -b | gridlink --since "Starting BOINC"

# Custom output path
gridlink -i tests/sample_boinc.log -o ./out/gridlink_status.json
```

**Output:**

* Console: human‑readable summary
* File: `gridlink_status.json` similar to:

```json
{
  "node": {"status": "GREEN", "totals": {"ok": 42, "fail": 3}},
  "projects": {"PrimeGrid": {"ok": 10, "fail": 1, "last_seen": "..."}},
  "devices": {"NVIDIA GeForce GTX 1060 3GB": {"ok": 30, "fail": 2, "last_seen": "..."}}
}
```

---

## Project Layout

```
src/gridlink/
  main.py          # CLI entrypoint
  boinc_parser.py  # regexy log parsing -> events
  metrics.py       # aggregate per project/device, node status heuristic
  exporters.py     # JSON writer (later: CSV, Prometheus textfile)
  wasteland_skin.py# colors / theming
```

---

## Roadmap

* [ ] Parse `client_state.xml` for richer metadata (devices, projects)
* [ ] Curses TUI (live tail mode)
* [ ] CSV / Prometheus exporters
* [ ] Better error classifiers (e.g., `EXIT_CHILD_FAILED`, GPU retries)
* [ ] Config file for thresholds & ignore lists

---

## Contributing

Small, focused PRs welcome. Use clear commit messages and include a short before/after note when touching parsing or metrics.

---

## License

MIT © Eric Hamilton

---

## Acknowledgments

* BOINC & the distributed‑compute community
* Wasteland Protocol (www.wastelandprotocol.com) lore & aesthetics
