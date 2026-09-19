---
name: statistics-deck-authoring
description: "Use when creating, revising, or auditing statistics slide decks, worksheets, or paired answer keys within the audited M1–M9 scope: center measures, outliers, stem-and-leaf plots, circle graphs, histograms, probability, and counting. Supports the source decks' Spanish-concept/English-practice pattern and deterministic numeric-key checks."
tags:
  - statistics
  - worksheets
  - assessment
  - probability
  - permutations
  - combinations
---

# Statistics Deck Authoring

Create new material from the durable structure of three audited class decks. Treat their question patterns and teaching sequence as evidence; do not copy their wording, graphics, typos, omissions, or page order.

Do not use this skill for Socrative conversion, raw slide transcription, or a general statistics curriculum.

## Source boundary

The source set has 143 distinct slides across three revisions. It supports:

- M1–M9 below;
- 46 blank → key pairs plus one unpaired, mislabeled v1 task;
- reusable generators such as finite outcome boards, spinners, card decks, stated-total circle graphs, interval histograms, no-replacement draws, and permutation/combination classification.

It does **not** teach variance, standard deviation, quartiles or IQR as a topic, box plots, sampling, bias, population-versus-sample reasoning, or categorical-versus-quantitative data types. Quartiles and the 1.5×IQR rule may be added only as an explicit extension before an IQR-outlier task. Say when a request crosses this curriculum ceiling.

Use `statistics-decks-master-reference.md` beside the PDFs for provenance and slide inventory. Write new student-facing language; never treat a source answer slide as a layout or wording template.

## Authoring workflow

1. Fix audience, lesson length, output language pattern, and module(s).
2. Follow M1–M9 order for a full course. For a partial deck, include the prerequisites below and teach each rule before practice.
3. Create one canonical JSON item for each supported numeric prompt: stable `id`, supported `type`, input data, and `key`.
4. Render both student prompt and teacher key from that same item. Keep answers absent from the student version; keep data, labels, units, category order, and visual encoding identical.
5. Run the verifier on the complete item list. Change the model or derived key—not one rendered copy—when data changes.
6. Manually inspect mathematical meaning, pedagogy, language, unsupported calculations, and every chart.
7. Inspect the rendered student and teacher decks for answer leaks, cropping, unreadable notation, broken legends, and prompt/key drift.

## Module sequence and dependencies

| Module | Teach and practise | Required first |
|---|---|---|
| M1 | One overview definition of statistics and its role in working with data | None |
| M2 | Mean, median, mode, range | Addition, division, ordering |
| M3 | What an outlier is; effects on M2 measures | M2 |
| M4 | Stem, leaf, key; reconstruct data and apply M2 measures | Ordering, place value, M2 |
| M5 | Circle-graph sectors; compare percentages; find a percent of a stated total | Percentages |
| M6 | Continuous data, interval choice, frequency tables, histograms, counts, cumulative counts, percentages | Intervals, counts, percentages |
| M7 | Experiment, outcome, sample space, simple probability, complements, theoretical versus experimental probability | Fractions, decimals, percentages |
| M8 | Compound events; independent and dependent events; replacement state | M7 |
| M9 | Factorial, then permutations and combinations; decide whether order matters | Multiplication; factorial before `P` and `C` |

The source places one compound-events definition early in v3; do not copy that exception. M8 follows M7. M9 still follows M8 in the established course order, though its direct dependency is factorial and order reasoning.

## Calculation rules

