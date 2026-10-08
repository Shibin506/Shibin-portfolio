#!/usr/bin/env python3
"""
Stage 2 -- data cleaning and validation.  [owner: Shibin]

Reads the flattened corpus from stage 1 and applies an ordered list of rules.
Every rule is one of three kinds, and every one is counted:

  transform  changes a cell but keeps the row (Unicode, whitespace, PII ...)
  drop       removes the row, with the reason recorded
  flag       keeps the row but records the problem for the datasheet

The counts form a ledger -- rows in, rows affected per rule, rows out -- which
is what the cleaning report, the waterfall plot and the datasheet quote. A
number that cannot be traced to a ledger line should not appear in a report.

What this stage deliberately does NOT do
----------------------------------------
It does not normalise Romanized spelling. `nahi`, `nhi` and `nahin` stay as
written, because spelling variance is the phenomenon the project measures
(README, "The claim being tested"). Lowercasing is skipped for the same reason.
It does not filter WAC/PAC rows by rating either: whether low-rated synthetic
references enter training is a modelling decision, so the ratings are parsed
and kept, and the policy lives in the training config.

After the rules run, a validation gate re-checks the output against hard
invariants (schema, no empty text, no Devanagari in Hinglish, ratings on the
1-10 scale, no duplicate pairs). If any check fails, nothing is written and
the stage exits non-zero.

Usage
-----
  python pipeline/clean.py
  python pipeline/clean.py --input data/interim/hinge_flat.tsv --out data/interim/hinge_clean.tsv
"""

import argparse
import re
import sys
import unicodedata
from collections import Counter, OrderedDict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.common import (  # noqa: E402
    COLUMNS, DEVANAGARI_RE, INTERIM_DIR, MANIFEST_DIR, REF_SOURCES, REPORT_DIR,
    norm_key, read_tsv, rel, script_shares, sha256_file, stage, write_json, write_tsv,
)

TEXT_COLUMNS = ("english", "hinglish", "hindi")
LATIN_COLUMNS = ("english", "hinglish")

# Length ratio (Hinglish words / English words) outside these bounds is treated
# as a misaligned or truncated reference. Hinglish typically runs at 0.8-1.4x
# the English word count; the bounds are wide on purpose so that only clear
# breakage is dropped. Any change is a DECISIONS.md entry, not a quiet edit.
MIN_LEN_RATIO = 0.30
MAX_LEN_RATIO = 3.00
RATING_RANGE = (1, 10)
N_EXAMPLES = 3

# Invisible characters. ZWJ/ZWNJ (U+200D/U+200C) can be meaningful inside
# Devanagari (they control conjunct rendering), so they are removed from the
# Latin-script columns only.
INVISIBLE_ALL = dict.fromkeys(map(ord, "\u200b\ufeff\u00ad\u2060"), None)
INVISIBLE_LATIN = dict.fromkeys(map(ord, "\u200b\ufeff\u00ad\u2060\u200c\u200d"), None)

PUNCT_ASCII = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'", "\u2032": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"', "\u2033": '"',
    "\u2013": "-", "\u2014": "-", "\u2026": "...",
})

URL_RE = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
# Phone candidates never contain a dot and must hold 10-13 digits. Without
# those two conditions the rule masked dates (13.08.2003) and figures
# (2015-16 16.11 crore) in the real corpus.
PHONE_RE = re.compile(r"(?<![\w.])\+?\d[\d\s()-]{8,}\d(?![\w.])")
PHONE_DIGITS = (10, 13)
_WS_RE = re.compile(r"\s+")


# ------------------------------------------------------------------ ledger

class Ledger:
    def __init__(self, rows_in):
        self.rows_in = rows_in
        self.entries = []

    def add(self, rule, kind, description, affected, remaining):
        """affected: list of (row, before, after). For a transform, before and
        after are the changed cell; for a drop or flag they are None and the
        example shows the row's Hinglish text."""
        by_source = Counter(r["ref_source"] for r, _, _ in affected)
        examples = []
        for r, before, after in affected[:N_EXAMPLES]:
            ex = {"src_id": r["src_id"], "ref_source": r["ref_source"]}
            if before is None:
                ex["text"] = r["hinglish"]
            else:
                ex["before"], ex["after"] = before, after
            examples.append(ex)
        self.entries.append(OrderedDict(
            rule=rule, kind=kind, description=description, rows_affected=len(affected),
            by_source={s: by_source.get(s, 0) for s in REF_SOURCES},
            rows_remaining=remaining, examples=examples))
        mark = {"transform": "~", "drop": "-", "flag": "!"}[kind]
        print(f"  {mark} {rule:<26} {kind:<9} {len(affected):>6} rows   "
              f"(remaining {remaining:,})")


