# DocuRule 发布与增长执行包

> 状态：执行中。GitHub Release、GitHub Discussion 与知乎已有公开内容；当前 Chrome 会话的 X 仍停在登录页，尚未发布 X 内容；HN、Reddit、V2EX、掘金等仍不得自动发布。事实快照与平台规则复核日期：2026-08-13。
>
> 本文只是一套发布前工作稿。平台规则会变化；每次发帖前必须重新打开对应规则页。Hacker News 与 r/LocalLLaMA 对 AI 生成文案有明确限制，因此相关草稿只能帮助作者梳理事实，不能原样复制发布。

## 0. 发布控制台

### 0.1 当前结论

- 公开仓库：<https://github.com/wangyinlong-wang/docurule-ai>
- 版本线：`v0.2.0` 首次发布采购 Hero；`v0.2.1` 增加公开 recipe/golden fixture；`v0.3.0` 增加安全、可执行的 schema-v1 YAML recipes；`v0.4.0` 增加可审计 CSV 字段导出；`v0.5.0` 增加 provider-aware 空字段提示；`v0.5.1` 增加上传扩展名/MIME 配对校验；当前 Latest Release `v0.5.2` 增加五分钟 Recipe 贡献路径并修复 `make demo`。仓库创建于 2026-08-12，属于不足 3 个月的新项目。
- 当前首发 Hero：合成的采购三单匹配 Demo（采购订单 + 发票 + 收货单），`3 documents · 8 normalized fields · 6 rules · 2 exceptions · 1 review decision`。
- 初始结果固定为 `4 passed / 2 failed`；把 `Received quantity` 从 `90` 改为 `96` 后重新校验为 `6 / 6 passed`。内置 Demo 不调用 AI provider。
- README 当前动态 GIF 为 `docs/assets/docurule-recipe-demo.gif`，502,499 bytes（约 491 KB）、14.7 秒；`docs/assets/docurule-demo.gif` 是 v0.2 的 16.0 秒旧版演示。医疗理赔 Demo 作为第二场景保留。
- 无需安装的浏览器演示已公开：<https://wangyinlong-wang.github.io/docurule-ai/>。它只使用合成数据，在浏览器标签页内运行，不上传文件、不连接后端且刷新即清空。
- 首发只承诺可验证的功能，不承诺 Star 数、准确率、节省时间或生产可用性。
- 已公开一篇知乎文章及其项目更新；GitHub Discussion #18 已作为 Show and tell 入口。X 当前仍需作者在登录后亲自确认账号状态再发布；尚未发布 HN、Reddit、V2EX、掘金或 LinkedIn 内容。未发布平台的草稿仍须作者按平台规则复核。

### 0.2 发布前必须逐项确认

- [ ] 作者亲自在干净环境执行 README 的 `docker compose up --build`，并记录操作系统、CPU/内存、总耗时与结果。
- [ ] 作者点击采购 Demo，核对初始结果为 `3 documents / 8 normalized fields / 6 rules / 4 passed / 2 failed`；把 `Received quantity` 从 `90` 改为 `96`，核对 `6 / 6 passed`，再完成批准或拒绝与 JSON 导出。
- [ ] GitHub 上的 `v0.5.2` tag 与 Latest Release 已公开可见；README 默认分支已提供 v0.3 recipe Hero、v0.4 CSV 导出、v0.5 空字段提示、v0.5.1 上传校验、v0.5.2 贡献入口与浏览器演示入口。（待本轮发布后核验）
- [x] **采购三单匹配已在公开 `v0.2.0` 合入：** API/engine tests 覆盖三文档、8 个目标 normalized fields、6 条规则、初始 4 pass + 2 fail，以及修正后 6/6。
- [x] **当前动态 Demo 已生成：** `docs/assets/docurule-recipe-demo.gif`，502,499 bytes、14.7 秒；README 已引用该素材。
- [ ] 已从公开页面核验 README Hero、Latest Release `v0.5.2` 与无需登录的 GitHub Pages 演示。（待本轮发布后核验）
- [x] GitHub Social Preview 已上传 1280×640 成图；公开仓库 HTML 的 `og:image` 已指向 `repository-images.githubusercontent.com`。
- [ ] 作者确认 AI 在**代码、测试、文档和发帖文案**中的真实参与方式，填写各渠道的 `AI Involvement`/披露占位；不得写成模糊的“少量辅助”来规避社区规则。
- [ ] 在发帖当天重新检查 Show HN、目标 subreddit、V2EX、掘金、知乎规则；若与本文冲突，以当天规则为准。
- [ ] 作者能在首帖后的 4–6 小时保持在线，并在首日及时回复技术问题。
- [ ] 不向朋友、群聊或其他平台索要 HN/Reddit 点赞；不购买、不交换、不抽奖换 Star。

### 0.3 已公开内容与信号快照

截至 2026-08-13（Asia/Shanghai）：

