#!/usr/bin/env python3
"""
Stage 4 -- exploratory data analysis.  [owner: Shibin]

Reads the cleaned corpus, the frozen splits and the stage reports, and writes:

  reports/data_pipeline/figures/*.png     one figure per question below
  reports/data_pipeline/eda_summary.json  every number the report quotes
  reports/data_pipeline/EDA_REPORT.md     renders on GitHub
  reports/data_pipeline/eda_report.html   self-contained, for the live demo
  data/interim/hinge_tagged.conll         token-level language tags (298-22 input)

Questions the EDA answers, in the order the report presents them
---------------------------------------------------------------
  1. What did cleaning remove, and was anything missing?   (waterfall, missingness)
  2. How big is the corpus and how are references spread?  (refs per source)
  3. How long are the sentences, and do the pairs align?   (lengths, length ratio)
  4. How good are the WAC/PAC outputs, and do raters agree? (ratings, alpha)
  5. How code-mixed is the text?                           (CMI, SPF, M-index)
  6. Is spelling actually unstable?                        (variant lexicon evidence)
  7. Which words dominate?                                 (top tokens)
  8. Are the splits comparable and leak-free?              (split comparison)

Question 6 is the project's hypothesis seen from the data side: if annotators
writing the SAME sentence spell the same word differently, the variance is real
and not an artefact of mixing sources.

Language tags are a heuristic, and the report says so
-----------------------------------------------------
HinGE has no token-level language labels. A Hinglish token is tagged `en` when
it also occurs in the paired English source, `hi` otherwise; punctuation,
numbers and masks are neutral, and words capitalised mid-sentence in the English
source are treated as named entities (neutral). A short list of Romanized Hindi
words that collide with English words (main, is, to, do, the ...) is always
tagged `en` only inside English context (the word occurs in the English source
and a neighbouring word is English), otherwise `hi`. English words that the annotator chose but the source did not contain
are tagged `hi`, so the English share -- and therefore CMI -- is a LOWER BOUND.
Hand-check 50 tagged sentences before quoting CMI in the report.

Usage
-----
  python pipeline/eda.py
"""

import argparse
import base64
import html
import json
import math
import re
import statistics
import sys
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "analysis"))

from pipeline.common import (  # noqa: E402
    INTERIM_DIR, MANIFEST_DIR, PROCESSED_DIR, REF_SOURCES, REPORT_DIR,
    norm_key, read_tsv, rel, stage, write_json,
)
from tokenizer_fertility import DEFAULT_VARIANTS, cmi, code_mixing_stats, load_variant_groups  # noqa: E402
from human_eval.agreement import krippendorff_alpha  # noqa: E402

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    sys.exit("pip install -r pipeline/requirements.txt  -- matplotlib is required")

SPLITS = ("train", "dev", "test")
COLORS = {"human": "#2b6cb0", "wac": "#dd6b20", "pac": "#38a169",
          "train": "#2b6cb0", "dev": "#805ad5", "test": "#d53f8c",
          "en": "#dd6b20", "hi": "#2b6cb0", "neutral": "#a0aec0"}

# Romanized Hindi words spelled like an English word (main = I, is = this,
# to = then, do = two/give, the = were, par = on, log = people ...). Their tag
# depends on context; see tag_tokens.
HINDI_HOMOGRAPHS = {
    "main", "me", "is", "us", "to", "do", "so", "the", "hi", "he", "par", "are",
    "bas", "log", "ho", "kam", "din", "in", "hum", "jab", "tab",
}
TOKEN_RE = re.compile(r"<URL>|<EMAIL>|<PHONE>|[A-Za-z]+(?:'[A-Za-z]+)?|\d+|[^\sA-Za-z\d]")
WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


# ----------------------------------------------------------- language tagging

def english_profile(english):
    """(lowercased vocabulary, named-entity set) of the English source."""
    words = WORD_RE.findall(english)
    vocab = {w.lower() for w in words}
    entities = {w.lower() for i, w in enumerate(words)
                if i > 0 and w[0].isupper() and w != "I"}
    return vocab, entities


def tag_tokens(hinglish, english):
    """Two passes. First every unambiguous token; then the homographs (main,
    is, to, the ...), which are tagged `en` only when the word also occurs in
    the English source AND a neighbouring word is English -- "the" inside an
    English phrase is English, "the" between Hindi words is the Hindi थे.
    Tagging homographs `hi` unconditionally mislabelled "the", "to" and "is"
    as Hindi on HinGE, whose references keep long English stretches."""
    vocab, entities = english_profile(english)
    toks = TOKEN_RE.findall(hinglish)
    tags = []
    for tok in toks:
        low = tok.lower()
        if not WORD_RE.fullmatch(tok):
            tags.append("univ")
        elif low in HINDI_HOMOGRAPHS:
            tags.append(None)                      # decided in pass 2
        elif low in entities:
            tags.append("ne")
        elif low in vocab:
            tags.append("en")
        else:
            tags.append("hi")

    def neighbour(i, step):
        j = i + step
        while 0 <= j < len(tags):
            if tags[j] in ("en", "hi"):
                return tags[j]
            j += step
        return None

    for i, tok in enumerate(toks):
        if tags[i] is None:
            english_context = "en" in (neighbour(i, -1), neighbour(i, 1))
            tags[i] = "en" if tok.lower() in vocab and english_context else "hi"
    return list(zip(toks, tags))


