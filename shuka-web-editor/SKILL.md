---
name: shuka-web-editor
description: 将飞书文档、Word、Markdown、TXT、PDF 提取内容、网页文章或直接图文，通过本地 Agent 和薯卡网站默认直接生成并导出卡片成品，同时保留可编辑任务包。用户提到“文档转小红书”“原文成卡”“AI 主编”“直接生成薯卡”“调整换行/分页/图片位置”时使用。默认 original 原文成卡、直接出图；只有用户明确要求提炼或 AI 主编时才使用 ai_editor，只有用户要求编辑时才需要先进入网站修改。无需安装薯卡源码，不使用豆包工作。
---

# 薯卡网站联动编辑

Agent 负责读取材料、生成 CardSpec 和任务包，网站负责预览、渲染与导出。**默认直接给用户 PNG/ZIP 成品，同时保留可编辑任务包；编辑是可选步骤，不是必经步骤。**不要要求用户克隆薯卡仓库或安装项目依赖。

## 1. 确定模式和输入

- 未说明时使用 `original`，不改写、不提炼，保留换行。
- 用户明确选择「AI 主编」「提炼重点」「重新编辑」时使用 `ai_editor`。
- 用户明确说「先让我编辑」时才在导入后停下等待编辑，否则默认直接导出成品。
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

## 3. 打包为可编辑任务包

```bash
python scripts/pack_job.py --job /absolute/path/to/job.json --output /absolute/path/to/shuka-job.zip
```

包内只包含 `job.json` 和所需源素材，不包含飞书授权、Cookie、模型密钥或历史导出结果。这个包用于网站编辑备份，**不是最终卡片成品，不要把 `shuka-job.zip` 当成卡片 ZIP 交付。**

## 4. 导入网站并验证

优先加载当前环境的 `web-access` Skill 并遵循其浏览器规则。先检查 CDP；不可用时把任务包交给用户，请他在网站点「导入任务包」并点击导出，不要反复尝试其他绕过方式。

网站：`https://jinsan.ok.kimi.link/`

1. 在自己的后台 tab 打开网站，不占用用户已有 tab。
2. 等待 `input[type="file"][accept=".zip,.json"]` 出现。
3. 通过 CDP `/setFiles` 把 `shuka-job.zip` 设置给该输入框。
4. 用 `/eval` 检查 `window.ShukaAgent && window.ShukaAgent.ready("任务jobId")`。
5. 调用 `window.ShukaAgent.render()` 验证实际页数与内容，确认没有导入错误。

```bash
curl -s -X POST "http://localhost:3456/setFiles?target=TARGET_ID" \
  -d '{"selector":"input[type=file][accept=\".zip,.json\"]","files":["/absolute/path/to/shuka-job.zip"]}'
```

网站在浏览器本地解析 ZIP，不会把任务包 POST 到网站服务器。

## 5. 默认直接导出成品

只有用户明确要求先编辑时才跳过本步骤。

1. 在导出前记录 Unix 时间戳，例如 `date +%s`。
2. 如果页面出现「示例名片」提示或导出确认，先让用户修改头像、昵称和水印，或由用户明确选择保留；不得绕过确认直接导出。确认状态只保存在当前浏览器，用户修改后不应反复打断。
3. 通过 CDP `/eval` 点击页面上的「导出卡片」或「导出实况图文」按钮，不点击任何小红书发布按钮。
4. 等待浏览器完成下载，然后运行：

   ```bash
   python scripts/collect_export.py \
     --after <导出前时间戳> \
     --output /absolute/path/to/final-output
   ```

   脚本会在「下载」和「桌面」中查找本次 `xhs-card-*.png/.livp/.mp4` 或 `xhs-cards-*.zip`，校验后复制到结果目录。

5. 向用户交付：
   - 实际生成的 PNG、ZIP、实况或 MP4 路径与页数；
   - 可编辑备份 `shuka-job.zip`，并说明「不满意时可导入网站修改，不是必须编辑」。

浏览器阻止下载时，明确告诉用户需要在网站手动点击导出，不要声称已下载。出现实况助手安装或照片授权弹窗时，停止并让用户选择，不自动安装或授权。不得自动发布到小红书。

### 自动排查与自纠

- 缺图、占位图、读取失败或格式不支持必须报错，不能静默丢图后假装成功。
- 网站会检测超长图是否被过度缩小，按原比例自动分段，避免整页小字难读。
- 预览、导出按钮和成品必须使用同一套分段规则，页数不一致时停止交付并排查。
- `render()` 返回的 `warnings` 会说明第几张长图被分成几页，交付时如实展示。
- 导出后检查 ZIP 可读性与媒体数量，缺页或损坏不得称为成功。
- 这些属于规则型质量保障，不能替代语义、事实、审美和 OCR 可读性审查；效果不确定时交给用户检查，不宣称所有结果都完美。

## 6. 可选：先编辑再导出

用户说「先让我看看」「我要改一下」时，在导入后保留 tab，让用户直接修改文字、换行、图片、昵称和风格。

- 输入 `[page]` 或 `[分页]` 可调整分页，标记不会显示在卡片上。
- 修改后按当前编辑器内容重新分页。
- 用户检查预览后，由用户自己点击导出；需要时代为执行第 5 步。

继续让 Agent 修改时，保留原任务，复制新目录并更换 `jobId`，只改指定页面或字段，再重新打包导入。

## 边界

- 网站是交互与渲染入口，不是文档存储后台；模型、飞书和网页服务的数据边界取决于用户自己的账号与设置。
- 前端压缩包可被发现和分析，不要在网站中放密钥或私密服务端逻辑。
- 实际飞书权限、手机相册、实况识别和小红书发布仍需分别验证。
