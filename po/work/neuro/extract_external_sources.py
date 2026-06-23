from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pdfplumber


ROOT = Path("/Users/maksymilianjaneczek/Documents/Codex/2026-06-23/po")
WORK = ROOT / "work" / "neuro"
OUT = WORK / "external_sources.json"

DOWNLOADS = Path("/Users/maksymilianjaneczek/Downloads")

QUESTION_DOCS = [
    DOWNLOADS / "egzamin neurologia 2026 cykl A-2.docx",
    DOWNLOADS / "egzamin neurologia II 2026 cykl A-3.docx",
]

CONTENT_SOURCES = [
    DOWNLOADS / "Miopatie MPO KZF pt.pptx",
    DOWNLOADS / "14. Neuroinfekcje 2024.pptx",
    DOWNLOADS / "12. Choroby neurozwyrodnieniowe przebigające z otępieniem.pptx.pdf",
    DOWNLOADS / "8. Choroby nerwowo-mięsniowe EZT JM pt1.pdf",
    DOWNLOADS / "10. Padaczka KZF JTP pon2.pdf",
    DOWNLOADS / "3. Badanie układu ruchu - układ pozapiramidowy JG MTpon.pdf",
    DOWNLOADS / "13. SM AWH AK MPO śr2.pdf",
    DOWNLOADS / "1. nerwy czaszkowe.pdf",
    DOWNLOADS / "2. badanie układu ruchu-zespół piramidowy PR, JTP,pon.pdf",
    DOWNLOADS / "4. Zespół móżdzkowy, zaburzenia czucia MT EZT śr.pdf",
    DOWNLOADS / "Podstawowe zespoły neurologiczne AS AK 2.pdf",
    DOWNLOADS / "3. choroby układu pozapiramidowego JG MT czw2.pdf",
]

TOPIC_KEYWORDS: dict[str, list[str]] = {
    "badanie": [
        "nerw czaszkowy",
        "nerwu twarzowego",
        "nerw twarzowy",
        "nerwy czaszkowe",
        "badanie neurologiczne",
        "układ ruchu",
        "lovetta",
        "objaw babińskiego",
    ],
    "diagnostyka": ["pmr", "płyn mózgowo-rdzeniowy", "eeg", "emg", "eng", "potencjały", "punkcja"],
    "zespoly": [
        "piramidowy",
        "móżdżk",
        "czucia",
        "afazja",
        "agnozja",
        "apraksja",
        "zespół",
        "zaburzenia wyższych",
        "rdzeń",
        "brown",
    ],
    "naczyniowe": [
        "udar",
        "tia",
        "krwotok",
        "trombol",
        "trombekt",
        "migotanie",
        "noac",
        "warfaryna",
        "lakunarny",
        "sah",
        "cadasil",
        "notch3",
        "ciśnienie tętnicze",
    ],
    "infekcje": ["zomr", "opon", "hsv", "neuroinfek", "bakteryj", "wirusow", "encephalitis", "zapalenie mózgu"],
    "demielinizacja": ["stwardnienie rozsiane", " sm ", "adem", "nmo", "devic", "pml", "dawsona", "demieliniz"],
    "pozapiramidowe": [
        "parkinson",
        "drżenie",
        "huntington",
        "dystoni",
        "pląsaw",
        "wilson",
        "pozapiramid",
        "lewy",
        "msa",
        "psp",
    ],
    "otepienia": ["otęp", "alzheimer", "mci", "poznawcz", "amyloid", "tau", "lewy"],
    "bole_zawroty": ["migrena", "ból głowy", "zawroty", "vertigo", "bppv", "meniere"],
    "padaczka": [
        "padacz",
        "napad",
        "lekooporn",
        "fenytoin",
        "karbamazep",
        "walpro",
        "stan padaczkowy",
        "odstawienia alkoholu",
    ],
    "guzy_urazy": [
        "uraz",
        "krwiak",
        "gcs",
        "glasgow",
        "cushing",
        "nadtward",
        "podtward",
        "stłuczenie",
        "aksonal",
        "ciśnienia śródczaszkowego",
        "guz",
    ],
    "toksyczne_sen": ["alkohol", "zatruc", "wernicke", "sen", "narkoleps", "delirium"],
    "swiadomosc": ["śpiącz", "świadomo", "śmierć mózgu", "gcs"],
    "obwodowe": [
        "miopati",
        "mięśni",
        "miasten",
        "neuropat",
        "gbs",
        "cidp",
        "złącze nerwowo",
        "lambert",
    ],
    "neuron": ["sla", "als", "neuron ruchowy", "sma", "kennedy"],
    "systemowe_psychiczne": ["systemow", "cukrzyc", "b12", "tarczy", "psychic", "paranowotwor"],
    "bol_rozwoj": ["ból neuropatyczny", "mpd", "dzieci", "rozwoj", "porażenie dziecięce"],
}

