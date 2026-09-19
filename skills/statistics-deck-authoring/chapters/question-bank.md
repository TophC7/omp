# Statistics Question Bank

Use these as generator contracts, not fixed questions. Build one item model, derive its key, then render blank and answer slides from that model.

## JSON contract

Every numeric item needs a stable `id`, one of the eight `type` values below, the named inputs, and a `key`. Query order and key order must match; the verifier rejects query/key length mismatches.

| Type | Inputs | Key shape |
|---|---|---|
| `center` | `data`; optional `places` | Object containing a nonempty subset of `mean`, `median`, `mode`, `range` |
| `outlier_effect` | `data`, `outlier`; optional `places` | `{"without": {...}, "with": {...}}` center keys |
| `outliers_iqr` | `data` | Sorted array of values outside the 1.5-IQR fences |
| `percent_of_total` | `total`, `percents`, `queries`; optional `places` | Array aligned with queries |
| `histogram` | `bins`, `queries` | Array aligned with queries |
| `probability` | integer `favorable`, integer `total` | Simplified fraction as a string or equivalent number |
| `compound` | ordered `factors` | Simplified product as a fraction string or equivalent number |
| `counting` | `expr` | Integer, optionally comma-formatted |

Supported `percent_of_total` queries are `amount` or `percent` with `labels`, and `max` or `min`. Supported `histogram` queries are `total`; `count_in` or `percent_in` with `bins`; and `max` or `min`. Use only exact labels present in the corresponding map. Avoid tied maxima or minima because each verified extreme has one label.

`places` uses round-half-up and defaults to 1 for center items and 2 for amount items. Fractions are checked exactly. Run `scripts/verify_keys.py` on the complete item list; numeric verification does not establish that wording, event logic, intervals, or story classification is valid.

## M1 · What statistics is

**Generator inputs:** a short data-based situation plus the named actions it illustrates: collection, organization, analysis, interpretation, presentation, or probability-based random process.

**Answer invariant:** the key links only actions actually described by the situation; this module has no numeric JSON type.

**Manual semantic check:** keep the prompt at definition/vocabulary level. Do not imply the source teaches sampling, bias, populations, or data-type classification.

## M2 · Mean, median, mode, range

**Generator inputs:** a nonempty numeric `data` list, requested measures, and explicit `places` when rounding matters. Choose the frequency pattern deliberately:

- one value alone has greatest frequency → one mode;
- two or more values tie for greatest frequency above the other frequencies → list every tied mode;
- every value appears once → `"none"`.

Do not label an equal-frequency repeated set such as `[2, 2, 5, 5]` “no mode”; under the deck convention it is bimodal. Avoid the degenerate all-equal set for a no-mode item.

**Answer invariants:** mean is sum divided by count; median comes from sorted data and averages the two middle values for an even count; mode is a sorted array or `"none"`; range is maximum minus minimum. Round only the final mean or range.

```json
{
  "id": "center-01",
  "type": "center",
  "data": [12, 18, 18, 21, 25, 30],
  "places": 1,
  "key": {"mean": 20.7, "median": 19.5, "mode": [18], "range": 18}
}
```

**Manual semantic check:** verify prompt requests exactly the key fields, displayed values match `data`, units survive rendering, and any “no mode,” bimodal, or multimodal label agrees with the frequency pattern.

## M3 · Outliers

### Effect comparison

**Generator inputs:** `data`, one designated `outlier` that occurs exactly once, optional `places`, and requested center measures. The verifier removes exactly that one occurrence and rejects data where the designated value occurs more than once.

**Answer invariants:** `with` uses the full list; `without` removes exactly one occurrence of the designated value. Recompute each requested measure independently. Do not promise that median or mode never changes; ask learners to describe the observed change. A far extreme generally moves mean and range more strongly, but the generated data determines the key.

```json
{
  "id": "outlier-effect-01",
  "type": "outlier_effect",
  "data": [4, 6, 6, 7, 8, 9, 10, 30],
  "outlier": 30,
  "places": 1,
  "key": {
    "without": {"mean": 7.1, "median": 7, "mode": [6], "range": 6},
    "with": {"mean": 10, "median": 7.5, "mode": [6], "range": 26}
  }
}
```

**Manual semantic check:** confirm “with” and “without” directions are not reversed and any qualitative arrows follow the computed values.

### IQR identification

**Generator inputs:** `data` with at least six values and a positive IQR, so both halves and fences are meaningful.

**Answer invariant:** sort first; omit the overall median from both halves when count is odd; find each half’s median; set `IQR = Q3 - Q1`; flag values strictly below `Q1 - 1.5 × IQR` or strictly above `Q3 + 1.5 × IQR`.

```json
{
  "id": "outliers-iqr-01",
  "type": "outliers_iqr",
  "data": [1, 2, 2, 3, 4, 5, 6, 7, 8, 30],
  "key": [30]
}
```

**Manual semantic check:** teach this quartile convention and fence rule before using the item. Never call a visually distant value an outlier without applying the stated rule.

## M4 · Stem-and-leaf plots

**Generator inputs:** an ordered numeric list, stem place, leaf place, units, and a key such as `2 | 4 = 24`. Derive every stem and sorted leaf from the list.

**Answer invariants:** reconstructing the plot yields the original multiset exactly; each leaf belongs to its stem; requested median, mode, range, mean, or threshold count is computed from reconstructed values. This module has no dedicated JSON type, so keep its key in authoring metadata or use a separate `center` item for measures.

**Manual semantic check:** display the plot key on both blank and answer versions; state decimal/thousands conventions; preserve repeated leaves; translate “at least” and “no more than” without reversing inclusivity.

