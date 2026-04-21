from difflib import SequenceMatcher
from storage import get_all_urls, get_all_titles

def is_duplicate(title: str, source_url: str) -> bool:
    known_urls = get_all_urls()
    if source_url and source_url in known_urls:
        return True
    known_titles = get_all_titles()
    for known in known_titles:
        ratio = SequenceMatcher(None, title.lower(), known.lower()).ratio()
        if ratio > 0.75:
            return True
    return False
