#!/usr/bin/env python3
"""
End-to-end data pipeline, one command.  [owner: Shibin]

    extract  ->  clean  ->  split  ->  eda

  python pipeline/run_pipeline.py --input data/raw/HinGE.pkl
  python pipeline/run_pipeline.py --input data/raw/HinGE.pkl --pause      # live demo
  python pipeline/run_pipeline.py --fixture                              # rehearsal / CI

--pause waits for Enter between stages, so the presenter can talk through each
stage's output before the next one scrolls it away.

--fixture runs on tests/fixtures/hinge_fixture.csv, a hand-written SYNTHETIC
file in HinGE's layout. Its outputs go to out/fixture_run/ (gitignored) and the
report is stamped as synthetic, so a fixture number can never be mistaken for a
HinGE number. Use it to rehearse, never to report.

--workdir sends every output (interim, processed, manifests, reports) under one
directory instead of the repository's data/ and reports/ folders.

Outputs on a real run
---------------------
  data/interim/hinge_flat.tsv, hinge_clean.tsv, hinge_tagged.conll   gitignored
  data/processed/{train,dev,test}.tsv and model-ready exports         gitignored
  data/processed/manifests/{extract,clean,hinge_split}_manifest.json  COMMIT
  reports/data_pipeline/  figures, EDA_REPORT.md, eda_report.html     COMMIT
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import clean, eda, extract, split  # noqa: E402
from pipeline.common import (  # noqa: E402
    INTERIM_DIR, MANIFEST_DIR, PROCESSED_DIR, REPO_ROOT, REPORT_DIR, rel,
)

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "hinge_fixture.csv"
STAGES = ("extract", "clean", "split", "eda")


def paths(workdir):
    if workdir is None:
        return dict(interim=INTERIM_DIR, processed=PROCESSED_DIR, manifests=MANIFEST_DIR,
                    reports=REPORT_DIR)
    w = Path(workdir)
    return dict(interim=w / "interim", processed=w / "processed",
                manifests=w / "processed" / "manifests", reports=w / "reports")


def run(input_path=None, hf=None, workdir=None, stages=STAGES, seed=42,
        expected_sha256=None, pause=False):
    p = paths(workdir)
    flat = p["interim"] / "hinge_flat.tsv"
    cleaned = p["interim"] / "hinge_clean.tsv"
    t0 = time.time()

    def maybe_pause(name):
        if pause and name != stages[-1]:
            input("\n  [press Enter for the next stage] ")

    for name in stages:
        if name == "extract":
            extract.run(input_path, hf, flat, p["manifests"] / "extract_manifest.json",
                        p["reports"], seed=seed, expected_sha256=expected_sha256)
        elif name == "clean":
            clean.run(flat, cleaned, p["manifests"] / "clean_manifest.json", p["reports"])
        elif name == "split":
            split.run(cleaned, p["processed"], p["manifests"], p["reports"], seed=seed)
        elif name == "eda":
            eda.run(cleaned, p["processed"], p["manifests"], p["reports"],
                    p["interim"] / "hinge_tagged.conll")
        maybe_pause(name)

    print(f"\n{'=' * 72}\n  PIPELINE COMPLETE in {time.time() - t0:.1f}s -- stages: "
          f"{' -> '.join(stages)}\n{'=' * 72}")
    print(f"  open {rel(p['reports'] / 'eda_report.html')} for the full report")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--input", help="HinGE.pkl (or csv/tsv/json/jsonl/parquet)")
    src.add_argument("--hf", help="Hugging Face dataset id, e.g. LingoIITGN/HinGE")
    src.add_argument("--fixture", action="store_true",
                     help="run on the synthetic test fixture (outputs to out/fixture_run/)")
    ap.add_argument("--workdir", help="write every output under this directory")
    ap.add_argument("--stages", nargs="+", choices=STAGES, default=list(STAGES),
                    help="run a subset, e.g. --stages clean split eda")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--expected-sha256", help="refuse to load the input unless it has this hash")
    ap.add_argument("--pause", action="store_true", help="wait for Enter between stages (demo)")
    a = ap.parse_args()

    input_path, workdir = a.input, a.workdir
    if a.fixture:
        input_path = str(FIXTURE)
        workdir = workdir or str(REPO_ROOT / "out" / "fixture_run")
    if "extract" in a.stages and not (input_path or a.hf):
        ap.error("--input, --hf or --fixture is required when running the extract stage")
    run(input_path, a.hf, workdir, tuple(a.stages), a.seed, a.expected_sha256, a.pause)


if __name__ == "__main__":
    main()
