"""Data pipeline tests: each cleaning rule, the language tagger, and one full
extract -> clean -> split -> eda run over the synthetic fixture.

The fixture (tests/fixtures/hinge_fixture.csv) plants exactly one instance of
each defect, so the expected ledger counts below are hand-derived, not
snapshots of whatever the code happened to output.

Skipped, not failed, when the pipeline dependencies are missing, so the rest of
the suite still runs on a bare environment.
"""

import json
import tempfile
import unittest
from pathlib import Path

import pytest

pytest.importorskip("pandas")
pytest.importorskip("matplotlib")
pytest.importorskip("datasketch")

from pipeline import clean, extract  # noqa: E402
from pipeline.common import COLUMNS, norm_key, read_tsv  # noqa: E402
from pipeline.eda import tag_tokens  # noqa: E402
from pipeline.run_pipeline import FIXTURE, run  # noqa: E402


def row(**kw):
    base = {c: "" for c in COLUMNS}
    base.update(english="I will call you.", hinglish="Main tumhe call karunga.",
                hindi="मैं तुम्हें फोन करूंगा।", ref_source="human", src_id="0", ref_idx="0")
    base.update(kw)
    return base


class ExtractUnitTest(unittest.TestCase):
    def test_reference_list_parsing(self):
        self.assertEqual(extract.as_ref_list(["a", "b"]), ["a", "b"])
        self.assertEqual(extract.as_ref_list("['a', 'b']"), ["a", "b"])
        self.assertEqual(extract.as_ref_list("just one"), ["just one"])
        self.assertEqual(extract.as_ref_list(float("nan")), [])

    def test_literal_eval_never_executes(self):
        payload = "[__import__('os').system('echo pwned')]"
        self.assertEqual(extract.as_ref_list(payload), [payload])

    def test_columns_resolved_by_name(self):
        cols = extract.resolve_columns(["English", "Hindi", "Human-generated Hinglish (list)",
                                        "WAC", "WAC rating1", "WAC rating2",
                                        "PAC", "PAC rating1", "PAC rating2"])
        self.assertEqual(cols["human"], ["Human-generated Hinglish (list)"])
        self.assertEqual(cols["wac_r2"], "WAC rating2")

    def test_missing_column_fails_loudly(self):
        with self.assertRaises(SystemExit):
            extract.resolve_columns(["English", "Hindi", "WAC", "PAC"])


class CleanUnitTest(unittest.TestCase):
    def run_clean(self, rows):
        out, ledger = clean.clean(rows)
        return out, {e["rule"]: e["rows_affected"] for e in ledger.entries}

    def test_spelling_is_never_normalised(self):
        out, _ = self.run_clean([row(hinglish="Mujhe nhi pata kya hua.",
                                     english="I don't know what happened.")])
        self.assertEqual(out[0]["hinglish"], "Mujhe nhi pata kya hua.")

    def test_out_of_range_rating_becomes_missing_not_clipped(self):
        out, counts = self.run_clean([row(ref_source="wac", rating1="11", rating2="7")])
        self.assertEqual((out[0]["rating1"], out[0]["rating2"]), ("", "7"))
        self.assertEqual(counts["invalid_rating"], 1)

    def test_url_masked_keeping_trailing_punctuation(self):
        self.assertEqual(clean._pii("see https://x.org/a.", "english"), "see <URL>.")
        self.assertEqual(clean._pii("mail me at a.b@c.com", "english"), "mail me at <EMAIL>")

    def test_dates_and_figures_are_not_masked_as_phones(self):
        for text in ("par 13.08.2003 ko", "2015-16 16.11 crore", "between 1947 - 1950"):
            self.assertEqual(clean._pii(text, "english"), text)
        self.assertEqual(clean._pii("call +91 98765 43210 now", "english"), "call <PHONE> now")

    def test_zwnj_kept_in_devanagari_removed_in_latin(self):
        self.assertEqual(clean._invisible("a‌b", "hinglish"), "ab")
        self.assertEqual(clean._invisible("क‌ष", "hindi"), "क‌ष")

    def test_human_row_wins_duplicate_against_wac(self):
        rows = [row(ref_source="wac", rating1="5", rating2="5"), row()]
        out, counts = self.run_clean(rows)
        self.assertEqual([r["ref_source"] for r in out], ["human"])
        self.assertEqual(counts["duplicate_pair"], 1)


