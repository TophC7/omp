---
name: socrative-exam-templating
description: Design, review, and deliver exams in the Socrative exam website's Excel import format. Use when Gabriel asks for a Socrative-ready quiz, a Socrative spreadsheet, or conversion of a question bank into the Socrative template. This is unrelated to Socratic tutoring.
tags: [assessment, exams, socrative, excel]
---

# Socrative Exam Templating

This skill is for the **Socrative exam website**, not the Socratic teaching method. Produce an assessment first and a spreadsheet second. Use `/home/gabrielve/Downloads/socrativeQuizTemplate.xlsx` as the authoritative workbook whenever the requested deliverable is a Socrative import.

## Choose the first move

- If Gabriel explicitly asks to "serve up," convert, export, or create a ready-to-import Socrative exam, proceed directly after reading and reviewing the source.
- If the request leaves the assessment design open, discuss the exam's purpose, taught scope, learner level, coverage, difficulty, timing, and evidence of learning before templating.
- Do not force spreadsheet production into an exploratory discussion about assessment value.

## Assessment standard

1. Read the complete source bank and its assembly contract, exclusions, metadata, explanations, and learner-support notes.
2. Review every item for an eighth-grade-through-high-school audience, adjusted to the level Gabriel names.
3. Require a clear stem, one defensible key for single-answer multiple choice, plausible misconception-based distractors, age-appropriate wording, and an explanation that teaches the governing rule.
4. Reject ambiguity, duplicated answers, accidental clues, trick wording, filler, trivia, content outside the taught scope, and difficulty caused only by obscure vocabulary.
5. Use assessment structures grounded in credible educational institutions and preserve source records in the internal bank. Do not put internal source metadata into the student-facing workbook unless requested.
6. When the bank provides a Spanish tip, append it to the Socrative explanation as `Consejo en español: ...`.
7. If items or options are reordered, remap every key and verify the remapped key against the final option text.

## Authoritative workbook map

Preserve the workbook, sheet names, hidden sheet, styling, validations, and blank rows. Populate only the intended cells on the `Quick Quiz` sheet:

- `B3`: quiz name, 2–255 characters.
- Rows `7:200`: quiz items.
- Column `A`: exact question type, normally `Multiple choice` or `Open-ended`.
- Column `B`: question text.
- Columns `C:G`: Answer A through Answer E. Use `C:F` for four-option items and leave `G` blank.
- Columns `H:L`: correct-answer selections corresponding to the final five answer columns. For one-key four-option items, place the answer letter in `H` and leave `I:L` blank.
- Column `M`: explanation.

Socrative's official import guidance permits up to five multiple-choice answers and one or more correct answers. Students must select every marked correct answer. The Excel template accepts at most 100 questions per imported quiz; split and later merge larger exams only when Gabriel asks for that workflow. Source: https://help.socrative.com/en/articles/2155335-import-a-quiz (verified 2026-08-13).

## Conversion procedure

1. Parse the complete source into structured items: stable source ID, stem, options, key, explanation, Spanish tip, scope, skill, difficulty, and exclusions.
2. Confirm the requested count does not exceed 100 and does not exceed the usable, approved source material.
3. Build the exam blueprint from the source contract. Preserve requested coverage and difficulty rather than selecting convenient items.
4. Reorder questions and choices only when the assembly contract or Gabriel requests it. Use one stable permutation for the delivered form and remap keys immediately.
5. Combine each explanation and Spanish tip without adding source notes, licensing text, hidden metadata, or teacher-only feedback.
6. Fill a copy of the authoritative workbook. Never rebuild a look-alike workbook when the template is available.
7. Save the canonical finished exam under the current project's `library/exams/` and place a delivery copy in `/home/gabrielve/Downloads/`.

## Required verification

Before delivery, inspect the finished workbook and prove all of the following:

- the quiz name is populated;
- the requested number of item rows is populated and later rows remain blank;
- every multiple-choice row has a stem and the intended number of nonempty answers;
- every single-answer row has exactly one key;
- every key points to the intended final option text after reordering;
- every explanation is nonempty and contains its Spanish tip when required;
- no source IDs, class metadata, difficulty labels, source records, or option feedback leaked into student-facing cells;
- the workbook still contains the `Quick Quiz` sheet and hidden `Data` sheet and retains the template validations;
- the `.xlsx` archive passes an integrity check and can be opened by an installed spreadsheet application when available.

Deliver the workbook path and concise verification evidence. Do not add generic licensing warnings to the exam delivery.
