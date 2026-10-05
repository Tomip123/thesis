import json
from pathlib import Path

import streamlit as st

from src.analysis.regulation import article_sort_key, get_article_text
from src.codebook import criteria_count_flags, duplicate_flags
from src.data.storage import load_objectives, verification_counts
from src.review_bundle import (
    article_review_progress,
    group_objectives_by_article,
    read_article_corrections,
    review_dir_for,
    write_article_corrections,
)

DRAFTS_DIR = Path("output/objective_drafts")


def render(ctx):
    st.header("🎯 Codebook Review")
    _review_tab(ctx)


def _review_tab(ctx):
    st.subheader("Review generated objectives, one article at a time")
    st.info("Each article's `.md` in the review bundle is what the model produced; saving here "
            "records your verdict in that article's `.corrections.json`. Nothing is written to "
            "the database until you run the sync command.")

    draft_path = _select_draft(ctx.regulation)
    if draft_path is None:
        return

    review_dir = review_dir_for(draft_path)
    if not review_dir.is_dir():
        st.error(f"No review bundle next to `{draft_path}` (expected `{review_dir}`). "
                 f"Regenerate it with `python scripts/generate_objectives.py … --draft {draft_path}`.")
        return

    objectives = _load_draft(draft_path)
    if objectives is None:
        return

    regulation = objectives[0].get("regulation") or ctx.regulation
    if regulation != ctx.regulation:
        st.warning(f"This draft is **{regulation}**, while the sidebar is set to "
                   f"**{ctx.regulation}**. Reviewing it as {regulation}.")

    articles = group_objectives_by_article(objectives)
    refs = sorted(articles, key=article_sort_key)
    _render_review_progress(objectives, review_dir, draft_path, regulation)
    _article_stepper(regulation, refs, articles, review_dir, draft_path)


def _select_draft(regulation):
    drafts = sorted(DRAFTS_DIR.glob("*.json")) if DRAFTS_DIR.is_dir() else []
    if not drafts:
        st.error(f"No objective drafts in `{DRAFTS_DIR}`. Generate one with "
                 f"`python scripts/generate_objectives.py --regulation \"{regulation}\" "
                 f"--articles … --draft {DRAFTS_DIR}/<name>.json`.")
        return None

    names = [p.name for p in drafts]
    slug = regulation.lower().replace(" ", "_")
    default = next((n for n in names if n.startswith(slug)), names[0])
    chosen = st.selectbox("Draft under review", names, index=names.index(default),
                          help="The review bundle beside this file is where corrections are written.")
    return DRAFTS_DIR / chosen


def _load_draft(draft_path):
    try:
        objectives = json.loads(draft_path.read_text())
    except json.JSONDecodeError as e:
        st.error(f"`{draft_path}` is not valid JSON: {e}")
        return None
    if not isinstance(objectives, list) or not objectives:
        st.error(f"`{draft_path}` contains no objectives.")
        return None
    return objectives


def _render_review_progress(objectives, review_dir, draft_path, regulation):
    reviewed, total = article_review_progress(objectives, review_dir)
    st.progress(reviewed / total if total else 0.0, text=f"Reviewed: {reviewed} / {total} articles")
    if reviewed == total:
        st.success(f"All {total} articles reviewed. Sync them with "
                   f"`python scripts/approve_objectives.py {draft_path}`.")
    verified, in_db = verification_counts(regulation=regulation, table="compliance_objectives")
    st.caption(f"In reviews.db for {regulation}: {verified} of {in_db} objectives verified "
               f"(updated when you run the sync).")


def _article_stepper(regulation, refs, articles, review_dir, draft_path):
    scope_token = f"codebook:{draft_path}"
    if st.session_state.get("codebook_review_scope") != scope_token:
        st.session_state.codebook_review_scope = scope_token
        st.session_state.codebook_review_idx = 0

    total = len(refs)
    idx = max(0, min(st.session_state.get("codebook_review_idx", 0), total - 1))
    st.session_state.codebook_review_idx = idx
    ref = refs[idx]

    correction = _corrections_or_none(review_dir, ref)
    generated = articles[ref]
    current = correction["objectives"] if correction else generated

    st.progress((idx + 1) / total)
    st.caption(f"Reviewing article {idx + 1} of {total}: **{ref}** — {len(generated)} generated "
               f"{'✅ reviewed' if correction is not None else '⬜ not reviewed yet'}")

    _render_article_context(regulation, ref, generated)
    _render_article_form(regulation, ref, current, generated, review_dir, draft_path, total)

    back, forward = st.columns(2)
    if back.button("⬅️ Previous article") and idx > 0:
        st.session_state.codebook_review_idx -= 1
        st.rerun()
    if forward.button("➡️ Next article (without saving)") and idx < total - 1:
        st.session_state.codebook_review_idx += 1
        st.rerun()


