薯卡网站联动 Skill · 新手体验包
================================

你不用先理解技术原理，按下面做就行。

如果你完全不用 Agent：
--------------------
直接打开 https://jinsan.ok.kimi.link/ ，粘贴文字和图片，或导入 Word。
这个压缩包可以不用下载。

如果你有本地 Agent：
------------------
1. 先解压本包，找到 shuka-web-editor.skill。
2. 在支持 .skill 的 Agent 里安装它。
   Kimi Agent 可将它解压到 ~/.agents/skills/：
   unzip shuka-web-editor.skill -d ~/.agents/skills/
   如果技能列表没有刷新，使用 /new 或 /reload。

3. 先体验一次，不用准备自己的文档：
   打开 https://jinsan.ok.kimi.link/
   点击「导入任务包」，选择本包里的 shuka-job-demo.zip。
   导入后直接修改文字、换行、分页和风格，再自己点击导出。

4. 再处理自己的文档，把这句话发给 Agent：
   用薯卡网站联动版，把这篇文档生成 shuka-job.zip：[粘贴飞书链接或上传文件]。
   默认原文成卡，不需要自动打开网站，我会手动导入。

   想让 AI 提炼时，再补一句：
   用 AI 主编，控制在 6 页。

5. Agent 生成新的 shuka-job.zip 后，再在网站点「导入任务包」。

自动导入（可选）：
----------------
如果你允许 Agent 操作浏览器，它也可以自动把任务包导入网站。
不会配置或导入失败时，使用上面的手动导入即可，不影响使用。

包内文件：
--------
- shuka-web-editor.skill：需要安装的联动 Skill
- shuka-job-demo.zip：可直接导入网站的示例
- original-job.json：原文成卡任务单示例
- ai-editor-job.json：AI 主编任务单示例

注意：
----
任务包在浏览器本地解析，不会 POST 到网站服务器。
但 Agent 使用的模型、飞书和网页服务的数据边界，取决于你自己的账号与设置。
敏感文档请谨慎处理，不要把授权文件、Cookie 或密钥放进任务包。

开源仓库：
https://github.com/ren644/shuka-web-editor
