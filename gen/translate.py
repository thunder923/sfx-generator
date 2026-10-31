"""Japanese -> English translation for AI prompts.

AudioLDM2 only understands English, so free-form Japanese input is
translated before it reaches the model. Routes, in order:
  1. Local MarianMT (Helsinki-NLP/opus-mt-ja-en) — fully offline once the
     model (~300 MB) is downloaded; needs the `sentencepiece` package.
  2. Google Translate web endpoint — no API key, needs internet.
  3. Keyword table (gen.presets.translate_free) — offline last resort.
Returns None for ASCII input (already English) or when all routes fail.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

_cache: dict[str, str] = {}
_marian = None
_marian_failed = False


def _marian_translate(text: str) -> str | None:
    global _marian, _marian_failed
    if _marian_failed:
        return None
    try:
        if _marian is None:
            from transformers import MarianMTModel, MarianTokenizer

            name = "Helsinki-NLP/opus-mt-ja-en"
            tok = MarianTokenizer.from_pretrained(name)
            model = MarianMTModel.from_pretrained(name)
            _marian = (tok, model)
        tok, model = _marian
        batch = tok([text], return_tensors="pt", padding=True, truncation=True)
        out = model.generate(**batch, max_new_tokens=128)
        return tok.decode(out[0], skip_special_tokens=True).strip() or None
    except Exception:
        _marian_failed = True
        return None


def _google_translate(text: str) -> str | None:
    try:
        q = urllib.parse.quote(text)
        url = ("https://translate.googleapis.com/translate_a/single"
               f"?client=gtx&sl=ja&tl=en&dt=t&q={q}")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as r:
            data = json.loads(r.read().decode("utf-8"))
        parts = [seg[0] for seg in data[0] if seg and seg[0]]
        return "".join(parts).strip() or None
    except Exception:
        return None


def to_english(text: str) -> str | None:
    text = (text or "").strip()
    if not text or all(ord(c) < 128 for c in text):
        return None  # empty or already English/ASCII
    if text in _cache:
        return _cache[text]
    out = _marian_translate(text) or _google_translate(text)
    if not out:
        from gen.presets import translate_free

        out = translate_free(text)
    if out:
        _cache[text] = out
    return out
