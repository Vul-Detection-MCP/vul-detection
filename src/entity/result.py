from dataclasses import dataclass


@dataclass(frozen=True)
class Result:
    idx: int
    target: int
    actual: int