- **Mean:** sum all values, then divide by their count.
- **Median:** order values first; use the middle value, or average the two middle values for an even count.
- **Mode:** use “no mode” only when no value repeats (the greatest frequency is 1). Otherwise, return every repeated value tied for the greatest frequency, including when all distinct values share that repeated frequency.
- **Range:** maximum minus minimum.
- **Displayed rounding:** state precision in the prompt and round only the final result. The audited key establishes half-up rounding (`13.25 → 13.3`). In JSON, `places` defaults to 1 and the verifier applies it to mean and range; medians remain unrounded numeric values.
- **Outlier effect:** compare the same list with and without the designated value. Report observed changes; do not claim mean, median, mode, or range always reacts the same way.
- **IQR outliers:** this is an extension, not source-taught curriculum. Sort; exclude the median when splitting an odd-sized list; find Q1 and Q3; flag values strictly below `Q1 − 1.5×IQR` or above `Q3 + 1.5×IQR`. State this quartile convention.
- **Stem-and-leaf:** order leaves within stems and include a key such as `2 | 1 = 21 minutes`. Reconstruct the values before calculating M2 measures.
- **Circle graph:** percentages total 100%. For an amount, calculate `total × percentage / 100`; identify whether the requested result is a percent, amount, or category.
- **Histogram:** use non-overlapping intervals and count each observation once. Grouped bins give exact frequencies, cumulative counts, and percentages, but only estimates of center or spread; label estimates as such.
- **Simple probability:** for equally likely outcomes, `P(E) = favorable outcomes / total outcomes`. Define the sample space, simplify the fraction, and distinguish theoretical probability from observed experimental frequency.
- **Compound probability:** for an “and” path, multiply each stage's probability given prior stages. Keep denominators fixed only for independent or replacement cases; update counts without replacement. Add mutually exclusive alternative paths rather than sending that sum through the product-only verifier.
- **Counting:** `n!` arranges all `n` distinct objects; `P(n,k)` selects and orders `k`; `C(n,k)` selects `k` without order. Decide whether a changed order creates a different outcome before choosing notation.

## Bilingual presentation

When matching the audited deck style, teach concepts in Spanish and give most practice in English. This is a deliberate cross-slide pattern, not permission to mix fragments accidentally.

For a monolingual deck or parallel language editions, choose the audience language first. Translate prompt, labels, units, directions, and key together. Keep one term per concept, and keep the same item `id` and numeric model across language variants so arithmetic is verified once. Newly write translations; do not preserve source translation artifacts.

## JSON and numeric verification

The file contract is:

```json
{"items": [{"id": "unique-id", "type": "center", "data": [1, 2, 3], "key": {"mean": 2}}]}
```

Supported `type` values are `center`, `outlier_effect`, `outliers_iqr`, `percent_of_total`, `histogram`, `probability`, `compound`, and `counting`. See [question-bank.md](chapters/question-bank.md) for their fields and generator patterns; keep this simple contract rather than inventing another schema.

From this skill's directory, run the generated spec—not only the example:

```sh
python3 scripts/verify_keys.py path/to/items.json
```

Exit 0 means every submitted key the script evaluates matches its deterministic calculation and targeted structural checks pass. It covers center measures and rounding; before/after outlier measures; 1.5×IQR flags; circle-graph totals, sector queries, and amounts; histogram frequency queries; one simple-probability fraction; compound products; and factorial/permutation/combination arithmetic. It also rejects malformed numeric fields, mismatched `queries`/`key` list lengths, and ambiguous maximum/minimum queries when multiple categories tie.

It does **not** validate complete worksheet semantics or rendering: it cannot decide whether a prompt chose the right data, sample space, histogram bins, replacement model, operation, or counting formula. It does not validate stem-and-leaf rendering, probability decimal/percent equivalents, theoretical-versus-experimental labeling, translations, pedagogy, or slide layout. Product-only `compound` items do not verify sums of alternative paths.

These are targeted calculations and structural checks, not full semantic validation. As defense in depth, manually confirm every requested answer has a key and each `queries` list aligns one-for-one with its `key` list.

See [defects.md](chapters/defects.md) before reusing any source pattern.

## Release gate

Release only when all are true:

- every prompt/key pair is generated from one canonical item; student material contains no answer values;
- all supported numeric items are in the complete JSON spec and the verifier exits 0;
- prerequisites and the IQR curriculum boundary are explicit;
- prompt and key match in data, labels, units, categories, interval boundaries, replacement state, and rounding instruction;
- probability sample spaces and counting-formula choices pass manual semantic review;
- bilingual wording is complete and consistent; no source typo or mistranslation survives;
- circle sectors total 100%, histogram bins cover intended observations once, and grouped-data claims distinguish exact results from estimates;
- the rendered student and teacher decks were both inspected for legibility, cropping, legends, formulas, answer leaks, and pairing.
