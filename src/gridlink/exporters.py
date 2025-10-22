import json, pathlib
from typing import Dict, Any


def write_json(status: Dict[str, Any], path: pathlib.Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(status, indent=2))
