# nlp-service/extract/preprocess.py
import re

TIMESTAMP_RE = re.compile(r'\[?\b(?:\d{1,2}:)?\d{1,2}:\d{2}\b\]?')  # matches 00:12:34 and 12:34
SPEAKER_PREFIX_RE = re.compile(r'^[\s"\']*([A-Za-z][A-Za-z0-9 .\-]{0,40})\s*[:\-–—]+\s*')  # Name: or Name -
MULTIPLE_SPACES_RE = re.compile(r'\s+')
BULLET_RE = re.compile(r'^[\-\*\u2022]\s*')  # leading bullets

def strong_clean_transcript(text: str) -> str:
    """
    Strong cleanup for transcripts:
    - remove timestamps like [00:12:34] or 12:34
    - remove speaker prefixes like "Mark: " or "Sarah - "
    - remove timestamps inside parentheses
    - collapse whitespace
    - remove typical export artifacts
    """
    if not text:
        return ""

    # Normalize line endings
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # remove explicit timestamps
        line = TIMESTAMP_RE.sub("", line)
        # remove timestamps in parentheses like (00:12)
        line = re.sub(r'\(\s*\d{1,2}:\d{2}\s*\)', '', line)
        # remove leading bullets
        line = BULLET_RE.sub("", line)
        # remove leading speaker name tokens like "Mark: " heuristically
        line = SPEAKER_PREFIX_RE.sub("", line)
        # remove excessive punctuation repeated
        line = re.sub(r'[_]{3,}', '', line)
        # collapse spaces
        line = MULTIPLE_SPACES_RE.sub(" ", line)
        # trim again
        line = line.strip()
        if line:
            cleaned_lines.append(line)
    # Join with two newlines to help LLM see paragraph breaks
    result = "\n\n".join(cleaned_lines)
    # restrict overall length (safety)
    return result.strip()
