from pathlib import Path

import streamlit as st

from src.data.storage import DB_PATH
from views.pages import navigation
from views.runtime import build_context

st.set_page_config(page_title="EU Coverage Reviewer", layout="wide")
st.title("🇪🇺 EU Regulation Coverage Reviewer")

if not Path(DB_PATH).exists():
    st.error(f"There is no `{DB_PATH}` yet. Build it from the drafts first: "
             f"`python scripts/build_reviews_db.py`")
    st.stop()

navigation(build_context()).run()
