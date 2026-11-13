import csv
import json
import re
import subprocess
from pathlib import Path

ROOT = Path.home() / "update"
PROJECT = ROOT / "EduBridge-Private-main"
IMAGE_DIR = ROOT / "data/data/images"
FORM_CSV = PROJECT / "backend/artifacts/assessment/fixed_form.csv"
OUTPUT = PROJECT / "backend/content/eedi_ocr_draft.json"
RAW_DIR = PROJECT / "backend/content/ocr_raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)

def clean_lines(text):
    lines = []
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            lines.append(line)
    return lines

items = []

with FORM_CSV.open(newline="", encoding="utf-8") as f:
    questions = list(csv.DictReader(f))

for index, row in enumerate(questions, start=1):
    qid = int(row["QuestionId"])
    image_path = IMAGE_DIR / f"{qid}.jpg"

    print(f"[{index}/{len(questions)}] OCR QuestionId {qid}")

    if not image_path.exists():
        print(f"  WARNING: image missing: {image_path}")
        raw_text = ""
        status = "missing_image"
    else:
        result = subprocess.run(
            ["tesseract", str(image_path), "stdout", "--psm", "6"],
            capture_output=True,
            text=True,
            check=False,
        )

        raw_text = result.stdout.strip()
        status = "needs_manual_review" if raw_text else "ocr_failed"

        if result.returncode != 0:
            print(f"  WARNING: Tesseract exit code {result.returncode}")

    lines = clean_lines(raw_text)

    (RAW_DIR / f"{qid}.txt").write_text(
        raw_text + "\n", encoding="utf-8"
    )

    items.append({
        "question_id": qid,
        "concept_id": int(row["concept_ids"]),
        "concept_name": row["concept_names"],
        "correct_answer": int(row["correct_answer"]),
        "question_text": None,
        "options": {
            "1": None,
            "2": None,
            "3": None,
            "4": None
        },
        "ocr_lines": lines,
        "ocr_raw": raw_text,
        "review_status": status
    })

OUTPUT.write_text(
    json.dumps(
        {
            "source": "Eedi NeurIPS 2020",
            "assessment_id": "eedi_pdina_fixed_v1",
            "count": len(items),
            "note": "OCR draft only. Question text and options require visual verification.",
            "items": items
        },
        ensure_ascii=False,
        indent=2
    ),
    encoding="utf-8"
)

print()
print(f"Completed: {len(items)} questions")
print(f"JSON draft: {OUTPUT}")
print(f"Raw OCR files: {RAW_DIR}")
