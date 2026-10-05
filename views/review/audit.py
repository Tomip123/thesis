import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.analysis.regulation import article_label, article_number, article_sort_key
from src.data.corpus import load_document
from src.data.storage import load_objectives, verification_counts
from src.review_bundle import (
    read_corrections,
    read_unit_explanation,
    review_dir_for,
    review_progress,
    write_corrections,
)
from src.scoring import coverage_score
from src.ui.components import criterion_is_met
from src.ui.quotes import render_grouped_quotes
from views.review._assets import KEYBOARD_SHORTCUTS_JS, STICKY_FOOTER_CSS

DRAFTS_DIR = Path("output/audit_drafts")


def render(ctx):
    st.header(f"⚡ {ctx.regulation} Coverage Review")
    st.info("Verify one finding at a time; each save writes that unit's corrections file. "
            "**Keyboard:** `→` Save & Next, `←` Previous. (Ignored while typing.)")
    components.html(KEYBOARD_SHORTCUTS_JS, height=1, width=1)

    draft_path = _select_draft(ctx.regulation)
    if draft_path is None:
        return

    review_dir = review_dir_for(draft_path)
    if not review_dir.is_dir():
        st.error(f"No review bundle next to `{draft_path}` (expected `{review_dir}`). "
                 f"Regenerate it with `python scripts/run_audit.py --draft {draft_path} …`.")
        return

    results = _load_draft(draft_path)
    if results is None:
        return

    units_df = _units_frame(results, review_dir)
    if units_df.empty:
        st.warning("None of this draft's results match an objective in the codebook.")
        return

    _render_progress(results, review_dir, draft_path, ctx.regulation)

    units_df = _apply_article_filter(units_df)
    if units_df.empty:
        st.warning("No results match the selected article filter.")
        return

    mode = st.segmented_control(
        "Step through by", ["Objective", "Provider"], default="Objective", key="review_mode",
    ) or "Objective"

    items, scope_token = _objective_scope(units_df) if mode == "Objective" else _provider_scope(units_df)
    if items is None or items.empty:
        return

    _stepper(items, scope_token, review_dir)


def _select_draft(regulation):
    drafts = sorted(DRAFTS_DIR.glob("*.json")) if DRAFTS_DIR.is_dir() else []
    if not drafts:
        st.error(f"No audit drafts in `{DRAFTS_DIR}`. Generate one with "
                 f"`python scripts/run_audit.py --regulation \"{regulation}\" --providers all "
                 f"--objectives all --yes --draft {DRAFTS_DIR}/<name>.json`.")
        return None

    default = DRAFTS_DIR / f"{regulation.lower().replace(' ', '_')}_audit.json"
    names = [p.name for p in drafts]
    index = names.index(default.name) if default.name in names else 0
    chosen = st.selectbox("Draft under review", names, index=index,
                          help="The review bundle beside this file is where corrections are written.")
    return DRAFTS_DIR / chosen


def _load_draft(draft_path):
    try:
        results = json.loads(draft_path.read_text())
    except json.JSONDecodeError as e:
        st.error(f"`{draft_path}` is not valid JSON: {e}")
        return None
    if not isinstance(results, list) or not results:
        st.error(f"`{draft_path}` contains no results.")
        return None
    return results


def _units_frame(results, review_dir):
    objectives = load_objectives()
    objectives_by_id = {row["id"]: row for row in objectives.to_dict("records")} if not objectives.empty else {}

    rows = []
    for result in results:
        objective = objectives_by_id.get(result["objective_id"])
        if objective is None:
            continue
        correction = _corrections_or_none(review_dir, result)
        met = (correction or {}).get("corrected_met_criteria", result.get("met_criteria", []))
        rows.append({
            "provider": result["provider"],
            "objective_id": result["objective_id"],
            "title": objective["title"],
            "description": objective["description"],
            "source_ref": objective["source_ref"],
            "criteria": objective["criteria"],
            "met_criteria": met,
            "quotes": result.get("quotes", []),
            "reviewed": correction is not None,
            "result": result,
        })
    return pd.DataFrame(rows)


def _corrections_or_none(review_dir, result):
    try:
        return read_corrections(review_dir, result["provider"], result["objective_id"])
    except ValueError as e:
        st.warning(str(e))
        return None


def _explanation_or_none(review_dir, row):
    try:
        return read_unit_explanation(review_dir, row["provider"], row["objective_id"])
    except ValueError as e:
        st.warning(str(e))
        return None


