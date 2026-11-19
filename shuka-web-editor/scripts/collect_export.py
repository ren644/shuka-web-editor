#!/usr/bin/env python3
"""Collect the newest Shuka browser exports from Downloads/Desktop into a result directory.

一次导出可能同时产生 PNG 单张与 ZIP 打包，本脚本收集时间窗内的全部导出文件，
逐个校验 PNG/JPG 魔数、最小尺寸与 ZIP 完整性，不静默放过损坏文件。
"""
import argparse
import json
from pathlib import Path
import shutil
import sys
import time
import zipfile

SUFFIXES = {".png", ".zip", ".livp", ".jpg", ".mp4"}
MIN_BYTES = 100
MAGIC = {".png": b"\x89PNG\r\n\x1a\n", ".jpg": b"\xff\xd8\xff"}
ZIP_MEDIA = (".png", ".livp", "mp.jpg", ".mp4")


def find_candidates(sources, after):
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
            if mtime >= after - 1:
                candidates.append((mtime, path))
    return candidates


def validate(path):
    """返回 None 表示通过，否则返回错误说明。"""
    suffix = path.suffix.lower()
    size = path.stat().st_size
    if size < MIN_BYTES:
        return f"文件过小（{size} 字节），可能尚未下载完成"
    if suffix in MAGIC:
        with path.open("rb") as handle:
            if handle.read(len(MAGIC[suffix])) != MAGIC[suffix]:
                return "文件头校验失败，不是有效的图片"
    elif suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                return "ZIP 已损坏"
            if not [n for n in archive.namelist() if n.lower().endswith(ZIP_MEDIA)]:
                return "ZIP 中没有卡片文件"
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--after", required=True, type=float, help="Unix timestamp captured before export")
    parser.add_argument("--output", required=True, help="Result directory")
    parser.add_argument("--source", action="append", help="Additional download directory; can repeat")
    parser.add_argument("--wait", type=float, default=10, help="没有候选文件时等待下载的秒数")
    args = parser.parse_args()
    sources = [Path(p).expanduser() for p in (args.source or [])] + [Path.home() / "Downloads", Path.home() / "Desktop"]

    candidates = find_candidates(sources, args.after)
    deadline = time.time() + max(0.0, args.wait)
    while not candidates and time.time() < deadline:
        time.sleep(1)
        candidates = find_candidates(sources, args.after)

    if not candidates:
        raise SystemExit("没有找到本次导出的薯卡文件。请检查浏览器是否阻止下载，或手动点击网站导出按钮。")

    newest = max(item[0] for item in candidates)
    latest = [path for mtime, path in candidates if mtime >= newest - 3]
    dropped = [path.name for mtime, path in candidates if mtime < newest - 3]
    if dropped:
        print(f"提示：时间窗内的早期文件已忽略（可能属于上一次导出）：{dropped}", file=sys.stderr)

    output = Path(args.output).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    files = []
    failures = []
    for source in sorted(latest):
        problem = validate(source)
        if problem:
            failures.append({"file": source.name, "reason": problem})
            continue
        destination = output / source.name
        shutil.copy2(source, destination)
        files.append(str(destination))

    if failures:
        for failure in failures:
            print(f"错误：{failure['file']}：{failure['reason']}", file=sys.stderr)
        raise SystemExit("部分导出文件校验未通过")

    print(json.dumps({"ok": True, "files": files, "count": len(files)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
