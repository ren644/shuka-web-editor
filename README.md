# 薯卡网站联动 Skill · Shuka Web Editor

把飞书文档、Word、Markdown、TXT、网页文章或直接图文交给本地 Agent，默认通过[薯卡网站](https://jinsan.ok.kimi.link/)直接生成并导出卡片成品，同时保留可编辑任务包，需要时再修改。

**不需要下载薯卡源码，不需要本地部署渲染项目，不需要豆包工作。**

## 工作方式

```text
飞书 / Word / Markdown / TXT / 直接图文
                  ↓
        本地 Agent 生成 CardSpec
                  ↓
          shuka-job.zip 任务包
                  ↓
      薯卡网站本地解析并渲染导出
                  ↓
     默认交付 PNG / ZIP 成品
                  ↓
     需要时再导入任务包修改（可选）
```

网站负责交互与渲染，Skill 只负责材料整理和任务打包。任务包在浏览器本地解析，不会 POST 到网站服务器。

## 下载

**只需要下载一个文件：**

- [下载 shuka-web-editor.skill](https://github.com/ren644/shuka-web-editor/releases/latest/download/shuka-web-editor.skill)
- [打开薯卡网站](https://jinsan.ok.kimi.link/)

示例和说明都放在仓库里，不需要再下载新手包。

## 安装

以支持 `.skill` 的本地 Agent 为例。Kimi Agent 已实测，其他 Agent 可能需要调整安装目录和浏览器工具。

### 最省事：把链接和指令发给 Agent

**不用先手动下载文件。**把下面这段指令和文档链接一起发给 Agent：

```text
请从下面地址下载 shuka-web-editor.skill 并安装到当前 Agent，然后按默认原文成卡，把这篇文档直接生成并导出卡片成品，同时保留可编辑任务包，方便我之后修改：
Skill 下载地址：https://github.com/ren644/shuka-web-editor/releases/latest/download/shuka-web-editor.skill
文档地址：【粘贴文档链接】
```

Agent 会按公开链接自行下载并安装。**不需要额外安装工程，也不需要分别为 Mac 和 Windows 适配。**如果你的 Agent 不支持这种方式，再用下面的命令行。

### Kimi Agent 命令行安装示例

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

## 默认直接出成品，编辑可选

1. 安装 Skill。
2. 把飞书链接、Word 或图文交给 Agent。
3. 复制下面的指令给 Agent：

   ```text
   用薯卡网站联动版，把这篇文档直接生成并导出薯卡卡片：[粘贴飞书链接或上传文件]。
   默认原文成卡，同时保留可编辑任务包；如果我想修改，再导入网站。
   ```

4. Agent 会把任务导入网站、验证页数并默认导出成品。
5. 你直接下载 PNG 或卡片 ZIP 即可；`shuka-job.zip` 是编辑备份，不是卡片成品。
6. 需要改换行、分页或图片时，再把备份导入[薯卡网站](https://jinsan.ok.kimi.link/)修改并重新导出。

**第一次导出前请确认名片。**默认头像、昵称「金三啊」和水印「Created by JINSAN」都是示例。网站会提醒你修改或明确保留，确认状态只保存在当前浏览器；Agent 直出也会经过同一个确认，不会绕过。

如果浏览器自动化不可用，手动把任务包导入网站并点击导出即可，不需要先编辑。

## 自动排查与自纠

当前是**规则型质量保障**，不是“生成什么都说成功”：

- 缺图、占位图和读取失败会明确报错。
- 超长图会被检测并按原比例自动分段，避免整页小字难读。
- 预览、导出按钮和成品页数必须一致。
- `render()` 的 `warnings` 会说明哪张长图被分成几页。
- 导出后检查 ZIP 可读性和媒体数量。

它不能替代事实核查、语义判断、审美判断和 OCR 可读性检查；效果不确定时仍应让用户或 Agent 复核。

想让 AI 提炼时，补一句：

```text
用 AI 主编，控制在 6 页。
```

## 可选：自动导入网站

如果 Agent 支持浏览器文件操作，可以让它自动把任务包导入网站。以 `web-access` CDP 为例：

1. 在 Chrome 打开 `chrome://inspect/#remote-debugging`。
2. 允许当前浏览器实例进行远程调试。
3. Agent 在新的后台 tab 打开网站，通过文件输入框导入任务包。
4. 导入成功后默认导出成品；只有用户要求先编辑时才保留页面，不自动发布。

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

## 实况时长

- **3 秒以内**：导出真正的实况照片；苹果会自动写入「照片」（需 Mac 实况助手）。
- **超过 3 秒**：导出 MP4 视频，自己在手机上转实况。
- 任务单里 `liveSeconds` 可设 1–30；要实况就把时长压在 3 秒内。

## 支持的输入

| 输入 | 说明 |
|---|---|
| 飞书文档 | 需要相应文档读取能力与权限 |
| Word `.docx` | 支持正文与内嵌图片 |
| Markdown `.md` | 本地图片放在任务目录内，远程图片先用 `scripts/fetch_remote_assets.py` 下载 |
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

只依赖 Python 3 标准库。打包前会校验素材引用、重复 id 和字段取值，引用缺失或取值非法会直接报错；远程素材先用 `scripts/fetch_remote_assets.py` 下载到任务目录。

## 隐私与数据边界

- 本仓库不包含后端服务，也不要求用户公开薯卡源码。
- 任务包由用户的 Agent 在本地生成，并由网站在浏览器本地解析。
- **本地运行不等于内容永远不出电脑。** Agent 所用模型、飞书、网页读取和图片服务的数据处理，取决于用户自己的账号、工具和设置。
- 网站静态前端可能被发现和分析，不要在其中放 API Key、Cookie 或私密服务端逻辑。
- 不要提交真实文档、个人任务目录、授权信息或包含隐私的图片。
- 飞书权限、手机相册、实况识别和小红书发布需要分别验证；Skill 不会自动发布笔记。

## 许可

[MIT License](LICENSE)
