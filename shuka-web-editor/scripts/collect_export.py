#!/usr/bin/env python3
"""Collect the newest Shuka browser export from Downloads/Desktop into a result directory."""
import argparse
import json
from pathlib import Path
import shutil
import zipfile

SUFFIXES = {".png", ".zip", ".livp", ".jpg", ".mp4"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--after", required=True, type=float, help="Unix timestamp captured before export")
    parser.add_argument("--output", required=True, help="Result directory")
    parser.add_argument("--source", action="append", help="Additional download directory; can repeat")
    args = parser.parse_args()
    sources = [Path(p).expanduser() for p in (args.source or [])] + [Path.home() / "Downloads", Path.home() / "Desktop"]
    candidates = []
    for directory in sources:
        if not directory.is_dir():
            continue
        for path in directory.iterdir():
            if not path.is_file() or path.suffix.lower() not in SUFFIXES:
                continue
            if not (path.name.startswith("xhs-card-") or path.name.startswith("xhs-cards-")):
                continue
            mtime = path.stat().st_mtime
            if mtime >= args.after - 1:
                candidates.append((mtime, path))
    if not candidates:
        raise SystemExit("没有找到本次导出的薯卡文件。请检查浏览器是否阻止下载，或手动点击网站导出按钮。")
    _, source = max(candidates, key=lambda item: item[0])
    output = Path(args.output).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    destination = output / source.name
    media_count = 1
    if source.suffix.lower() == ".zip":
        with zipfile.ZipFile(source) as archive:
            assert archive.testzip() is None, "导出的 ZIP 已损坏"
            media = [n for n in archive.namelist() if n.lower().endswith((".png", ".livp", "mp.jpg", ".mp4"))]
            if not media:
                raise SystemExit("导出的 ZIP 中没有卡片文件")
            media_count = len(media)
    elif source.stat().st_size < 100:
        raise SystemExit("导出文件过小，可能尚未下载完成")
    shutil.copy2(source, destination)
    print(json.dumps({"ok": True, "file": str(destination), "media_count": media_count, "size_bytes": destination.stat().st_size}, ensure_ascii=False))


if __name__ == "__main__":
    main()
