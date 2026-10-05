import os

import streamlit as st

DATA_DIR = "data"


def scan_providers():
    if not os.path.isdir(DATA_DIR):
        st.error(f"'{DATA_DIR}' directory not found.")
        return []

    try:
        providers = [
            item for item in sorted(os.listdir(DATA_DIR))
            if os.path.isdir(os.path.join(DATA_DIR, item))
            and (os.path.isdir(os.path.join(DATA_DIR, item, "md"))
                 or os.path.isdir(os.path.join(DATA_DIR, item, "clean_md")))
        ]
    except Exception as e:
        st.error(f"Error scanning directories: {e}")
        return []
    return providers


def load_document(provider):
    clean_path = os.path.join(DATA_DIR, provider, "clean_md", "combined_all.md")
    raw_path = os.path.join(DATA_DIR, provider, "md", "combined_all.md")
    path = clean_path if os.path.exists(clean_path) else raw_path

    try:
        if not os.path.exists(path):
            st.warning(f"Combined file not found for {provider} at {path}")
            return ""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        st.error(f"Error reading document for {provider}: {e}")
        return ""
