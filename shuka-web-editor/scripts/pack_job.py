#!/usr/bin/env python3
"""Package a Shuka CardSpec and its local assets for browser-based editing.

打包前校验任务单：
- content / pages 中引用的素材 id 必须在 assets 中存在；
- 重复素材 id、非法字段取值直接报错；
- 从未被引用的素材只警告，不阻断。
"""
import argparse
import json
from pathlib import Path
import re
import sys
import zipfile

MARKER_RE = re.compile(r"^[\t ]*\[(img|video|视频)(\d*)[\t ]*\]$", re.I | re.M)
THEMES = {"day", "night", "x"}
LAYOUTS = {"cover", "text", "image", "video", "mixed", "summary"}
WHITESPACE = {"preserve", "single-blank-line", "compact"}
SOURCE_TYPES = {"docx", "markdown", "text"}
LIVE_TARGETS = {"apple", "android"}


def safe_job_file(root, relative):
    if not relative:
        raise ValueError("任务包含空素材路径")
    path = (root / relative).resolve()
    if root.resolve() not in path.parents:
        raise ValueError(f"素材必须位于任务目录内：{relative}")
    if not path.is_file():
        raise FileNotFoundError(f"素材不存在：{relative}")
    return path


def referenced_ids(job):
    """content 标记与 ai_editor pages 中实际引用到的素材 id。"""
    refs = set()
    content = job.get("content")
    if isinstance(content, str):
        for match in MARKER_RE.finditer(content):
            # 省略编号的 [img] / [视频] 由网站按位置解析，不做 id 校验
            if match.group(2):
                refs.add(match.group(1).lower() + match.group(2))
    for page in job.get("pages") or []:
        for media in page.get("media") or []:
            source = media.get("source_id") or media.get("sourceId")
            if source:
                refs.add(str(source).lower())
    return refs


def asset_ids(job):
    assets = job.get("assets", {})
    ids = {"image": [], "video": []}
    for group, kind in (("images", "image"), ("videos", "video")):
        for asset in assets.get(group) or []:
            if asset.get("id"):
                ids[kind].append(str(asset["id"]).lower())
    return ids


def validate(job):
    errors, warnings = [], []
    mode = job.get("mode", "original")

    if mode not in {"original", "ai_editor"}:
        errors.append(f"未知生成模式：{mode}")
        return errors, warnings

    if mode == "original" and job.get("pages"):
        warnings.append("original 模式不应包含 pages；请改用 ai_editor 或删除 pages")
    if mode == "ai_editor" and not job.get("pages"):
        errors.append("ai_editor 模式必须提供非空 pages")

    if job.get("theme") and job["theme"] not in THEMES:
        errors.append(f"未知主题：{job['theme']}（可选 {sorted(THEMES)}）")
    whitespace = (job.get("textLayout") or {}).get("whitespace")
    if whitespace and whitespace not in WHITESPACE:
        errors.append(f"未知换行选项：{whitespace}（可选 {sorted(WHITESPACE)}）")

    source = job.get("sourceFile")
    if source:
        if not source.get("path"):
            errors.append("sourceFile 缺少 path")
        elif source.get("type", "docx") not in SOURCE_TYPES:
            errors.append(f"未知 sourceFile.type：{source.get('type')}（可选 {sorted(SOURCE_TYPES)}）")

    for page in job.get("pages") or []:
        if page.get("layout") and page["layout"] not in LAYOUTS:
            errors.append(f"未知页面版式：{page['layout']}（可选 {sorted(LAYOUTS)}）")

    if isinstance(job.get("note_title"), str) and len(job["note_title"]) > 20:
        errors.append(f"note_title 超过 20 字：{len(job['note_title'])} 字")
    if isinstance(job.get("note_content"), str) and len(job["note_content"]) > 1000:
        errors.append(f"note_content 超过 1000 字：{len(job['note_content'])} 字")
    if job.get("liveTarget") and job["liveTarget"] not in LIVE_TARGETS:
        errors.append(f"未知 liveTarget：{job['liveTarget']}（可选 {sorted(LIVE_TARGETS)}）")
    if job.get("liveSeconds") is not None and not 1 <= job["liveSeconds"] <= 30:
        errors.append(f"liveSeconds 必须在 1–30 之间：{job['liveSeconds']}")

    ids = asset_ids(job)
    for kind, values in ids.items():
        duplicates = sorted({v for v in values if values.count(v) > 1})
        if duplicates:
            errors.append(f"{kind} 素材 id 重复：{duplicates}")

    refs = referenced_ids(job)
    declared = set(ids["image"]) | set(ids["video"])
    missing = sorted(refs - declared)
    if missing:
        errors.append(f"任务单引用了未声明的素材 id：{missing}")
    unused = sorted(declared - refs)
    if unused:
        warnings.append(f"已声明但未被引用的素材：{unused}")

    return errors, warnings


def collect_files(root, job):
    files = set()
    for group in ("images", "videos"):
        for asset in job.get("assets", {}).get(group) or []:
            if asset.get("path"):
                files.add(asset["path"])
    source = job.get("sourceFile")
    if source and source.get("path"):
        files.add(source["path"])
        if source.get("type") == "markdown" or source["path"].lower().endswith((".md", ".markdown")):
            text = safe_job_file(root, source["path"]).read_text(encoding="utf-8")
            for match in re.finditer(r"!\[[^\]]*\]\(([^)\s]+)[^)]*\)", text):
                src = match.group(1)
                if not re.match(r"^(data:|https?:)", src, re.I):
                    files.add(src)
    return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True, help="job.json 路径")
    parser.add_argument("--output", required=True, help="输出 shuka-job.zip 路径")
    args = parser.parse_args()
    job_path = Path(args.job).resolve()
    root = job_path.parent
    job = json.loads(job_path.read_text(encoding="utf-8"))
    if not job.get("jobId"):
        raise SystemExit("任务单缺少 jobId")

    errors, warnings = validate(job)
    if errors:
        for error in errors:
            print(f"错误：{error}", file=sys.stderr)
        raise SystemExit("任务单校验未通过，未生成任务包")

    files = collect_files(root, job)

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("job.json", json.dumps(job, ensure_ascii=False, indent=2))
        for relative in sorted(files):
            archive.write(safe_job_file(root, relative), relative)
    print(json.dumps({
        "ok": True,
        "jobId": job["jobId"],
        "output": str(output),
        "assets": len(files),
        "warnings": warnings,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
