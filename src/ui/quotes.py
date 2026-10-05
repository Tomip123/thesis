import markdown
import streamlit as st
import streamlit.components.v1 as components

from src.ui.matching import find_quote_match

_QUOTE_CSS = """
<style>
    .legal-container {
        height: 450px;
        overflow-y: auto;
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 40px;
        border-radius: 8px;
        font-family: 'Georgia', 'Times New Roman', serif;
        font-size: 16px;
        line-height: 1.7;
        background-color: var(--background-color, #fdfdfd);
        color: var(--text-color, #2c3e50);
        box-shadow: inset 0 0 10px rgba(0,0,0,0.02);
    }
    .legal-highlight {
        background-color: #ffd900;
        color: #000;
        padding: 2px 0;
        border-radius: 2px;
        font-weight: 500;
        box-shadow: 0 0 4px rgba(255, 217, 0, 0.4);
    }
    @media (prefers-color-scheme: dark) {
        .legal-container { background-color: #1e1e1e; color: #e0e0e0; }
        .legal-highlight { background-color: #9b7d00; color: #fff; }
    }
    blockquote {
        border-left: 3px solid #ccc;
        margin-left: 0;
        padding-left: 20px;
        font-style: italic;
        color: #666;
    }
</style>
"""


def _locate_quotes(full_text, quotes):
    matches, unmatched = [], []
    for q in quotes:
        loc = find_quote_match(full_text, q)
        if loc:
            matches.append({"start": loc[0], "end": loc[1], "original_quote": q})
        else:
            unmatched.append(q)
    matches.sort(key=lambda m: m["start"])
    return matches, unmatched


def _group_nearby(matches, merge_distance):
    if not matches:
        return []
    groups = [[matches[0]]]
    for m in matches[1:]:
        if m["start"] - groups[-1][-1]["end"] <= merge_distance:
            groups[-1].append(m)
        else:
            groups.append([m])
    return groups


def _snap_to_boundary(text, start_target, end_target):
    s = text.rfind("\n\n", 0, start_target)
    if s == -1:
        s = text.rfind(". ", 0, start_target)
    start = s + 2 if s != -1 else 0

    e = text.find("\n\n", end_target)
    if e == -1:
        e = text.find(". ", end_target)
    end = e + 1 if e != -1 else len(text)
    return start, end


def _highlighted_html(window_text, relative_matches, block_index):
    marked = ""
    cursor = 0
    for r_start, r_end, match_idx in relative_matches:
        if r_start > cursor:
            marked += window_text[cursor:r_start]
        if r_end > cursor:
            segment = window_text[max(r_start, cursor):r_end]
            marked += f'<mark class="legal-highlight" id="highlight-{block_index}-{match_idx}">{segment}</mark>'
            cursor = r_end
    if cursor < len(window_text):
        marked += window_text[cursor:]
    return markdown.markdown(marked, extensions=["extra", "nl2br"]), f"highlight-{block_index}-0"


def _render_block(full_text, group, block_index, context_chars):
    st.markdown(f"#### 🔍 Legal Analysis View: Block {block_index + 1}")
    unique_quotes = len({m["original_quote"] for m in group})
    st.caption(f"📍 Contains evidence for **{unique_quotes}** extracted quote{'s' if unique_quotes > 1 else ''}")

    raw_start = max(0, group[0]["start"] - context_chars)
    raw_end = min(len(full_text), group[-1]["end"] + context_chars)
    window_start, window_end = _snap_to_boundary(full_text, raw_start, raw_end)
    window_text = full_text[window_start:window_end]

    relative_matches = [
        (m["start"] - window_start, m["end"] - window_start, idx)
        for idx, m in enumerate(group)
        if 0 <= m["start"] - window_start and m["end"] - window_start <= len(window_text)
    ]

    html_content, first_id = _highlighted_html(window_text, relative_matches, block_index)
    components.html(
        f"""
        {_QUOTE_CSS}
        <div class="legal-container">{html_content}</div>
        <script>
            setTimeout(function() {{
                var el = document.getElementById('{first_id}');
                if (el) el.scrollIntoView({{behavior: "smooth", block: "center"}});
            }}, 800);
        </script>
        """,
        height=480,
    )
    st.divider()


def render_grouped_quotes(full_text, quotes, context_chars=3000, merge_distance=2000):
    if not quotes:
        st.write("No specific quotes extracted.")
        return

    matches, unmatched = _locate_quotes(full_text, quotes)
    for i, group in enumerate(_group_nearby(matches, merge_distance)):
        _render_block(full_text, group, i, context_chars)

    if unmatched:
        st.warning(f"Could not locate {len(unmatched)} quotes in the text:")
        for q in unmatched:
            st.markdown(f"> {q}")
            st.divider()
