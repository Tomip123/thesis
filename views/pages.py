import streamlit as st

from views.review import audit, codebook


def _page(render_fn, ctx, title, icon, url_path):
    return st.Page(lambda: render_fn(ctx), title=title, icon=icon, url_path=url_path)


def navigation(ctx):
    return st.navigation({
        "Human review": [
            _page(codebook.render, ctx, "Codebook review", "🎯", "codebook"),
            _page(audit.render, ctx, "Audit review", "⚡", "review"),
        ],
    })
