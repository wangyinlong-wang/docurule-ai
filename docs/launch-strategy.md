# DocuRule launch strategy

> 竞品与命名快照：2026-08-12。Star 数会持续变化；本文件用于决定产品首发范围、README 叙事和发布节奏，不承诺增长结果。

## 1. 一页结论

- **品牌名：** `DocuRule`；GitHub 仓库使用 `docurule-ai`；“AI”只做检索副标题，不放进主 Logo。
- **品类：** local-first、open-source intelligent document processing（IDP）。
- **核心承诺：** **Turn document packets into auditable decisions.**
- **中文定位：** 把一组业务文档变成可追溯、可人工复核的规则结论。
- **首发切口：** 不与大项目争夺“PDF 转 Markdown/OCR”；复用现有解析能力，专攻 **跨文档校验 + 确定性规则 + 异常复核 + 字段级证据**。
- **Hero demo：** 采购订单（PO）+ 发票 + 收货单的三单匹配。合成资料，无隐私风险，20 秒内展示 6 条规则、2 个异常和一次人工决定。
- **30 天增长目标：** 基准 300、目标 800、冲刺 1,500 Star；以“合格访客 × README 转化率”管理，不购买、不互刷、不用 Star 换权益。

## 2. 命名校验与使用规范

### 2.1 2026-08-12 快照

| 检查项 | 结果 | 决策 |
|---|---|---|
| GitHub 仓库名搜索 | `docurule in:name` 仅发现 `DocuRuleFix`（0 Star），未发现同名主流项目 | `docurule-ai` 冲突风险低 |
| GitHub 用户名搜索 | 未发现 `docurule` 登录名 | 可以尝试同时保留组织/账号名 |
| PyPI `docurule` | JSON 包接口返回 404 | 若要发布 Python SDK/CLI，应尽早保留 |
| npm `docurule` | registry 返回 404 | 若要发布 JS SDK，应尽早保留 |
| `docurule.ai` / `.com` / `.io` RDAP | 未返回已注册记录 | **不等于购买保证**；发布前在注册商复查并立即保留 |
| 商标 | 搜到一条 1997 年 `DOCURULE` 美国申请（序列号 75389398），第三方状态显示已放弃 | 可继续做工作名；商业化或申请商标前由专业人士做目标国家/类别正式检索 |

命名判定：**保留 DocuRule**。它短、可读，并直接连接“document + rule”差异点。不要再同时传播 DocuRule AI、DocuRules、DocRule 等变体。

统一用法：

- 产品/Logo：`DocuRule`
- 仓库：`docurule-ai`
- 一句话：`Turn document packets into auditable decisions.`
- GitHub About：`Open-source, local-first IDP for cross-document validation and human review.`
- CLI / PyPI（如发布）：`docurule`
- Docker：`ghcr.io/<owner>/docurule-ai`

发布前当天再次检查 GitHub、PyPI、npm、域名与商标。命名检查是碰撞筛查，不构成法律意见。

## 3. 当前竞品格局与差异化

Star 为 GitHub API 在 2026-08-12 的近似快照。

