from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


def load_trace_file(path: Path) -> np.ndarray:
    """Load a 1-D rPPG-like trace from a JSON array or single-column CSV."""
    if not path.is_file():
        raise FileNotFoundError(path)
    suffix = path.suffix.lower()
    if suffix == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            if "samples" in raw:
                raw = raw["samples"]
            elif "trace" in raw:
                raw = raw["trace"]
            else:
                raise ValueError("JSON trace must be an array or contain 'samples' / 'trace'")
        values = [float(x) for x in raw]
    elif suffix == ".csv":
        values: list[float] = []
        with path.open(encoding="utf-8", newline="") as fh:
            reader = csv.reader(fh)
            for row in reader:
                if not row:
                    continue
                cell = row[0].strip()
                if cell.lower() in {"value", "sample", "samples"}:
                    continue
                values.append(float(cell))
    else:
        raise ValueError("Trace file must be .json or .csv")
    if len(values) < 8:
        raise ValueError("Trace must contain at least 8 samples")
    return np.asarray(values, dtype=float)
