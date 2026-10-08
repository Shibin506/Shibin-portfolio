#!/usr/bin/env python3
"""
Stage 3 -- frozen splits, leakage check and model-ready exports.  [owner: Shibin]

The split itself is Yash's scripts/make_splits.py (Linear 298-11), called
unchanged: exact normalised match plus MinHash/LSH near-duplicate clusters,
whole clusters assigned to one split, seed 42, manifest with SHA-256 hashes.
This stage only feeds it the cleaned corpus and then does three things the
models and the harness need:

  1. re-checks leakage independently of make_splits.py -- English sources,
     Hinglish references, and the team-authored gold set against train
  2. exports the files the other scripts read:
       train.human.tsv            English<TAB>Hinglish, human references only
                                  (few-shot pool for generate_zeroshot.py, SFT data)
       {dev,test}.en.txt          one English source per line
       {dev,test}.hinglish.txt    first human reference, aligned line by line
       {dev,test}.hi.txt          Devanagari Hindi, aligned (monolingual reference
                                  for the code-switching penalty)
       {dev,test}.refs.jsonl      every human reference per source (multi-ref)
       slices/{en,hi_deva,hinglish}.txt
                                  train-only text slices for tokenizer_fertility.py
     Machine outputs (WAC/PAC) are never used as dev/test references: scoring a
     model against another system's output is not a reference-based metric.
  3. writes reports/data_pipeline/split_report.json

A dev/test source enters the aligned files only if it kept at least one human
reference AND a Hindi sentence, so the Hinglish and Hindi files score the same
sources and the code-switching penalty is a paired comparison.

Usage
-----
  python pipeline/split.py
"""

import argparse
import csv
import json
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.common import (  # noqa: E402
    INTERIM_DIR, MANIFEST_DIR, PROCESSED_DIR, REPO_ROOT, REPORT_DIR,
    norm_key, read_tsv, rel, stage, write_json,
)

MAKE_SPLITS = REPO_ROOT / "scripts" / "make_splits.py"
GOLD_SET = REPO_ROOT / "data" / "goldtestset" / "gold_set.csv"
SPLITS = ("train", "dev", "test")


def run_make_splits(clean_path, outdir, manifest_dir, seed):
    if not MAKE_SPLITS.exists():
        sys.exit(f"{rel(MAKE_SPLITS)} not found -- merge the 298-11 branch first")
    cmd = [sys.executable, str(MAKE_SPLITS), "--input", str(clean_path),
           "--outdir", str(outdir), "--manifest-dir", str(manifest_dir), "--seed", str(seed)]
    print(f"  $ python {rel(MAKE_SPLITS)} --input {rel(clean_path)} --seed {seed}\n")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    for line in proc.stdout.splitlines():
        print(f"    | {line}")
    if proc.returncode != 0:
        sys.exit(f"make_splits.py failed:\n{proc.stderr}")


def group_sources(rows):
    """One record per English source (by normalised key), human refs only."""
    groups = OrderedDict()
    for r in rows:
        g = groups.setdefault(norm_key(r["english"]), {
            "english": r["english"], "hindi": "", "refs": [], "src_ids": set()})
        g["src_ids"].add(r["src_id"])
        if r["hindi"] and not g["hindi"]:
            g["hindi"] = r["hindi"]
        if r["ref_source"] == "human" and r["hinglish"] not in g["refs"]:
            g["refs"].append(r["hinglish"])
    return groups


def read_gold_sources():
    if not GOLD_SET.exists():
        return []
    with open(GOLD_SET, encoding="utf-8", newline="") as fh:
        return [row["english_source"] for row in csv.DictReader(fh)
                if row.get("english_source", "").strip()]


def leakage(split_rows):
    keys = {s: {norm_key(r["english"]) for r in rows} for s, rows in split_rows.items()}
    refs = {s: {norm_key(r["hinglish"]) for r in rows if r["ref_source"] == "human"}
            for s, rows in split_rows.items()}
    out = OrderedDict()
    for i, a in enumerate(SPLITS):
        for b in SPLITS[i + 1:]:
            out[f"english {a}&{b}"] = len(keys[a] & keys[b])
            out[f"human hinglish {a}&{b}"] = len(refs[a] & refs[b])
    gold = {norm_key(t) for t in read_gold_sources()}
    out["gold_set_items_checked"] = len(gold)
    out["gold english & train"] = len(gold & keys["train"])
    out["gold english & dev"] = len(gold & keys["dev"])
    return out


def write_lines(path, lines):
    path.write_text("".join(line + "\n" for line in lines), encoding="utf-8")