| 项目 | 约 Star | 它占据的心智 | 对 DocuRule 的启示 |
|---|---:|---|---|
| [Microsoft MarkItDown](https://github.com/microsoft/markitdown) | 173k | 多格式转 Markdown | “格式转换”已是红海，不做主卖点 |
| [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | 87.5k | OCR、文档解析、多语言 | 作为可替换底层，不从头造 OCR |
| [MinerU](https://github.com/opendatalab/MinerU) | 77.4k | 复杂 PDF/Office 到 Markdown/JSON | 不用解析准确率做首发正面对比 |
| [Docling](https://github.com/docling-project/docling) | 64.6k | 本地解析、统一文档结构、GenAI 集成 | 适合作为解析适配器；DocuRule 从其输出继续做业务校验 |
| [Marker](https://github.com/datalab-to/marker) | 38.7k | 快速高质量 Markdown/JSON、表格与公式 | “PDF → JSON”不是足够清晰的差异 |
| [Unstract](https://github.com/Zipstack/unstract) | 7.1k | Prompt Studio、结构化抽取 API、ETL | 最接近的平台竞品；避开“又一个 Prompt Studio”叙事 |
| [ContextGem](https://github.com/shcherbak-ai/contextgem) | 2.0k | 代码优先的 LLM 抽取、来源引用 | 证据溯源是用户预期，不应当作唯一卖点 |
| [ExtractThinker](https://github.com/enoch3712/ExtractThinker) | 1.6k | ORM 式分类、契约抽取、工作流 | 分类和 schema 抽取属于基础能力 |
| [Documind](https://github.com/DocumindHQ/documind) | 1.5k | AI 结构化文档抽取平台 | 单文档抽取 UI 本身不足以建立新品类 |

竞品 README 的高频核心是 **convert / parse / extract**。DocuRule 应占据它们输出之后的一层：

```text
document packet
  -> classify and extract
  -> normalize fields with source evidence
  -> run deterministic and AI-assisted rules
  -> send only exceptions to human review
  -> export an auditable decision
```

### 3.1 必须守住的四个差异点

1. **Packet-first，而非 single-document-first**：一次处理一组相互关联的资料，跨文件比对姓名、编号、金额、日期、数量等。
2. **Rules-first，而非 prompt-first**：相等、范围、日期、求和等由可读、可测试的确定性规则完成；只有模糊语义才调用 LLM。
3. **Exception-first human review**：人只看低置信字段和失败规则，并能看到原页证据、修改值和记录理由。
4. **Local-first auditability**：Docker 一键运行，Ollama 无密钥路径可完成 Hero demo；每个结论保留字段、文档、页码/区域、规则版本和人工操作。

不要声称“行业最高准确率”“100% 安全”或“支持任意文档”。发布时只宣传已经通过演示资料和自动化测试验证的能力，未完成项明确标为 roadmap。

## 4. 目标用户优先级

### P0：会 Star、会贡献的开发者

- 正在为财务、保险、KYC、法务、供应链做文档工作流的 AI/后端工程师。
- 现状是把 OCR、Pydantic、LLM、规则脚本和人工表格拼在一起。
- 首屏要回答：能否本地跑、多久跑起来、规则怎样写、结果能否追溯、能否换模型/解析器。

### P1：会试用、会内部传播的团队

- 有隐私或私有部署需求的解决方案架构师、技术负责人和自动化团队。
- 关注 Docker/Ollama、可审计性、失败处理、API 和扩展点。

### P2：会带来模板生态的领域贡献者

- 财务运营、理赔、采购、合规等懂规则但不一定训练模型的人。
- 通过 YAML/JSON 模板贡献“发票三单匹配、报销资料完整性、KYC 资料一致性”等 recipe。

非首发用户：只想聊天问 PDF 的个人用户、只需要 OCR SDK 的开发者、寻求完整企业 BPM/权限中台的大客户。迎合这些人会稀释定位。

## 5. README 第一屏信息架构

第一屏必须在滚动前回答“是什么、与解析器有什么不同、能否立即体验”。建议直接使用以下英文文案：

```markdown
<p align="center">[Logo]</p>

# DocuRule

### Turn document packets into auditable decisions.

Open-source, local-first IDP that classifies mixed documents, extracts
schema-validated data, checks cross-document rules, and routes only
exceptions to human review.

[Quick start] [Watch 20s demo] [Documentation] [中文]

[CI] [Docker] [License] [Latest release]

[Hero GIF: PO + Invoice + Delivery Note -> 6 checks -> 2 exceptions]

**3 documents · 8 normalized fields · 6 rules · 2 exceptions · 1 review decision**

`docker compose up --build`
```

首屏约束：

- GIF 第一帧就显示三个文件和最终结果，不用空白上传页开场；控制在 15–20 秒、自动循环、文件小于约 8 MB。
- Hero 下方只放一条已验证的启动命令；如果首次启动仍需手工下载模型，就明确写出预计下载量和时间。
- Badge 控制在 4–5 个；不要用十几个图标挤掉价值主张。
- README 默认英文，顶部提供 `README.zh-CN.md`；演示界面尽量使用数字、勾选和警告，降低语言门槛。
- Social Preview 使用 1280×640：左侧品牌和一句话，右侧显示 `3 docs -> 6 rules -> 2 exceptions`，不要放小字号架构图。

首屏之后的固定顺序：

1. `Why DocuRule`：PDF-to-JSON 之后仍缺少什么。
2. `See it work`：Hero demo 的输入、规则和审计结果。
3. `Quick start`：Ollama 默认路径，5 分钟内跑通合成示例。
4. `How it works`：五步流程，不先展示微服务架构。
5. `Write a rule`：一个 8–12 行可复制示例。
6. `DocuRule vs parsers/extractors`：明确 Docling/Marker 等是可集成底层，不贬低竞品。
7. Providers / API / recipes / roadmap / contributing / community。

## 6. 首发 Hero demo：三单匹配

### 6.1 合成输入

当前通过内置 `/api/v1/demo/procurement` 创建三份可公开复现的合成文本单据：

- `purchase-order-PO-2026-0812.txt`
- `supplier-invoice-INV-1048.txt`
- `delivery-note-DN-7721.txt`

可独立贡献的 recipe 文件夹、`expected-result.json` 和 `rules.yml` 仍保留在 roadmap；当前确定性 API/engine 测试是 golden behavior 的权威来源。

示例供应商使用虚构名称 `Northstar Components`。不得使用真实个人、公司、地址、银行账号或医疗资料。

### 6.2 六条可一眼理解的规则

| 规则 | 预期 |
|---|---|
| 三种必需文档齐全 | PASS |
| 三份文件供应商一致 | PASS |
| 发票 PO 号等于采购订单号 | PASS |
| 币种一致 | PASS |
| 发票数量 96 不得大于收货数量 90 | **FAIL** |
| 发票金额 2,400 不得大于已收货价值 2,250 | **FAIL** |

### 6.3 16 秒实录流程

- `0–5s`：首页直接展示 `PO + Invoice + Delivery Note` 与两条预期异常。
- `5–9s`：进入结果页，显示 3 份文档、8 个字段、`4/6 passed` 和数量/金额异常。
- `9–13s`：把 `Received quantity` 从 `90` 改为 `96`，规则立即重算为 `6/6 passed`。
- `13–16s`：批准案件，结束帧保留可导出的审计结果。

Hero demo 的验收不是“录出来了”，而是：新机器仅按 README 操作可复现相同 6 条结果；`expected-result.json` 在 CI 中作为 golden fixture 校验。

医疗理赔作为第二个合成 Demo 保留；KYC、合同核验可作为后续 recipe。首发动态演示仍只讲采购，避免让项目被误解为单行业产品。

## 7. GitHub Topics

首发建议 18 个，全部小写；只有功能已经可用时才添加对应词：

```text
document-ai
document-intelligence
intelligent-document-processing
idp
document-processing
document-extraction
document-validation
cross-document-validation
structured-output
pdf-extraction
ocr
llm
ollama
local-first
self-hosted
human-in-the-loop
rule-engine
docker
```

GitHub 最多允许 20 个 topics。首发后每周查看 GitHub 搜索/流量来源，低相关 topic 替换为实际带来访客的集成词；不要为了蹭热度添加尚未支持的模型名。

## 8. 首发门槛

以下任一项未完成就不做大规模首发，只做小范围预览：

- 全新 Docker 环境按 README 一条路径成功启动；默认 Ollama 路径无需云 API key。
- 合成 demo 一键导入，20 秒 GIF 和 60–90 秒带旁白视频已上传。
- Hero 的 6 条规则有自动化测试，输出与 `expected-result.json` 一致。
- README 英文主文档 + 中文入口；LICENSE、CONTRIBUTING、CODE_OF_CONDUCT、SECURITY、Issue/PR templates 齐全。
- 至少 5 个边界清楚的 `good first issue`，每个有验收标准和相关文件位置。
- `v0.2.0` GitHub Release 有变更、限制、动态演示和升级/反馈入口。
- 仓库 About、Topics、Social Preview、Discussions 已配置；README 中所有链接在无登录窗口验证。
- 已知局限公开列出，例如支持格式、CPU/内存、模型大小、首次启动时间和不保证的准确率。

## 9. 30 天 Star 增长执行表

### 9.1 指标模型

```text
new stars = qualified unique repo visitors × README star conversion
```

每周记录：GitHub unique visitors、referring sites、clones、new stars、Star/unique visitor、Quick Start 成功反馈、Issue 首次响应时间。GitHub traffic 只保留有限窗口，应每周截图/抄表。

| 30 天档位 | 合格独立访客 | Star 转化 | 结果 |
|---|---:|---:|---:|
| 基准 | 10,000 | 3% | 300 |
| 目标 | 20,000 | 4% | 800 |
| 冲刺 | 30,000 | 5% | 1,500 |

如果访问高、转化低，先修首屏/启动体验；如果转化高、访问低，才扩大分发。不要用发帖数量替代漏斗指标。

### 9.2 发布前 7 天（准备，不计入 30 天）

- 找 10–15 位目标开发者做干净环境试跑；逐项记录卡点，不要求 Star。
- 准备一套素材：20 秒 GIF、90 秒视频、5 张图、英文/中文各 3 个长短版本、架构图、FAQ。
- 预写 `v0.2.0` Release、Show HN、Reddit、V2EX/掘金/知乎文章；每个平台以其受众改写，避免复制群发。
- 建立公开 roadmap 和 5–10 个 issues；邀请首批试用者把真实问题留在 GitHub。

### 9.3 Day 0–2：集中首发

**目标：100–200 Star，得到 10 个真实安装反馈。**

- 发布 `v0.2.0`，同步开启 Discussions 的 `Show and tell`、`Q&A`、`Ideas`。
- 英文：Show HN、r/selfhosted、r/LocalLLaMA、DEV/Hashnode、X/LinkedIn；遵守社区自推广规则，正文先讲三单匹配和本地复现，不只贴链接。
- 中文：V2EX、掘金、知乎、开发者微信群/社群；标题统一围绕“PDF 转 JSON 之后，如何跨文档核验”。
- 所有帖子只使用一个主 CTA：`Run the local demo`；结尾再自然请求“有用的话 Star”。
- 作者当天保持在线，12 小时内回复 issue/discussion；将最高频阻塞在 24 小时内发布 `v0.1.1`。

### 9.4 Day 3–7：证明可用

**累计目标：250–350 Star；Quick Start 成功率达到 80%+。**

- 发布一篇可复现技术文：`Why PDF-to-JSON is only half of document automation`，包含规则 YAML、审计 JSON 和失败案例。
- 发布 3–5 分钟从零安装视频；分别给 CPU 与 Ollama 模型写清资源要求。
- 把用户问题整理成 troubleshooting；发 `v0.1.2`，Release notes 点名感谢贡献者。
- 只向真正相关的 awesome-list / newsletter 提交；PR 说明类别和可复现 demo，不群发目录站。

### 9.5 Day 8–14：制造第二个传播理由

**累计目标：400–550 Star；至少 3 位外部贡献者。**

- 发布 `v0.2.0`：选择一个能形成标题的功能，如“可视化字段证据”或“可导入 recipe”，不要把多个半成功能堆在一起。
- 发布 `Build a local document validation workflow with Ollama in 5 minutes`，附完整命令和真实运行时间。
- 开放 `Recipe challenge`：征集真实但去敏后的校验规则；奖励是贡献者展示和 Release mention，**不以 Star 作为参与条件**。
- 在首发帖子发布有实质更新的 follow-up，避免无变化顶帖。

### 9.6 Day 15–21：扩展生态

**累计目标：550–750 Star；2 个社区 recipe 合并。**

- 发布第二个 recipe（报销资料完整性或 KYC 一致性），证明不是只做采购。
- 做一篇透明对比：DocuRule 与 Docling/Marker/Unstract 分别负责哪一层；使用公开输入和脚本，不宣称未经测量的准确率。
- 联合一个 Ollama、Docling、n8n 或 self-hosting 社区贡献者做教程/直播；先提供可运行集成，再请求转发。
- 将 2–3 个最常见扩展点标成 `help wanted`，保证 24 小时内 review PR。

### 9.7 Day 22–30：第三次发布与复盘

**累计目标：800；冲刺 1,500。**

- 发布 `v0.3.0`，用一个用户请求驱动的功能作为故事；制作新旧前后对比 GIF。
- 产品已经稳定且有真实评价后再做 Product Hunt/相关 newsletter；首日维护问答，不组织互赞群。
- 发布 `30 days in public`：安装卡点、规则通过率、社区贡献和 roadmap，数据可核查，承认未解决问题。
- 根据来源复盘：保留高转化渠道与内容；砍掉带来访问但不带来 Star/安装的广泛曝光。
- 固化后续节奏：每 2 周一个可体验 Release、每周一个短 demo、每月一个新 recipe。

### 9.8 每日运营底线

- Issue 首次响应 < 12 小时，PR 首次 review < 24 小时；无法修复也要给复现状态和下一次更新时间。
- 每个 Release 都包含一张图/一段 GIF、可复制升级命令、已知限制和贡献者感谢。
- 内容比例约为：60% 可复现教程/案例，25% 产品进展，15% 请求反馈。
- 禁止购买 Star、互刷、抽奖换 Star、机器人账号或大规模非相关私信。短期虚高会破坏访客转化判断和项目可信度。

## 10. 研究来源与复核入口

- 竞品：各 GitHub 仓库首页及 GitHub REST API 快照——[MarkItDown](https://api.github.com/repos/microsoft/markitdown)、[PaddleOCR](https://api.github.com/repos/PaddlePaddle/PaddleOCR)、[MinerU](https://api.github.com/repos/opendatalab/MinerU)、[Docling](https://api.github.com/repos/docling-project/docling)、[Marker](https://api.github.com/repos/datalab-to/marker)、[Unstract](https://api.github.com/repos/Zipstack/unstract)、[ContextGem](https://api.github.com/repos/shcherbak-ai/contextgem)、[ExtractThinker](https://api.github.com/repos/enoch3712/ExtractThinker)、[Documind](https://api.github.com/repos/DocumindHQ/documind)。
- 命名：[GitHub repository search API](https://api.github.com/search/repositories?q=docurule%20in:name)、[PyPI JSON endpoint](https://pypi.org/pypi/docurule/json)、[npm registry endpoint](https://registry.npmjs.org/docurule)、[USPTO TSDR](https://tsdr.uspto.gov/)；商标状态在正式使用前应以官方系统和专业检索为准。
- GitHub 官方：[Topics 最多 20 个及发现机制](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics)、[Repository customization / Social Preview](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository)、[Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)、[Community profile](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories)。
