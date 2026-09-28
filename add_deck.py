#!/usr/bin/env python3
"""新增簡報：python3 add_deck.py 檔案.pdf "簡報標題"
PDF → 每頁一張 JPG，放進 decks/<id>/，並更新 decks.json。
PowerPoint 請先「檔案 → 匯出 → PDF」。
移除簡報：python3 add_deck.py --remove <id>
"""
import json, re, shutil, subprocess, sys, datetime
from pathlib import Path

ROOT = Path(__file__).parent
MANIFEST = ROOT / "decks.json"

def load(): return json.loads(MANIFEST.read_text("utf-8"))
def save(d): MANIFEST.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", "utf-8")

def add(pdf, title):
    pdf = Path(pdf).expanduser()
    if pdf.suffix.lower() != ".pdf":
        sys.exit("請先把簡報匯出成 PDF")
    deck_id = re.sub(r"[^a-z0-9]+", "-", pdf.stem.lower()).strip("-") or "deck"
    deck_id = f"{datetime.date.today():%Y%m%d}-{deck_id}"
    out = ROOT / "decks" / deck_id
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    subprocess.run(["pdftoppm", "-jpeg", "-jpegopt", "quality=92", "-r", "200", str(pdf), str(out / "s")], check=True)
    slides = sorted(p.name for p in out.glob("s-*.jpg"))
    decks = [d for d in load() if d["id"] != deck_id]
    decks.append({"id": deck_id, "title": title or pdf.stem, "date": f"{datetime.date.today()}", "slides": slides})
    save(decks)
    print(f"已新增 {deck_id}：{len(slides)} 頁")

def remove(deck_id):
    shutil.rmtree(ROOT / "decks" / deck_id, ignore_errors=True)
    save([d for d in load() if d["id"] != deck_id])
    print(f"已移除 {deck_id}")

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--remove":
        remove(sys.argv[2])
    elif len(sys.argv) >= 2:
        add(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        print(__doc__)
