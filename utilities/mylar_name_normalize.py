#!/usr/bin/env python3
"""Mylar-compatible filename normalization helpers."""

from __future__ import annotations

import re


def latin_to_ascii(text: str) -> str:
    xlate = {
        0xC0: "A",
        0xC1: "A",
        0xC2: "A",
        0xC3: "A",
        0xC4: "A",
        0xC5: "A",
        0xC6: "Ae",
        0xC7: "C",
        0xC8: "E",
        0xC9: "E",
        0xCA: "E",
        0xCB: "E",
        0xCC: "I",
        0xCD: "I",
        0xCE: "I",
        0xCF: "I",
        0xD0: "Th",
        0xD1: "N",
        0xD2: "O",
        0xD3: "O",
        0xD4: "O",
        0xD5: "O",
        0xD6: "O",
        0xD8: "O",
        0xD9: "U",
        0xDA: "U",
        0xDB: "U",
        0xDC: "U",
        0xDD: "Y",
        0xDE: "th",
        0xDF: "ss",
        0xE0: "a",
        0xE1: "a",
        0xE2: "a",
        0xE3: "a",
        0xE4: "a",
        0xE5: "a",
        0xE6: "ae",
        0xE7: "c",
        0xE8: "e",
        0xE9: "e",
        0xEA: "e",
        0xEB: "e",
        0xEC: "i",
        0xED: "i",
        0xEE: "i",
        0xEF: "i",
        0xF0: "th",
        0xF1: "n",
        0xF2: "o",
        0xF3: "o",
        0xF4: "o",
        0xF5: "o",
        0xF6: "o",
        0xF8: "o",
        0xF9: "u",
        0xFA: "u",
        0xFB: "u",
        0xFC: "u",
        0xFD: "y",
        0xFE: "th",
        0xFF: "y",
    }
    out = ""
    for ch in text:
        code = ord(ch)
        if code in xlate:
            out += xlate[code]
        elif code >= 0x80:
            continue
        else:
            out += ch
    return out


def clean_name(value: str) -> str:
    text = latin_to_ascii(value).lower()
    text = re.sub(r'[\/\@\#\$\%\^\*\+\"\[\]\{\}\<\>\=\_]', " ", text)
    return " ".join(text.split())


def clean_title(value: str) -> str:
    text = re.sub(r"[\.\-\/\_]", " ", value).lower()
    text = " ".join(text.split())
    return text.title()


def normalize_filename(value: str) -> str:
    """Broad normalization suitable for duplicate detection and loose matching."""
    text = latin_to_ascii(value)
    text = text.replace("_", " ")
    text = re.sub(r"[\.\-\/\@\#\$\%\^\*\+\"\[\]\{\}\<\>\=\(\)]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.casefold()
