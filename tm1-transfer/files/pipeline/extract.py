#!/usr/bin/env python3
"""
Stage 1 -- data extraction.  [owner: Shibin]

Turns the HinGE release (Srivastava & Singh, 2021) into one flat TSV with one
row per (English source, Hinglish reference) pair, and records exactly what was
read so that every downstream count is traceable to a file hash.

Sources this stage understands
------------------------------
  * the authors' pickle, HinGE.pkl (Google Drive link in docs/datasheet.md)
  * the same table as .csv / .tsv / .json / .jsonl / .parquet
  * the Hugging Face copy, LingoIITGN/HinGE, via --hf (needs `datasets`)

Collection steps, in order
--------------------------
  1. fingerprint the input: SHA-256, size, modification time
  2. load it and resolve the columns (English, Hindi, human Hinglish list,
     WAC, PAC and their two ratings each) by name, tolerating the small
     naming differences between the pickle and the Hugging Face copy
  3. profile the release AS RELEASED -- row counts, unique sources, human
     references per source, missing cells per column -- before anything is
     changed, so the cleaning stage has a baseline to report against
  4. flatten: every human reference, the WAC output and the PAC output each
     become one row, carrying the source's English and Hindi with them
  5. write data/interim/hinge_flat.tsv (gitignored) and
     data/processed/manifests/extract_manifest.json (committed: counts and
     hashes only, no corpus text)
  6. print a few representative samples, seeded, for the demo

Nothing is filtered here. Extraction is faithful to the release; every
decision to drop or change a row belongs to the cleaning stage, where it is
counted.

A note on the pickle: unpickling runs code from the file. Only load HinGE.pkl
from the authors' link, and pass --expected-sha256 once the team has recorded
the hash, so a substituted file fails before it is opened.

Usage
-----
  python pipeline/extract.py --input data/raw/HinGE.pkl
  python pipeline/extract.py --hf LingoIITGN/HinGE
"""

import argparse
import ast
import random
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.common import (  # noqa: E402
    COLUMNS, INTERIM_DIR, MANIFEST_DIR, REPORT_DIR, rel, sha256_file, stage, write_json, write_tsv,
)

try:
    import pandas as pd
except ImportError:
    sys.exit("pip install -r pipeline/requirements.txt  -- pandas is required")


# --------------------------------------------------------------- column names

