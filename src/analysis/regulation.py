import os
import re

REGULATIONS = {
    "EU Data Act": "eu_regulation/eu_data_act_striped.md",
    "GDPR": "eu_regulation/gdpr_striped.md",
    "NIS2": "eu_regulation/nis2_striped.md"
}

def article_number(source_ref):
    match = re.search(r"Article\s+(\d+)", str(source_ref), re.IGNORECASE)
    return int(match.group(1)) if match else None

def article_label(source_ref):
    num = article_number(source_ref)
    return f"Article {num}" if num is not None else "Other"

def article_sort_key(label):
    num = article_number(label)
    return num if num is not None else 999

def get_article_text(article_ref, regulation="EU Data Act"):
    path = REGULATIONS.get(regulation)
    if not path or not os.path.exists(path):
        return None

    match = re.search(r"Article\s+(\d+)", article_ref, re.IGNORECASE)
    if not match:
        return None
    article_num = match.group(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        start_match = re.search(rf"^(?:##\s*)?Article {article_num}\b", content, re.MULTILINE | re.IGNORECASE)
        if not start_match:
            return None

        rest = content[start_match.end():]
        next_match = re.search(r"^(?:##\s*)?Article \d+\b", rest, re.MULTILINE | re.IGNORECASE)
        end = start_match.end() + next_match.start() if next_match else len(content)
        return content[start_match.start():end].strip()
    except OSError:
        return None

def list_all_articles(regulation="EU Data Act"):
    path = REGULATIONS.get(regulation)
    if not path or not os.path.exists(path):
        return []
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        article_matches = re.finditer(r"^(?:##\s*)?Article (\d+)\b", content, re.MULTILINE | re.IGNORECASE)
        
        articles = []
        for m in article_matches:
            art_num = m.group(1)
            full_ref = f"Article {art_num}"
            
            lookahead = content[m.end():m.end()+200]
            lines = [l.strip() for l in lookahead.split('\n') if l.strip()]
            
            title = "Untitled"
            if lines:
                potential_title = lines[0]
                if potential_title.startswith("##"):
                    potential_title = potential_title[2:].strip()
                
                if not re.match(r"^Article \d+$", potential_title, re.I):
                    title = potential_title
            
            articles.append(f"{full_ref}: {title}")
        
        return articles
    except Exception as e:
        print(f"Error listing articles: {e}")
        return []