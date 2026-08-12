<p align="center">
  <img src="docs/assets/logo.svg" width="76" alt="DocuRule Logo" />
</p>

<h1 align="center">DocuRule</h1>

<h3 align="center">把一组业务文档变成可追溯的规则结论。</h3>

<p align="center">
  开源、本地优先的文档智能工作台：文档分类、字段提取、跨文档核验、人工复核和审计导出。
</p>

<p align="center"><a href="README.md">English</a> · <a href="#快速开始">快速开始</a> · <a href="docs/product-spec.md">产品规格</a></p>

![DocuRule 采购三单匹配动态演示](docs/assets/docurule-demo.gif)

**3 份文档 · 8 个归一化字段 · 6 条规则 · 2 个异常 · 1 次人工决定**

## 它解决什么问题

OCR 或 PDF 转 JSON 只完成了一半工作。真实业务面对的是一组有关联的资料：姓名、日期、编号和金额是否一致？异常值来自哪一页？规则为什么失败？谁修改并批准了结果？

DocuRule 专注解析后的业务核验层：

- 一次处理一组有关联的 PDF、图片和文本，而不是单个文件；
- 字段保留置信度和原文证据；
- 相等、金额、日期等确定性规则不交给 LLM 猜；
- 只把异常交给人工修改、批准或拒绝；
- 默认 Docker 本地运行，支持 Ollama，无云端密钥也能体验 Demo。

## 快速开始

需要 Docker Desktop 和 Docker Compose：

```bash
git clone https://github.com/wangyinlong-wang/docurule-ai.git
cd docurule-ai
docker compose up --build
```

访问 [http://localhost:8080](http://localhost:8080)，点击「Explore a 10-second demo」。内置演示会创建采购订单、供应商发票和收货单，固定得到 4 条通过、2 条异常；把 `Received quantity` 从 `90` 改为 `96` 后，六条规则全部通过。它不需要模型、API Key 或真实文档。

如需用本地视觉模型处理扫描件和图片：

```bash
ollama serve
ollama pull gemma4:latest
docker compose up --build
```

## 当前已经可用

- PDF、PNG、JPG、Markdown 和文本混合上传；
- 文本 PDF 解析，图片可接 Ollama 或 OpenAI 兼容接口；
- 模型离线时自动使用确定性规则兜底；
- 字段置信度和原文引用；
- 采购订单、发票、收货单的三单匹配：文档齐全、供应商、PO 号、币种、数量和金额校验；
- 保留医疗理赔示例的跨文档姓名和金额校验；
- 字段人工修改、案件批准/拒绝、JSON 审计记录导出；
- SQLite 和文件本地持久化；
- React + FastAPI 的响应式页面；
- 单容器 Docker Compose 部署；
- 后端单元/接口测试与 GitHub Actions。

![字段证据、校验结果和人工审批](docs/assets/docurule-review.png)

## 开发路线

- [x] 采购订单 + 发票 + 收货单的三单匹配模板；
- YAML 规则模板和可视化解释；
- PDF 页内坐标高亮；
- Docling、PaddleOCR 等解析器适配；
- PostgreSQL/S3/独立任务 Worker 和多人复核队列。

完整边界和验收标准见[产品规格](docs/product-spec.md)，技术演进见[架构文档](docs/architecture.md)。

## 参与贡献

欢迎提交场景模板、Provider 适配、Bug 修复和文档改进。请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，Issue 和 PR 中只使用合成或彻底匿名化的文档。

项目采用 [MIT License](LICENSE)。如果它对你有帮助，一个 ⭐ 能让更多开发者发现它。
