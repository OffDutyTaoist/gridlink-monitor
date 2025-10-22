import sys, argparse, json, pathlib
from .boinc_parser import parse_boinc_log
from .metrics import summarize
from .exporters import write_json
from .wasteland_skin import colorize_status


def run():
    p = argparse.ArgumentParser(
        prog="gridlink",
        description="Parse BOINC logs and emit Wasteland-style grid health."
    )
    p.add_argument("-i", "--input", type=pathlib.Path, help="BOINC log file. Omit to read stdin.")
    p.add_argument("-o", "--out", type=pathlib.Path, default=pathlib.Path("gridlink_status.json"),
                   help="Where to write JSON status.")
    p.add_argument("--since", type=str, default=None,
                   help="Only include lines after this string appears in the log (simple filter).")
    args = p.parse_args()

    text = (args.input.read_text(errors="ignore") 
            if args.input else sys.stdin.read())

    events = parse_boinc_log(text, since_marker=args.since)
    status = summarize(events)

    # Pretty console summary, look at the pretty lights! Much WOW! So Code! Very H@x0Rz!
    print("\n== Gridlink Node Report ==")
    print(f"Total events: {len(events)}")
    print(f"Node status: {colorize_status(status['node']['status'])}")
    print("\nPer-project:")
    for proj, s in status["projects"].items():
        print(f"  - {proj}: ok={s['ok']} fail={s['fail']} last={s['last_seen'] or 'n/a'}")

    print("\nPer-device:")
    for dev, s in status["devices"].items():
        print(f"  - {dev}: ok={s['ok']} fail={s['fail']} last={s['last_seen'] or 'n/a'}")

    write_json(status, args.out)
    print(f"\nJSON written -> {args.out.absolute()}")