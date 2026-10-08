# Test fixtures

`hinge_fixture.csv` is **synthetic**. It was written by hand for the test suite
and is **not HinGE data**: no row comes from the release, and no number computed
from it may appear in a report.

It mirrors the column layout of `HinGE.pkl` (English, Hindi, Human-generated
Hinglish (list), WAC, WAC rating1/2, PAC, PAC rating1/2) and plants one instance
of each defect the cleaning stage has to catch, so each rule is exercised:

| Source row | Planted defect |
|---|---|
| 2 | PAC output identical to a human reference (duplicate pair) |
| 7 | a human reference written in Devanagari |
| 7 | a rating of 11, outside the 1-10 scale |
| 8 | a missing WAC rating |
| 11 | a URL in every column (masked) |
| 12 | a "reference" that is the English source copied unchanged |
| 14 | a one-word reference ("haan") against a seven-word source |
| 15 | a curly apostrophe and a zero-width space |
| 16 | a missing Hindi sentence |
| 18 | an empty human reference |
| 20 | an English source duplicated from row 0 |
| 23 | leading, trailing and doubled whitespace |

Row numbers are 0-based `src_id` values, as the pipeline reports them.
