import streamlit as st

from views.context import Context


def build_context() -> Context:
    st.sidebar.header("Settings")
    regulation = st.sidebar.selectbox(
        "Target Regulation", ["EU Data Act", "GDPR", "NIS2"],
        help="The regulation every screen is scoped to.",
    )
    return Context(regulation=regulation)
