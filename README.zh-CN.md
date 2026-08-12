<p align="center">
  <img src="docs/assets/logo.svg" width="76" alt="DocuRule Logo" />
</p>

<h1 align="center">DocuRule</h1>

<h3 align="center">把一组业务文档变成可追溯的规则结论。</h3>

<p align="center">
  开源、本地优先的文档智能工作台：文档分类、字段提取、跨文档核验、人工复核和审计导出。
</p>

<p align="center"><a href="README.md">English</a> · <a href="https://wangyinlong-wang.github.io/docurule-ai/"><strong>在线体验</strong></a> · <a href="#快速开始">快速开始</a> · <a href="#五分钟贡献一个-recipe">贡献 Recipe</a> · <a href="docs/csv-export.md">CSV 导出契约</a> · <a href="docs/product-spec.md">产品规格</a></p>

[![最新版本](https://img.shields.io/github/v/release/wangyinlong-wang/docurule-ai?style=flat-square&label=latest&color=376b59)](https://github.com/wangyinlong-wang/docurule-ai/releases/latest) **v0.5.3：在线演示 Star 入口，以及本地模型证据报告。**

[![GitHub Stars](https://img.shields.io/github/stars/wangyinlong-wang/docurule-ai?style=flat-square&label=stars&color=f2b84b)](https://github.com/wangyinlong-wang/docurule-ai) 如果这个工作流对你有用，欢迎在 GitHub 上点 Star，方便跟进后续更新。

![DocuRule 可执行 YAML 规则与采购三单匹配动态演示](docs/assets/docurule-recipe-demo.gif)

**rules.yml · 3 份文档 · 8 个归一化字段 · 6 条规则 · 2 个异常 · 1 次人工决定**

> [!WARNING]
> 当前 MVP 尚无登录认证。请只在可信本机或私有网络运行，不要把 `8080` 端口直接暴露到公网。

## 它解决什么问题

OCR 或 PDF 转 JSON 只完成了一半工作。真实业务面对的是一组有关联的资料：姓名、日期、编号和金额是否一致？异常值来自哪一页？规则为什么失败？谁修改并批准了结果？

DocuRule 专注解析后的业务核验层：

- 一次处理一组有关联的 PDF、图片和文本，而不是单个文件；
- 字段保留置信度和原文证据；
- 相等、金额、日期等确定性规则不交给 LLM 猜；
- 只把异常交给人工修改、批准或拒绝；
- 默认 Docker 本地运行，支持 Ollama，无云端密钥也能体验 Demo。

## 快速开始

**[直接打开浏览器在线体验 →](https://wangyinlong-wang.github.io/docurule-ai/)** 在线版只使用公开的合成资料包，不上传文件、不连接后端，刷新页面后复核记录即清空。上传自己的文件或连接 AI Provider 仍需在本地运行 DocuRule。

需要 Docker Desktop 和 Docker Compose：

```bash
git clone https://github.com/wangyinlong-wang/docurule-ai.git
cd docurule-ai
docker compose up --build
```

访问 [http://localhost:8080](http://localhost:8080)，点击「Explore the demo」。内置演示会创建采购订单、供应商发票和收货单，固定得到 4 条通过、2 条异常；把 `Received quantity` 从 `90` 改为 `96` 后，六条规则全部通过。它不需要模型、API Key 或真实文档。

三份合成文档、声明式规则契约和 golden JSON 结果全部公开在[三单匹配 recipe](demo/three-way-match/)中。内置 API Demo 与确定性测试读取的也是同一组文件。

### 运行自己的 YAML 规则

在首页点击「Run rules.yml」，选择 schema v1 的 `rules.yml`，再选择清单中声明的文本文件，即可创建一条可复核流程。也可以直接调用 API：

```bash
curl -F 'recipe=@demo/three-way-match/rules.yml' \
  -F 'files=@demo/three-way-match/purchase-order-PO-2026-0812.txt;type=text/plain' \
  -F 'files=@demo/three-way-match/supplier-invoice-INV-1048.txt;type=text/plain' \
  -F 'files=@demo/three-way-match/delivery-note-DN-7721.txt;type=text/plain' \
  http://localhost:8080/api/v1/recipes/run
```

安全边界是明确的：规则不能执行 Python、Shell、模板或网络请求，只能使用允许的文档齐全、跨文档相等和数值大小比较。当前上传 recipe 支持文件名与清单完全一致的 UTF-8 TXT、Markdown 和 CSV。完整格式见[规则编写指南](docs/recipes.md)。

### 五分钟贡献一个 Recipe

最容易开始的贡献，是一个完全合成的资料包和一条可解释的跨文档校验。直接复制公开的[三单匹配 fixture](demo/three-way-match/)：

```bash
cp -R demo/three-way-match demo/my-recipe
```

1. 所有输入只使用合成或彻底匿名化内容。
2. 修改 recipe 的 id/title，并按需重命名文件；`rules.yml` 的 `documents` 清单必须与文件名完全一致，规则只使用[规则指南](docs/recipes.md)列出的 schema v1 算子。
3. 补齐 `README.md` 和 `expected-result.json`，写清预期通过/失败的校验，以及一个复核者可以重现的字段修正。
4. 在页面点击「Run rules.yml」或运行上面的 API 命令验证，再提交一个范围明确的 PR，附上命令和结果。

第一次只想改文档，可以先阅读 [CSV 导出契约](docs/csv-export.md)，再查看当前的 [good first issue](https://github.com/wangyinlong-wang/docurule-ai/labels/good%20first%20issue) 列表或 [Discussions](https://github.com/wangyinlong-wang/docurule-ai/discussions)。Docker 到 Ollama 的排障任务目前已有贡献者负责，请不要重复开工；不确定字段或规则怎么选时，先开 Issue 再写代码。不要上传真实发票、病历、身份信息或其他机密资料。

如需用本地视觉模型处理扫描件和图片：

```bash
ollama serve
ollama pull gemma4:latest
docker compose up --build
```

文件与 SQLite 数据默认保存在本地 Docker volume；如果配置远程 OpenAI-compatible provider，文档输入会发送到你指定的远程端点。

如果要记录可复现的本地模型证据，请查看[模型兼容性报告模板与实测记录](docs/model-compatibility.md)。它记录精确模型 digest 和有限范围的 smoke test，不是准确率排行榜。

## 当前已经可用

- PDF、PNG、JPG、Markdown 和文本混合上传；
- 文本 PDF 解析，图片可接 Ollama 或 OpenAI 兼容接口；
- 模型离线时自动使用确定性规则兜底；
- 字段置信度和原文引用；
- 采购订单、发票、收货单的三单匹配：文档齐全、供应商、PO 号、币种、数量和金额校验；
- 可上传执行的 schema v1 YAML 规则，并在字段人工修正后自动重算；
- 公开的三单匹配 recipe：合成输入、`rules.yml` 和 CI 精确核对的预期结果；
- 保留医疗理赔示例的跨文档姓名和金额校验；
- 字段人工修改、案件批准/拒绝、完整 JSON 审计导出和一行一个字段的 CSV 导出；
- 空字段状态会区分视觉 provider 不可用、图片需要视觉模型和文本未识别字段；
- 文件会在写入前校验扩展名与声明的 MIME 类型是否匹配；
- SQLite 和文件本地持久化；
- React + FastAPI 的响应式页面；
- 单容器 Docker Compose 部署；
- 后端单元/接口测试与 GitHub Actions。

![字段证据、校验结果和人工审批](docs/assets/docurule-review.png)

## 开发路线

- [x] 采购订单 + 发票 + 收货单的三单匹配模板；
- [x] 面向确定性文本资料包的可执行 YAML 规则；
- 更多规则算子、可视化编写和 PDF/图片 recipe；
- PDF 页内坐标高亮；
- Docling、PaddleOCR 等解析器适配；
- PostgreSQL/S3/独立任务 Worker 和多人复核队列。

完整边界和验收标准见[产品规格](docs/product-spec.md)，技术演进见[架构文档](docs/architecture.md)。

## 参与贡献

欢迎提交场景模板、Provider 适配、Bug 修复和文档改进。请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，Issue 和 PR 中只使用合成或彻底匿名化的文档。

项目采用 [MIT License](LICENSE)。如果它对你有帮助，一个 ⭐ 能让更多开发者发现它。
