"""
pdf-extractor: D:\논문집 의 PDF → raw_text/*.txt + metadata.json
"""
import fitz  # pymupdf
import json
import os
import re
import sys
from pathlib import Path

# Windows 콘솔 인코딩 문제 우회
def safe_print(*args, **kwargs):
    text = " ".join(str(a) for a in args)
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        print(text.encode("ascii", errors="replace").decode("ascii"), **kwargs)

SOURCE_DIR = Path("D:/논문집")
OUTPUT_DIR = Path("raw_text")
OUTPUT_DIR.mkdir(exist_ok=True)

# 한국 학술지(★교육공학연구 등 최상위 ★ 폴더)는 영어 단어장 대상이 아니므로 제외
EXCLUDE_TOP_PREFIX = "★"


def collect_pdfs() -> list[Path]:
    return [p for p in SOURCE_DIR.rglob("*.pdf")
            if not p.relative_to(SOURCE_DIR).parts[0].startswith(EXCLUDE_TOP_PREFIX)]

REFERENCE_HEADERS = re.compile(
    r"^\s*(references|bibliography|works cited|reference list)\s*$",
    re.IGNORECASE
)

def slug(path: Path) -> str:
    name = path.stem
    name = re.sub(r"[^\w가-힣]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name[:100]


def extract_pdf(pdf_path: Path) -> tuple[str, int]:
    doc = fitz.open(str(pdf_path))
    page_count = doc.page_count
    pages_text = []
    for page_num, page in enumerate(doc):
        lines = page.get_text("text").splitlines()
        # 헤더/푸터 제거: 각 페이지 첫 2줄, 마지막 2줄
        if len(lines) > 5:
            lines = lines[2:-2]
        pages_text.append("\n".join(lines))
    doc.close()

    full_text = "\n".join(pages_text)

    # 참고문헌 섹션 이후 제거
    lines = full_text.splitlines()
    cut = len(lines)
    for i, line in enumerate(lines):
        if REFERENCE_HEADERS.match(line):
            cut = i
            break
    cleaned = "\n".join(lines[:cut])
    return cleaned, page_count


def main():
    pdf_paths = collect_pdfs()
    safe_print(f"총 PDF 발견: {len(pdf_paths)}개 (★ 폴더 제외)")

    metadata = {}
    success = 0
    errors = []

    for i, pdf_path in enumerate(pdf_paths, 1):
        s = slug(pdf_path)
        # 슬러그 충돌 방지
        base_slug = s
        idx = 1
        while s in metadata:
            s = f"{base_slug}_{idx}"
            idx += 1

        out_file = OUTPUT_DIR / f"{s}.txt"
        try:
            text, page_count = extract_pdf(pdf_path)
            if len(text.strip()) < 100:
                raise ValueError("텍스트가 너무 짧음 (스캔 PDF 가능성)")
            out_file.write_text(text, encoding="utf-8")
            metadata[s] = {
                "original_path": str(pdf_path),
                "filename": pdf_path.name,
                "slug": s,
                "page_count": page_count,
                "char_count": len(text)
            }
            success += 1
            if i % 50 == 0 or i == len(pdf_paths):
                safe_print(f"  [{i}/{len(pdf_paths)}] 완료: {pdf_path.name[:50]}")
        except Exception as e:
            errors.append({"path": str(pdf_path), "error": str(e)})
            safe_print(f"  [오류] {pdf_path.name}: {e}")

    meta_file = OUTPUT_DIR / "metadata.json"
    meta_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    safe_print(f"\n완료: {success}개 추출 성공, {len(errors)}개 오류")
    safe_print(f"결과: {OUTPUT_DIR}/")
    if errors:
        safe_print(f"오류 목록: {[e['path'] for e in errors[:5]]}")

    return success


if __name__ == "__main__":
    main()
