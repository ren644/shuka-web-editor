#!/usr/bin/env python3
"""Download remote (http/https) assets of a Shuka job into the task directory and rewrite paths.

- assets.images / assets.videos 中的远程地址会下载到任务目录，并把 job.json 的路径改成本地相对路径；
- Markdown 源文件中的远程图片会下载到任务目录，改写后的正文另存为 <name>.local.md，
  原文件不动，job.json 的 sourceFile.path 指向改写副本；
- 下载失败会明确报错并退出，不生成半成品的任务单。
"""
import argparse
import json
import mimetypes
from pathlib import Path
import re
import shutil
import sys
import urllib.request

MAX_BYTES = 50 * 1024 * 1024
TIMEOUT = 30
EXT_FALLBACK = {"image": ".png", "video": ".mp4"}
MIME_EXT = {
    "image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif",
    "video/mp4": ".mp4", "video/quicktime": ".mov", "video/webm": ".webm",
}
MD_IMAGE_RE = re.compile(r"(!\[[^\]]*\]\()([^)\s]+)([^)]*\))")


class DownloadError(Exception):
    pass


def unique_path(root, filename):
    path = root / filename
    stem, suffix = path.stem, path.suffix
    counter = 2
    while path.exists():
        path = root / f"{stem}-{counter}{suffix}"
        counter += 1
    return path


def fetch(url, root, kind, filename=None):
    if not filename:
        suffix = Path(url.split("?")[0]).suffix.lower()
        if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".mov", ".webm"}:
            suffix = ""
        filename = f"remote-{kind}{suffix}"
    target = unique_path(root, filename)
    request = urllib.request.Request(url, headers={"User-Agent": "shuka-web-editor/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            content_type = (response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            if not target.suffix:
                target = target.with_suffix(MIME_EXT.get(content_type, EXT_FALLBACK[kind]))
                target = unique_path(root, target.name)
            total = 0
            with target.open("wb") as handle:
                while True:
                    chunk = response.read(1024 * 256)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_BYTES:
                        raise DownloadError(f"文件超过 50MB：{url}")
                    handle.write(chunk)
    except DownloadError:
        target.unlink(missing_ok=True)
        raise
    except Exception as exc:
        target.unlink(missing_ok=True)
        raise DownloadError(f"下载失败：{url}（{exc}）")
    return target.name


def rewrite_markdown(root, source_path):
    text = (root / source_path).read_text(encoding="utf-8")

    def replace(match):
        url = match.group(2)
        if re.match(r"^(data:|https?:)", url, re.I) and not url.lower().startswith("data:"):
            try:
                local = fetch(url, root, "image")
            except DownloadError as exc:
                raise SystemExit(str(exc))
            return match.group(1) + local + match.group(3)
        return match.group(0)

    rewritten = MD_IMAGE_RE.sub(replace, text)
    target = unique_path(root, Path(source_path).with_suffix(".local.md").name)
    target.write_text(rewritten, encoding="utf-8")
    return target.name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True, help="job.json 路径（会被原地更新）")
    args = parser.parse_args()
    job_path = Path(args.job).resolve()
    root = job_path.parent
    job = json.loads(job_path.read_text(encoding="utf-8"))

    downloaded = []
    try:
        for group, kind in (("images", "image"), ("videos", "video")):
            for asset in job.get("assets", {}).get(group) or []:
                path = asset.get("path") or ""
                if re.match(r"^https?://", path, re.I):
                    local = fetch(path, root, kind, filename=Path(path.split("?")[0]).name or None)
                    asset["path"] = local
                    downloaded.append({"from": path, "to": local})

        source = job.get("sourceFile")
        if source and source.get("path") and re.search(r"\.(md|markdown)$", source["path"], re.I):
            text = (root / source["path"]).read_text(encoding="utf-8")
            if re.search(r"!\[[^\]]*\]\(\s*https?://", text, re.I):
                local = rewrite_markdown(root, source["path"])
                source["path"] = local
                downloaded.append({"from": "markdown 远程图片", "to": local})
    except SystemExit:
        raise
    except Exception as exc:
        raise SystemExit(f"处理远程素材失败：{exc}")

    if downloaded:
        job_path.write_text(json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "job": str(job_path), "downloaded": downloaded}, ensure_ascii=False))


if __name__ == "__main__":
    main()
