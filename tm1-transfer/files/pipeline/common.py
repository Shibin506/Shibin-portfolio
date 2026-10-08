"""
Shared helpers for the data pipeline.  [owner: Shibin]

Everything the four stages (extract, clean, split, eda) agree on lives here:
directory layout, the column order of the flattened corpus, script detection
and hashing. Keeping it in one place is what stops the stages from quietly
disagreeing about what column 1 means.
"""

import hashlib
import json
import re
import sys
import time
import unicodedata
from contextlib import contextmanager
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directory layout from the data management plan (Workbook 1, section 2.1).
# raw/ interim/ processed/ are gitignored; manifests/ and reports/ are not,
# because they hold counts and hashes rather than corpus text.
RAW_DIR = REPO_ROOT / "data" / "raw"
INTERIM_DIR = REPO_ROOT / "data" / "interim"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
MANIFEST_DIR = PROCESSED_DIR / "manifests"
REPORT_DIR = REPO_ROOT / "reports" / "data_pipeline"

# Column order of every flattened TSV the pipeline writes (no header row --
# scripts/make_splits.py reads every line as data).
#
# Column 0 is English because make_splits.py groups near-duplicates on it.
# Column 1 is Hinglish because models/generate_zeroshot.py reads few-shot
# examples as (parts[0], parts[1]) = (English, Hinglish). Putting Hindi in
# column 1 would silently turn every 5-shot prompt into English -> Devanagari.
COLUMNS = [
    "english",      # source sentence (IIT Bombay, via HinGE)
    "hinglish",     # one reference: human-written, or WAC / PAC machine output
    "hindi",        # Devanagari Hindi for the same source (monolingual reference)
    "ref_source",   # human | wac | pac
    "rating1",      # 1-10 quality rating, rater 1 (WAC/PAC only; empty for human)
    "rating2",      # 1-10 quality rating, rater 2
    "src_id",       # row index of the English source in the raw release
    "ref_idx",      # position of this reference among the source's human refs
]
REF_SOURCES = ("human", "wac", "pac")

DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
LATIN_LETTER_RE = re.compile(r"[A-Za-z]")


_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)
_WS = re.compile(r"\s+")


def norm_key(text):
    """Same normalisation as dedup_key() in scripts/make_splits.py (NFKC,
    lowercase, punctuation stripped, whitespace collapsed). Duplicated rather
    than imported because make_splits.py exits at import time without
    datasketch, and the cleaning stage should not need it."""
    t = unicodedata.normalize("NFKC", str(text)).lower()
    t = _PUNCT.sub(" ", t)
    return _WS.sub(" ", t).strip()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def script_shares(text):
    """(devanagari_share, latin_share) over letters only, so punctuation and
    digits do not dilute the ratio. Returns (0, 0) for a string with no letters."""
    letters = [c for c in str(text) if unicodedata.category(c).startswith(("L", "M"))]
    if not letters:
        return 0.0, 0.0
    deva = sum(1 for c in letters if DEVANAGARI_RE.match(c))
    latin = sum(1 for c in letters if LATIN_LETTER_RE.match(c))
    return deva / len(letters), latin / len(letters)


def write_tsv(path, rows):
    """rows: iterable of dicts keyed by COLUMNS. Tabs and newlines inside a
    field would shift every later column, so they are rejected rather than
    escaped -- the cleaning stage is responsible for removing them first."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            cells = ["" if row.get(c) is None else str(row.get(c)) for c in COLUMNS]
            for c, cell in zip(COLUMNS, cells):
                if "\t" in cell or "\n" in cell or "\r" in cell:
                    raise ValueError(f"tab/newline inside column {c!r}: {cell[:60]!r}")
            fh.write("\t".join(cells) + "\n")
            n += 1
    return n


def read_tsv(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.rstrip("\n")
            if not line:
                continue
            cells = line.split("\t")
            if len(cells) != len(COLUMNS):
                sys.exit(f"{path}:{lineno}: expected {len(COLUMNS)} columns, got {len(cells)}")
            rows.append(dict(zip(COLUMNS, cells)))
    return rows


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str) + "\n",
                    encoding="utf-8")


def rel(path):
    """Repo-relative path for manifests, so they do not leak a home directory."""
    try:
        return str(Path(path).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


@contextmanager
def stage(title):
    """Banner + timing around a stage. Built for the live demo: each stage
    announces itself, so the audience can follow which step produced what."""
    bar = "=" * 72
    print(f"\n{bar}\n  {title}\n{bar}")
    t0 = time.time()
    yield
    print(f"  -- {title.split(':')[0]} finished in {time.time() - t0:.1f}s")
