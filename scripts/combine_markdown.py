#!/usr/bin/env python3
import argparse
from pathlib import Path
import tiktoken

_ROOT = Path(__file__).resolve().parents[1]

def get_token_count(text: str, model: str = "gpt-4o-mini") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def combine_md_in_folder(md_folder: Path, output_file_name: str, model: str):
    output_path = md_folder / output_file_name
    
    md_files = sorted(
        p for p in md_folder.glob("*.md")
        if p.is_file() and p.name != output_file_name
    )

    if not md_files:
        return

    print(f"\nProcessing folder: {md_folder.parent.name}/md/")
    
    parts = []
    for i, md_file in enumerate(md_files, start=1):
        try:
            content = md_file.read_text(encoding="utf-8").rstrip()
            file_tokens = get_token_count(content, model=model)
            print(f"  - {md_file.name}: {file_tokens} tokens")
            
            parts.append(f"# File: {md_file.name}\n\n")
            parts.append(content)
            
            if i != len(md_files):
                parts.append("\n\n---\n\n")
        except Exception as e:
            print(f"  ! Error reading {md_file.name}: {e}")

    if parts:
        combined_text = "".join(parts)
        output_path.write_text(combined_text, encoding="utf-8")
        
        total_tokens = get_token_count(combined_text, model=model)
        print(f"  >> Created {output_path.name} ({total_tokens} total tokens)")

def main():
    parser = argparse.ArgumentParser(
        description="Traverse directories and combine .md files inside 'md' folders."
    )
    parser.add_argument(
        "-o", "--output", 
        default="combined_all.md", 
        help="Name of the combined file (default: combined_all.md)"
    )
    parser.add_argument(
        "-m", "--model", 
        default="gpt-4o-mini", 
        help="tiktoken model for counting (default: gpt-4o-mini)"
    )
    args = parser.parse_args()

    root_dir = _ROOT / "data"
    
    md_folders = [p for p in root_dir.rglob("md") if p.is_dir()]

    if not md_folders:
        print("No folders named 'md' found.")
        return

    print(f"Found {len(md_folders)} 'md' folders. Counting tokens with '{args.model}'...")

    for md_folder in md_folders:
        combine_md_in_folder(md_folder, args.output, args.model)

if __name__ == "__main__":
    main()