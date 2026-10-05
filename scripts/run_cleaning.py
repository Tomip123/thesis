#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

from src.llm.cleaning import clean_all_providers

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        sys.exit("Set OPENROUTER_API_KEY (e.g. in .env) first.")
    clean_all_providers(api_key=api_key, provider_name=sys.argv[1] if len(sys.argv) > 1 else None)
