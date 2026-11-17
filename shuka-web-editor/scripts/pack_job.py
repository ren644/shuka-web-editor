#!/usr/bin/env python3
"""Package a Shuka CardSpec and its local assets for browser-based editing."""
import argparse
import json
from pathlib import Path
import re
import zipfile


def safe_job_file(root, relative):
    if not relative:
        raise ValueError("任务包含空素材路径")
    path = (root / relative).resolve()
    if root.resolve() not in path.parents:
        raise ValueError(f"素材必须位于任务目录内：{relative}")
    if not path.is_file():
        raise FileNotFoundError(f"素材不存在：{relative}")
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True, help="job.json 路径")
    parser.add_argument("--output", required=True, help="输出 shuka-job.zip 路径")
    args = parser.parse_args()
    job_path = Path(args.job).resolve()
    root = job_path.parent
    job = json.loads(job_path.read_text(encoding="utf-8"))
    if not job.get("jobId"):
        raise ValueError("任务单缺少 jobId")
    if job.get("mode", "original") not in {"original", "ai_editor"}:
        raise ValueError("未知生成模式")

    files = set()
    for group in ("images", "videos"):
        for asset in job.get("assets", {}).get(group, []):
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

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("job.json", json.dumps(job, ensure_ascii=False, indent=2))
        for relative in sorted(files):
            archive.write(safe_job_file(root, relative), relative)
    print(json.dumps({"ok": True, "jobId": job["jobId"], "output": str(output), "assets": len(files)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
