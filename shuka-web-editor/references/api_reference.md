# 网站任务包格式

ZIP 根目录必须有 `job.json`，素材使用相对路径。不要把 `output/`、飞书授权、Cookie、密钥或个人信息放入包内。

## 原文成卡

```json
{
  "jobId": "doc-original-v1",
  "mode": "original",
  "theme": "day",
  "textLayout": { "whitespace": "preserve" },
  "content": "第一段。\n\n[img1]\n\n第二段。",
  "assets": {
    "images": [{ "id": "img1", "path": "image-01.png" }],
    "videos": []
  }
}
```

也可以导入源文件：

```json
{
  "jobId": "word-v1",
  "mode": "original",
  "sourceFile": { "type": "docx", "path": "source.docx" }
}
```

`sourceFile.type` 支持 `docx`、`markdown`、`text`。Markdown 图片与源文件放在同一目录。

## AI 主编

```json
{
  "jobId": "doc-ai-v1",
  "mode": "ai_editor",
  "theme": "day",
  "pages": [
    { "id": "p1", "layout": "cover", "text": "封面标题", "media": [] },
    {
      "id": "p2",
      "layout": "mixed",
      "text": "一个重点\n\n==一句高亮==",
      "media": [{ "type": "image", "source_id": "img1", "position": "after_text" }]
    }
  ],
  "assets": {
    "images": [{ "id": "img1", "path": "image-01.png" }],
    "videos": []
  }
}
```

- `theme`：`day`、`night`、`x`。
- `layout`：`cover`、`text`、`image`、`video`、`mixed`、`summary`。
- 视频使用 `type=video`，素材路径位于 `assets.videos`。
- `liveTarget` 可选 `apple` / `android`，`liveSeconds` 可选 1–30。
- `note_title` 最多 20 字，`note_content` 最多 1000 字。
- 任务包（含素材）不能超过 250 MB，超过会被网站拒绝。
- 修改时更换 `jobId`，保持未修改页面的 ID 和内容。续改示例见 [examples/continue-edit/job.json](examples/continue-edit/job.json)。