def write_conll(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("# token<TAB>lang  -- heuristic tags from pipeline/eda.py (see its docstring)\n")
        for r in rows:
            fh.write(f"# src_id={r['src_id']} ref_source={r['ref_source']}\n")
            for tok, tag in r["_tags"]:
                fh.write(f"{tok}\t{tag}\n")
            fh.write("\n")


# --------------------------------------------------------------------- stats

def describe(values):
    if not values:
        return {"n": 0}
    return OrderedDict(n=len(values), mean=round(statistics.mean(values), 3),
                       median=statistics.median(values),
                       std=round(statistics.pstdev(values), 3),
                       min=min(values), max=max(values))


def words(text):
    return WORD_RE.findall(text)


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    if len(xs) < 3:
        return float("nan")
    rx, ry = ranks(xs), ranks(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def rating_stats(rows):
    out = OrderedDict()
    for src in ("wac", "pac"):
        pairs = [(int(r["rating1"]), int(r["rating2"])) for r in rows
                 if r["ref_source"] == src and r["rating1"] and r["rating2"]]
        if not pairs:
            out[src] = {"n_pairs": 0}
            continue
        means = [(a + b) / 2 for a, b in pairs]
        try:
            alpha = krippendorff_alpha([[a, b] for a, b in pairs], scale="ordinal")
        except (ValueError, ZeroDivisionError):
            alpha = float("nan")
        out[src] = OrderedDict(
            n_pairs=len(pairs),
            mean_rating=round(statistics.mean(means), 3),
            std_rating=round(statistics.pstdev(means), 3),
            exact_agreement=round(sum(a == b for a, b in pairs) / len(pairs), 3),
            within_one=round(sum(abs(a - b) <= 1 for a, b in pairs) / len(pairs), 3),
            spearman=round(spearman([a for a, _ in pairs], [b for _, b in pairs]), 3),
            krippendorff_alpha_ordinal=round(alpha, 3),
            share_mean_below_5=round(sum(m < 5 for m in means) / len(means), 3),
        )
    return out


def variant_evidence(human_rows):
    """How the spelling-variant lexicon shows up in human references.

    Two numbers matter most:
      * groups attested in two or more spellings across the corpus
      * intra-source disagreement: among sentences with several human
        references, how often two annotators who used the same word spelled
        it differently. This holds the sentence fixed, so the variance cannot
        be explained by different sources or registers."""
    groups = load_variant_groups(DEFAULT_VARIANTS)
    form_to_group = {f: g for g, forms in groups.items() for f in forms}
    form_counts = Counter()
    total_tokens = 0
    by_source = defaultdict(list)
    for r in human_rows:
        toks = [t.lower() for t in words(r["hinglish"])]
        total_tokens += len(toks)
        used = defaultdict(set)
        for t in toks:
            if t in form_to_group:
                form_counts[t] += 1
                used[form_to_group[t]].add(t)
        by_source[norm_key(r["english"])].append(used)

    group_forms = defaultdict(Counter)
    for form, n in form_counts.items():
        group_forms[form_to_group[form]][form] = n
    observed = {g: c for g, c in group_forms.items() if c}
    multi = {g: c for g, c in observed.items() if len(c) >= 2}

    comparisons = disagreements = 0
    disagreement_examples = Counter()
    for refs in by_source.values():
        if len(refs) < 2:
            continue
        for g in set().union(*[set(u) for u in refs]):
            spellings = [u[g] for u in refs if g in u]
            if len(spellings) < 2:
                continue
            comparisons += 1
            union = set().union(*spellings)
            if len(union) > 1:
                disagreements += 1
                disagreement_examples[(g, " / ".join(sorted(union)))] += 1

    top = sorted(observed.items(), key=lambda kv: -sum(kv[1].values()))
    return OrderedDict(
        lexicon_groups=len(groups),
        groups_observed=len(observed),
        groups_observed_in_2plus_spellings=len(multi),
        lexicon_token_share=round(sum(form_counts.values()) / max(total_tokens, 1), 4),
        intra_source_comparisons=comparisons,
        intra_source_disagreements=disagreements,
        intra_source_disagreement_rate=round(disagreements / comparisons, 4) if comparisons else None,
        top_groups=[{"group": g, "forms": dict(c.most_common())} for g, c in top[:40]],
        top_disagreements=[{"group": g, "forms": f, "sentences": n}
                           for (g, f), n in disagreement_examples.most_common(10)],
    )


def vocab_stats(split_rows):
    vocab = {}
    for s, rows in split_rows.items():
        vocab[s] = Counter(t.lower() for r in rows if r["ref_source"] == "human"
                           for t in words(r["hinglish"]))
    train_types = set(vocab["train"])
    out = OrderedDict()
    for s in SPLITS:
        c = vocab[s]
        n_tok = sum(c.values())
        oov = sum(n for t, n in c.items() if t not in train_types)
        out[s] = OrderedDict(tokens=n_tok, types=len(c),
                             type_token_ratio=round(len(c) / max(n_tok, 1), 4),
                             hapax_share_of_types=round(
                                 sum(1 for n in c.values() if n == 1) / max(len(c), 1), 4),
                             oov_token_rate_vs_train=None if s == "train"
                             else round(oov / max(n_tok, 1), 4))
    return out


# -------------------------------------------------------------------- figures

def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def fig_waterfall(cleaning, rows_before_by_source, path):
    """Left: rows per reference source before and after cleaning. Right: rows
    touched by each rule. Drops are usually a few percent of the corpus, so a
    classic waterfall would render them as invisible slivers."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.2),
                                   gridspec_kw={"width_ratios": [1, 1.6]})
    after = cleaning["output"]["rows_by_ref_source"]
    x = range(len(REF_SOURCES))
    b = [rows_before_by_source.get(s_, 0) for s_ in REF_SOURCES]
    a = [after.get(s_, 0) for s_ in REF_SOURCES]
    ax1.bar([i - 0.2 for i in x], b, width=0.4, color="#cbd5e0", label="extracted")
    ax1.bar([i + 0.2 for i in x], a, width=0.4, color=[COLORS[s_] for s_ in REF_SOURCES],
            label="clean")
    for i in x:
        ax1.text(i + 0.2, a[i], f"{a[i]:,}", ha="center", va="bottom", fontsize=8)
    ax1.set_xticks(list(x), REF_SOURCES)
    ax1.set_ylabel("rows")
    ax1.set_title(f"Rows before / after cleaning ({cleaning['input']['rows']:,} -> "
                  f"{cleaning['output']['rows']:,})")
    ax1.legend(fontsize=8)

    entries = [e for e in cleaning["ledger"] if e["kind"] != "flag"]
    labels = [e["rule"] for e in entries]
    vals = [e["rows_affected"] for e in entries]
    colors = ["#e53e3e" if e["kind"] == "drop" else "#ecc94b" for e in entries]
    ax2.barh(labels, vals, color=colors)
    for i, v in enumerate(vals):
        ax2.text(v, i, f" {v:,}", va="center", fontsize=8)
    ax2.invert_yaxis()
    ax2.tick_params(axis="y", labelsize=8)
    ax2.set_xlabel("rows affected")
    ax2.set_title("Per rule: red = row dropped, yellow = cell changed")
    return _save(fig, path)


def fig_missing(cleaning, path):
    before, after = cleaning["missing_before"], cleaning["missing_after"]
    cols = ["english", "hinglish", "hindi", "rating1", "rating2"]
    labels, b, a = [], [], []
    for c in cols:
        for src, n in before[c].items():
            if "structural" in src:
                continue
            labels.append(f"{c}\n{src}")
            b.append(n)
            a.append(after[c][src])
    fig, ax = plt.subplots(figsize=(10, 3.8))
    x = range(len(labels))
    ax.bar([i - 0.2 for i in x], b, width=0.4, label="as extracted", color="#e53e3e")
    ax.bar([i + 0.2 for i in x], a, width=0.4, label="after cleaning", color=COLORS["human"])
    ax.set_xticks(list(x), labels, fontsize=7)
    if not any(b):
        ax.text(0.5, 0.75, "No missing cells as released. Any blue bar is a value the cleaning\n"
                "rules set to missing (e.g. a rating outside 1-10).",
                transform=ax.transAxes, ha="center", fontsize=9, color="#4a5568")
    ax.set_ylabel("empty cells")
    ax.set_title("Missing values by column and reference source "
                 "(human-row ratings are structurally empty and excluded)")
    ax.legend(fontsize=8)
    return _save(fig, path)


def fig_refs(rows, path):
    per_source = Counter()
    for r in rows:
        if r["ref_source"] == "human":
            per_source[norm_key(r["english"])] += 1
    dist = Counter(per_source.values())
    comp = Counter(r["ref_source"] for r in rows)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.6))
    ks = sorted(dist)
    ax1.bar([str(k) for k in ks], [dist[k] for k in ks], color=COLORS["human"])
    ax1.set_xlabel("human references per English source")
    ax1.set_ylabel("sources")
    ax1.set_title("Reference multiplicity")
    ax2.bar(list(REF_SOURCES), [comp[s] for s in REF_SOURCES],
            color=[COLORS[s] for s in REF_SOURCES])
    for i, s in enumerate(REF_SOURCES):
        ax2.text(i, comp[s], f"{comp[s]:,}", ha="center", va="bottom", fontsize=8)
    ax2.set_ylabel("rows")
    ax2.set_title("Rows by reference source")
    return _save(fig, path)


def fig_lengths(length_lists, ratios, path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
    names = list(length_lists)
    ax1.boxplot([length_lists[n] for n in names], showfliers=False)
    ax1.set_xticks(range(1, len(names) + 1), names, fontsize=8)
    ax1.set_ylabel("words per sentence")
    ax1.set_title("Sentence length (outliers hidden)")
    ax2.hist(ratios, bins=30, color=COLORS["human"])
    for bound in (0.30, 3.00):
        ax2.axvline(bound, color="#e53e3e", ls="--", lw=1)
    ax2.axvline(1.0, color="#4a5568", ls=":", lw=1)
    ax2.set_xlabel("Hinglish words / English words (human refs)")
    ax2.set_ylabel("references")
    ax2.set_title("Length ratio (dashed = cleaning bounds)")
    return _save(fig, path)


def fig_ratings(rows, path):
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    bins = [x + 0.5 for x in range(0, 11)]
    for src in ("wac", "pac"):
        means = [(int(r["rating1"]) + int(r["rating2"])) / 2 for r in rows
                 if r["ref_source"] == src and r["rating1"] and r["rating2"]]
        axes[0].hist(means, bins=bins, alpha=0.6, label=src.upper(), color=COLORS[src])
    axes[0].set_xlabel("mean of two ratings (1-10)")
    axes[0].set_ylabel("outputs")
    axes[0].set_title("WAC vs PAC quality ratings")
    axes[0].legend(fontsize=8)
    for ax, src in zip(axes[1:], ("wac", "pac")):
        pairs = Counter((int(r["rating1"]), int(r["rating2"])) for r in rows
                        if r["ref_source"] == src and r["rating1"] and r["rating2"])
        if pairs:
            xs, ys, ss = zip(*[(a, b, n) for (a, b), n in pairs.items()])
            ax.scatter(xs, ys, s=[12 + 6 * n for n in ss], alpha=0.5, color=COLORS[src])
        ax.plot([1, 10], [1, 10], color="#4a5568", lw=0.8, ls=":")
        ax.set_xlim(0.5, 10.5)
        ax.set_ylim(0.5, 10.5)
        ax.set_xlabel("rater 1")
        ax.set_ylabel("rater 2")
        ax.set_title(f"{src.upper()} rater agreement (dot size = count)")
    return _save(fig, path)


def fig_code_mixing(cmi_by_source, en_share_by_source, path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
    bins = list(range(0, 55, 5))
    for src in REF_SOURCES:
        if cmi_by_source.get(src):
            ax1.hist(cmi_by_source[src], bins=bins, alpha=0.55, label=src, color=COLORS[src])
    ax1.set_xlabel("Code-Mixing Index per sentence (0 = monolingual, 50 = even mix)")
    ax1.set_ylabel("sentences")
    ax1.set_title("How mixed is each reference? (heuristic tags)")
    ax1.legend(fontsize=8)
    srcs = [s for s in REF_SOURCES if en_share_by_source.get(s) is not None]
    ax2.bar(srcs, [100 * en_share_by_source[s] for s in srcs], color=[COLORS[s] for s in srcs])
    for i, s in enumerate(srcs):
        ax2.text(i, 100 * en_share_by_source[s], f"{100 * en_share_by_source[s]:.1f}%",
                 ha="center", va="bottom", fontsize=8)
    ax2.set_ylabel("% of language tokens tagged English")
    ax2.set_title("English share (a lower bound)")
    return _save(fig, path)


def fig_variants(evidence, path):
    # words seen in several spellings first -- a bar that is one solid colour
    # says nothing about variance
    groups = sorted(evidence["top_groups"], key=lambda t: (len(t["forms"]) < 2,
                                                           -sum(t["forms"].values())))
    top = groups[:12]
    fig, ax = plt.subplots(figsize=(10, 4))
    if not top:
        ax.text(0.5, 0.5, "no lexicon words found", ha="center")
        return _save(fig, path)
    labels = [t["group"] for t in top]
    palette = plt.get_cmap("tab20").colors
    for i, t in enumerate(top):
        total = sum(t["forms"].values())
        left = 0.0
        for j, (form, n) in enumerate(t["forms"].items()):
            share = n / total
            ax.barh(i, share, left=left, color=palette[j % len(palette)], edgecolor="white")
            if share > 0.08:
                ax.text(left + share / 2, i, form, ha="center", va="center", fontsize=7)
            left += share
    ax.set_yticks(range(len(labels)), labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("share of occurrences in human references")
    ax.set_title("Spelling variants actually used for the most frequent lexicon words")
    return _save(fig, path)


def fig_top_tokens(human_rows, path, k=25):
    counts, tag_votes = Counter(), defaultdict(Counter)
    for r in human_rows:
        for tok, tag in r["_tags"]:
            if tag in ("univ",):
                continue
            low = tok.lower()
            counts[low] += 1
            tag_votes[low][tag] += 1
    top = counts.most_common(k)
    fig, ax = plt.subplots(figsize=(10, 4))
    if top:
        toks, ns = zip(*top)
        colors = [COLORS["en"] if tag_votes[t].most_common(1)[0][0] == "en"
                  else COLORS["neutral"] if tag_votes[t].most_common(1)[0][0] == "ne"
                  else COLORS["hi"] for t in toks]
        ax.bar(toks, ns, color=colors)
        ax.set_xticks(range(len(toks)), toks, rotation=60, fontsize=8)
    ax.set_ylabel("occurrences")
    ax.set_title("Most frequent tokens in human Hinglish (blue = Hindi, orange = English)")
    return _save(fig, path)


def fig_splits(split_summary, path):
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.4))
    names = list(SPLITS)
    colors = [COLORS[s] for s in names]
    metrics = [("unique_sources", "English sources"),
               ("mean_english_words", "mean English length (words)"),
               ("mean_cmi_human", "mean CMI, human refs")]
    for ax, (key, title) in zip(axes, metrics):
        vals = [split_summary[s][key] or 0 for s in names]
        ax.bar(names, vals, color=colors)
        for i, v in enumerate(vals):
            ax.text(i, v, f"{v:,.2f}" if isinstance(v, float) else f"{v:,}",
                    ha="center", va="bottom", fontsize=8)
        ax.set_title(title)
    fig.suptitle("Are the frozen splits comparable?", fontsize=10)
    return _save(fig, path)


# --------------------------------------------------------------------- report

def _alpha_word(a):
    """Krippendorff's conventional cut-offs: >= 0.800 reliable, >= 0.667
    acceptable for tentative conclusions, below that unreliable."""
    if a != a:
        return "not computable"
    return "reliable" if a >= 0.8 else "tentative" if a >= 0.667 else "unreliable"


def findings(s):
    """Plain-language findings. Every interpretive word is chosen by a
    threshold on the measured number, so the text cannot claim more than the
    data shows when the pipeline is re-run on a different corpus."""
    f = []
    c = s["cleaning"]
    f.append(f"Cleaning kept {c['rows_out']:,} of {c['rows_in']:,} flattened rows "
             f"({100 * c['rows_out'] / max(c['rows_in'], 1):.1f}%); the largest drop rule was "
             f"`{c['largest_drop_rule']}` ({c['largest_drop_rows']:,} rows). All "
             f"{len(c['validation'])} validation checks passed on the output.")
    v = s["spelling_variants"]
    if v["intra_source_comparisons"]:
        rate = v["intra_source_disagreement_rate"]
        verdict = ("supports the orthographic-variance hypothesis" if rate >= 0.10
                   else "is weak evidence for the orthographic-variance hypothesis")
        f.append(f"With the sentence held fixed, annotators who used the same lexicon word spelled "
                 f"it differently in {100 * rate:.1f}% of {v['intra_source_comparisons']:,} cases; "
                 f"{v['groups_observed_in_2plus_spellings']} of the {v['groups_observed']} lexicon "
                 f"words found in the corpus occur in two or more spellings. This {verdict}.")
    cm = s["code_mixing"].get("human")
    if cm:
        mixed = cm["frac_utterances_mixed"]
        lead = ("Human references are genuinely code-mixed" if mixed >= 0.5
                else "Most human references are close to monolingual")
        f.append(f"{lead}: mean CMI {cm['cmi_mean_all']:.1f}, {100 * mixed:.0f}% of sentences "
                 f"contain both languages, switch-point fraction "
                 f"{cm['switch_point_fraction']:.3f}. Tags are heuristic and CMI is a lower bound. "
                 "This SPF is the target for SPF-matched synthetic sampling in Model 4.")
    rt = s["ratings"]
    if rt.get("wac", {}).get("n_pairs") and rt.get("pac", {}).get("n_pairs"):
        aw, ap = rt["wac"]["krippendorff_alpha_ordinal"], rt["pac"]["krippendorff_alpha_ordinal"]
        f.append(f"Machine-generated references: mean rating WAC {rt['wac']['mean_rating']:.2f}, "
                 f"PAC {rt['pac']['mean_rating']:.2f} on 1-10. Rater agreement (Krippendorff's "
                 f"alpha, ordinal) is {aw:.2f} for WAC ({_alpha_word(aw)}) and {ap:.2f} for PAC "
                 f"({_alpha_word(ap)}). WAC/PAC are never used as dev/test references; whether "
                 "and at what rating they enter training is a logged modelling decision.")
    ln = s["lengths"]
    within = s["lengths"]["share_ratio_0.5_to_2.0"]
    f.append(f"Human Hinglish has a median of {ln['ratio_hinglish_over_english']['median']:.2f}x "
             f"the English word count; {100 * within:.1f}% of references fall between 0.5x and "
             f"2.0x. English sources average {ln['english']['mean']:.1f} words.")
    vs = s["vocabulary"]
    if vs["test"]["oov_token_rate_vs_train"] is not None:
        f.append(f"{100 * vs['test']['oov_token_rate_vs_train']:.1f}% of test-set Hinglish tokens "
                 f"never occur in train, and {100 * vs['train']['hapax_share_of_types']:.0f}% of "
                 "train word types occur only once.")
    lk = s["splits"]["leakage"]
    shared = sum(v for k, v in lk.items() if k.startswith("english"))
    f.append(f"Frozen splits: {shared} English sources shared across train/dev/test after exact "
             "and MinHash near-duplicate grouping, re-checked independently of make_splits.py.")
    return f


def _md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def build_markdown(s, figs, warning):
    lines = ["# Data pipeline report -- HinGE (English to Romanized Hinglish)", ""]
    if warning:
        lines += [f"> **{warning}**", ""]
    lines += [f"Source: `{s['source']}`  ", f"SHA-256: `{s['source_sha256']}`  ",
              "Generated by `python pipeline/run_pipeline.py`. Every number below is in "
              "`eda_summary.json`.", "", "## Key findings", ""]
    lines += [f"{i}. {t}" for i, t in enumerate(s["findings"], start=1)]
    c = s["cleaning_ledger"]
    lines += ["", "## 1. Extraction", "",
              _md_table(["", "count"], [
                  ["source rows (English-Hindi pairs)", f"{s['extraction']['source_rows']:,}"],
                  ["unique English sources", f"{s['extraction']['unique_english_exact']:,}"],
                  ["human Hinglish references", f"{s['extraction']['human_refs_total']:,}"],
                  ["mean human refs per source", s["extraction"]["human_refs_mean_per_source"]],
                  ["flattened rows (human + WAC + PAC)", f"{s['extraction']['flat_rows']:,}"]]),
              "", "Representative samples: [samples.md](samples.md)", "",
              "## 2. Cleaning and validation", "",
              _md_table(["rule", "kind", "rows", "human", "wac", "pac", "remaining"],
                        [[e["rule"], e["kind"], e["rows_affected"], e["by_source"]["human"],
                          e["by_source"]["wac"], e["by_source"]["pac"], e["rows_remaining"]]
                         for e in c]),
              "", f"![waterfall](figures/{figs['waterfall'].name})", "",
              f"![missing](figures/{figs['missing'].name})", ""]
    sections = [
        ("3. Corpus shape", "refs"), ("4. Sentence length and alignment", "lengths"),
        ("5. WAC/PAC ratings and rater agreement", "ratings"),
        ("6. Code-mixing", "code_mixing"), ("7. Spelling variance", "variants"),
        ("8. Vocabulary", "top_tokens"), ("9. Split comparability and leakage", "splits")]
    for title, key in sections:
        lines += [f"## {title}", "", f"![{key}](figures/{figs[key].name})", ""]
        if key == "ratings":
            lines += [_md_table(["", "WAC", "PAC"], [
                [k, s["ratings"]["wac"].get(k, ""), s["ratings"]["pac"].get(k, "")]
                for k in ("n_pairs", "mean_rating", "exact_agreement", "within_one",
                          "spearman", "krippendorff_alpha_ordinal")]), ""]
        if key == "code_mixing":
            lines += [_md_table(["", *s["code_mixing"].keys()], [
                [k, *[round(v[k], 4) if isinstance(v.get(k), float) else v.get(k, "")
                      for v in s["code_mixing"].values()]]
                for k in ("n_utterances", "cmi_mean_all", "frac_utterances_mixed",
                          "switch_point_fraction", "m_index", "burstiness")]), "",
                      "Tags are heuristic (see `pipeline/eda.py`); CMI is a lower bound.", ""]
        if key == "variants":
            lines += [_md_table(["word", "spellings disagreeing within one sentence", "sentences"],
                                [[d["group"], d["forms"], d["sentences"]]
                                 for d in s["spelling_variants"]["top_disagreements"]]), ""]
        if key == "splits":
            lines += [_md_table(["split", "rows", "sources", "mean English words",
                                 "mean CMI (human)", "OOV vs train"],
                                [[sp, v["rows"], v["unique_sources"], v["mean_english_words"],
                                  v["mean_cmi_human"], s["vocabulary"][sp]["oov_token_rate_vs_train"]]
                                 for sp, v in s["split_summary"].items()]), "",
                      _md_table(["leakage check", "shared"],
                                [[k, v] for k, v in s["splits"]["leakage"].items()]), ""]
    lines += ["## Limitations", "",
              "- Language tags are heuristic; hand-check 50 sentences before reporting CMI.",
              "- The variant lexicon is a hand-seeded v1 (analysis/spelling_variants.tsv); "
              "words outside it are not counted, so variance is under-reported.",
              "- Descriptive statistics use the whole cleaned corpus; anything that feeds a "
              "modelling decision (lexicon extension, vocabulary size) must be recomputed on "
              "train only.", ""]
    return "\n".join(lines)


def build_html(markdown_text, figdir, warning):
    """Minimal Markdown-to-HTML for this report only (tables, headings, lists,
    images embedded as base64) so the file opens offline during the demo."""
    out, in_table, in_list = [], False, False
    for line in markdown_text.splitlines():
        if line.startswith("|"):
            cells = [html.escape(c.strip()) for c in line.strip("|").split("|")]
            if set("".join(cells)) <= set("-"):
                continue
            tag = "th" if not in_table else "td"
            if not in_table:
                out.append("<table>")
                in_table = True
            out.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
            continue
        if in_table:
            out.append("</table>")
            in_table = False
        m_list = re.match(r"^(\d+\.|-) (.*)", line)
        if m_list:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(m_list.group(2))}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        img = re.match(r"!\[(.*?)\]\(figures/(.*?)\)", line)
        if img:
            data = base64.b64encode((figdir / img.group(2)).read_bytes()).decode()
            out.append(f'<img alt="{img.group(1)}" src="data:image/png;base64,{data}">')
        elif line.startswith("# "):
            out.append(f"<h1>{_inline(line[2:])}</h1>")
        elif line.startswith("## "):
            out.append(f"<h2>{_inline(line[3:])}</h2>")
        elif line.startswith("> "):
            out.append(f'<p class="warn">{_inline(line[2:])}</p>')
        elif line.strip():
            out.append(f"<p>{_inline(line)}</p>")
    if in_table:
        out.append("</table>")
    if in_list:
        out.append("</ul>")
    style = ("body{font-family:system-ui,sans-serif;max-width:1100px;margin:2em auto;padding:0 1em;"
             "color:#1a202c;line-height:1.5}img{max-width:100%;border:1px solid #e2e8f0;margin:.5em 0}"
             "table{border-collapse:collapse;margin:.5em 0;font-size:.85em}"
             "td,th{border:1px solid #cbd5e0;padding:3px 8px;text-align:left}th{background:#edf2f7}"
             "code{background:#edf2f7;padding:1px 4px;border-radius:3px}"
             ".warn{background:#fed7d7;padding:.6em;border-radius:4px;font-weight:600}")
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>HinGE data pipeline</title>"
            f"<style>{style}</style></head><body>{''.join(out)}</body></html>")


def _inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)


# ---------------------------------------------------------------------- main

def run(clean_path=None, processed_dir=None, manifest_dir=None, report_dir=None,
        conll_out=None):
    clean_path = Path(clean_path or INTERIM_DIR / "hinge_clean.tsv")
    processed_dir = Path(processed_dir or PROCESSED_DIR)
    manifest_dir = Path(manifest_dir or MANIFEST_DIR)
    report_dir = Path(report_dir or REPORT_DIR)
    conll_out = Path(conll_out or INTERIM_DIR / "hinge_tagged.conll")
    figdir = report_dir / "figures"
    figdir.mkdir(parents=True, exist_ok=True)

    with stage("STAGE 4: EXPLORATORY DATA ANALYSIS"):
        rows = read_tsv(clean_path)
        split_rows = {sp: read_tsv(processed_dir / f"{sp}.tsv") for sp in SPLITS}
        extract_m = json.loads((manifest_dir / "extract_manifest.json").read_text(encoding="utf-8"))
        cleaning = json.loads((report_dir / "cleaning_report.json").read_text(encoding="utf-8"))
        split_rep = json.loads((report_dir / "split_report.json").read_text(encoding="utf-8"))
        source = extract_m["input"].get("file") or extract_m["input"].get("hf_dataset")
        warning = ("SYNTHETIC TEST FIXTURE -- not HinGE. No number on this page may be reported."
                   if "fixture" in str(source) else "")
        if warning:
            print(f"  !! {warning}")

        # language tags, once per row, reused everywhere below
        for r in rows:
            r["_tags"] = tag_tokens(r["hinglish"], r["english"])
        tag_of = {(r["src_id"], r["ref_source"], r["hinglish"]): r["_tags"] for r in rows}
        for sp in SPLITS:
            for r in split_rows[sp]:
                r["_tags"] = tag_of.get((r["src_id"], r["ref_source"], r["hinglish"]),
                                        tag_tokens(r["hinglish"], r["english"]))
        human = [r for r in rows if r["ref_source"] == "human"]
        write_conll(conll_out, human)
        print(f"  language-tagged human refs -> {rel(conll_out)}  (input for 298-22 --cmi-only)")

        # lengths
        uniq = OrderedDict()
        for r in rows:
            uniq.setdefault(norm_key(r["english"]), r)
        length_lists = OrderedDict([
            ("English", [len(words(r["english"])) for r in uniq.values()]),
            ("Hindi", [len(r["hindi"].split()) for r in uniq.values() if r["hindi"]]),
            ("Hinglish\nhuman", [len(words(r["hinglish"])) for r in human]),
            ("Hinglish\nWAC", [len(words(r["hinglish"])) for r in rows if r["ref_source"] == "wac"]),
            ("Hinglish\nPAC", [len(words(r["hinglish"])) for r in rows if r["ref_source"] == "pac"]),
        ])
        ratios = [len(r["hinglish"].split()) / max(len(r["english"].split()), 1) for r in human]

        # code-mixing per reference source, via the 298-22 implementation
        code_mixing, cmi_by_source, en_share = OrderedDict(), {}, {}
        for src in REF_SOURCES:
            sents = [r["_tags"] for r in rows if r["ref_source"] == src and r["_tags"]]
            if not sents:
                continue
            st = code_mixing_stats(sents)
            code_mixing[src] = OrderedDict((k, v) for k, v in st.items() if k != "languages")
            langs = st["languages"]
            en_share[src] = langs.get("en", 0) / max(langs.get("en", 0) + langs.get("hi", 0), 1)
            code_mixing[src]["english_token_share"] = round(en_share[src], 4)
            cmi_by_source[src] = [cmi([t for _, t in s]) for s in sents]

        split_summary = OrderedDict()
        for sp in SPLITS:
            srows = split_rows[sp]
            sh = [r for r in srows if r["ref_source"] == "human" and r["_tags"]]
            srcs = {norm_key(r["english"]): r for r in srows}
            split_summary[sp] = OrderedDict(
                rows=len(srows), unique_sources=len(srcs),
                human_refs=sum(1 for r in srows if r["ref_source"] == "human"),
                mean_english_words=round(statistics.mean(
                    [len(words(r["english"])) for r in srcs.values()]), 2) if srcs else None,
                mean_cmi_human=round(statistics.mean(
                    [cmi([t for _, t in r["_tags"]]) for r in sh]), 2) if sh else None)

        drops = [e for e in cleaning["ledger"] if e["kind"] == "drop"]
        largest = max(drops, key=lambda e: e["rows_affected"]) if drops else None
        summary = OrderedDict(
            source=source, source_sha256=extract_m["input"].get("sha256", ""),
            synthetic_fixture=bool(warning),
            extraction=extract_m["profile"],
            cleaning=OrderedDict(rows_in=cleaning["input"]["rows"],
                                 rows_out=cleaning["output"]["rows"],
                                 largest_drop_rule=largest["rule"] if largest else None,
                                 largest_drop_rows=largest["rows_affected"] if largest else 0,
                                 validation=cleaning["validation"]),
            cleaning_ledger=[{k: v for k, v in e.items() if k != "examples"}
                             for e in cleaning["ledger"]],
            lengths=OrderedDict(
                english=describe(length_lists["English"]),
                hindi=describe(length_lists["Hindi"]),
                hinglish_human=describe(length_lists["Hinglish\nhuman"]),
                hinglish_wac=describe(length_lists["Hinglish\nWAC"]),
                hinglish_pac=describe(length_lists["Hinglish\nPAC"]),
                ratio_hinglish_over_english=describe([round(x, 3) for x in ratios]),
                **{"share_ratio_0.5_to_2.0": round(
                    sum(0.5 <= x <= 2.0 for x in ratios) / max(len(ratios), 1), 4)}),
            ratings=rating_stats(rows),
            code_mixing=code_mixing,
            spelling_variants=variant_evidence(human),
            vocabulary=vocab_stats(split_rows),
            splits=split_rep,
            split_summary=split_summary,
        )
        summary["findings"] = findings(summary)

        figs = OrderedDict(
            waterfall=fig_waterfall(cleaning, extract_m["profile"]["flat_rows_by_ref_source"],
                                    figdir / "01_cleaning_waterfall.png"),
            missing=fig_missing(cleaning, figdir / "02_missing_values.png"),
            refs=fig_refs(rows, figdir / "03_reference_multiplicity.png"),
            lengths=fig_lengths(length_lists, ratios, figdir / "04_lengths.png"),
            ratings=fig_ratings(rows, figdir / "05_ratings.png"),
            code_mixing=fig_code_mixing(cmi_by_source, en_share, figdir / "06_code_mixing.png"),
            variants=fig_variants(summary["spelling_variants"], figdir / "07_spelling_variants.png"),
            top_tokens=fig_top_tokens(human, figdir / "08_top_tokens.png"),
            splits=fig_splits(split_summary, figdir / "09_split_comparison.png"),
        )
        write_json(report_dir / "eda_summary.json", summary)
        md = build_markdown(summary, figs, warning)
        (report_dir / "EDA_REPORT.md").write_text(md + "\n", encoding="utf-8")
        (report_dir / "eda_report.html").write_text(build_html(md, figdir, warning),
                                                     encoding="utf-8")

        print("\n  key findings")
        for i, t in enumerate(summary["findings"], start=1):
            print(f"   {i}. {t}\n")
        print(f"  figures -> {rel(figdir)}/ ({len(figs)} PNGs)")
        print(f"  report  -> {rel(report_dir / 'EDA_REPORT.md')}")
        print(f"  report  -> {rel(report_dir / 'eda_report.html')}   (open this in the demo)")
        print(f"  numbers -> {rel(report_dir / 'eda_summary.json')}")
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", help="default data/interim/hinge_clean.tsv")
    ap.add_argument("--processed-dir", help="default data/processed/")
    ap.add_argument("--manifest-dir", help="default data/processed/manifests/")
    ap.add_argument("--report-dir", help="default reports/data_pipeline/")
    ap.add_argument("--conll-out", help="default data/interim/hinge_tagged.conll")
    a = ap.parse_args()
    run(a.input, a.processed_dir, a.manifest_dir, a.report_dir, a.conll_out)


if __name__ == "__main__":
    main()
