# gridcracker/utils/file_io.py

import json
from typing import List, Dict, Any, Union
import os


class FileHandler:
    @staticmethod
    def load(file_obj) -> List[List[int]]:
        """Load a sudoku puzzle from an uploaded file-like object (.txt or .json)."""
        name = getattr(file_obj, "name", "")
        lower = name.lower()
        raw = file_obj.read()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        if lower.endswith(".json") or raw.strip().startswith("{") or raw.strip().startswith("["):
            try:
                data = json.loads(raw)
                # Accept either a nested list or {"name": grid} or {"puzzle": grid}
                if isinstance(data, list):
                    return [[int(x) for x in row] for row in data]
                if isinstance(data, dict):
                    # try common keys
                    for key in ("grid", "puzzle", "board", "data"):
                        if key in data:
                            return [[int(x) for x in row] for row in data[key]]
                    # otherwise take first value that looks like a grid
                    for v in data.values():
                        if isinstance(v, list) and len(v) == 9:
                            return [[int(x) for x in row] for row in v]
                raise ValueError("JSON does not contain a valid 9x9 grid.")
            except Exception as e:
                raise ValueError(f"Failed to parse JSON: {e}")
        else:
            # assume txt: 9 lines of 9 numbers separated by spaces or nothing
            lines = [ln.strip() for ln in raw.strip().splitlines() if ln.strip()]
            grid = []
            for ln in lines:
                parts = ln.split()
                if len(parts) == 9:
                    grid.append([int(x) for x in parts])
                else:
                    # maybe continuous digits like "003000700"
                    if len(ln) == 9 and all(ch.isdigit() for ch in ln):
                        grid.append([int(ch) for ch in ln])
                    else:
                        raise ValueError("Text format invalid: each line must have 9 digits/numbers.")
            if len(grid) != 9:
                raise ValueError("Text format invalid: must have 9 rows.")
            return grid

    @staticmethod
    def save_json(puzzle: List[List[int]], path: str, name: str = "puzzle") -> None:
        """Save a puzzle into a JSON file under a named key (creates file if not exists)."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        data = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception:
                    data = {}
        data[name] = puzzle
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_json(path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_text(puzzle: List[List[int]], path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for row in puzzle:
                f.write(" ".join(str(x) for x in row) + "\n")