- X：当前 Chrome 会话显示登录入口，尚无已核验的公开帖；不要把草稿或失败提交写成已发布。
- GitHub Release：<https://github.com/wangyinlong-wang/docurule-ai/releases/tag/v0.5.2>（待本轮发布后核验）
- GitHub Discussion：<https://github.com/wangyinlong-wang/docurule-ai/discussions/18>，已追加 v0.5.0/v0.5.1 更新；v0.5.2 发布后再追加贡献路径更新
- 知乎长文：<https://zhuanlan.zhihu.com/p/2071029793122939690>，正文含 v0.4 CSV 导出与在线演示链接
- Issues [#3 上传类型校验](https://github.com/wangyinlong-wang/docurule-ai/issues/3)、[#4 CSV 导出](https://github.com/wangyinlong-wang/docurule-ai/issues/4) 与 [#5 空字段提示](https://github.com/wangyinlong-wang/docurule-ai/issues/5) 已关闭（分别在 v0.5.1、v0.4.0 与 v0.5.0 实现）；新增 good-first 贡献入口：[#19 文档化 CSV 导出契约](https://github.com/wangyinlong-wang/docurule-ai/issues/19)。当前公开列表有 3 个可认领的 good-first issue。
- 已出现首个外部 fork 与首位贡献者 PR（[#6](https://github.com/wangyinlong-wang/docurule-ai/pull/6)）。该 PR 基于旧版 `main`，与 v0.5.1 存在冲突；维护者已留下说明并关闭，功能由 v0.5.1 当前实现覆盖，未强行合入过时改动。

不要把 fork 或 PR 换算成“社区采用”。它们只用于决定下一步：优先帮助真实贡献者完成合入，并继续测试在线 Demo 到 GitHub 的转化。

## 1. 统一产品事实表（single source of truth）

发布者应从这张表取事实。标为“待确认/roadmap”的内容不能写成现成功能。

| 事实 | 可公开表述 | 证据/边界 |
|---|---|---|
| 名称 | `DocuRule`；仓库名 `docurule-ai` | README 与仓库 |
| 定位 | Open-source, local-first document intelligence for cross-document validation and human review | 不写“完整企业 IDP 平台” |
| 核心差异 | 处理一组相关文档；字段带证据；确定性校验优先；人工做最终决定 | README 的 Why / How it works |
| 许可证 | MIT | `LICENSE` 与 GitHub 仓库元数据 |
| 成熟度 | Early, working MVP | 不写 production-ready、enterprise-ready 或 battle-tested |
| 当前功能版本 | `v0.5.2` | `v0.2.0` 首发采购 Hero；`v0.2.1` 增加公开 recipe/golden fixture；`v0.3.0` 增加安全可执行 YAML recipe runtime；`v0.4.0` 增加可审计 CSV 字段导出；`v0.5.0` 增加 provider-aware 空字段提示；`v0.5.1` 增加上传扩展名/MIME 配对校验；`v0.5.2` 增加五分钟 Recipe 贡献路径并修复 `make demo` |
| Hero Demo | 合成采购资料：采购订单 + 供应商发票 + 收货单；不需要模型或 API Key | 所有机构、编号、数量和金额均为虚构；Demo 强制 rules-only |
| Hero 实测摘要 | 3 份文档、8 个 normalized fields、6 条规则、初始 4 pass + 2 fail、1 次人工决定 | 把 received quantity `90 → 96` 后为 6/6 passed；API/engine tests 覆盖 |
| 第二场景 | 合成医疗理赔资料：发票 + 理赔表 | `/api/v1/demo` 保留；不作为首发 Hero |
| 上传格式 | PDF、PNG、JPG、Markdown、text；默认每个文件 20 MB | 图片处理需要合适的视觉模型/provider |
| PDF | 使用 `pypdf` 提取带文本层 PDF | 不宣称完整 OCR 或任意复杂版式解析 |
| AI provider | Ollama 原生 API；OpenAI-compatible chat-completion API | “OpenAI-compatible”不等于验证了每个供应商/模型 |
| 无模型路径 | 内置 Demo 可离线运行；provider 不可用时有 rules-only fallback | 不等于所有真实图片都能无模型解析 |
| 数据与部署 | Docker Compose 单容器；SQLite、本地文件存储、Docker volume | 若配置远程 provider，文档内容会按配置发给远程端点 |
| 当前校验 | 采购 Hero：文档齐全、供应商、PO 号、币种、数量、金额/已收货价值；医疗示例：存在性、姓名和金额等；schema-v1 recipes 支持 3 个 allowlisted 断言 | 不写“支持任意业务规则” |
| 人工复核 | 字段可编辑；可批准或拒绝；导出 JSON 审计记录 | 不宣称多用户队列、RBAC 或不可篡改审计 |
| 证据 | 字段包含置信度和 source quote | 坐标高亮与页内预览仍是 roadmap |
| API | 创建案件、Demo、读取、修正字段、人工决定、JSON/CSV 导出、读取与执行 YAML recipe；`/docs` 提供 OpenAPI UI | JSON 是完整审计源；CSV 是一行一个 normalized field 的审阅视图 |
| 前端/后端 | React + TypeScript；FastAPI | 当前小型单应用架构 |
| 采购三单匹配 | 从 `v0.2.0` 起提供；`v0.3.0` 起同一份公开 `rules.yml` 可通过 UI/API 执行；`v0.4.0` 可导出一行一个 normalized field 的 CSV；`v0.5.0` 对空字段状态给出 provider-aware 指引；`v0.5.1` 在普通上传入口校验扩展名/MIME 配对 | 使用 3 docs、8 fields、6 rules、4/6→6/6 的实测数字 |
| 动态 GIF | 当前 `docs/assets/docurule-recipe-demo.gif`，502,499 bytes、14.7 秒 | v0.2 的 16 秒 GIF 仍保留但不再是 README Hero |
| 在线演示 | `https://wangyinlong-wang.github.io/docurule-ai/` | 浏览器内合成 packet；不上传、不持久化，不代表真实文件处理能力 |
| Social Preview | `docs/assets/social-preview.png`，1280×640 | 已上传 GitHub；公开 `og:image` 已切换到 repository image |
| 真实准确率 | 未建立可泛化 benchmark | 不给百分比，不与 OCR/IDP 产品做准确率排名 |
| 隐私/安全 | 默认本地保存；可配本机 Ollama | 不写“100% private/secure”“数据绝不离开机器”；远程 provider 是明确例外 |
| 目标行业 | 可用于探索财务、保险、KYC、法务、供应链等 packet workflow | 当前只验证了合成 Demo，不能说已在这些行业落地 |

### 1.1 统一一句话

英文：

> DocuRule is an open-source, local-first workspace that turns related document packets into grounded fields, deterministic checks, and a human-reviewed JSON decision.

中文：

> DocuRule 是一个开源、本地优先的文档核验工作台：把一组相关资料变成带原文证据的字段、确定性校验和人工确认后的 JSON 结论。

### 1.2 统一 Quick Start

```bash
git clone https://github.com/wangyinlong-wang/docurule-ai.git
cd docurule-ai
docker compose up --build
```

打开 <http://localhost:8080>，点击 **Explore the demo**。这句话只用于当前 README 对应的内置合成 Demo；14.7 秒是 README GIF 时长，不是性能承诺。只想先理解流程时，可直接打开无需安装的浏览器演示：<https://wangyinlong-wang.github.io/docurule-ai/>。

### 1.3 统一限制说明

> DocuRule is an early MVP. The bundled synthetic demo is deterministic, but real image-only documents need a compatible vision model. Text-layer PDFs use pypdf. Custom extraction schemas, PDF/image recipe packets, additional rule operators, coordinate highlights, and multi-user review queues remain roadmap items.

### 1.4 不能混淆的两个“本地”

- **可以说：** 内置合成 Demo 无需云 API；默认文件和 SQLite 数据保存在本地 Docker volume；可连接本机 Ollama。
- **必须补充：** 配置 OpenAI-compatible 远程 provider 时，文档会发送到用户指定的远程端点。
- **不可以说：** “任何模式都不联网”“所有数据永远不会离开设备”“完全安全”。

## 2. 2026-08 平台自推广规则

### 2.1 Show HN / Hacker News

关键规则：

- Show HN 必须是作者亲自做、用户现在可以试用的非 trivial 项目；标题以 `Show HN:` 开头，最好无需注册或留邮箱。
- 提交原始来源；不要使用夸张标题、全大写或营销形容词。
- 不要让朋友点赞或评论，不要索要投票，也不要删除后重发。
- HN 不应主要用于推广；自有项目只能是正常社区参与的一部分。
- **当前 HN Guidelines 明确写着不要发布 generated text 或 AI-edited text。** 因此第 3 节只能作为事实提纲。作者必须脱离草稿，用自己的经历和语气重新写第一条评论。
- 若新账号遇到 Show HN 临时限制，先正常参与社区，不规避限制。

发布门槛：项目可立即运行；作者亲写文字；作者能在线讨论；不组织任何投票。

来源：[Show HN Guidelines](https://news.ycombinator.com/showhn.html)、[Hacker News Guidelines](https://news.ycombinator.com/newsguidelines.html)、[Show HN temporary restrictions](https://news.ycombinator.com/showlim)。

### 2.2 Reddit 通用、r/selfhosted 与 r/LocalLLaMA

Reddit 通用：

- 官方 2026 Spam 指南禁止重复或未经请求的大规模互动、重复群发和用自动化/生成式 AI 扩散 spam。
- 宣传内容本身不一定是 spam，但各社区可以更严格；账号若主要发自己受益的链接，应降低频率、参与真实讨论，疑问先问版主。
- 禁止多账号、组织群体或自动化操纵投票；不在其他平台喊人给 Reddit 帖子投票。

`r/selfhosted`：

- 当前规则要求被推广的应用可 self-host、已发布可下载/试用、有最小安装文档；帖子需解释用途、功能和对 self-hoster 的价值。
- **不足 3 个月的新项目只能发布在当前周 `New Project Megathread`，不能发独立帖。** DocuRule 创建于 2026-08-12，首发必须以当周 Megathread 的顶层评论形式出现。
- Megathread 当前模板要求：Project Name、Repo/Website、Description、Deployment、AI Involvement。必须真实披露 AI 参与。
- 发布时先在 r/selfhosted 搜索最新的 `New Project Megathread`；不要复用本文引用的旧周链接。

`r/LocalLLaMA`：

- 帖子必须与 LLM/local model 直接相关，先搜索已有内容，拒绝 low-effort。
- 自推广以不超过内容历史的约 1/10 为指导线，必须披露 affiliation，不能装成“偶然发现”。
- 规则明确禁止 completely/primarily LLM-generated copy 与 code；非英语母语作者若只用 LLM 翻译/润色，必须清楚披露。
- 因 DocuRule 开发过程存在 AI 协作，且本文是 AI 辅助草稿，**在作者确认代码参与方式、账号已有足够真实社区参与、并向版主确认可接受性之前，不发布。** 这不是 Day 0 必选渠道。

来源：[Reddit Spam](https://support.reddithelp.com/hc/en-us/articles/360043504051-Spam)、[Reddit community disruption / vote manipulation](https://support.reddithelp.com/hc/en-us/articles/360043066412-Disrupting-Communities)、[r/selfhosted 当前新项目机制示例](https://www.reddit.com/r/selfhosted/comments/1ulvzjo/new_project_megathread_week_of_02_jul_2026/)、[r/LocalLLaMA rules](https://old.reddit.com/r/LocalLLaMA/about/rules)。

### 2.3 V2EX

- 官方帮助明确欢迎独立开发者在 **分享创造 `/go/create`** 发布新作品并获取第一批用户反馈。
- 企业营销内容应进入 **推广 `/go/promotions`**；持续把营销内容放错节点可能影响账号。
- DocuRule 是免费开源项目，正文以开发过程、可复现 Demo 和反馈请求为主时选“分享创造”；若内容改成商业服务、付费版或营销活动，则改投“推广”。
- 每个主题只能选一个节点；发布后 10 分钟内可以自行移动。不要重复发相同内容到多个节点。
- 2026-05 更新的“好好说话”页要求尽量描述事实、提供建设性增益，并明确不要把 AI 生成的回复冒充自己的回复。第 5.1 节只能作为作者的事实底稿；作者应亲自改写主题，后续回复也不能原样复制第 9 节模板冒充个人回答。

来源：[V2EX 节点帮助](https://www.v2ex.com/help/node)、[V2EX 好好说话](https://www.v2ex.com/help/assertive)。

### 2.4 掘金

- 稀土掘金用户协议要求内容文明、理性、友善、高质量且真实；禁止商业广告、类似商业招揽、过度营销与垃圾信息。
- 内容应原创或拥有授权，不泄露隐私、不做虚假信息。
- 协议要求发布/传播利用深度学习等技术生成的信息时显著标识或提示。因此若使用本发布包组织/润色文章，文首保留 AI 辅助披露。
- 实操上以“可复现技术文章”为主体：给出问题、架构取舍、命令、失败边界和代码链接；只放一个自然的仓库 CTA，不写成产品广告页。

建议披露（作者按真实情况修改）：

> 说明：本文在资料整理与文字润色中使用了生成式 AI；项目事实、命令、截图和技术判断由作者逐项复核。项目代码中的 AI 参与方式见文末披露。

来源：[稀土掘金用户协议](https://lf3-cdn-tos.draftstatic.com/obj/ies-hotsoon-draft/juejin/86857833-55f6-4d9e-9897-45cfe9a42be4.html)（重点看 5.2、5.4）。

### 2.5 知乎

- 知乎将“以推广曝光为目的、影响体验或扰乱秩序”的内容视为垃圾广告风险；重视专业可信、内容详实、有启发的内容。
- 禁止强制、诱导或雇佣用户点击、分享、赞同、关注；禁止短期重复发布相同回答、批量带推广链接、私信导流或作弊。
- 不要为了介绍项目自问自答多个问题。优先发一篇能独立成立的技术文章，或只回答一个高度相关的既有问题；明确自己是作者。
- 只在结尾放一次 GitHub 链接，不以 Star 作为阅读或更新条件。若使用 AI 辅助撰写，按发布界面和当日规则做显著披露，并由作者核验全部事实。

来源：[知乎盐值 / 遵守公约指数](https://www.zhihu.com/term/credit)、[知乎机构号使用规范（其中多项举例同时涵盖普通用户）](https://www.zhihu.com/org_use_norm)、[知乎协议](https://www.zhihu.com/term/zhihu-terms)。

## 3. Show HN 完整事实稿（作者必须亲自重写）

> **不可原样发布：** HN 当前禁止 generated 或 AI-edited text。下面提供的是结构完整的事实 briefing，方便作者用自己的英语、开发动机和真实经历重新写。提交类型为 GitHub URL + 作者第一条评论，不是长篇 landing-page 广告。

### 3.1 标题

```text
Show HN: DocuRule – Local three-way document matching with auditable rules
```

如果作者更希望强调通用品类，可用：

```text
Show HN: DocuRule – Local-first cross-document validation with human review
```

不要添加 `best`、`revolutionary`、`100% private`、Star 数目标或感叹号。

### 3.2 提交 URL

```text
https://github.com/wangyinlong-wang/docurule-ai
```

### 3.3 第一条评论事实稿

```text
Hi HN — I built DocuRule because extracting JSON from one PDF was not the end of the document workflows I was dealing with. The next step was usually a collection of ad-hoc code and spreadsheets: compare values across related files, explain a mismatch, let a person correct it, and keep the decision trail.

DocuRule is an early MIT-licensed MVP for that layer. It accepts a packet of PDFs, images, Markdown, or text; attaches a source quote and confidence to extracted fields; runs deterministic checks; and lets a reviewer edit values, approve or reject the case, and export JSON.

The current built-in sample is a synthetic procurement three-way match: a purchase order, supplier invoice, and delivery note. It normalizes eight fields and starts with four passing checks and two failures because the invoice quantity and total exceed the goods received. Changing received quantity from 90 to 96 re-runs the checks and makes all six pass. The sample is deterministic, so it can be tried without an API key or a running model.

Image-only documents outside the sample need a compatible vision model. The provider boundary supports Ollama and OpenAI-compatible endpoints, and the app falls back to text rules when a provider is unavailable. A separate synthetic medical-claim sample remains available to exercise name and amount consistency checks.

The implementation is deliberately small for now: React/TypeScript, FastAPI, SQLite and local file storage in one Docker Compose application.

To try it:

git clone https://github.com/wangyinlong-wang/docurule-ai.git
cd docurule-ai
docker compose up --build

Then open http://localhost:8080 and run the built-in demo.

This is not an OCR benchmark or a production-ready workflow system. Text-layer PDFs currently use pypdf. Schema-v1 YAML recipes are executable today; custom extraction schemas, PDF/image recipe packets, richer OCR/layout adapters, page-coordinate highlights, additional operators and multi-user queues are still on the roadmap.

I would especially value feedback on the boundary between deterministic rules and model-assisted extraction, and on the smallest useful recipe format for real document packets. I will be here to answer implementation questions.
```

作者重写时必须补入真实的“为什么做”细节，并删掉自己无法亲口解释的句子。Show HN CTA：**本地运行 Demo，然后指出规则/模型边界哪里设计错了。** 不在 HN 请求 Star 或投票。

## 4. Reddit 两个差异化版本

### 4.1 r/selfhosted：当周 New Project Megathread 顶层评论

> 不发独立帖。发布前找到当周最新 Megathread，并按帖子要求调整字段。若作者/项目使用 AI，必须真实填写 `AI Involvement`。

````markdown
**Project Name:** DocuRule

**Repo/Website Link:** https://github.com/wangyinlong-wang/docurule-ai

**Description:**

DocuRule is an MIT-licensed, local-first workspace for reviewing related document packets. I built it for the step after PDF-to-JSON: compare fields across files, show where each value came from, run deterministic checks, and keep a human in control of the final decision.

The current early MVP includes:

- mixed PDF, PNG, JPG, Markdown and text uploads;
- text-layer PDF extraction, with Ollama or an OpenAI-compatible provider for vision extraction;
- grounded fields with confidence and source quotes;
- packet-level presence, name and amount checks;
- procurement three-way-match checks for required documents, supplier, PO number, currency, quantity and received value;
- a three-document synthetic sample with eight normalized fields and six rules (four pass/two fail initially; all six pass after correcting received quantity from 90 to 96);
- editable fields, approve/reject decisions and JSON audit export;
- a synthetic, deterministic built-in demo that needs no API key.

It is intentionally not presented as production-ready. Schema-v1 YAML recipes support three allowlisted assertion types today; complex OCR/layout parsing, custom extraction schemas, PDF/image recipe packets, coordinate highlights, additional operators and multi-user queues are roadmap items.

**Deployment:**

One Docker Compose application with React, FastAPI, SQLite and local file storage. The default persistent data lives in a Docker volume.

```bash
git clone https://github.com/wangyinlong-wang/docurule-ai.git
cd docurule-ai
docker compose up --build
```

Open http://localhost:8080 and click the built-in demo. No cloud API is needed for that synthetic demo. Real image-only documents need a compatible vision model; if you configure a remote OpenAI-compatible endpoint, the document data is sent to that endpoint.

**AI Involvement:**

[AUTHOR: replace this bracket with an accurate disclosure covering both product functionality and how AI assisted the code/tests/docs. Do not publish until completed.]

If you try it, I would appreciate the exact Docker/OS setup and the first step that was unclear or failed. Issues with reproduction are more useful to me than general praise.
````

若 Megathread 不支持嵌套 fenced code block，把三条命令改为三行普通文本。CTA：**报告 Quick Start 的第一个卡点，并附 Docker/OS 环境。** 不要求 upvote 或 Star。

### 4.2 r/LocalLLaMA：Ollama 与规则边界版

> **条件式稿件。** 只有当作者账号满足有意义社区参与、作者确认代码并非违反该社区的“primarily LLM-generated code”禁令、作者亲自重写正文，并在不确定时获得版主同意后才使用。否则跳过该渠道。

建议 flair：发布当天从现有 flair 中选择最接近的 `Resources` 或 `Other`，不要猜测不存在的 flair。

建议标题：

```text
I built a local document validation workspace around Ollama and deterministic rules
```

事实稿（作者亲自重写；若只是用 AI 翻译/润色，按 Rule 3 明确披露）：

```markdown
Disclosure: I am the author of DocuRule. [AUTHOR: accurately disclose any AI assistance in the code and in translating/refining this post.]

I have been experimenting with where a local vision model should stop in a document workflow.

For extracting a field from a scan, a vision model can be useful. For checking whether two normalized amounts are equal, whether a required document exists, or whether an invoice exceeds another amount, I do not want the model to improvise. I want a readable, testable deterministic result with the source value still attached.

That experiment became DocuRule, an early MIT-licensed local-first app. Its provider boundary speaks Ollama's native API as well as OpenAI-compatible chat-completion APIs. A packet is classified and extracted into fields with confidence/source quotes; deterministic checks run next; then a reviewer can correct values, approve or reject, and export JSON.

The bundled synthetic procurement demo deliberately runs without a model, which also exercises the rules-only path. It starts with two deterministic exceptions and re-runs all six checks after a field correction. Real image-only files require a compatible vision model. I am not claiming a cross-model accuracy result: there is no general benchmark yet, and text-layer PDFs currently use pypdf.

Docker quick start and code:
https://github.com/wangyinlong-wang/docurule-ai

I would value concrete local-model feedback on two questions:

1. Which structured-output/vision model and hardware combination should be in a small reproducible test matrix?
2. Which extraction uncertainty should trigger a human review instead of a second model call?
```

CTA：**贡献一个可复现的本地模型/硬件结果，或回答上面两个工程问题。** 不把相同正文复制到其他 subreddit，不请求投票。

## 5. 中文渠道稿件

### 5.1 V2EX「分享创造」完整稿

> 这是 AI 辅助的事实底稿，不应冒充作者自己的原文。作者发布前应结合真实开发动机亲自重写；发布后的评论回复也由作者本人作答。

标题：

```text
[开源] DocuRule：PDF 转 JSON 之后，把跨文档核验和人工复核补上
```

正文：

```markdown
大家好，我做了一个早期的开源项目 DocuRule，想请大家试跑并直接挑问题。

它不是另一个 OCR 或 PDF 转 Markdown 工具。我遇到的实际问题是：一组相关资料被解析成 JSON 以后，仍然要继续核对姓名、日期、编号和金额是否一致；异常值要能回到原文；最后还要让人修改并确认结论。

所以现在这个 MVP 先做了四件事：

1. 一次上传一组 PDF、PNG、JPG、Markdown 或文本；
2. 字段保留置信度和原文引用；
3. 文档齐全、姓名和金额等检查优先走确定性规则；
4. 人可以修改字段、批准或拒绝，并导出 JSON 审计记录。

首发 Demo 使用完全合成的采购订单、供应商发票和收货单。系统规范化 8 个字段，跑 6 条确定性规则：初始 4 条通过、2 条失败，因为发票数量和金额超过已收货数量/价值；把 `Received quantity` 从 `90` 改为 `96` 后会立即重跑为 6/6 通过。医疗理赔的双文档示例也继续保留。

项目采用 MIT License。当前技术栈比较克制：React + TypeScript、FastAPI、SQLite、本地文件存储，一个 Docker Compose 应用。支持 Ollama 原生接口和 OpenAI-compatible 接口；模型不可用时会退回文本规则。内置的合成 Demo 不需要模型或 API Key。

启动：

git clone https://github.com/wangyinlong-wang/docurule-ai.git
cd docurule-ai
docker compose up --build

然后访问 http://localhost:8080，点击内置 Demo。

仓库：https://github.com/wangyinlong-wang/docurule-ai

先把限制说清楚：它还是 early MVP。带文本层 PDF 目前用 pypdf；复杂 OCR/版式解析、页内坐标高亮、可配置规则模板和多人复核队列都还在 roadmap。真实图片需要兼容的视觉模型；如果配置远程 provider，文档会发送到你指定的远程端点。

我这次最想收集的不是泛泛的“不错”，而是两个具体反馈：

- 你在什么系统和 Docker 版本上跑，第一处卡住在哪里？
- 对“模型只做抽取，确定性逻辑交给规则”这个边界，你会怎么改？

如果愿意试跑，直接在帖子或 GitHub Issue 留复现步骤即可，我会逐条处理。
```

发帖时优先附上当前 README 使用的约 14.7 秒、491 KB `docs/assets/docurule-recipe-demo.gif`；旧版 16 秒、2.3 MB GIF 只在需要讲 v0.2 历史时使用。

CTA：**给出系统/Docker 环境与第一个复现卡点。** “开源项目”放分享创造；若后来增加付费产品营销，改投推广节点。

### 5.2 掘金技术文章完整大纲

标题：

```text
PDF 转 JSON 只完成了一半：我如何把跨文档核验拆成抽取、规则和人工复核
```

文首披露：

```text
说明：本文在资料整理与文字润色中使用了生成式 AI；项目事实、命令、截图和技术判断由作者逐项复核。[作者补充代码开发中的真实 AI 参与方式。]
```

文章大纲（建议 1,800–2,500 字，必须加入作者自己的设计过程与实际截图）：

1. **问题不是“读出一个 PDF”**
   - 单文件抽取输出之后，仍要跨文件比对姓名、编号、日期和金额。
   - 审核人员需要知道值从哪里来，以及谁改过、为什么批准。
   - 用当前 `v0.5.2` recipe Hero GIF/截图开场：3 份文档、8 个 normalized fields、6 条规则、2 个初始异常，并展示 `rules.yml` 的同源执行、CSV 导出、空字段提示、上传类型边界与五分钟贡献路径。
2. **为什么不把所有检查都写进 prompt**
   - 模型适合从复杂输入提取候选字段。
   - 相等、存在性、金额比较等应可读、可测、可重复。
   - 不声称 LLM 一定不可靠；只解释工程边界和可审计性。
3. **当前 MVP 的五步链路**
   - packet 上传 → 分类/抽取 → 字段规范化与 source quote → 确定性校验 → 人工决定与 JSON 导出。
   - 说明 provider error 不会静默捏造字段，而是暴露当前 engine 并回退文本规则。
4. **为什么先做成一个小应用**
   - React/TypeScript + FastAPI + SQLite + 本地存储。
   - 单容器 Docker Compose 降低首次试跑成本。
   - 当前结构不是性能或生产架构结论。
5. **快速复现**
   - 原样放第 1.2 节三条命令。
   - 写清内置 Demo 无需模型；真实图片需要兼容视觉模型。
   - 配置远程 provider 时补充数据边界。
6. **当前能做与明确不能做**
   - 能做：事实表中已验证功能。
   - 不能做：复杂 OCR/版式 benchmark、坐标高亮、任意规则模板、RBAC/多人队列。
7. **下一步如何选择**
   - 解释三单匹配的初始 4/6 与修正 `90 → 96` 后 6/6；不把单个合成 fixture 泛化成准确率。
   - 邀请读者提供脱敏/合成的 packet recipe，而不是上传敏感真实资料。
8. **结尾 CTA**
   - “如果你正在拼 OCR + 规则脚本 + 人工表格，请按 README 跑一次合成 Demo，把第一个卡点或最想贡献的 recipe 留在 Issue。”
   - 只放一次仓库链接，不以点赞、关注或 Star 为更新条件。

推荐标签：`人工智能`、`Python`、`Docker`、`开源`；以发布界面当天实际可选标签为准。

### 5.3 知乎文章大纲

标题：

```text
PDF 转成 JSON 以后，企业文档自动化为什么仍然没有结束？
```

不要创建多个自问自答问题。优先发布为文章；若回答已有问题，必须让文章独立解决问题，并在首次提及项目时写明“我是该开源项目作者”。

结构：

1. **先给结论**：抽取只是输入层，业务结论还需要跨文档规范化、确定性规则、异常解释和人工决定。
2. **用一个合成案例拆流程**：主案例用采购订单 + 发票 + 收货单，写明 8 个 normalized fields、初始 4 pass + 2 fail，以及修正 `Received quantity` 后 6/6；医疗理赔是第二示例。
3. **哪些交给模型，哪些不交**：扫描件理解/字段候选可由模型辅助；存在性、相等、求和、上下限等由规则处理。
4. **“可追溯”不是一句口号**：字段需带原文 quote、confidence、来源文档；人工改值与决定进入导出记录。坐标级高亮尚未实现。
5. **本地优先的准确含义**：内置 Demo、本地 volume、本机 Ollama；同时诚实说明远程 provider 例外。
6. **用 DocuRule 做了一个最小验证**：技术栈、三条 Docker 命令、当前 3 文档 / 8 字段 / 6 规则 / 2 初始异常实测摘要。
7. **失败边界**：不把 early MVP 包装成生产系统；列出复杂 OCR、规则 recipe、多人复核等 roadmap。
8. **开放问题**：实际业务里最常见的 packet 是什么？哪些低置信字段必须人工看？
9. **一次性链接**：结尾给 GitHub 仓库，邀请读者运行合成 Demo 或提交脱敏 recipe；不要求点赞、关注或 Star。

建议披露：

```text
利益相关：我是 DocuRule 的作者，项目采用 MIT License。本文在资料整理与文字润色中使用了生成式 AI，事实和技术判断由我复核。[作者补充代码开发中的真实 AI 参与方式。]
```

CTA：**分享一个脱敏/合成的文档 packet 及可确定性描述的规则。** 不通过私信群发仓库链接。

## 6. X / LinkedIn 短文

### 6.1 X（英文，采购 Hero 版）

```text
Open-sourced DocuRule: an early local-first MVP for the step after PDF-to-JSON.

PO + invoice + delivery note → 8 normalized fields → 6 deterministic rules → human review → JSON

Docker demo; no API key. MIT.
https://github.com/wangyinlong-wang/docurule-ai

Try it and report the first setup snag.
```

附上当前约 14.7 秒、491 KB 的 recipe Hero GIF。CTA：**先试在线合成演示；需要真实文件处理再运行 Docker，并报告可复现的 setup issue**。

### 6.2 X（中文）

```text
我把 DocuRule 开源了：补上 PDF 转 JSON 之后的跨文档核验。

采购订单 + 发票 + 收货单 → 8 个字段 → 6 条确定性规则 → 人工决定 → JSON 导出

当前是 early MVP，Docker 可跑，内置合成 Demo 不要 API Key，MIT License。
https://github.com/wangyinlong-wang/docurule-ai

欢迎直接给可复现的安装卡点，不做准确率夸张宣传。
```

### 6.3 LinkedIn（英文）

```text
I have open-sourced DocuRule, an early local-first document validation MVP.

The project starts where many extraction tools stop. It takes a related packet of documents, keeps source quotes and confidence with extracted fields, runs deterministic checks, and lets a reviewer correct values and export a JSON decision trail.

The current synthetic procurement demo matches a purchase order, invoice and delivery note: eight normalized fields, six rules, and two initial exceptions. Correcting received quantity from 90 to 96 re-runs the rules from 4/6 to 6/6. It runs in Docker without an API key. For real image-only documents, DocuRule can use Ollama or an OpenAI-compatible vision endpoint. It is MIT licensed and intentionally small today: React, FastAPI, SQLite and local file storage.

It is not production-ready and I am not publishing a generalized accuracy claim. Schema-v1 YAML recipes are executable today; rich OCR/layout adapters, custom extraction schemas, PDF/image recipe packets, coordinate highlights, additional operators and multi-user queues remain on the roadmap.

Repository and quick start: https://github.com/wangyinlong-wang/docurule-ai

If you work on document workflows, I would value feedback on one design question: which checks belong in deterministic rules, and which genuinely benefit from a model?
```

CTA：**回答一个明确设计问题。** 不把“请 Star”作为首句或唯一目的。

## 7. 推荐发布顺序

原则：每个渠道讲不同角度；一次发布后先处理反馈，再开下一个线程。不要在多个社区同一时刻复制群发。

| 时间 | 渠道 | 发布物 | 主 CTA | 放行条件 |
|---|---|---|---|---|
| T-1 | GitHub（只做准备） | 固定 Release、README、截图/可选 GIF、已知限制 | Run local demo | 第 0.2 节全部事实确认 |
| Day 0 上午 | V2EX 分享创造 | 第 5.1 节作者校对版 | 给出首个安装卡点 | 作者可在线回复；节点仍适用 |
| Day 0 晚间或 Day 1 | Show HN | 作者亲写标题与第一评论 | 讨论规则/模型边界 | HN 账号可发、作者亲写、无需注册可试 |
| 同日稍后 | X / LinkedIn | 第 6 节短文 + 已验证截图 | 运行 Demo/回答设计问题 | **直接链仓库**，不号召去 HN 投票 |
| Day 2 | r/selfhosted | 当周 New Project Megathread 评论 | 报告 Docker/OS 复现 | 找到最新周帖；AI disclosure 填写 |
| Day 3 | 掘金 | 可复现技术长文 | 报告卡点/贡献 recipe | AI 标识、实测命令与截图就绪 |
| Day 4–5 | 知乎 | 独立技术文章或一个相关回答 | 分享 packet/rule | 利益相关与 AI 辅助披露 |
| Day 5+（可跳过） | r/LocalLLaMA | 本地模型实验版 | 提交模型/硬件结果 | 账号 1/10 合规、作者亲写、代码/AI 情况可被社区接受 |

若首个渠道发现 Quick Start 阻塞，暂停后续发布，修复、验证并发布小版本后再继续。不要为了“集中爆发”把已知失败扩散到所有平台。

## 8. 每个平台 CTA 对照

| 平台 | 唯一主 CTA | 不使用的 CTA |
|---|---|---|
| Show HN | 本地运行并批评规则/模型边界 | 给 HN 点赞、帮顶、求 Star |
| r/selfhosted | 附 Docker/OS 报告第一个安装卡点 | 跨帖复制、私信推广、求 upvote |
| r/LocalLLaMA | 给一个可复现模型/硬件结果 | 泛泛“支持一下”、未经验证的最佳模型投票 |
| V2EX | 报告首个卡点或工程边界建议 | 刷回复顶帖、同时发多个节点 |
| 掘金 | 复现 Demo 或贡献合成 recipe | 点赞/关注达到多少才更新 |
| 知乎 | 分享脱敏 packet 与确定性规则 | 批量回答导流、私信群发、诱导赞同 |
| X | 跑 Demo 并提交可复现 issue | 夸大趋势、假装用户背书 |
| LinkedIn | 回答一个架构问题 | “行业第一”“企业级开箱即用” |

README 自身可以保留自然的 Star 请求；社区正文以试跑和反馈为主。Star 是有用结果，不是用户获得功能的条件。

## 9. 回复模板

模板必须根据对方问题个性化，不能批量粘贴相同回复。

### 9.1 “和 Docling / PaddleOCR / Marker 有什么区别？”

> DocuRule 不打算替代它们。它们主要解决解析/OCR/结构转换；DocuRule 当前关注它们之后的一层：把相关文件组成 packet，保留字段证据，运行跨文档确定性检查，再让人处理异常。解析器 adapter 仍在 roadmap，所以今天的复杂 OCR 能力有限。

### 9.2 “真的完全本地吗？”

> 内置合成 Demo、本地文件/SQLite 存储，以及连接本机 Ollama 的路径可以留在本机。若你主动配置远程 OpenAI-compatible provider，文档会发送到那个端点。因此我使用 “local-first”，没有声称所有配置都永不联网。

### 9.3 “不用模型能做什么？”

> 内置 Demo 是确定性的，不需要模型或 API Key；带文本层的简单文档也可以走文本规则。真实图片/扫描件需要兼容视觉模型。provider 不可用时系统会回退到 rules-only，而不是静默编造数据。

### 9.4 “准确率多少？”

> 目前没有足以支持泛化百分比的 benchmark，所以我不会给一个准确率数字。当前自动化测试覆盖的是合成流程和确定性行为，不代表任意真实文档的抽取准确率。后续希望建立公开的合成/脱敏 recipe 测试集。

### 9.5 “可以上生产吗？”

> 现在是 early working MVP，适合本地试验和讨论架构，不应被描述成 production-ready。复杂 OCR、坐标高亮、可配置 recipes、权限/多人队列和可扩展持久化等仍需完善。

### 9.6 “为什么选采购三单匹配？医疗 Demo 还在吗？”

> 采购三单匹配适合作为首发 Hero，因为三份文件和六条规则能直观展示 packet-first 与确定性校验：初始 4 条通过、2 条失败，修正收货数量后 6/6。医疗理赔的双文档 Demo 仍保留，用来证明流程不局限于采购场景。两个样例都完全是合成数据。

### 9.7 “为什么用 LLM，不全写规则？”

> 两者承担不同职责：模型可辅助从图像或复杂文本中提取候选字段；存在性、相等、范围和金额比较这类逻辑更适合可读、可测的确定性规则。DocuRule 的重点就是把这个边界显式化，而不是把所有判断塞进一个 prompt。

### 9.8 “AI 在这个项目开发里做了多少？”

> [作者必须用真实情况替换：具体列出 AI 用于哪些代码、测试、文档或文字工作；列出作者亲自做的需求、架构、评审、运行验证和最终责任。不要填百分比，除非有可审计依据。]

### 9.9 “支持我的模型/provider 吗？”

> 当前边界支持 Ollama 原生 API 和 OpenAI-compatible chat-completion API，但这不等于已经验证每个模型。请告诉我模型名、版本、硬件、输入类型和错误日志；有复现信息后才能列入兼容矩阵。

### 9.10 “我应该上传真实业务资料吗？”

> 请不要把含个人信息、商业秘密或真实医疗/财务数据的文件提交到公开 Issue/PR。优先使用合成或彻底匿名化的最小复现；安全问题请按 SECURITY.md 的私下渠道报告。

### 9.11 “我可以贡献什么？”

> 最有价值的是一个合成/彻底脱敏的 document packet、预期字段、确定性规则和预期结果；也欢迎 provider/parser adapter、测试和文档修正。请先看 CONTRIBUTING.md 与 good first issue。

### 9.12 复现信息不足

> 谢谢你试跑。为了复现，能否补充：操作系统与架构、Docker/Compose 版本、DocuRule Release/commit、执行的命令、完整错误（请先删除密钥和敏感路径），以及是否配置 Ollama/远程 provider？我会按这个信息建立最小复现。

### 9.13 已确认 Bug

> 我已经在 [环境/版本] 复现，问题记录在 [Issue URL]。当前影响是 [准确边界]，临时绕过方式是 [若已验证再填写]。下一次更新会放在 Issue/Release，不会在这里承诺未经确认的日期。

## 10. 禁止夸大与替代表述

| 禁止表述 | 原因 | 可用替代 |
|---|---|---|
| “100% private / secure” | 远程 provider 例外；安全未经完整审计 | “local-first; local storage and Ollama paths are available” |
| “数据绝不离开机器” | 取决于用户 provider 配置 | “the bundled demo needs no cloud API; remote providers receive configured inputs” |
| “支持任意文档/任意规则” | 当前格式、解析器和规则范围有限 | 列出当前格式与已实现校验 |
| “行业最高/领先准确率” | 无公开 benchmark | “no generalized accuracy claim yet” |
| “生产可用/企业级” | README 明确 early MVP | “early working MVP for local evaluation” |
| “一键部署” | 实际需要 clone、build、Docker 环境 | “Docker Compose quick start” |
| “5 分钟跑通” | 未记录干净环境耗时 | 先实测再给时间；否则只说三条命令 |
| “完整 OCR” | 当前文本 PDF 用 pypdf，图像依赖视觉模型 | “text-layer PDF extraction; vision provider for images” |
| “可审计/不可篡改审计” | 有 JSON trail，不等于合规或 tamper-proof | “exportable JSON decision/audit record” |
| “模型永不幻觉” | 不可保证 | “provider errors do not silently invent fields; rules-only fallback is exposed” |
| “所有版本都支持采购三单匹配” | Hero 从 `v0.2.0` 开始；可执行 recipe runtime 从 `v0.3.0` 开始；CSV 字段导出从 `v0.4.0` 开始；空字段提示从 `v0.5.0` 开始；上传扩展名/MIME 配对校验从 `v0.5.1` 开始 | 分别写各功能的实际版本，不把后续能力倒写成早期功能 |
| “20 秒动态 Demo” | 当前 README 素材实测为 14.7 秒 | “a 15-second demo GIF”或“约 15 秒动态演示” |
| “已被真实企业/用户采用” | 没有公开证据 | 不提；以后只引用获授权、可核查的案例 |
| “节省 80% 时间/成本” | 未做测量 | 描述流程，不量化收益 |
| “支持 OpenAI / Gemini / Qwen 等所有模型” | 只验证协议边界，不代表具体模型 | “Ollama and OpenAI-compatible provider interfaces” |
| “Docker 当前健康运行” | 是某一时刻本机状态，不是产品恒常能力 | “Docker Compose deployment is provided” |
| “CI 全绿所以功能可靠” | CI 范围有限 | 说明具体测试覆盖，不泛化 |
| “帮忙点 Star / upvote” | HN/Reddit 投票规则与社区信任风险 | 请求试跑、复现反馈或贡献 recipe |

## 11. 首周数据记录表

### 11.1 发布前基线

| 时间（Asia/Shanghai） | Release | Stars | Forks | Open issues | GitHub unique visitors（14d） | Unique cloners（14d） | 备注 |
|---|---|---:|---:|---:|---:|---:|---|
| 发布前 1 小时 |  |  |  |  |  |  | 截图/抄表；Traffic 有保留窗口 |

### 11.2 渠道事件表

| 渠道 | 帖子 URL | 发布时间 | 版本/文案变体 | 媒体 | 平台曝光 | 平台互动 | 可识别点击/引荐 | 首个有用反馈 | 作者首次回复耗时 | 状态 |
|---|---|---|---|---|---:|---:|---:|---|---:|---|
| V2EX |  |  | 采购 Hero | GIF |  |  |  |  |  | planned |
| Show HN |  |  | 作者亲写 | screenshot / GIF |  |  |  |  |  | planned |
| X |  |  | EN / ZH | screenshot / GIF |  |  |  |  |  | planned |
| LinkedIn |  |  | EN | screenshot / GIF |  |  |  |  |  | planned |
| r/selfhosted Megathread |  |  | self-hosted | screenshot |  |  |  |  |  | gated |
| 掘金 |  |  | 技术长文 | screenshots |  |  |  |  |  | planned |
| 知乎 |  |  | 技术文章 | screenshots |  |  |  |  |  | planned |
| r/LocalLLaMA |  |  | Ollama | screenshot |  |  |  |  |  | optional/gated |

### 11.3 每日漏斗

每天固定在同一时间记录；`New stars` 使用当天快照差值，`Star / visitor` 只能作为全仓近似，不强行归因到单个平台。

| 日 | 日期 | Stars 总数 | New stars | Forks | GitHub unique visitors | Unique cloners | Issues opened | Quick Start 成功反馈 | Quick Start 失败反馈 | 外部贡献者 | 主要 referrer | 当日变更/解释 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 0 |  |  |  |  |  |  |  |  |  |  |  |  |
| 1 |  |  |  |  |  |  |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |  |  |  |  |  |  |
| 5 |  |  |  |  |  |  |  |  |  |  |  |  |
| 6 |  |  |  |  |  |  |  |  |  |  |  |  |
| 7 |  |  |  |  |  |  |  |  |  |  |  |  |

计算：

```text
7-day star conversion ≈ 7-day new stars / 7-day GitHub unique visitors
Quick Start reported success rate = success reports / (success reports + failure reports)
```

两个指标都只代表可见样本：GitHub visitor 与 referrer 有统计窗口和归因限制，主动反馈也有幸存者偏差。不要用它们制造营销结论。

### 11.4 反馈到行动

| 反馈原文/链接 | 分类（安装/抽取/规则/UI/文档） | 可复现？ | 严重度 | Issue | Owner | 下一动作 | Release | 已回复？ |
|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |

首周决策规则：

- 访客高、Star/试跑低：先修 README 首屏、Quick Start 与限制说明，不继续堆渠道。
- 试跑失败集中：暂停发帖，先修复并发布 patch release。
- 访客少、已有试跑者反馈好：针对最高相关渠道写新角度，不复制旧帖。
- 任何平台出现删除/版主提醒：停止重发，记录具体规则，必要时通过官方渠道询问；不换小号规避。

## 12. 发帖前 90 秒终检

- [ ] 我明确说自己是作者，没有伪装成第三方推荐。
- [ ] 标题没有最高级、虚假数字、感叹号堆叠或未经验证的结果。
- [x] 正文中的版本、Demo、字段数、规则数与当前公开 Release 一致。
- [ ] Latest Release `v0.5.2` 已公开；采购 Hero 实测数字、16.0 秒 recipe GIF、CSV 导出、空字段提示、上传校验、五分钟贡献路径和在线演示与公开 README 一致。（待本轮发布后核验）
- [ ] 我没有写准确率、生产可用、企业采用、绝对隐私等无证据结论。
- [ ] AI 参与披露真实，且该平台允许这类代码/文案；HN 文案由作者本人重写。
- [ ] 链接直接指向 GitHub 原始仓库，无投票链接、隐藏跳转或短链。
- [ ] CTA 是试跑/反馈/贡献，不是 upvote/赞同/Star 交换。
- [ ] 我已经打开当天的平台规则，并确认发帖位置、flair/节点与账号资格。
- [ ] 我现在有时间回复问题，并准备承认限制或暂停发布修 Bug。
