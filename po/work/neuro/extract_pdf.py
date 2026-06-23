from __future__ import annotations

import json
from pathlib import Path

import pdfplumber


SOURCE = Path("/Users/maksymilianjaneczek/Downloads/2. NASIOSKRYPT-NEUROLOGIA.pdf")
OUT_DIR = Path("work/neuro")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    pages: list[dict[str, object]] = []
    full_text_parts: list[str] = []

    with pdfplumber.open(SOURCE) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
            record = {"page": index, "text": text}
            pages.append(record)
            full_text_parts.append(f"\n\n===== PAGE {index} =====\n{text}")

    (OUT_DIR / "pages.json").write_text(
        json.dumps(pages, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / "source.txt").write_text("".join(full_text_parts), encoding="utf-8")

    print(f"pages={len(pages)}")
    print(f"characters={sum(len(str(page['text'])) for page in pages)}")
    print(f"empty_pages={sum(1 for page in pages if not str(page['text']).strip())}")


if __name__ == "__main__":
    main()
