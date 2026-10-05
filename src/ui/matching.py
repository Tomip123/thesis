import re
import difflib

def normalize_text(text):
    if not text:
        return ""
    text = re.sub(r'[*#_~`\[\]\(\)>]', ' ', text)
    text = " ".join(text.split()).lower()
    return text

def find_quote_match(full_text, quote):
    if not quote or not full_text:
        return None
    
    idx = full_text.find(quote)
    if idx != -1:
        return (idx, idx + len(quote))

    norm_quote = normalize_text(quote)
    if not norm_quote:
        return None
        
    doc_words = full_text.split()
    doc_word_starts = []
    curr_pos = 0
    for w in doc_words:
        start = full_text.find(w, curr_pos)
        doc_word_starts.append(start)
        curr_pos = start + len(w)

    def tokenize_with_pos(text):
        words = []
        indices = []
        for m in re.finditer(r'[\w§]+', text):
            words.append(m.group(0).lower())
            indices.append(m.start())
        return words, indices

    words_doc, indices_doc = tokenize_with_pos(full_text)
    words_quote, _ = tokenize_with_pos(quote)
    
    if not words_quote:
        return None
        
    matcher = difflib.SequenceMatcher(None, words_doc, words_quote)
    blocks = matcher.get_matching_blocks()
    
    best_match = None
    max_coverage = 0
    
    if blocks:
        start_w = -1
        end_w = -1
        matched_count = 0
        
        for b in blocks:
            if b.size == 0: continue
            
            if start_w != -1 and b.a - end_w > 50:
                coverage = matched_count / len(words_quote)
                if coverage > max_coverage:
                    max_coverage = coverage
                    best_match = (start_w, end_w)
                
                start_w = b.a
                matched_count = 0
            
            if start_w == -1:
                start_w = b.a
            
            end_w = b.a + b.size - 1
            matched_count += b.size

        coverage = matched_count / len(words_quote)
        if coverage > max_coverage:
            max_coverage = coverage
            best_match = (start_w, end_w)

    if best_match and max_coverage > 0.6:
        s_idx, e_idx = best_match
        start_char = indices_doc[s_idx]
        last_word_start = indices_doc[e_idx]
        last_word_len = len(words_doc[e_idx])
        end_char = last_word_start + last_word_len
        
        if (end_char - start_char) < len(quote) * 2.5:
            return (start_char, end_char)
                
    return None