def _corrections_or_none(review_dir, ref):
    try:
        return read_article_corrections(review_dir, ref)
    except ValueError as e:
        st.warning(str(e))
        return None


def _render_article_context(regulation, ref, generated):
    with st.expander(f"📜 {ref} — full text", expanded=False):
        st.text(get_article_text(ref, regulation=regulation) or "(article text not found)")

    existing_df = load_objectives(regulation=regulation)
    existing = existing_df[["title", "description"]].to_dict("records") if not existing_df.empty else []
    flags = duplicate_flags(generated, existing)
    counts = criteria_count_flags(generated)
    if flags:
        st.warning("Possible duplicates: " + "; ".join(
            f"*{c['title']}* ≈ *{m['title']}* ({score:.2f})" for c, m, score in flags))
    if counts:
        st.warning("Unusual criteria count (aim for 3-6): " + ", ".join(
            f"*{o['title']}* ({n})" for o, n in counts))

    if existing:
        with st.expander(f"🗂️ Existing {regulation} objectives — check for semantic overlap"):
            for row in existing:
                st.caption(f"• **{row['title']}** — {row['description']}")


def _render_article_form(regulation, ref, current, generated, review_dir, draft_path, total):
    scope = f"{draft_path.stem}_{ref}"
    nonce = st.session_state.get(f"codebook_gen_{scope}", 0)

    extra = st.number_input("Add blank objectives", min_value=0, max_value=5, value=0,
                            key=f"codebook_extra_{scope}_{nonce}",
                            help="Room to add an objective the model missed.")

    with st.form(key=f"codebook_review_form_{scope}_{nonce}"):
        reviewed = []
        for i, objective in enumerate(current):
            reviewed.append(_objective_fields(f"{scope}_{nonce}", i, objective, regulation))
            st.divider()
        for i in range(int(extra)):
            reviewed.append(_objective_fields(f"{scope}_{nonce}", len(current) + i, None,
                                              regulation, default_source_ref=ref))

        if st.form_submit_button("✅ Save & Next article", type="primary"):
            kept = [o for o in reviewed if o is not None]
            dropped = len(reviewed) - len(kept)
            write_article_corrections(review_dir, ref, kept, generated)
            st.session_state[f"codebook_gen_{scope}"] = nonce + 1
            st.toast(f"Recorded {len(kept)} objective(s) for {ref}"
                     + (f", {dropped} dropped" if dropped else ""))
            if st.session_state.codebook_review_idx < total - 1:
                st.session_state.codebook_review_idx += 1
            st.rerun()


def _objective_fields(scope, i, objective, regulation, default_source_ref=""):
    objective = objective or {}
    key = f"codebook_obj_{scope}_{i}"
    if objective and st.checkbox("🗑️ Drop this objective", key=f"{key}_drop"):
        st.caption(f"~~{objective.get('title', '')}~~")
        return None

    title = st.text_input("Title", value=objective.get("title", ""), key=f"{key}_title")
    description = st.text_area("Description", value=objective.get("description", ""),
                               height=68, key=f"{key}_desc")
    criteria_text = st.text_area("Criteria — one per line",
                                 value="\n".join(objective.get("criteria", [])),
                                 height=120, key=f"{key}_criteria")
    source_ref = st.text_input("Source", value=objective.get("source_ref", default_source_ref),
                               key=f"{key}_src")

    if not title.strip():
        return None
    return {
        "title": title.strip(),
        "description": description.strip(),
        "criteria": [c.strip() for c in criteria_text.splitlines() if c.strip()],
        "source_ref": source_ref.strip(),
        "regulation": objective.get("regulation") or regulation,
    }