class TaggerTest(unittest.TestCase):
    def test_tags(self):
        tags = dict(tag_tokens("Main kal office jaunga, is Friday.",
                               "I will go to the office on Friday."))
        self.assertEqual(tags["office"], "en")
        self.assertEqual(tags["kal"], "hi")
        self.assertEqual(tags["Main"], "hi")      # homograph, Hindi "I"
        self.assertEqual(tags["is"], "hi")        # homograph, Hindi "this"
        self.assertEqual(tags["Friday"], "ne")    # capitalised mid-sentence in the source
        self.assertEqual(tags[","], "univ")

    def test_homograph_is_english_inside_english_phrase(self):
        tags = tag_tokens("Is window ko close karo, click the button",
                          "Close this window, click the button")
        self.assertEqual([t for w, t in tags if w == "the"], ["en"])
        self.assertEqual(dict(tags)["Is"], "hi")


class EndToEndFixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.w = Path(cls.tmp.name)
        run(str(FIXTURE), workdir=cls.w)
        cls.report = json.loads((cls.w / "reports" / "cleaning_report.json").read_text())
        cls.counts = {e["rule"]: e["rows_affected"] for e in cls.report["ledger"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_extraction_counts(self):
        m = json.loads((self.w / "processed" / "manifests" / "extract_manifest.json").read_text())
        self.assertEqual(m["profile"]["source_rows"], 24)
        self.assertEqual(m["profile"]["human_refs_total"], 54)
        self.assertEqual(m["profile"]["flat_rows"], 54 + 24 + 24)
        self.assertEqual(m["profile"]["duplicated_english_rows"], 1)

    def test_every_planted_defect_is_caught_once(self):
        expected = {"missing_hinglish": 1, "hinglish_has_devanagari": 1,
                    "hinglish_copies_english": 1, "length_ratio_outlier": 1,
                    "invalid_rating": 1, "invisible_chars": 1}
        for rule, n in expected.items():
            self.assertEqual(self.counts[rule], n, rule)
        # PAC row 2 and WAC rows 15 and 21 repeat a human reference
        self.assertEqual(self.counts["duplicate_pair"], 3)
        self.assertEqual(self.report["output"]["rows"], 102 - 1 - 1 - 1 - 1 - 3)
        self.assertTrue(all(self.report["validation"].values()))

    def test_splits_are_disjoint_and_exports_aligned(self):
        p = self.w / "processed"
        keys = {s: {norm_key(r["english"]) for r in read_tsv(p / f"{s}.tsv")}
                for s in ("train", "dev", "test")}
        self.assertFalse(keys["train"] & keys["dev"])
        self.assertFalse(keys["train"] & keys["test"])
        self.assertFalse(keys["dev"] & keys["test"])
        for s in ("dev", "test"):
            n = {suffix: len((p / f"{s}.{suffix}").read_text().splitlines())
                 for suffix in ("en.txt", "hinglish.txt", "hi.txt", "refs.jsonl")}
            self.assertEqual(len(set(n.values())), 1, n)

    def test_fertility_slices_written(self):
        for name in ("en", "hi_deva", "hinglish"):
            self.assertTrue((self.w / "processed" / "slices" / f"{name}.txt").read_text().strip())

    def test_few_shot_file_is_english_then_hinglish_human_only(self):
        lines = (self.w / "processed" / "train.human.tsv").read_text().splitlines()
        self.assertTrue(lines)
        for line in lines:
            en, hg = line.split("\t")
            self.assertTrue(en and hg)
            self.assertFalse(any("ऀ" <= ch <= "ॿ" for ch in hg))

    def test_eda_outputs_and_fixture_stamp(self):
        r = self.w / "reports"
        summary = json.loads((r / "eda_summary.json").read_text())
        self.assertTrue(summary["synthetic_fixture"])
        self.assertIn("SYNTHETIC", (r / "EDA_REPORT.md").read_text())
        self.assertEqual(len(list((r / "figures").glob("*.png"))), 9)
        self.assertTrue(summary["findings"])
        self.assertTrue((self.w / "interim" / "hinge_tagged.conll").stat().st_size > 0)