# ---------------------------------------------------------------- transforms

def _apply(rows, ledger, rule, description, fn, columns=TEXT_COLUMNS):
    affected = []
    for r in rows:
        before = {c: r[c] for c in columns}
        changed = False
        for c in columns:
            new = fn(r[c], c)
            if new != r[c]:
                r[c] = new
                changed = True
        if changed:
            first = next(c for c in columns if before[c] != r[c])
            affected.append((r, f"[{first}] {before[first]}", f"[{first}] {r[first]}"))
    ledger.add(rule, "transform", description, affected, len(rows))


def _nfc(text, _col):
    return unicodedata.normalize("NFC", text)


def _invisible(text, col):
    text = text.translate(INVISIBLE_LATIN if col in LATIN_COLUMNS else INVISIBLE_ALL)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Cc" or ch in " ")


def _punct(text, _col):
    return text.translate(PUNCT_ASCII)


def _whitespace(text, _col):
    return _WS_RE.sub(" ", text.replace("\u00a0", " ")).strip()


def _url_sub(match):
    url = match.group(0)
    trail = re.search(r"[.,;:!?)\]]+$", url)
    return "<URL>" + (trail.group(0) if trail else "")


def _pii(text, _col):
    text = URL_RE.sub(_url_sub, text)
    text = EMAIL_RE.sub("<EMAIL>", text)
    return PHONE_RE.sub(_phone_sub, text)


def _phone_sub(match):
    digits = sum(ch.isdigit() for ch in match.group(0))
    lo, hi = PHONE_DIGITS
    return "<PHONE>" if lo <= digits <= hi else match.group(0)


def parse_ratings(rows, ledger):
    """Ratings to integers on the 1-10 scale. Out-of-range or non-numeric
    values become missing (never clipped -- an 11 is not a 10). Human rows carry
    no ratings in HinGE, so an empty rating there is structural, not missing."""
    affected = []
    lo, hi = RATING_RANGE
    for r in rows:
        bad = []
        for c in ("rating1", "rating2"):
            raw = r[c].strip()
            if not raw:
                r[c] = ""
                continue
            try:
                value = float(raw)
            except ValueError:
                value = None
            if value is None or not value.is_integer() or not lo <= value <= hi:
                bad.append(f"{c}={raw}")
                r[c] = ""
            else:
                r[c] = str(int(value))
        if bad:
            affected.append((r, ", ".join(bad), "missing"))
    ledger.add("invalid_rating", "transform",
               f"ratings outside {lo}-{hi} or non-numeric set to missing (not clipped)",
               affected, len(rows))


# --------------------------------------------------------------------- drops

def _drop(rows, ledger, rule, description, predicate):
    kept, affected = [], []
    for r in rows:
        (affected if predicate(r) else kept).append(r)
    ledger.add(rule, "drop", description, [(r, None, None) for r in affected], len(kept))
    return kept


def _flag(rows, ledger, rule, description, predicate):
    affected = [(r, None, None) for r in rows if predicate(r)]
    ledger.add(rule, "flag", description, affected, len(rows))
    return [r for r, _, _ in affected]


def _len_ratio(r):
    en = len(r["english"].split())
    return len(r["hinglish"].split()) / en if en else 0.0


def drop_duplicate_pairs(rows, ledger):
    """Same (English, Hinglish) pair after normalisation. When a WAC/PAC output
    equals a human reference, the human row is the one kept."""
    priority = {s: i for i, s in enumerate(REF_SOURCES)}
    order = sorted(range(len(rows)), key=lambda i: (priority[rows[i]["ref_source"]], i))
    seen, dupes = set(), set()
    for i in order:
        key = (norm_key(rows[i]["english"]), norm_key(rows[i]["hinglish"]))
        if key in seen:
            dupes.add(i)
        seen.add(key)
    kept = [r for i, r in enumerate(rows) if i not in dupes]
    affected = [(rows[i], None, None) for i in sorted(dupes)]
    ledger.add("duplicate_pair", "drop",
               "same English+Hinglish pair after normalisation (human row kept over WAC/PAC)",
               affected, len(kept))
    return kept


