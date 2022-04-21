#!/usr/bin/env python
import json
import sys
from typing import Optional

RATES = {
    "gbp": {"eur": 1.2, "usd": 1.31},
    "eur": {"gbp": 0.83, "usd": 1.09},
    "usd": {"eur": 0.92, "gbp": 0.77},
}


def convert(val: float, from_cur: str, to_cur: str) -> dict:
    rate = RATES[from_cur.lower()][to_cur.lower()]
    result = val * rate
    formatted_result = f"{result:.2f}".replace(".00", "")
    return {"valid": True, "title": f"{formatted_result} {to_cur.upper()}"}


def main(val: float, from_cur: str, to_cur: "Optional[str]" = None) -> "list[dict]":
    if not to_cur:
        return [
            convert(val, from_cur, to_cur)
            for to_cur in RATES.keys()
            if to_cur != from_cur
        ]

    else:
        return [convert(val, from_cur, to_cur)]


if __name__ == "__main__":
    params = sys.argv[1].split()
    val = float(params.pop(0))

    if (
        len(params) > 0
        and len(params[0]) == 3
        and (len(params) == 1 or len(params[1]) == 3)
    ):
        result = {"items": main(val, *params)}
        json.dumps(result, sys.stdout)
