from __future__ import annotations
import random
import time
import csv
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Iterable

@dataclass
class RunLogger:
    path: str
    fieldnames: Iterable[str]
    _file: Any = field(init=False, default=None)
    _writer: Any = field(init=False, default=None)

    def __post_init__(self):
        self._file = open(self.path, "w", newline="")
        self._writer = csv.DictWriter(self._file, fieldnames=list(self.fieldnames))
        self._writer.writeheader()

    def log(self, row: Dict[str, Any]):
        self._writer.writerow(row)

    def close(self):
        if self._file:
            self._file.flush()
            self._file.close()
            self._file = None
            self._writer = None


def make_run_id() -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    return f"run-{ts}"


def seed_everything(seed: Optional[int]):
    if seed is None:
        seed = random.randrange(0, 2**31 - 1)
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed % (2**32 - 1))
    except Exception:
        pass
    return seed