# ---------------------------------------------------------------- missingness

def missing_table(rows):
    """Empty cells per column, split by reference source. Ratings on human rows
    are reported as structural: HinGE never rated human references."""
    table = OrderedDict()
    for c in COLUMNS:
        if c in ("src_id", "ref_idx"):
            continue
        per = {s: sum(1 for r in rows if r["ref_source"] == s and not str(r[c]).strip())
               for s in REF_SOURCES}
        if c in ("rating1", "rating2"):
            per = {"human (structural)": per["human"], "wac": per["wac"], "pac": per["pac"]}
        table[c] = per
    return table


# ---------------------------------------------------------------- validation

def validate(rows):
    lo, hi = RATING_RANGE
    keys = [(norm_key(r["english"]), norm_key(r["hinglish"])) for r in rows]
    checks = OrderedDict([
        ("schema: ref_source in human/wac/pac",
         all(r["ref_source"] in REF_SOURCES for r in rows)),
        ("no empty English", all(r["english"].strip() for r in rows)),
        ("no empty Hinglish", all(r["hinglish"].strip() for r in rows)),
        ("no Devanagari in Hinglish", not any(DEVANAGARI_RE.search(r["hinglish"]) for r in rows)),
        ("ratings integer in 1-10 or empty",
         all(r[c] == "" or (r[c].isdigit() and lo <= int(r[c]) <= hi)
             for r in rows for c in ("rating1", "rating2"))),
        ("human rows carry no ratings",
         all(not r["rating1"] and not r["rating2"] for r in rows if r["ref_source"] == "human")),
        ("no duplicate English+Hinglish pairs", len(keys) == len(set(keys))),
        ("no invisible characters in Latin columns",
         not any(ch in r[c] for r in rows for c in LATIN_COLUMNS for ch in "\u200b\ufeff\u200c\u200d")),
        ("no leading/trailing/double whitespace",
         all(r[c] == _whitespace(r[c], c) for r in rows for c in TEXT_COLUMNS)),
        ("length ratio within bounds",
         all(MIN_LEN_RATIO <= _len_ratio(r) <= MAX_LEN_RATIO for r in rows)),
    ])
    return checks


# ---------------------------------------------------------------------- main

def clean(rows):
    ledger = Ledger(len(rows))
    print(f"  rows in: {len(rows):,}\n")
    print("  transforms")
    _apply(rows, ledger, "unicode_nfc", "Unicode NFC normalisation", _nfc)
    _apply(rows, ledger, "invisible_chars",
           "zero-width, BOM, soft hyphen and control characters removed "
           "(ZWJ/ZWNJ kept inside Devanagari)", _invisible)
    _apply(rows, ledger, "punctuation_ascii", "curly quotes, dashes and ellipses to ASCII",
           _punct)
    _apply(rows, ledger, "pii_mask", "URLs, e-mail addresses and phone numbers masked "
           "(<URL>, <EMAIL>, <PHONE>)", _pii)
    _apply(rows, ledger, "whitespace", "whitespace collapsed and trimmed", _whitespace)
    parse_ratings(rows, ledger)

    print("\n  drops")
    rows = _drop(rows, ledger, "missing_english", "English source empty",
                 lambda r: not r["english"])
    rows = _drop(rows, ledger, "missing_hinglish", "Hinglish reference empty",
                 lambda r: not r["hinglish"])
    rows = _drop(rows, ledger, "english_not_latin",
                 "English column under 50% Latin letters (likely misaligned columns)",
                 lambda r: script_shares(r["english"])[1] < 0.5)
    rows = _drop(rows, ledger, "hinglish_has_devanagari",
                 "Hinglish reference contains Devanagari (target is Romanized)",
                 lambda r: bool(DEVANAGARI_RE.search(r["hinglish"])))
    rows = _drop(rows, ledger, "hinglish_copies_english",
                 "Hinglish reference identical to the English source (no translation)",
                 lambda r: norm_key(r["hinglish"]) == norm_key(r["english"]))
    rows = _drop(rows, ledger, "length_ratio_outlier",
                 f"Hinglish/English word ratio outside {MIN_LEN_RATIO}-{MAX_LEN_RATIO} "
                 "(truncated or misaligned)",
                 lambda r: not MIN_LEN_RATIO <= _len_ratio(r) <= MAX_LEN_RATIO)
    rows = drop_duplicate_pairs(rows, ledger)

    print("\n  flags (kept, recorded)")
    _flag(rows, ledger, "missing_hindi",
          "no Devanagari Hindi; kept for Hinglish, excluded from monolingual references",
          lambda r: not r["hindi"])
    _flag(rows, ledger, "hindi_not_devanagari", "Hindi column under 50% Devanagari letters",
          lambda r: r["hindi"] and script_shares(r["hindi"])[0] < 0.5)
    _flag(rows, ledger, "synthetic_missing_rating",
          "WAC/PAC row with at least one rating missing after parsing",
          lambda r: r["ref_source"] != "human" and not (r["rating1"] and r["rating2"]))
    return rows, ledger


