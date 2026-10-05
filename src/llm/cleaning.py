import glob
import json
import logging
import os
import re

from openai import OpenAI

from src.data.corpus import DATA_DIR


class LLMCleaner:
    def __init__(self, api_key, model="google/gemini-3.8-flash"):
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        self.model = model

    def clean(self, raw_content):
        if not raw_content or len(raw_content) < 200: 
            return raw_content
        
        def robust_find(full_text, anchor, from_end=False):
            if not anchor: return -1
            idx = full_text.rfind(anchor) if from_end else full_text.find(anchor)
            if idx != -1: return idx
            
            def normalize(t):
                t = re.sub(r'[#*_\[\]\(\)]', '', t)
                return " ".join(t.split()).lower()
            
            norm_anchor = normalize(anchor)
            if not norm_anchor: return -1
            
            words = anchor.split()
            if len(words) > 3:
                sub_anchor = " ".join(words[:3])
                idx = full_text.rfind(sub_anchor) if from_end else full_text.find(sub_anchor)
                if idx != -1: return idx
            return -1

        try:
            system_prompt = """
            Role: You are a high-precision Content Extraction Engine.
            Objective: Isolate the 'Semantic Core' of a document.
            
            **Surgical Instructions:**
            1. Identify the 'Content Entry Point': Locate the absolute FIRST line where the actual article or contract begins.
               - IMPORTANT: If the document is already 'clean' and starts with the title or content, return the VERY FIRST LINE of the text.
            2. Identify the 'Footer Gateway': Locate the absolute FIRST line where the website's global footer or directory begins (e.g., 'Learn', 'Resources', 'Contact Us').
               - IMPORTANT: If the document ends with relevant content and has NO website footer, return 'END_OF_DOCUMENT'.
            3. Extraction Rule: Discard only what is clearly website infrastructure. If in doubt, keep the text.
            """

            user_prompt = f"""
            Analyze this text and find the entry and exit points.
            
            **Target Anchors:**
            - 'content_entry_point': The exact unique string where the actual document starts. If it starts with content, use the first line.
            - 'footer_gateway': The absolute first line of the site footer infrastructure. If no footer exists, return "END_OF_DOCUMENT".
            
            **FULL TEXT:**
            {raw_content}
            
            **Output Format (JSON only):**
            {{
                "content_entry_point": "string",
                "footer_gateway": "string"
            }}
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            analysis = json.loads(response.choices[0].message.content)
            
            entry = analysis.get("content_entry_point")
            gateway = analysis.get("footer_gateway")
            
            content = raw_content
            
            
            if entry:
                entry_idx = robust_find(content, entry, from_end=False)
                if entry_idx > 0:
                    content = content[entry_idx:]
                
            if gateway and gateway != "END_OF_DOCUMENT":
                gate_idx = robust_find(content, gateway, from_end=True)
                if gate_idx != -1:
                    content = content[:gate_idx]
            
            return content.strip()
            
        except Exception as e:
            logging.error(f"LLM Clean failed: {e}")
            return raw_content

def _combine_cleaned_files(provider_path, output_name="combined_all.md"):
    clean_dir = os.path.join(provider_path, "clean_md")
    md_files = sorted(
        f for f in glob.glob(os.path.join(clean_dir, "*.md"))
        if os.path.basename(f) != output_name
    )
    if not md_files:
        return

    parts = []
    for i, md_file in enumerate(md_files, start=1):
        with open(md_file, "r", encoding="utf-8") as f:
            parts.append(f"# Source File: {os.path.basename(md_file)}\n\n" + f.read().rstrip())
        if i != len(md_files):
            parts.append("\n\n---\n\n")

    with open(os.path.join(clean_dir, output_name), "w", encoding="utf-8") as f:
        f.write("".join(parts))
    print(f"  >> Created combined cleaned file for {os.path.basename(provider_path)}")


def clean_all_providers(api_key, provider_name=None):
    if not api_key:
        print("Error: API Key required for LLM cleaning.")
        return

    all_providers = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    if provider_name and provider_name != "All":
        if provider_name not in all_providers:
            print(f"Error: Provider '{provider_name}' not found.")
            return
        targets = [provider_name]
    else:
        targets = all_providers

    print(f"Cleaning & combining for: {', '.join(targets)}")
    cleaner = LLMCleaner(api_key=api_key)

    for provider in targets:
        provider_path = os.path.join(DATA_DIR, provider)
        md_dir = os.path.join(provider_path, "md")
        if not os.path.isdir(md_dir):
            continue

        source_files = [f for f in glob.glob(os.path.join(md_dir, "*.md")) if "combined_all.md" not in f]
        print(f"Processing {provider} ({len(source_files)} source files)...")
        clean_dir = os.path.join(provider_path, "clean_md")
        os.makedirs(clean_dir, exist_ok=True)

        for file_path in source_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                with open(os.path.join(clean_dir, os.path.basename(file_path)), "w", encoding="utf-8") as f:
                    f.write(cleaner.clean(content))
            except Exception as e:
                print(f"  Error cleaning {os.path.basename(file_path)}: {e}")

        _combine_cleaned_files(provider_path)

    print("Cleaning and combining complete.")