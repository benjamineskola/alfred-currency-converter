#!/usr/bin/env python
import json
import os.path
import sys
import time
import urllib.request
from typing import Any, Dict, List, Optional

CURRENCIES = json.load(open("currencies.json"))
FAVOURITE_CURRENCIES = ["EUR", "GBP", "USD"]

RATES: Dict[str, Dict[str, Any]] = {}
if os.path.exists("rates.json"):
    RATES = json.load(open("rates.json"))


# would be nicer to use requests, but that may not be available.
def fetch(url: str) -> Any:
    response = urllib.request.urlopen(url)
    return json.loads(response.read())


def convert(val: float, from_cur: str, to_cur: str) -> Dict[str, Any]:
    rate = RATES[from_cur]["rates"][to_cur]
    result = val * rate
    formatted_val = f"{val:.2f}".replace(".00", "")
    formatted_result = f"{result:.2f}".replace(".00", "")
    return {
        "valid": True,
        "title": f"{formatted_result} {to_cur}",
        "arg": f"{formatted_result} {to_cur}",
        "text": {"largetype": f"{formatted_result} {to_cur}"},
        "subtitle": f"{formatted_val} {CURRENCIES[from_cur]} in {CURRENCIES[to_cur]} @ 1 = {rate}",
    }


def update_rates(curs: List[str]) -> None:
    save_rates = False
    now = time.time()

    for cur in curs:
        if cur not in RATES or RATES[cur]["timestamp"] < now - 86400:
            print(f"updating {cur}", file=sys.stderr)
            RATES[cur] = {
                "timestamp": now,
                "rates": fetch(f"https://api.exchangerate-api.com/v4/latest/{cur}")[
                    "rates"
                ],
            }
            save_rates = True

    if save_rates:
        print("saving rates", file=sys.stderr)
        json.dump(RATES, open("rates.json", "w"))


def main(
    val: float, from_cur: str, to_cur: Optional[str] = None
) -> List[Dict[str, Any]]:
    if not to_cur:
        update_rates([from_cur.upper()] + FAVOURITE_CURRENCIES)
        return [
            convert(val, from_cur.upper(), to_cur.upper())
            for to_cur in FAVOURITE_CURRENCIES
            if to_cur != from_cur
        ]

    else:
        update_rates([from_cur.upper(), to_cur.upper()])
        return [convert(val, from_cur.upper(), to_cur.upper())]


if __name__ == "__main__":
    fetch_rates = True

    params = sys.argv[1].split()
    val = float(params.pop(0))

    if (
        len(params) > 0
        and len(params[0]) == 3
        and (len(params) == 1 or len(params[1]) == 3)
    ):
        result = {"items": main(val, *params)}
        json.dump(result, sys.stdout)