def run(input_path=None, out=None, manifest=None, report_dir=None):
    input_path = Path(input_path or INTERIM_DIR / "hinge_flat.tsv")
    out = Path(out or INTERIM_DIR / "hinge_clean.tsv")
    manifest = Path(manifest or MANIFEST_DIR / "clean_manifest.json")
    report_dir = Path(report_dir or REPORT_DIR)
    if not input_path.exists():
        sys.exit(f"{rel(input_path)} not found -- run pipeline/extract.py first")

    with stage("STAGE 2: CLEANING AND VALIDATION"):
        rows = read_tsv(input_path)
        missing_before = missing_table(rows)
        sources_before = {r["src_id"] for r in rows if r["ref_source"] == "human"}
        rows, ledger = clean(rows)
        missing_after = missing_table(rows)
        sources_after = {r["src_id"] for r in rows if r["ref_source"] == "human"}
        lost = sorted(sources_before - sources_after, key=int)

        print("\n  validation gate")
        checks = validate(rows)
        for name, ok in checks.items():
            print(f"    [{'PASS' if ok else 'FAIL'}] {name}")
        if not all(checks.values()):
            sys.exit("validation failed -- nothing written")

        n = write_tsv(out, rows)
        by_source = dict(Counter(r["ref_source"] for r in rows))
        summary = OrderedDict(
            stage="clean",
            cleaned_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            input={"file": rel(input_path), "sha256": sha256_file(input_path),
                   "rows": ledger.rows_in},
            output={"file": rel(out), "sha256": sha256_file(out), "rows": n,
                    "rows_by_ref_source": by_source,
                    "unique_english": len({norm_key(r["english"]) for r in rows})},
            sources_that_lost_every_human_ref=len(lost),
            config={"min_len_ratio": MIN_LEN_RATIO, "max_len_ratio": MAX_LEN_RATIO,
                    "rating_range": list(RATING_RANGE),
                    "spelling_normalised": False, "lowercased": False,
                    "rating_filter_applied": False},
            validation={k: bool(v) for k, v in checks.items()},
        )
        # The manifest is committed, so it carries counts only; the report
        # (with before/after examples) is for the team and the datasheet.
        write_json(manifest, dict(summary, ledger=[
            {k: v for k, v in e.items() if k != "examples"} for e in ledger.entries]))
        write_json(report_dir / "cleaning_report.json", dict(
            summary, ledger=ledger.entries, missing_before=missing_before,
            missing_after=missing_after, sources_that_lost_every_human_ref_ids=lost))

        print(f"\n  rows out: {n:,} {by_source}  "
              f"({ledger.rows_in - n:,} dropped, {100 * (ledger.rows_in - n) / max(ledger.rows_in, 1):.1f}%)")
        if lost:
            print(f"  note: {len(lost)} source(s) lost every human reference: src_id {lost[:10]}")
        print(f"  wrote -> {rel(out)}   (gitignored)")
        print(f"  wrote -> {rel(manifest)}   (commit this)")
        print(f"  wrote -> {rel(report_dir / 'cleaning_report.json')}")
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", help="default data/interim/hinge_flat.tsv")
    ap.add_argument("--out", help="default data/interim/hinge_clean.tsv")
    ap.add_argument("--manifest", help="default data/processed/manifests/clean_manifest.json")
    ap.add_argument("--report-dir", help="default reports/data_pipeline/")
    a = ap.parse_args()
    run(a.input, a.out, a.manifest, a.report_dir)


if __name__ == "__main__":
    main()
