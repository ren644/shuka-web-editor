# 薯卡网站联动 Skill · Shuka Web Editor

把飞书文档、Word、Markdown、TXT、网页文章或直接图文交给本地 Agent，生成可编辑任务包，再导入[薯卡网站](https://jinsan.ok.kimi.link/)继续修改、预览和导出。

**不需要下载薯卡源码，不需要本地部署渲染项目，不需要豆包工作。**

## 工作方式

```text
飞书 / Word / Markdown / TXT / 直接图文
                  ↓
        本地 Agent 生成 CardSpec
                  ↓
          shuka-job.zip 任务包
                  ↓
      薯卡网站本地解析并载入编辑器
                  ↓
       用户修改、预览，并自行导出
```

网站负责交互与渲染，Skill 只负责材料整理和任务打包。任务包在浏览器本地解析，不会 POST 到网站服务器。

## 下载

- [下载最新 shuka-web-editor.skill](https://github.com/ren644/shuka-web-editor/releases/latest/download/shuka-web-editor.skill)
- [下载示例任务包](https://github.com/ren644/shuka-web-editor/releases/latest/download/shuka-job-demo.zip)
- [打开薯卡网站](https://jinsan.ok.kimi.link/)

## 安装

以支持 `.skill` 的本地 Agent 为例。Kimi Agent 已实测，其他 Agent 可能需要调整安装目录和浏览器工具。

### Kimi Agent 安装示例

把 `.skill` 文件解压到技能目录：

```bash
mkdir -p ~/.agents/skills
unzip shuka-web-editor.skill -d ~/.agents/skills/
```

安装后应存在：

```text
~/.agents/skills/shuka-web-editor/SKILL.md
~/.agents/skills/shuka-web-editor/scripts/pack_job.py
```

如果技能列表没有即时刷新，使用 `/new` 或 `/reload`。

## 最简单的使用方式：手动导入

这条路不需要开启浏览器自动化，推荐第一次使用。

1. 安装 Skill。
2. 把飞书链接、Word 或图文交给 Agent。
3. 复制下面的指令给 Agent：

   ```text
   用薯卡网站联动版，把这篇文档生成 shuka-job.zip：[粘贴飞书链接或上传文件]。
   默认原文成卡，不需要自动打开网站，我会手动导入。
   ```

4. Agent 生成任务包后，在[薯卡网站](https://jinsan.ok.kimi.link/)点「导入任务包」。
5. 直接修改文字、换行、分页、图片和风格，检查预览后自行导出。

想让 AI 提炼时，补一句：

```text
用 AI 主编，控制在 6 页。
```

## 可选：自动导入网站

如果 Agent 支持浏览器文件操作，可以让它自动把任务包导入网站。以 `web-access` CDP 为例：

1. 在 Chrome 打开 `chrome://inspect/#remote-debugging`。
2. 允许当前浏览器实例进行远程调试。
3. Agent 在新的后台 tab 打开网站，通过文件输入框导入任务包。
4. 导入成功后把页面留给用户编辑，不自动发布。

不能自动导入时，回到手动导入即可，不影响核心功能。

## 两种生成模式

### 原文成卡（默认）

- 不改写、不提炼、不总结。
- 保留原文顺序、换行和素材位置。
- 适合已经写好的文章、教程和逐字稿。

### AI 主编（用户主动选择）

- 自动提炼重点、重组逻辑页、安排图片和高亮。
- 可以只修改某一页，保留其他页面。
- 不应虚构事实、数据、案例或背书。

## 支持的输入

| 输入 | 说明 |
|---|---|
| 飞书文档 | 需要相应文档读取能力与权限 |
| Word `.docx` | 支持正文与内嵌图片 |
| Markdown `.md` | 本地图片放在任务目录内，远程图片先下载 |
| TXT `.txt` | 直接读取 UTF-8 文本 |
| 直接文字 + 图片/视频 | 一等输入，不必先建文档 |
| 网页、公众号文章 | 先读取正文与原图，再生成任务包 |
| PDF | 先提取正文与图片；扫描件需要 OCR |
| PPT、Excel | 先导出 PDF、复制内容或用对应文档能力整理 |

## 换行和分页

默认保留换行。可通过任务字段或自然语言调整：

- `textLayout.whitespace=preserve`：保留换行。
- `single-blank-line`：连续空行最多保留一个。
- `compact`：合并连续空行。
- 在 `content` 中单独一行写 `[page]` 或 `[分页]`，即可从新卡片开始，标记不会显示在图片中。

也可以直接对 Agent 说：

```text
空行少一点。
从这句话开始新一页。
只改第 2 页，其他页面不要动。
把图片移到这段后面。
```

## 任务包与示例

`shuka-job.zip` 根目录包含 `job.json` 和所需原始素材，不包含飞书授权、Cookie、模型密钥或历史导出结果。

- 字段说明：[shuka-web-editor/references/api_reference.md](shuka-web-editor/references/api_reference.md)
- 原文示例：[examples/original/job.json](examples/original/job.json)
- AI 主编示例：[examples/ai-editor/job.json](examples/ai-editor/job.json)
- 可导入网站的示例：[examples/shuka-job-demo.zip](examples/shuka-job-demo.zip)

手动打包：

```bash
python3 shuka-web-editor/scripts/pack_job.py \
  --job /absolute/path/to/job.json \
  --output /absolute/path/to/shuka-job.zip
```

只依赖 Python 3 标准库。

## 隐私与数据边界

- 本仓库不包含后端服务，也不要求用户公开薯卡源码。
- 任务包由用户的 Agent 在本地生成，并由网站在浏览器本地解析。
- **本地运行不等于内容永远不出电脑。** Agent 所用模型、飞书、网页读取和图片服务的数据处理，取决于用户自己的账号、工具和设置。
- 网站静态前端可能被发现和分析，不要在其中放 API Key、Cookie 或私密服务端逻辑。
- 不要提交真实文档、个人任务目录、授权信息或包含隐私的图片。
- 飞书权限、手机相册、实况识别和小红书发布需要分别验证；Skill 不会自动发布笔记。

## 许可

[MIT License](LICENSE)