SOURCE_TOPIC_HINTS = {
    "Miopatie": "obwodowe",
    "Neuroinfekcje": "infekcje",
    "otępieniem": "otepienia",
    "nerwowo-mięsniowe": "obwodowe",
    "nerwowo-mięśniowe": "obwodowe",
    "Padaczka": "padaczka",
    "pozapiramidowy": "pozapiramidowe",
    "pozapiramidowego": "pozapiramidowe",
    "SM": "demielinizacja",
    "nerwy czaszkowe": "badanie",
    "piramidowy": "zespoly",
    "móżdzkowy": "zespoly",
    "móżdzkowy": "zespoly",
    "móżdżkowy": "zespoly",
    "Podstawowe zespoły": "zespoly",
}


def norm(value: str) -> str:
    value = unicodedata.normalize("NFC", value)
    value = value.replace("\u00a0", " ")
    value = value.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    value = value.replace("\u2794", "->").replace("\u2192", "->")
    value = re.sub(r"[\ue000-\uf8ff]", " ", value)
    value = re.sub(r"[•▪◦●■□➢]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def assign_topic(text: str, fallback: str = "zespoly") -> str:
    lowered = f" {norm(text).lower()} "
    scores: dict[str, int] = defaultdict(int)
    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in lowered:
                scores[topic] += 1 + min(3, len(keyword) // 8)
    if not scores:
        return fallback
    return max(scores.items(), key=lambda item: item[1])[0]


def docx_paragraphs(path: Path) -> list[dict[str, Any]]:
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    paras: list[dict[str, Any]] = []
    for p in root.findall(".//w:p", ns):
        runs = []
        for r in p.findall(".//w:r", ns):
            txt = "".join(t.text or "" for t in r.findall(".//w:t", ns))
            if not txt:
                continue
            rpr = r.find("w:rPr", ns)
            bold = False
            if rpr is not None:
                b = rpr.find("w:b", ns)
                bold = b is not None and b.attrib.get(f"{{{ns['w']}}}val", "1") != "0"
            runs.append({"text": txt, "bold": bold})
        text = norm("".join(run["text"] for run in runs))
        if text:
            paras.append({"text": text, "bold": any(run["bold"] for run in runs), "runs": runs})
    return paras


def parse_questions(path: Path) -> list[dict[str, Any]]:
    paras = docx_paragraphs(path)
    questions: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    intro_buffer: list[str] = []
    for para in paras:
        text = para["text"]
        match = re.match(r"^(\d+)\.\s*(.*)", text)
        is_next_question = False
        if match and current is None:
            is_next_question = True
        elif match and current is not None and int(match.group(1)) == int(current["number"]) + 1:
            is_next_question = True
        if match and is_next_question:
            if current:
                questions.append(current)
            number = int(match.group(1))
            current = {
                "source": path.name,
                "number": number,
                "stem": match.group(2).strip(),
                "options": [],
                "answer": "",
                "answer_index": None,
            }
            intro_buffer = []
            continue
        if current is None:
            continue
        if not current["options"] and text.endswith(":") and len(current["stem"]) > 120:
            current["stem"] = norm(current["stem"] + " " + text)
            continue
        option_text = re.sub(r"^\d+[\.\)]\s+", "", text).strip()
        option_text = re.sub(r"^[A-Ea-e][\.\)]?\s+", "", option_text).strip()
        option_text = norm(option_text)
        if not option_text:
            continue
        option = {"text": option_text, "correct": bool(para["bold"])}
        current["options"].append(option)
        if para["bold"] and not current["answer"]:
            current["answer"] = option_text
            current["answer_index"] = len(current["options"]) - 1
    if current:
        questions.append(current)

    for question in questions:
        qtext = question["stem"] + " " + " ".join(opt["text"] for opt in question["options"])
        question["topic"] = assign_topic(qtext)
        question["id"] = f"{Path(question['source']).stem}-{question['number']}"
        question["answer_letter"] = (
            chr(ord("A") + question["answer_index"]) if question.get("answer_index") is not None else "?"
        )
    return questions


def extract_pptx_text(path: Path) -> list[str]:
    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    chunks: list[str] = []
    with ZipFile(path) as zf:
        slide_names = sorted(
            [name for name in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", name)],
            key=lambda name: int(re.search(r"slide(\d+)\.xml", name).group(1)),  # type: ignore[union-attr]
        )
        for idx, name in enumerate(slide_names, start=1):
            root = ET.fromstring(zf.read(name))
            texts = [norm(t.text or "") for t in root.findall(".//a:t", ns)]
            texts = [text for text in texts if text]
            if texts:
                chunks.append(f"Slajd {idx}: " + " | ".join(texts))
    return chunks


def extract_pdf_text(path: Path, max_pages: int | None = None) -> list[str]:
    chunks: list[str] = []
    with pdfplumber.open(path) as pdf:
        pages = pdf.pages[:max_pages] if max_pages else pdf.pages
        for idx, page in enumerate(pages, start=1):
            text = norm(page.extract_text(x_tolerance=1, y_tolerance=3) or "")
            if text:
                chunks.append(f"Strona {idx}: {text}")
    return chunks


def source_topic(path: Path, chunks: list[str]) -> str:
    name = norm(path.name)
    for hint, topic in SOURCE_TOPIC_HINTS.items():
        if hint.lower() in name.lower():
            return topic
    return assign_topic(" ".join(chunks[:20]))


def score_line(line: str) -> int:
    lowered = line.lower()
    score = 0
    for word in [
        "objaw",
        "rozpozn",
        "diagnost",
        "leczen",
        "różnic",
        "najczę",
        "charakterystycz",
        "pmr",
        "mri",
        "tk",
        "eeg",
        "emg",
        "definic",
        "kryter",
        "przeciwcia",
        "typowe",
        "zespół",
        "rokown",
    ]:
        if word in lowered:
            score += 3
    if re.search(r"\d", line):
        score += 1
    if 45 <= len(line) <= 230:
        score += 2
    if len(line) > 320:
        score -= 3
    return score


def select_key_points(chunks: list[str], limit: int = 30) -> list[str]:
    candidates: list[str] = []
    for chunk in chunks:
        chunk = re.sub(r"^(Slajd|Strona)\s+\d+:\s*", "", chunk)
        parts = re.split(r"(?<=[.;:])\s+|\s+\|\s+", chunk)
        for part in parts:
            line = norm(part)
            if 28 <= len(line) <= 260 and not re.match(r"^\d+$", line):
                candidates.append(line)
    seen: set[str] = set()
    ranked = sorted(candidates, key=lambda line: (-score_line(line), candidates.index(line)))
    selected: list[str] = []
    for line in ranked:
        key = re.sub(r"\W+", "", line.lower())[:90]
        if key in seen:
            continue
        seen.add(key)
        selected.append(line)
        if len(selected) >= limit:
            break
    return selected


def main() -> None:
    all_questions: list[dict[str, Any]] = []
    for path in QUESTION_DOCS:
        all_questions.extend(parse_questions(path))

    sources: list[dict[str, Any]] = []
    for path in CONTENT_SOURCES:
        if path.suffix.lower() == ".pptx":
            chunks = extract_pptx_text(path)
            kind = "pptx"
        else:
            chunks = extract_pdf_text(path)
            kind = "pdf"
        topic = source_topic(path, chunks)
        sources.append(
            {
                "file": path.name,
                "kind": kind,
                "topic": topic,
                "chunk_count": len(chunks),
                "key_points": select_key_points(chunks, limit=34),
            }
        )

    questions_by_topic: dict[str, int] = defaultdict(int)
    missing_answers = 0
    for question in all_questions:
        questions_by_topic[question["topic"]] += 1
        if not question["answer"]:
            missing_answers += 1

    data = {
        "questions": all_questions,
        "sources": sources,
        "stats": {
            "question_count": len(all_questions),
            "missing_answers": missing_answers,
            "questions_by_topic": dict(sorted(questions_by_topic.items())),
            "source_count": len(sources),
        },
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(data["stats"], ensure_ascii=False, indent=2))
    for source in sources:
        print(f"{source['topic']:>18} | {source['chunk_count']:>4} | {source['file']}")


if __name__ == "__main__":
    main()
