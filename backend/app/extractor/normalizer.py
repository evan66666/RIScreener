import re
import unicodedata

def normalize_text(text: str) -> str:
    """
    Normalizes Indonesian and English disclosure text:
    - Normalizes Unicode characters (NFKD)
    - Replaces multiple whitespaces and tabs with single space
    - Resolves hyphenated line breaks (e.g., 'penam- \nbahan' -> 'penambahan')
    - Converts newlines to single spaces while keeping sentence structure
    """
    if not text:
        return ""
    
    # Unicode normalize
    text = unicodedata.normalize("NFKD", text)
    
    # Fix hyphenation at line breaks (e.g. 'perusa-\nhaan' -> 'perusahaan')
    text = re.sub(r'(\w+)-\s*[\r\n]+\s*(\w+)', r'\1\2', text)
    
    # Replace newlines with spaces
    text = re.sub(r'[\r\n]+', ' ', text)
    
    # Normalize multiple spaces
    text = re.sub(r'[ \t\f\v]+', ' ', text)
    
    return text.strip()

def clean_for_search(text: str) -> str:
    """Lowercases and strips for pattern matching while keeping words."""
    norm = normalize_text(text).lower()
    return norm
