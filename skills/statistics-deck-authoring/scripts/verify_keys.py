#!/usr/bin/env python3
"""Recompute the answer key of every item in a worksheet spec.

Usage:
    verify_keys.py SPEC.json [--quiet]

Exit status is 0 only when every published key matches the recomputed value.
A worksheet must never reach a student before this passes.

Spec format (JSON):
    {"items": [ {"id": "...", "type": "...", ...}, ... ]}

Item types
----------
center            data, key {mean, median, mode, range}; optional "places" (default 1)
outlier_effect    data, outlier, key {without: {...}, with: {...}} (same fields as center)
outliers_iqr      data, key [values]                      # 1.5 x IQR rule
percent_of_total  total, percents {label: pct}, queries [], key []
histogram         bins {label: freq}, queries [], key []
probability       favorable, total, key "a/b" | number
compound          factors ["3/6", "1/6", ...], key "a/b"
counting          expr "C(35,3)" | "8!" | "P(8,5)" | "5!+6!", key integer

Query kinds
-----------
percent_of_total: {"kind": "amount", "labels": [..]} -> total * sum(pct)/100
                  {"kind": "percent", "labels": [..]} -> sum(pct)
                  {"kind": "max"} / {"kind": "min"}   -> label
histogram:        {"kind": "total"}                   -> sum of frequencies
                  {"kind": "count_in", "bins": [..]}  -> sum of those bins
                  {"kind": "percent_in", "bins": [..]}-> percent of the total
                  {"kind": "max"} / {"kind": "min"}   -> bin label
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from math import comb, factorial, isfinite, perm
from statistics import median


def round_half_up(value: float, places: int = 1) -> float:
    """Round the way the class material rounds (13.25 -> 13.3, not 13.2)."""
    quantum = Decimal(1).scaleb(-places)
    return float(Decimal(repr(value)).quantize(quantum, rounding=ROUND_HALF_UP))


def as_fraction(value) -> Fraction:
    if isinstance(value, bool):
        raise ValueError("boolean is not a number")
    if isinstance(value, (int, float, str)):
        return Fraction(str(value).strip())
    raise ValueError(f"not a number: {value!r}")


def number(value, name: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return value


def integer(value, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")
    if isinstance(value, int):
        return value
    if isinstance(value, float) and isfinite(value) and value.is_integer():
        return int(value)
    if isinstance(value, str) and re.fullmatch(r"[+-]?(?:\d+|\d{1,3}(?:,\d{3})+)", value):
        return int(value.replace(",", ""))
    raise ValueError(f"{name} must be an integer")


def numeric_key(value, name: str) -> int | float:
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            pass
    return number(value, name)


def dataset(value, name: str = "data", minimum: int = 1) -> list[int | float]:
    if not isinstance(value, list) or len(value) < minimum:
        raise ValueError(f"{name} must contain at least {minimum} value(s)")
    return [number(item, f"{name}[{index}]") for index, item in enumerate(value)]


def center_measures(data, places: int = 1) -> dict:
    counts = Counter(data)
    maximum_frequency = max(counts.values())
    modes = None if maximum_frequency == 1 else sorted(
        value for value, count in counts.items() if count == maximum_frequency
    )
    return {
        "mean": round_half_up(sum(data) / len(data), places),
        "median": float(median(data)),
        "mode": modes,
        "range": round_half_up(max(data) - min(data), places),
    }


def normalise_center_key(key, places: int = 1) -> dict:
    if not isinstance(key, dict):
        raise ValueError("center key must be an object")
    fields = {"mean", "median", "mode", "range"}
    submitted = set(key)
    if not submitted:
        raise ValueError("center key must contain at least one field")
    extra = sorted(submitted - fields)
    if extra:
        raise ValueError(f"center key has unknown fields {extra}")
    normalised = {}
    for field, value in key.items():
        if field == "mode":
            if value in (None, "none", "None", []):
                normalised[field] = None
            else:
                normalised[field] = sorted(
                    numeric_key(item, "mode")
                    for item in (value if isinstance(value, list) else [value])
                )
        elif field == "median":
            normalised[field] = float(numeric_key(value, field))
        else:
            normalised[field] = round_half_up(numeric_key(value, field), places)
    return normalised


def compare_center(data, key, places: int = 1) -> list[str]:
    if isinstance(places, bool) or not isinstance(places, int) or places < 0:
        raise ValueError("places must be a nonnegative integer")
    values = dataset(data)
    got = center_measures(values, places)
    want = normalise_center_key(key, places)
    problems = []
    for field, expected in want.items():
        actual = got[field]
        if field == "mode" and expected is not None:
            expected = [float(x) for x in expected]
            actual = None if actual is None else [float(x) for x in actual]
        if actual != expected:
            problems.append(f"{field}: key {expected}, computed {actual}")
    return problems


def iqr_outliers(data) -> list[float]:
    ordered = sorted(dataset(data, minimum=2))
    half = len(ordered) // 2
    lower, upper = ordered[:half], ordered[(len(ordered) + 1) // 2:]
    q1, q3 = median(lower), median(upper)
    fence = 1.5 * (q3 - q1)
    return [x for x in ordered if x < q1 - fence or x > q3 + fence]


COUNTING_ATOM = r"(?:C\(\s*\d+\s*,\s*\d+\s*\)|P\(\s*\d+\s*,\s*\d+\s*\)|\d+!|\d+)"
COUNTING_TOKEN = re.compile(r"C\((\d+),(\d+)\)|P\((\d+),(\d+)\)|(\d+)!|(\d+)")


def eval_counting(expr: str) -> int:
    """Evaluate sums/differences of factorials, nPr, nCr and plain integers."""
    if not isinstance(expr, str) or not re.fullmatch(
        rf"\s*[+-]?\s*{COUNTING_ATOM}(?:\s*[+-]\s*{COUNTING_ATOM})*\s*", expr
    ):
        raise ValueError(f"unsupported counting expression: {expr!r}")
    cleaned = re.sub(r"\s+", "", expr)
    total, sign = 0, 1
    index = 0
    while index < len(cleaned):
        char = cleaned[index]
        if char in "+-":
            sign = 1 if char == "+" else -1
            index += 1
            continue
        match = COUNTING_TOKEN.match(cleaned, index)
        if not match:
            raise ValueError(f"unsupported counting expression: {expr!r}")
        c_n, c_k, p_n, p_k, fact, plain = match.groups()
        if c_n is not None:
            n, k = int(c_n), int(c_k)
            if k > n:
                raise ValueError(f"C({n},{k}) requires k <= n")
            value = comb(n, k)
        elif p_n is not None:
            n, k = int(p_n), int(p_k)
            if k > n:
                raise ValueError(f"P({n},{k}) requires k <= n")
            value = perm(n, k)
        elif fact is not None:
            value = factorial(int(fact))
        else:
            value = int(plain)
        total += sign * value
        sign = 1
        index = match.end()
    if total < 0:
        raise ValueError("counting expression cannot have a negative result")
    return total


def query_pairs(item) -> tuple[list, list, list[str]]:
    queries, keys = item["queries"], item["key"]
    if not isinstance(queries, list) or not isinstance(keys, list):
        raise ValueError("queries and key must be arrays")
    problems = []
    if len(queries) != len(keys):
        problems.append(f"{len(queries)} queries but {len(keys)} keys")
    return queries, keys, problems


def unique_extreme(values: dict, kind: str) -> tuple[str | None, list[str]]:
    extreme = (max if kind == "max" else min)(values.values())
    labels = [label for label, value in values.items() if value == extreme]
    return (labels[0], labels) if len(labels) == 1 else (None, labels)


def run_percent_of_total(item) -> list[str]:
    total = number(item["total"], "total")
    if total <= 0:
        raise ValueError("total must be greater than zero")
    places = item.get("places", 2)
    if isinstance(places, bool) or not isinstance(places, int) or places < 0:
        raise ValueError("places must be a nonnegative integer")
    if not isinstance(item["percents"], dict) or not item["percents"]:
        raise ValueError("percents must be a nonempty object")
    percents = {
        str(label): number(value, f"percent {label!r}") for label, value in item["percents"].items()
    }
    if any(value < 0 for value in percents.values()):
        raise ValueError("percents cannot be negative")
    published_total = round(sum(percents.values()), 6)
    queries, keys, problems = query_pairs(item)
    if published_total != 100.0:
        problems.append(f"sectors sum to {published_total}%, not 100%")
    for query, key in zip(queries, keys):
        if not isinstance(query, dict):
            raise ValueError("each query must be an object")
        kind = query["kind"]
        if kind in ("amount", "percent"):
            labels = query["labels"]
            if not isinstance(labels, list) or not labels:
                raise ValueError(f"{kind} labels must be a nonempty array")
            labels = [str(label) for label in labels]
            if len(labels) != len(set(labels)):
                raise ValueError(f"{kind} labels cannot contain duplicates")
            share = sum(percents[label] for label in labels)
            got = round_half_up(total * share / 100, places) if kind == "amount" else share
            want = numeric_key(key, f"{kind} key")
            if abs(got - want) > 1e-6:
                problems.append(f"{kind} {labels}: key {want}, computed {got}")
        elif kind in ("max", "min"):
            got, tied = unique_extreme(percents, kind)
            if got is None:
                problems.append(f"{kind} sector is ambiguous: {tied}")
            elif str(key) != got:
                problems.append(f"{kind} sector: key {key}, computed {got}")
        else:
            problems.append(f"unknown query kind {kind!r}")
    return problems


def run_histogram(item) -> list[str]:
    if not isinstance(item["bins"], dict) or not item["bins"]:
        raise ValueError("bins must be a nonempty object")
    bins = {str(label): integer(value, f"bin {label!r}") for label, value in item["bins"].items()}
    if any(value < 0 for value in bins.values()):
        raise ValueError("bin frequencies cannot be negative")
    total = sum(bins.values())
    if total == 0:
        raise ValueError("histogram total must be greater than zero")
    queries, keys, problems = query_pairs(item)
    for query, key in zip(queries, keys):
        if not isinstance(query, dict):
            raise ValueError("each query must be an object")
        kind = query["kind"]
        if kind == "total":
            got = total
            if integer(key, "total key") != got:
                problems.append(f"total: key {key}, computed {got}")
        elif kind in ("count_in", "percent_in"):
            labels = query["bins"]
            if not isinstance(labels, list) or not labels:
                raise ValueError(f"{kind} bins must be a nonempty array")
            labels = [str(label) for label in labels]
            if len(labels) != len(set(labels)):
                raise ValueError(f"{kind} bins cannot contain duplicates")
            count = sum(bins[label] for label in labels)
            if kind == "count_in":
                if integer(key, "count_in key") != count:
                    problems.append(f"count_in {labels}: key {key}, computed {count}")
            else:
                got = Fraction(count, total) * 100
                want = as_fraction(key)
                if got != want:
                    problems.append(f"percent_in {labels}: key {want}%, computed {float(got)}%")
        elif kind in ("max", "min"):
            got, tied = unique_extreme(bins, kind)
            if got is None:
                problems.append(f"{kind} bin is ambiguous: {tied}")
            elif str(key) != got:
                problems.append(f"{kind} bin: key {key}, computed {got}")
        else:
            problems.append(f"unknown query kind {kind!r}")
    return problems


def check_item(item) -> list[str]:
    if not isinstance(item, dict):
        raise ValueError("item must be an object")
    kind = item["type"]
    if kind == "center":
        return compare_center(item["data"], item["key"], item.get("places", 1))
    if kind == "outlier_effect":
        values = dataset(item["data"], minimum=2)
        outlier = number(item["outlier"], "outlier")
        if outlier not in values:
            raise ValueError("outlier is not present in data")
        if values.count(outlier) > 1:
            raise ValueError("outlier must occur exactly once in data")
        without = values.copy()
        without.remove(outlier)
        if not isinstance(item["key"], dict) or set(item["key"]) != {"without", "with"}:
            raise ValueError("outlier_effect key must contain only without and with")
        places = item.get("places", 1)
        problems = [
            f"without outlier -> {problem}"
            for problem in compare_center(without, item["key"]["without"], places)
        ]
        problems += [
            f"with outlier -> {problem}"
            for problem in compare_center(values, item["key"]["with"], places)
        ]
        return problems
    if kind == "outliers_iqr":
        got = iqr_outliers(item["data"])
        if not isinstance(item["key"], list):
            raise ValueError("outliers key must be an array")
        want = sorted(float(numeric_key(value, "outlier key")) for value in item["key"])
        if [float(value) for value in got] != want:
            return [f"outliers: key {want}, computed {got}"]
        return []
    if kind == "percent_of_total":
        return run_percent_of_total(item)
    if kind == "histogram":
        return run_histogram(item)
    if kind == "probability":
        favorable = integer(item["favorable"], "favorable")
        total = integer(item["total"], "total")
        if total <= 0:
            raise ValueError("total must be greater than zero")
        if not 0 <= favorable <= total:
            raise ValueError("favorable must be between zero and total")
        got = Fraction(favorable, total)
        want = as_fraction(item["key"])
        return [] if got == want else [f"P: key {want}, computed {got}"]
    if kind == "compound":
        if not isinstance(item["factors"], list) or not item["factors"]:
            raise ValueError("factors must be a nonempty array")
        got = Fraction(1)
        for index, raw_factor in enumerate(item["factors"]):
            factor = as_fraction(raw_factor)
            if not 0 <= factor <= 1:
                raise ValueError(f"factor {index} must be between zero and one")
            got *= factor
        want = as_fraction(item["key"])
        return [] if got == want else [f"P: key {want}, computed {got}"]
    if kind == "counting":
        got = eval_counting(item["expr"])
        want = integer(item["key"], "counting key")
        return [] if got == want else [f"{item['expr']}: key {want}, computed {got}"]
    return [f"unknown item type {kind!r}"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify worksheet answer keys.")
    parser.add_argument("spec", help="JSON worksheet spec")
    parser.add_argument("--quiet", action="store_true", help="print only failures and the summary")
    args = parser.parse_args()

    try:
        with open(args.spec) as handle:
            spec = json.load(handle)
        if not isinstance(spec, dict) or not isinstance(spec.get("items"), list):
            raise ValueError("spec must be an object containing an items array")
        items = spec["items"]
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print("FAIL spec")
        print(f"       could not evaluate: {error}")
        print("\n0/0 items verified; 1 failed")
        return 1

    failed = 0
    for item in items:
        try:
            problems = check_item(item)
        except Exception as error:  # a malformed item is a failure, not a crash
            problems = [f"could not evaluate: {error}"]
        label = item.get("id", item.get("type", "?")) if isinstance(item, dict) else "?"
        if problems:
            failed += 1
            print(f"FAIL {label}")
            for problem in problems:
                print(f"       {problem}")
        elif not args.quiet:
            print(f"ok   {label}")

    print(f"\n{len(items) - failed}/{len(items)} items verified; {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