def _key(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


# Normalised column name -> role. The pickle uses "Human-generated Hinglish
# (list)"; other copies drop the "(list)" or split it into numbered columns,
# which is why human columns are matched by substring further down.
ALIASES = {
    "english": "english", "en": "english", "englishsentence": "english",
    "hindi": "hindi", "hi": "hindi", "hindisentence": "hindi",
    "wac": "wac", "wacrating1": "wac_r1", "wacrating2": "wac_r2",
    "pac": "pac", "pacrating1": "pac_r1", "pacrating2": "pac_r2",
}


def resolve_columns(columns):
    """Map each role to a column name. Exits with the column list on failure,
    because a guessed mapping would produce a plausible-looking wrong corpus."""
    mapping, human = {}, []
    for col in columns:
        k = _key(col)
        if k in ALIASES and ALIASES[k] not in mapping:
            mapping[ALIASES[k]] = col
        elif "human" in k and "rating" not in k:
            human.append(col)
    missing = [r for r in ("english", "hindi", "wac", "pac") if r not in mapping]
    if missing or not human:
        sys.exit("could not find column(s) {} in the release.\ncolumns present: {}\n"
                 "Add the name to ALIASES in pipeline/extract.py.".format(
                     missing + ([] if human else ["human-generated Hinglish"]), list(columns)))
    mapping["human"] = human
    return mapping


# --------------------------------------------------------------------- loading

def load_release(path=None, hf=None):
    if hf:
        try:
            from datasets import load_dataset
        except ImportError:
            sys.exit("pip install datasets  -- required for --hf")
        ds = load_dataset(hf)
        frames = [ds[split].to_pandas() for split in ds]
        return pd.concat(frames, ignore_index=True)

    path = Path(path)
    if not path.exists():
        sys.exit(f"input not found: {path}\nDownload HinGE first -- see docs/datasheet.md.")
    suffix = path.suffix.lower()
    if suffix in (".pkl", ".pickle"):
        obj = pd.read_pickle(path)
        return obj if isinstance(obj, pd.DataFrame) else pd.DataFrame(obj)
    if suffix == ".csv":
        return pd.read_csv(path, keep_default_na=True)
    if suffix == ".tsv":
        return pd.read_csv(path, sep="\t", keep_default_na=True)
    if suffix == ".jsonl":
        return pd.read_json(path, lines=True)
    if suffix == ".json":
        return pd.read_json(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    sys.exit(f"unsupported input format: {suffix}")


def is_missing(value):
    if value is None:
        return True
    if isinstance(value, float) and value != value:   # NaN
        return True
    return isinstance(value, str) and not value.strip()


def as_ref_list(value):
    """The human column holds a Python list in the pickle and a stringified
    list in CSV exports. literal_eval, never eval: the cell is data."""
    if is_missing(value):
        return []
    if hasattr(value, "tolist") and not isinstance(value, str):
        value = value.tolist()
    if isinstance(value, (list, tuple)):
        return ["" if is_missing(v) else str(v) for v in value]
    text = str(value).strip()
    if text.startswith("["):
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, (list, tuple)):
                return ["" if is_missing(v) else str(v) for v in parsed]
        except (ValueError, SyntaxError):
            pass
    return [text]


def cell(value):
    if is_missing(value):
        return ""
    # pandas turns an integer rating column into float as soon as one cell is
    # missing; write 6 rather than 6.0 so the file reads as released.
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


# ------------------------------------------------------------------- flatten

_TSV_UNSAFE = re.compile(r"[\t\r\n]+")


def flatten(df, cols):
    """One row per reference. Tabs and newlines inside a cell are the only
    thing changed here (a TSV cannot hold them); the count is reported."""
    rows, sanitised = [], 0

    def safe(text):
        nonlocal sanitised
        if _TSV_UNSAFE.search(text):
            sanitised += 1
            return _TSV_UNSAFE.sub(" ", text)
        return text

    for src_id, rec in enumerate(df.to_dict(orient="records")):
        english = safe(cell(rec[cols["english"]]))
        hindi = safe(cell(rec[cols["hindi"]]))
        refs = []
        for col in cols["human"]:
            refs.extend(as_ref_list(rec[col]))
        for ref_idx, ref in enumerate(refs):
            rows.append({"english": english, "hinglish": safe(ref), "hindi": hindi,
                         "ref_source": "human", "rating1": "", "rating2": "",
                         "src_id": src_id, "ref_idx": ref_idx})
        for source in ("wac", "pac"):
            rows.append({"english": english, "hinglish": safe(cell(rec[cols[source]])),
                         "hindi": hindi, "ref_source": source,
                         "rating1": cell(rec.get(cols.get(f"{source}_r1"))),
                         "rating2": cell(rec.get(cols.get(f"{source}_r2"))),
                         "src_id": src_id, "ref_idx": ""})
    return rows, sanitised


# ------------------------------------------------------------------- profile

def profile(df, cols, rows):
    human_counts = [sum(len(as_ref_list(r[c])) for c in cols["human"])
                    for r in df.to_dict(orient="records")]
    missing = {}
    for col in df.columns:
        if col in cols["human"]:
            missing[col] = int(sum(1 for v in df[col] if not as_ref_list(v)))
        else:
            missing[col] = int(sum(1 for v in df[col] if is_missing(v)))
    english = [cell(v).strip() for v in df[cols["english"]]]
    return {
        "source_rows": int(len(df)),
        "unique_english_exact": len(set(english)),
        "duplicated_english_rows": int(len(english) - len(set(english))),
        "human_refs_total": int(sum(human_counts)),
        "human_refs_per_source": {str(k): v for k, v in sorted(Counter(human_counts).items())},
        "human_refs_mean_per_source": round(sum(human_counts) / max(len(df), 1), 3),
        "sources_without_human_ref": int(sum(1 for k in human_counts if k == 0)),
        "missing_cells_per_column": missing,
        "flat_rows": len(rows),
        "flat_rows_by_ref_source": dict(Counter(r["ref_source"] for r in rows)),
    }


def samples(df, cols, k, seed):
    picks = random.Random(seed).sample(range(len(df)), min(k, len(df)))
    out = []
    for i in picks:
        rec = df.iloc[i]
        refs = []
        for col in cols["human"]:
            refs.extend(as_ref_list(rec[col]))
        out.append({
            "src_id": i,
            "english": cell(rec[cols["english"]]),
            "hindi": cell(rec[cols["hindi"]]),
            "human": refs,
            "wac": cell(rec[cols["wac"]]),
            "wac_ratings": [cell(rec.get(cols.get("wac_r1"))), cell(rec.get(cols.get("wac_r2")))],
            "pac": cell(rec[cols["pac"]]),
            "pac_ratings": [cell(rec.get(cols.get("pac_r1"))), cell(rec.get(cols.get("pac_r2")))],
        })
    return out


def print_samples(items):
    for s in items:
        print(f"\n  [source {s['src_id']}]")
        print(f"    English : {s['english']}")
        print(f"    Hindi   : {s['hindi']}")
        for j, ref in enumerate(s["human"]):
            print(f"    Human {j + 1} : {ref}")
        print(f"    WAC     : {s['wac']}   (ratings {', '.join(s['wac_ratings'])})")
        print(f"    PAC     : {s['pac']}   (ratings {', '.join(s['pac_ratings'])})")


def _md(text):
    return str(text).replace("|", "\\|")


def write_samples_md(path, items, source_label):
    lines = [f"# Representative samples -- {source_label}", "",
             "Drawn at random (seeded) by `pipeline/extract.py`, before any cleaning.",
             "HinGE is cited, non-commercial research data (see docs/datasheet.md).", ""]
    for s in items:
        lines += [f"## Source {s['src_id']}", "", "| Field | Text |", "|---|---|",
                  f"| English | {_md(s['english'])} |", f"| Hindi | {_md(s['hindi'])} |"]
        lines += [f"| Human {j + 1} | {_md(r)} |" for j, r in enumerate(s["human"])]
        lines += [f"| WAC ({', '.join(s['wac_ratings'])}) | {_md(s['wac'])} |",
                  f"| PAC ({', '.join(s['pac_ratings'])}) | {_md(s['pac'])} |", ""]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------- main

def run(input_path=None, hf=None, out=None, manifest=None, report_dir=None,
        n_samples=3, seed=42, expected_sha256=None):
    out = Path(out or INTERIM_DIR / "hinge_flat.tsv")
    manifest = Path(manifest or MANIFEST_DIR / "extract_manifest.json")
    report_dir = Path(report_dir or REPORT_DIR)

    with stage("STAGE 1: EXTRACTION"):
        if hf:
            fingerprint = {"hf_dataset": hf}
            print(f"  source            : Hugging Face dataset {hf}")
        else:
            path = Path(input_path)
            if not path.exists():
                sys.exit(f"input not found: {path}\nDownload HinGE first -- see docs/datasheet.md.")
            digest = sha256_file(path)
            if expected_sha256 and digest != expected_sha256.lower():
                sys.exit(f"SHA-256 mismatch for {path}:\n  expected {expected_sha256}\n"
                         f"  got      {digest}\nRefusing to load it.")
            fingerprint = {
                "file": rel(path), "sha256": digest, "bytes": path.stat().st_size,
                "file_modified_at": datetime.fromtimestamp(
                    path.stat().st_mtime, timezone.utc).isoformat(timespec="seconds"),
            }
            print(f"  source            : {rel(path)}")
            print(f"  sha256            : {digest}")
            print(f"  size              : {path.stat().st_size:,} bytes")

        df = load_release(input_path, hf)
        cols = resolve_columns(df.columns)
        print(f"  columns found     : {list(df.columns)}")
        rows, sanitised = flatten(df, cols)
        prof = profile(df, cols, rows)

        print(f"  source rows       : {prof['source_rows']:,}")
        print(f"  unique English    : {prof['unique_english_exact']:,} "
              f"({prof['duplicated_english_rows']} duplicated rows)")
        print(f"  human references  : {prof['human_refs_total']:,} "
              f"(mean {prof['human_refs_mean_per_source']} per source; "
              f"distribution {prof['human_refs_per_source']})")
        print(f"  flattened rows    : {prof['flat_rows']:,} {prof['flat_rows_by_ref_source']}")
        print("  missing cells as released:")
        for col, n in prof["missing_cells_per_column"].items():
            print(f"      {str(col):<32} {n}")

        n = write_tsv(out, rows)
        record = {
            "stage": "extract",
            "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "input": fingerprint,
            "column_mapping": cols,
            "profile": prof,
            "tsv_sanitised_cells": sanitised,
            "output": {"file": rel(out), "rows": n, "sha256": sha256_file(out),
                       "columns": COLUMNS},
        }
        write_json(manifest, record)
        print(f"\n  wrote {n:,} rows   -> {rel(out)}   (gitignored)")
        print(f"  wrote manifest     -> {rel(manifest)}   (commit this)")

        items = samples(df, cols, n_samples, seed)
        print(f"\n  representative samples (seed {seed}):")
        print_samples(items)
        label = hf or Path(input_path).name
        write_samples_md(report_dir / "samples.md", items, label)
    return record


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="HinGE.pkl, or the same table as csv/tsv/json/jsonl/parquet")
    src.add_argument("--hf", help="Hugging Face dataset id, e.g. LingoIITGN/HinGE")
    ap.add_argument("--out", help="flattened TSV (default data/interim/hinge_flat.tsv)")
    ap.add_argument("--manifest", help="default data/processed/manifests/extract_manifest.json")
    ap.add_argument("--report-dir", help="default reports/data_pipeline/")
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--expected-sha256", help="refuse to load the input unless it has this hash")
    a = ap.parse_args()
    run(a.input, a.hf, a.out, a.manifest, a.report_dir, a.samples, a.seed, a.expected_sha256)


if __name__ == "__main__":
    main()
