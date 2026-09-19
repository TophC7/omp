# Source Defects and Boundaries

These findings come from the three supplied decks and exist to prevent accidental copying. Slide IDs refer to the canonical inventory in `statistics-decks-master-reference.md`.

## Do not copy unchanged

| Slide(s) | Finding | Safe authoring rule |
|---|---|---|
| `s004` | The imported infographic repeats the full dataset on the mode line, orders the median example descending, and leaves the mean and median expressions unevaluated and ambiguous. | Replace it with a checked worked example; `s005` covers the same concepts correctly. |
| `s023`, `s024` | The published outlier key follows the 1.5 × IQR rule, but no deck teaches quartiles, IQR, or that threshold. | Teach one stated quartile convention and the 1.5 × IQR fences first, or reframe the task so visual identification is explicit. |
| `s028` | The exact mean `13.25` is reported as `13.3`, consistently with round-half-up to one decimal; this is a convention boundary, not a wrong key. | State precision and rounding convention before assigning decimal answers. |
| `s040`, `s041` | The prompt says `Mr. Jonson`, while the chart title says `Mr. Janson`. | Keep names and labels in one data model shared by prompt and key. |
| `s051` *(v1 only)* | A task titled “Histograms” shows a line graph, and it is the inventory's only task without an answer slide. | Match title to display type and require a checked key for every task before publishing. |
| `s070` | Unsimplified working appears beside simplified final answers. | Either use one required form throughout or label the simplification step explicitly. |
| `s072` *(v1/v2)* | An expected count of `62.5` is correctly reported as approximately 63, but it is the source set's only non-integer expected count. | Label expected counts as estimates and state how whole-event counts are rounded. |
| `s074` *(v1/v2)*, `s131` *(v3)* | Cropped factorial artwork drops `× 1 = 5040`, and its Spanish caption ends mid-sentence. | Typeset the complete formula and caption, then inspect the exported slide edges. |
| `s075` *(v1/v2)* | The heading reads `n! = n`, table rows omit `!`, and periods mark thousands. | Write `n! = n × (n−1) × … × 1`, label factorial values with `!`, and use locale-unambiguous number formatting. |
| `s076`, `s077`, `s133` | Spanish accent, wording, punctuation, and capitalization artefacts reduce clarity. | Proofread each language variant independently while sharing the underlying mathematics. |
| `s098` *(v2/v3)* | It says measures of center and range cannot be found from a histogram; exact raw-data values are unavailable, but grouped-data estimates may be possible. | Distinguish exact values from estimates and state what binning permits. |
| `s111` *(v3)* | The compound-events definition is at p72, while the compound-probability unit starts at p90. | Place the definition with `s121`-style instruction and practice after simple probability. |
| `s126` *(v3)* | The answer slide contains the orphaned phrase “or randomly selected” in a month-selection prompt. | Name one random experiment precisely and proofread answer slides as learner-facing material. |

## Version drift

The revisions share page prefixes, not stable page numbers throughout: v1 and v2 are identical through p47; v2 and v3 are identical through p67. Then:

- v2 removes the v1-only Spanish histogram sequence `s049`–`s051`, adds circle-graph pairs `s093`–`s096`, and replaces that histogram sequence with `s097`–`s108`;
- v3 removes 18 v2 slides and adds 35, including new simple-probability, compound-probability, and counting material;
- v3 retains combination examples but drops the dedicated `nCr` formula slide `s081`;
- v3 drops `s071`–`s072`, the source set's only explicit theoretical-versus-experimental probability treatment;
- v2 and v3 omit `s049`–`s050`, the only explicit continuous-data and learner-chosen interval-width treatment.

Identify content by canonical slide ID or item ID, never by page number across PDFs. When authoring from a later version, restore a missing concept only when it is a learning objective or prerequisite; do not assume later means cumulative.

Repeated exercise/key pairs and identical page images are not additional coverage. Deduplicate assets when auditing, while retaining source-page provenance.

## Curriculum omissions

The source set is not a complete statistics course. Across all three decks, dispersion stops at range: variance, standard deviation, quartiles, and box plots are absent. Population-versus-sample reasoning, sampling and bias, and categorical-versus-quantitative data types are also absent. Add separately sourced instruction before treating any of these as established knowledge.

## Release gate

Reject a generated deck when any of these remain:

- prompt and answer use different data, labels, units, or category order;
- an IQR answer lacks the stated quartile convention;
- a decimal answer lacks a stated precision or rounding convention;
- a chart title disagrees with its visual;
- grouped data is treated as exact raw data;
- formula artwork is cropped or ambiguous;
- working and final answers switch numeric form without an explicit simplification instruction;
- a task has no answer key;
- translation changes mathematical meaning;
- a definition or task is detached from its prerequisite instruction;
- a source-only omission is mistaken for a deliberate prerequisite.