def export(split_rows, outdir):
    exported = OrderedDict()
    train_pairs = [(r["english"], r["hinglish"]) for r in split_rows["train"]
                   if r["ref_source"] == "human"]
    write_lines(outdir / "train.human.tsv", [f"{en}\t{hg}" for en, hg in train_pairs])
    exported["train.human.tsv"] = len(train_pairs)

    # HinGE contains misaligned references: a source whose human "references"
    # translate a different sentence that sits in another split. Its English
    # source is not shared, so make_splits.py cannot see it, but scoring dev/test
    # against text the model trained on is leakage all the same. Such references
    # are dropped from the dev/test exports and counted.
    train_refs = {norm_key(hg) for _, hg in train_pairs}
    for split in ("dev", "test"):
        groups = group_sources(split_rows[split])
        seen = 0
        for g in groups.values():
            kept = [ref for ref in g["refs"] if norm_key(ref) not in train_refs]
            seen += len(g["refs"]) - len(kept)
            g["refs"] = kept
        exported[f"{split}_refs_dropped_seen_in_train"] = seen
        usable = [g for g in groups.values() if g["refs"] and g["hindi"]]
        write_lines(outdir / f"{split}.en.txt", [g["english"] for g in usable])
        write_lines(outdir / f"{split}.hinglish.txt", [g["refs"][0] for g in usable])
        write_lines(outdir / f"{split}.hi.txt", [g["hindi"] for g in usable])
        with open(outdir / f"{split}.refs.jsonl", "w", encoding="utf-8") as fh:
            for g in usable:
                fh.write(json.dumps({"english": g["english"], "hindi": g["hindi"],
                                     "refs": g["refs"]}, ensure_ascii=False) + "\n")
        exported[f"{split}_sources"] = len(groups)
        exported[f"{split}_sources_exported"] = len(usable)
        exported[f"{split}_sources_excluded_no_human_ref"] = sum(1 for g in groups.values()
                                                                 if not g["refs"])
        exported[f"{split}_sources_excluded_no_hindi"] = sum(1 for g in groups.values()
                                                             if g["refs"] and not g["hindi"])
        exported[f"{split}_refs_per_source_mean"] = round(
            sum(len(g["refs"]) for g in usable) / max(len(usable), 1), 3)

    # Text slices for analysis/tokenizer_fertility.py, from TRAIN only, because
    # the fertility numbers feed the Model 3 vocabulary decision. The fourth
    # slice, monolingual Romanized Hindi, needs Dakshina and is not built here.
    slices = outdir / "slices"
    slices.mkdir(parents=True, exist_ok=True)
    train_groups = group_sources(split_rows["train"]).values()
    for name, lines in (("en", [g["english"] for g in train_groups]),
                        ("hi_deva", [g["hindi"] for g in train_groups if g["hindi"]]),
                        ("hinglish", [en_hg[1] for en_hg in train_pairs])):
        write_lines(slices / f"{name}.txt", lines)
        exported[f"slices/{name}.txt"] = len(lines)
    return exported


def run(clean_path=None, outdir=None, manifest_dir=None, report_dir=None, seed=42):
    clean_path = Path(clean_path or INTERIM_DIR / "hinge_clean.tsv")
    outdir = Path(outdir or PROCESSED_DIR)
    manifest_dir = Path(manifest_dir or MANIFEST_DIR)
    report_dir = Path(report_dir or REPORT_DIR)
    if not clean_path.exists():
        sys.exit(f"{rel(clean_path)} not found -- run pipeline/clean.py first")

    with stage("STAGE 3: FROZEN SPLITS AND LEAKAGE CHECK"):
        run_make_splits(clean_path, outdir, manifest_dir, seed)
        split_rows = {s: read_tsv(outdir / f"{s}.tsv") for s in SPLITS}

        print("\n  independent leakage check (normalised English / human Hinglish)")
        leaks = leakage(split_rows)
        for k, v in leaks.items():
            flag = "" if v == 0 or k == "gold_set_items_checked" else "   <-- LEAKAGE"
            print(f"    {k:<28} {v}{flag}")
        if any(v for k, v in leaks.items() if k.startswith("human hinglish")):
            print("    note: identical human references across splits under different English "
                  "sources = misaligned references in HinGE; they are dropped from the dev/test "
                  "exports below")
        hard = [k for k, v in leaks.items() if v and k.startswith("english")]
        if hard:
            sys.exit(f"English sources shared across splits: {hard}")
        if any(v for k, v in leaks.items() if k.startswith("gold english")):
            print("    WARNING: gold-set sources occur in train/dev -- remove them before "
                  "the gold set is used for evaluation")

        exported = export(split_rows, outdir)
        print("\n  model-ready exports")
        for k, v in exported.items():
            print(f"    {k:<40} {v}")

        report = OrderedDict(
            stage="split", seed=seed,
            manifest=rel(manifest_dir / "hinge_split_manifest.json"),
            rows={s: len(r) for s, r in split_rows.items()},
            unique_english={s: len({norm_key(r['english']) for r in rows})
                            for s, rows in split_rows.items()},
            leakage=leaks, exports=exported)
        write_json(report_dir / "split_report.json", report)
        print(f"\n  wrote -> {rel(report_dir / 'split_report.json')}")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", help="default data/interim/hinge_clean.tsv")
    ap.add_argument("--outdir", help="default data/processed/")
    ap.add_argument("--manifest-dir", help="default data/processed/manifests/")
    ap.add_argument("--report-dir", help="default reports/data_pipeline/")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    run(a.input, a.outdir, a.manifest_dir, a.report_dir, a.seed)


if __name__ == "__main__":
    main()
