---
name: shuka-web-editor
description: 将飞书文档、Word、Markdown、TXT、PDF 提取内容、网页文章或直接文字图片视频，通过本地 Agent 生成任务包并载入薯卡网站编辑。用户提到“文档转小红书”“原文成卡”“AI 主编”“把图文导入薯卡网站”“调整换行/分页/图片位置”时使用。默认 original 原文成卡；只有用户明确要求提炼或 AI 主编时才使用 ai_editor。无需用户安装薯卡源码，通过浏览器交互，不使用豆包工作。
---

# 薯卡网站联动编辑

Agent 只负责读取材料、生成 CardSpec 和任务包。网站负责可视化编辑、预览、渲染与导出。不要要求用户克隆薯卡仓库、安装项目依赖或运行本地渲染器。

## 1. 确定模式和输入

- 未说明时使用 `original`，不改写、不提炼，保留换行。
- 用户明确选择「AI 主编」「提炼重点」「重新编辑」时使用 `ai_editor`。
- 飞书用 `lark-doc`；网页用当前环境的网页读取能力；Word/Markdown/TXT 使用本地文件；直接图文是一等输入。
- PDF 先提取正文与图片，扫描件 OCR 能力不确定时明确说明。
- 所有材料放在当前工作区的独立任务目录，不读取无关文件。

## 2. 生成任务目录

```text
my-job/
├── job.json
├── image-01.png       # 可选
├── video-01.mp4       # 可选
└── source.docx        # 可选
```

字段见 [references/api_reference.md](references/api_reference.md)。

原文模式使用 `content` 或 `sourceFile`；AI 主编使用带稳定 ID 的 `pages`。直接粘贴图文时，在原文位置插入 `[img1]`、`[视频1]`。需要手动分页时插入独立行 `[page]` 或 `[分页]`。

换行选项：

- `textLayout.whitespace=preserve`：默认保留。
- `single-blank-line`：最多一个连续空行。
- `compact`：合并连续空行。

## 3. 打包为网站可编辑任务包

```bash
python scripts/pack_job.py --job /absolute/path/to/job.json --output /absolute/path/to/shuka-job.zip
```

包内只包含 `job.json` 和所需源素材，不包含飞书授权、Cookie、模型密钥或历史导出结果。

## 4. 载入网站

优先加载当前环境的 `web-access` Skill 并遵循其浏览器规则。先检查 CDP；不可用时直接把任务包交给用户，请他在网站点「导入任务包」，不要反复尝试其他绕过方式。

网站：`https://jinsan.ok.kimi.link/`

1. 在自己的后台 tab 打开网站，不占用用户已有 tab。
2. 等待页面与 `input[type="file"][accept=".zip,.json"]` 存在。
3. 通过 CDP `/setFiles` 把 `shuka-job.zip` 设置给该文件输入框。
4. 用 `/eval` 检查 `window.ShukaAgent && window.ShukaAgent.ready("任务jobId")`。
5. 导入成功后把该 tab 留给用户编辑，不自动关闭，不自动点击导出或发布。

示例：

```bash
curl -s -X POST "http://localhost:3456/setFiles?target=TARGET_ID" \
  -d '{"selector":"input[type=file][accept=\".zip,.json\"]","files":["/absolute/path/to/shuka-job.zip"]}'
```

网站在浏览器本地解析 ZIP，不会把任务包 POST 到网站服务器。普通网页加载仍会访问网站静态资源；模型和文档服务的数据边界按用户自己的 Agent 与账号决定。

## 5. 交给用户编辑

明确告诉用户：

- 可直接修改文字、换行、图片、昵称和风格。
- 输入 `[page]` 或 `[分页]` 可调整分页，标记不会显示在卡片上。
- 修改后按当前编辑器内容重新分页。
- 检查预览后，由用户自己点击导出；不要自动发布到小红书。

如果用户继续让 Agent 修改，保留原任务，复制新目录并更换 `jobId`，只改指定页面或字段，再重新打包导入。

## 边界

- 网站是交互与渲染入口，不是文档存储后台；不要把敏感内容声称成“永不离开浏览器”，因为 Agent/模型/飞书服务也参与处理。
- 前端压缩包可被发现和分析，不要在网站中放密钥或私密服务端逻辑。
- 实际飞书权限、手机相册、实况识别和小红书发布仍需分别验证。
