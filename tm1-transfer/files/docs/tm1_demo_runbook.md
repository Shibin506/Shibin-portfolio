# Team Meeting 1 — data pipeline demo runbook

Checkpoint requirement: *clean dataset, fixed splits, metrics justified, end-to-end
data extraction and cleaning demonstrated live, leakage check documented.*

## Before the session (do tonight, not in the room)

1. **Get the data in place.** Copy `HinGE.pkl` (the file Yash counted — see
   `docs/datasheet.md`) to `data/raw/HinGE.pkl`.
2. **Install.** `pip install -r pipeline/requirements.txt`
3. **Run once, end to end:** `python pipeline/run_pipeline.py --input data/raw/HinGE.pkl`
4. **Sanity-check against the datasheet.** The extraction banner should report
   1,976 source rows, 1,973 unique English sources, 4,799 human references and
   8,751 flattened rows. If it does not, stop and find out why before the demo —
   a mismatch is a finding, not something to hide.
5. **Record the hash.** Copy the SHA-256 printed by stage 1 into the datasheet, and
   use `--expected-sha256` from now on.
6. **Read the report** (`reports/data_pipeline/eda_report.html`) and make sure every
   finding is something you can explain. The wording is generated from the numbers;
   if one reads wrong on the real data, fix it before showing it.
7. **Commit through the normal loop:** Linear issue → branch `shibin/298-XX-data-pipeline`
   → PR → a non-author review → merge. Commit `pipeline/`, `tests/`,
   `data/processed/manifests/`, `reports/data_pipeline/`. Never `data/raw/`.
8. **Keep a backup.** Leave the generated `eda_report.html` open in a browser tab.
   If the live run fails, show it and **say it was generated last night**. Never
   show the `--fixture` run as if it were HinGE — it is synthetic.

## In the room (~10 minutes)

Start in a terminal at the repo root with a large font.

```bash
python pipeline/run_pipeline.py --input data/raw/HinGE.pkl --pause
```

| Time | Stage on screen | What to say |
|---|---|---|
| 0:00 | *(before running)* `docs/datasheet.md` table | Five sources, licences recorded **before** ingestion. HinGE is the parallel supervision: English, Hindi, human Hinglish, and two rule-based outputs (WAC, PAC) rated 1–10 by two raters. |
| 1:00 | **Stage 1 — extraction** | Point at the SHA-256 (provenance), the resolved columns, the counts, and "missing cells as released". Read one sample aloud: same English sentence, several human Hinglish versions, WAC and PAC with ratings. Note the 4,799-vs-4,803 count discrepancy and that the manifest now measures it from the file. |
| 3:00 | **Stage 2 — cleaning** | Walk the ledger: transforms (`~`), drops (`-`), flags (`!`). **Key design decision:** we do *not* normalise spelling, because spelling variance is what we measure. WAC/PAC are not filtered by rating; that is a training decision. Then the validation gate: ten checks, all PASS, otherwise nothing is written. |
| 5:00 | **Stage 3 — splits** | The released HinglishEval splits leak (75.8% of dev's sources are in train), so we re-derive: exact plus MinHash near-duplicate clusters, whole clusters per split, seed 42, manifest with hashes. Our own independent check shows 0 overlap. Dev/test references are human-written only. |
| 6:30 | **Stage 4 — EDA**, then switch to `eda_report.html` | Show four figures, in this order: (1) cleaning before/after, (7) spelling variants — **the hypothesis in one picture**: annotators writing the *same* sentence spell the same word differently; (6) code-mixing — the references really are mixed, and the SPF is what Model 4's synthetic data must match; (9) the splits are comparable. |
| 9:00 | Terminal: `python -m pytest tests/` | Reproducible: committed manifests, a synthetic fixture that plants one of each defect, tests asserting every rule fires exactly once. |

**Metrics (also required today):** chrF++ primary (character-level, robust to
`nahi`/`nhi`), BLEU and ROUGE-L/WER secondary (the last two for comparability with
Gahoi et al.), plus the code-switching penalty. All fixed in writing before any
results; the justification is in the README's Evaluation section.

Suggested split so every member speaks: Yash on sources and splits, Jenil on
cleaning rules versus annotation guidelines, Sarvesh on code-mixing and fertility,
Prakhar on environment and reproducibility, Shibin leading and taking the EDA. Each
person should still be able to answer on any stage.

## Questions to expect

| Question | Answer |
|---|---|
| Why not normalise spelling during cleaning? | It is the phenomenon under study. Normalised chrF++ applies the variant lexicon at **evaluation** time, so raw and normalised scores can be compared. |
| Why keep WAC/PAC at all? | They are candidate training augmentation, with their ratings kept. They are never dev/test references. |
| How accurate is the language tagging? | It is a heuristic: a token counts as English when it also appears in the paired English source. That makes CMI a lower bound. We will hand-check 50 sentences before reporting it. |
| Why a 0.30–3.00 length ratio? | Deliberately wide, so it removes only clear truncation or misalignment. Every row it drops is counted in the ledger. |
| Is the HinGE test split your benchmark? | No. It is the development test split. The held-out benchmark is the team-authored three-column gold set, and the split stage already checks it for overlap with train/dev. |
| Can synthetic data leak into test? | It could, and this is a known risk. HinGE's English comes from the IIT Bombay corpus, which Samanantar also contains. Before generating Model 4 data, dev/test English sources must be removed from the GCM input (requirement DR-6). |
| Licences? | Recorded per source in `docs/datasheet.md` before ingestion. All four sources are research-only or non-commercial. |

## Alternative: present from the notebook

`notebooks/tm1_data_pipeline_demo.ipynb` walks through the same four stages with inline tables and figures.
Open it, choose **Kernel → Restart & Run All** once before the session (about 20 seconds), then scroll and narrate
section by section using the same timings as the table above. Run one or two cells live (for example the
extraction cell and the validation gate) to show that nothing is pre-baked. The committed copy already holds
the outputs, so it is also the backup if the live run fails.