def _render_progress(results, review_dir, draft_path, regulation):
    reviewed, total = review_progress(results, review_dir)
    st.progress(reviewed / total if total else 0.0, text=f"Reviewed: {reviewed} / {total} units")

    verified, in_db = verification_counts(regulation=regulation)
    if reviewed == total:
        st.success(f"All {total} units reviewed. Sync them with "
                   f"`python scripts/approve_audit.py {draft_path}`.")
    st.caption(f"In reviews.db for {regulation}: {verified} of {in_db} results verified "
               f"(updated when you run the sync).")


def _apply_article_filter(units_df):
    units_df = units_df.copy()
    units_df["Article"] = units_df["source_ref"].apply(article_label)
    articles = sorted(units_df["Article"].unique().tolist(), key=article_sort_key)
    selected = st.multiselect("Filter by Article (optional)", articles)
    if selected:
        units_df = units_df[units_df["Article"].isin(selected)]
    return units_df


def _objective_scope(units_df):
    options = units_df[["objective_id", "title"]].drop_duplicates()
    options["display"] = options.apply(lambda x: f"[{x['objective_id']}] {x['title']}", axis=1)
    display_map = dict(zip(options["display"], options["objective_id"]))

    chosen = st.selectbox("Select Objective", options["display"].tolist())
    if not chosen:
        return None, None
    obj_id = display_map[chosen]
    items = units_df[units_df["objective_id"] == obj_id].sort_values("provider").reset_index(drop=True)
    return items, f"obj:{obj_id}"


def _provider_scope(units_df):
    chosen = st.selectbox("Select Provider", sorted(units_df["provider"].unique().tolist()))
    if not chosen:
        return None, None
    items = units_df[units_df["provider"] == chosen].copy()
    items["_article"] = items["source_ref"].apply(lambda r: article_number(r) or 999)
    items = items.sort_values(["_article", "title"]).reset_index(drop=True)
    return items, f"prov:{chosen}"


def _stepper(items, scope_token, review_dir):
    if st.session_state.get("review_scope") != scope_token:
        st.session_state.review_scope = scope_token
        st.session_state.review_idx = 0

    total = len(items)
    idx = max(0, min(st.session_state.get("review_idx", 0), total - 1))
    st.session_state.review_idx = idx
    row = items.iloc[idx]

    st.progress((idx + 1) / total)
    st.caption(f"Reviewing {idx + 1} of {total}: **{row['provider']}** — {row['title']} "
               f"{'✅ reviewed' if row['reviewed'] else '⬜ not reviewed yet'}")

    _render_item(row)
    _render_sticky_form(row, total, review_dir)

    back, forward = st.columns(2)
    if back.button("⬅️ Previous") and idx > 0:
        st.session_state.review_idx -= 1
        st.rerun()
    if forward.button("➡️ Next (without saving)") and idx < total - 1:
        st.session_state.review_idx += 1
        st.rerun()


def _render_item(row):
    st.markdown(f"### 🏢 {row['provider']}")
    st.markdown(f"**Objective:** {row['title']}")
    st.markdown(f"**Goal:** {row['description']}")
    st.caption(f"Source: {row['source_ref']}")

    st.metric("Score", f"{coverage_score(row['met_criteria'], row['criteria'])}%",
              help="Share of the objective's criteria the contract addresses.")

    with st.expander("📜 Evidence & Context", expanded=True):
        if row["quotes"]:
            render_grouped_quotes(load_document(row["provider"]), row["quotes"])
        else:
            st.caption("No quotes were returned for this result.")

    st.divider()
    st.markdown("<div style='height: 400px;'></div>", unsafe_allow_html=True)


def _render_sticky_form(row, total, review_dir):
    with st.container():
        st.markdown(STICKY_FOOTER_CSS, unsafe_allow_html=True)

        with st.form(key=f"review_form_{row['provider']}_{row['objective_id']}"):
            c_verify, c_criteria, c_action = st.columns([2, 2, 1])
            with c_verify:
                st.caption("🤖 **Model's explanation**")
                with st.container(height=280):
                    explanation = _explanation_or_none(review_dir, row)
                    st.markdown(explanation or "_No explanation was recorded for this result._")
            with c_criteria:
                st.caption("✅ **Criteria Met** — the score follows from these")
                with st.container(height=280):
                    v_met = []
                    for c in row["criteria"]:
                        default = criterion_is_met(c, row["met_criteria"])
                        if st.checkbox(f"{'✅' if default else '❌'} {c}", value=default,
                                       key=f"chk_review_{row['provider']}_{row['objective_id']}_{c}"):
                            v_met.append(c)
            with c_action:
                st.write(" ")
                st.write(" ")
                st.write(" ")
                submitted = st.form_submit_button("✅ Save & Next", type="primary", width="stretch")

            if submitted:
                write_corrections(review_dir, row["result"], v_met)
                if st.session_state.review_idx < total - 1:
                    st.session_state.review_idx += 1
                st.rerun()
