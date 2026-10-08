# Data pipeline — extraction, cleaning, splits, EDA

Owner: Shibin. One command takes the HinGE release to frozen splits, model-ready
files and an EDA report:

```bash
pip install -r pipeline/requirements.txt
python pipeline/run_pipeline.py --input data/raw/HinGE.pkl
```

Then open `reports/data_pipeline/eda_report.html`.

| Flag | Use |
|---|---|
| `--pause` | wait for Enter between stages (live demo) |
| `--hf LingoIITGN/HinGE` | load the Hugging Face copy instead of the pickle (needs `datasets`) |
| `--expected-sha256 <hash>` | refuse to unpickle a file that is not the one we recorded |
| `--stages clean split eda` | re-run part of the pipeline |
| `--fixture` | run on the **synthetic** test fixture, outputs to `out/fixture_run/` — for rehearsal and CI only |

## Stages

```
HinGE.pkl ──► 1 extract ──► hinge_flat.tsv ──► 2 clean ──► hinge_clean.tsv ──► 3 split ──► train/dev/test ──► 4 eda
               │                                 │                               │                         │
               extract_manifest.json            clean_manifest.json             hinge_split_manifest.json  figures, EDA_REPORT.md,
               samples.md                       cleaning_report.json            split_report.json          eda_report.html, eda_summary.json
```

**1. Extract** (`extract.py`). Fingerprints the input (SHA-256, size), resolves the
columns by name, profiles the release *as released* (rows, unique sources, human
references per source, missing cells per column), and flattens it to one row per
reference: every human reference, the WAC output and the PAC output each become a
row. Nothing is filtered here.

**2. Clean** (`clean.py`). An ordered rule list, every rule counted in a ledger:

| Rule | Kind | What it does |
|---|---|---|
| `unicode_nfc` | transform | NFC normalisation |
| `invisible_chars` | transform | zero-width / BOM / soft hyphen / control characters removed (ZWJ/ZWNJ kept inside Devanagari) |
| `punctuation_ascii` | transform | curly quotes, dashes, ellipses to ASCII |
| `pii_mask` | transform | URLs, e-mails, phone numbers → `<URL>` `<EMAIL>` `<PHONE>` |
| `whitespace` | transform | collapse and trim |
| `invalid_rating` | transform | ratings outside 1–10 become missing (never clipped) |
| `missing_english` / `missing_hinglish` | drop | empty text |
| `english_not_latin` | drop | English column under 50% Latin letters (misaligned columns) |
| `hinglish_has_devanagari` | drop | the target is Romanized |
| `hinglish_copies_english` | drop | "reference" identical to the source |
| `length_ratio_outlier` | drop | Hinglish/English word ratio outside 0.30–3.00 |
| `duplicate_pair` | drop | same pair after normalisation; human row kept over WAC/PAC |
| `missing_hindi`, `hindi_not_devanagari`, `synthetic_missing_rating` | flag | kept, counted for the datasheet |

**Not done on purpose:** Romanized spelling is never normalised and text is never
lowercased. Spelling variance is the phenomenon the project measures; normalising
it here would delete the effect before anyone can measure it. WAC/PAC rows are not
filtered by rating either — that is a training decision, not a cleaning one.

A validation gate re-checks ten invariants on the output and writes nothing if any
fails.

**3. Split** (`split.py`). Calls Yash's `scripts/make_splits.py` (298-11) unchanged
on the cleaned corpus, re-checks leakage independently (English sources, human
references, and the gold set against train/dev), and exports:

| File | Contents |
|---|---|
| `train.human.tsv` | `English<TAB>Hinglish`, human refs only — few-shot pool for `generate_zeroshot.py --examples`, SFT data |
| `{dev,test}.en.txt` | one English source per line |
| `{dev,test}.hinglish.txt` | first human reference, line-aligned — `run_eval.py --ref` |
| `{dev,test}.hi.txt` | Devanagari Hindi, line-aligned — `run_eval.py --mono-ref` |
| `{dev,test}.refs.jsonl` | all human references per source |
| `slices/{en,hi_deva,hinglish}.txt` | train-only slices for `analysis/tokenizer_fertility.py --corpus` (the Romanized-Hindi slice needs Dakshina and is not built) |

WAC/PAC outputs are never dev/test references.

**4. EDA** (`eda.py`). Nine figures, a JSON of every number, a Markdown report and
a self-contained HTML report. It reuses `code_mixing_stats` from
`analysis/tokenizer_fertility.py` (298-22), `krippendorff_alpha` from
`human_eval/agreement.py`, and the variant lexicon in
`analysis/spelling_variants.tsv`. It also writes `data/interim/hinge_tagged.conll`,
the language-tagged input `--cmi-only` has been waiting for.

## Column order of every flattened TSV

No header (make_splits.py reads every line as data):

`english, hinglish, hindi, ref_source, rating1, rating2, src_id, ref_idx`

Column 1 is Hinglish, not Hindi, because `generate_zeroshot.py` reads few-shot
examples as `(column 0, column 1)`.

## What to commit

Commit `pipeline/`, `tests/`, `data/processed/manifests/*.json` and
`reports/data_pipeline/`. Never commit `data/raw/`, `data/interim/` or the split
TSVs (all gitignored).

## Known limitations

- Language tags are a heuristic (token appears in the paired English source → `en`),
  so the English share and CMI are lower bounds. Hand-check 50 sentences before
  quoting CMI.
- The variant lexicon v1 groups some distinct words (`hai`/`hain`, `chal`/`chalo`),
  which inflates the variance numbers slightly; fix in a versioned lexicon update.
- EDA describes the whole cleaned corpus. Anything that drives a modelling decision
  (lexicon extension, vocabulary size) must be recomputed on train only.

## Notebook for the demo

`notebooks/tm1_data_pipeline_demo.ipynb` runs the same four stages cell by cell, with tables and figures
inline. It calls the `pipeline/` modules, so its numbers are identical to the command line.

```bash
pip install notebook          # or open it in VS Code / JupyterLab
jupyter notebook notebooks/tm1_data_pipeline_demo.ipynb    # then Kernel -> Restart & Run All
```

It is committed **with outputs**, so it shows results on GitHub even before anyone re-runs it.

Optional: copy the HinglishEval `train.csv`, `valid.csv` and `test.csv` (same Drive folder as HinGE.pkl) to
`data/raw/HinglishEval/` and the notebook recomputes the leakage in the released splits live
(75.8% of valid and 78.1% of test sources also occur in train).