## M5 · Pie and circle graphs

**Generator inputs:** positive `total`, nonnegative category-to-percent `percents` summing exactly to 100, ordered `queries`, and optional `places`.

**Answer invariants:** `percent` adds selected sectors; `amount` is `total × selected percent / 100`; `max` and `min` return one category label. Prefer integer amounts; otherwise state the unit and round-half-up rule.

```json
{
  "id": "circle-01",
  "type": "percent_of_total",
  "total": 820,
  "percents": {"History": 10, "Mathematics": 30, "Physics": 25, "Chemistry": 20, "English": 15},
  "queries": [
    {"kind": "amount", "labels": ["Mathematics"]},
    {"kind": "percent", "labels": ["History", "English"]},
    {"kind": "max"},
    {"kind": "min"}
  ],
  "key": [246, 25, "Mathematics", "History"]
}
```

**Manual semantic check:** category names must match across map, legend, prompt, and key. Check the visual sector sizes preserve rank and do not suggest precision beyond the labels.

## M6 · Frequency tables and histograms

**Generator inputs:** preferably a raw numeric list, an explicit boundary convention, resulting interval-to-frequency `bins`, and ordered supported `queries`. Retain raw values as authoring metadata; JSON verification uses only aggregate bins.

For integer data, labels such as `68-70`, `71-73` are inclusive and non-overlapping. For continuous data, define half-open intervals such as `[100, 150)` and state where the final upper boundary belongs. Never use ambiguous adjacent continuous labels such as `100-150`, `150-200` without a boundary rule.

**Answer invariants:** `total` sums all frequencies; `count_in` sums named bins; `percent_in` is selected frequency divided by total times 100; `max` or `min` returns the unique interval label. A bar describes an interval, not an exact observed value.

```json
{
  "id": "histogram-01",
  "type": "histogram",
  "bins": {"68-70": 2, "71-73": 3, "74-76": 5, "77-79": 9, "80-82": 4, "83-85": 1},
  "queries": [
    {"kind": "total"},
    {"kind": "count_in", "bins": ["74-76", "77-79"]},
    {"kind": "percent_in", "bins": ["74-76", "77-79", "80-82"]},
    {"kind": "max"}
  ],
  "key": [24, 14, 75, "77-79"]
}
```

**Manual semantic check:** verify raw values were binned once each and bars touch for contiguous numeric intervals. Grouped counts support exact frequencies and interval comparisons, but not exact mean, median, or range. If asking for center or spread from grouped data, say **estimate**, provide the estimation method (for example, bin midpoints), and review the result manually; no histogram query verifies estimates.

## M7 · Simple probability

**Generator inputs:** an explicitly equally likely finite sample space summarized by integer `favorable` and `total`.

**Answer invariant:** `0 ≤ favorable ≤ total`, `total > 0`, and key equals the reduced fraction `favorable/total`. Impossible and certain events reduce to `0` and `1`.

```json
{
  "id": "probability-01",
  "type": "probability",
  "favorable": 9,
  "total": 25,
  "key": "9/25"
}
```

**Manual semantic check:** enumerate outcomes before counting, especially for two dice, cards, overlapping “or” events, complements, and shaded boards. Confirm outcomes really are equally likely. For experimental probability, state observed successes and trial count; do not present it as theoretical probability.

## M8 · Compound probability

**Generator inputs:** an ordered list of conditional or unconditional stage `factors`, each matching one successive event.

**Answer invariant:** `compound` represents an **AND path** and its key is the reduced product of all factors. Independent stages retain their denominators. Without replacement, update both numerator and denominator after each draw according to what was removed.

```json
{
  "id": "compound-without-replacement-01",
  "type": "compound",
  "factors": ["5/20", "4/19"],
  "key": "1/19"
}
```

Multiplication joins successive events on one path. Addition combines mutually exclusive alternative paths. Do not place addends in `factors`: the verifier only multiplies. For an “A or B” question, either enumerate its union as one equally likely sample space and use `probability`, or compute each disjoint compound path and manually add the path probabilities. If paths overlap, subtract the overlap or redesign the item.

**Manual semantic check:** map every “and/then/or” phrase to the operation, verify independence or dependence, and check replacement wording. Ensure the factor after a no-replacement draw reflects the actual first outcome, not a generic decrement.

## M9 · Factorials, permutations, combinations

**Generator inputs:** a story with distinct objects, explicit selection size, repetition rule, and a supported `expr`: integers, `n!`, `P(n,k)`, or `C(n,k)`, joined only by `+` or `-`.

**Answer invariants:** use `n!` to arrange all `n` distinct objects; use `P(n,k)` when selected objects occupy distinguishable positions or order creates a different outcome; use `C(n,k)` when only membership matters. Require `0 ≤ k ≤ n`. The current contract does not model repeated objects or selection with replacement.

```json
{
  "id": "counting-01",
  "type": "counting",
  "expr": "P(8,3)",
  "key": 336
}
```

**Manual semantic check:** classify the story before calculating. Ask whether swapping two selected objects changes the outcome: ranked prizes, codes, schedules, and assigned roles are permutations; committees, hands, and unordered selections are combinations. Avoid pairs where the wrong operation coincidentally gives the same number, because arithmetic verification cannot catch a misclassified story. Confirm “all objects” really means `n!` and “without repetition” is stated when the story needs it.

## Cross-language rendering

Store language outside the numeric model and keep the same item `id` across language variants. Translate prompt, labels, units, interval language, probability connectors, and key together. Manually check inclusive thresholds, replacement phrases, and order-sensitive wording; numeric verification runs once and cannot detect a translation that changes the event.
