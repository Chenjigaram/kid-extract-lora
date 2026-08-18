from __future__ import annotations

import random

LIGATURES = {"fi": "ﬁ", "fl": "ﬂ", "ff": "ﬀ"}

CHAR_CONFUSIONS = {"o": "0", "O": "0", "l": "1", "I": "l", "S": "5", "rn": "m"}

FOOTERS = {
    "en": ("Page {page} of {total}", "Document produced on {day}/{month}/2026", "{name} - Key Information"),
    "de": ("Seite {page} von {total}", "Dokument erstellt am {day}.{month}.2026", "{name} - Basisinformationen"),
    "fr": ("Page {page} sur {total}", "Document produit le {day}/{month}/2026", "{name} - Informations cles"),
    "nl": ("Pagina {page} van {total}", "Document opgesteld op {day}-{month}-2026", "{name} - Essentiele informatie"),
}


def _corrupt_line(line: str, rng: random.Random, rate: float) -> str:
    characters = list(line)
    for index, character in enumerate(characters):
        if character in CHAR_CONFUSIONS and rng.random() < rate:
            characters[index] = CHAR_CONFUSIONS[character]
    corrupted = "".join(characters)
    if rng.random() < rate * 4:
        for plain, ligature in LIGATURES.items():
            corrupted = corrupted.replace(plain, ligature)
    return corrupted


def _stretch_whitespace(line: str, rng: random.Random) -> str:
    if "  " in line and rng.random() < 0.4:
        return line.replace("  ", "   ", 1)
    if rng.random() < 0.15:
        return line + " "
    return line


def _hyphenate(line: str, rng: random.Random) -> str:
    words = line.split(" ")
    candidates = [i for i, word in enumerate(words) if len(word) > 7 and word.isalpha()]
    if not candidates:
        return line
    index = rng.choice(candidates)
    word = words[index]
    split = rng.randint(3, len(word) - 3)
    words[index] = f"{word[:split]}-\n{word[split:]}"
    return " ".join(words)


def _page_furniture(name: str, language: str, rng: random.Random) -> str:
    template = rng.choice(FOOTERS[language])
    return template.format(
        page=rng.randint(1, 3),
        total=3,
        day=f"{rng.randint(1, 28):02d}",
        month=f"{rng.randint(1, 12):02d}",
        name=name[:40],
    )


def inject_noise(
    text: str,
    protected: list[str],
    fund_name: str,
    language: str,
    rng: random.Random,
    rate: float = 0.02,
) -> str:
    guards = [value for value in protected if value]
    lines = text.split("\n")
    output: list[str] = []
    for line in lines:
        is_protected = any(guard in line for guard in guards)
        if is_protected:
            output.append(_stretch_whitespace(line, rng))
            continue
        noisy = _corrupt_line(line, rng, rate)
        noisy = _stretch_whitespace(noisy, rng)
        if len(noisy) > 40 and rng.random() < 0.08:
            noisy = _hyphenate(noisy, rng)
        output.append(noisy)

    if rng.random() < 0.6:
        position = rng.randint(len(output) // 2, len(output))
        output.insert(position, "")
        output.insert(position + 1, _page_furniture(fund_name, language, rng))
    return "\n".join(output)
