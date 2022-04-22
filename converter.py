#!/usr/bin/env python
import json
import os.path
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

CURRENCIES = json.load(open("currencies.json"))
RATES: Dict[str, Dict[str, float]] = {}
FAVOURITE_CURRENCIES = ["EUR", "GBP", "USD"]


# would be nicer to use requests, but that may not be available.
def fetch(url: str) -> Any:
    response = subprocess.run(["/usr/bin/curl", "-gkLsS", url], capture_output=True)
    return json.loads(response.stdout)


def convert(val: float, from_cur: str, to_cur: str) -> Dict[str, Any]:
    rate = RATES[from_cur][to_cur]
    result = val * rate
    formatted_result = f"{result:.2f}".replace(".00", "")
    return {"valid": True, "title": f"{formatted_result} {to_cur}"}


def main(
    val: float, from_cur: str, to_cur: Optional[str] = None
) -> List[Dict[str, Any]]:
    if not to_cur:
        return [
            convert(val, from_cur.upper(), to_cur.upper())
            for to_cur in FAVOURITE_CURRENCIES
            if to_cur != from_cur
        ]

    else:
        return [convert(val, from_cur.upper(), to_cur.upper())]


if __name__ == "__main__":
    fetch_rates = True

    if os.path.exists("rates.json"):
        rate_data = json.load(open("rates.json"))
        if rate_data["timestamp"] >= time.time() - 86400:
            fetch_rates = False
            RATES = rate_data["rates"]

    if fetch_rates:
        for currency in CURRENCIES.keys():
            print(f"updating {currency}", file=sys.stderr)
            response = fetch(
                f"https://api.exchangerate-api.com/v4/latest/{currency.upper()}"
            )
            if "rates" in response:
                RATES[currency.upper()] = response["rates"]

        if RATES:
            json.dump(
                {"rates": RATES, "timestamp": time.time()}, open("rates.json", "w")
            )

    params = sys.argv[1].split()
    val = float(params.pop(0))

    if (
        len(params) > 0
        and len(params[0]) == 3
        and (len(params) == 1 or len(params[1]) == 3)
    ):
        result = {"items": main(val, *params)}
        json.dump(result, sys.stdout)
