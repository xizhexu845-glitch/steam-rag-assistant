# Steam 游戏信息问答助手 | Steam RAG Assistant

[中文说明](#中文说明) · [English](#english)

## 中文说明

### 项目简介
基于检索增强生成（RAG）的中文游戏信息问答原型。将游戏信息转换为文档，使用智谱 Embedding 和 Chroma 构建知识库，再结合聊天模型生成回答，通过 Streamlit 展示对话和检索信息。


### 功能与技术流程
- 游戏信息文档化、向量化及本地索引更新。
- 根据用户问题检索相关文档，结合上下文生成回答。
- 利用聊天历史改写后续问题，支持多轮对话和流式输出。
- 在界面侧栏展示检索信息，便于查看上下文。
- 保留可选采集模块；默认演示与启动程序均不执行采集。

```text
JSON 游戏信息 → 文档整理 → Embedding → Chroma 向量库
用户问题 + 对话历史 → 检索 → 提示词 + 聊天模型 → Streamlit
```

### 安装与运行
在仓库根目录执行以下命令。原项目使用 Python 3.10；仓库整理时的离线测试使用 Windows / Python 3.12，详见 [验证记录](VERIFICATION.md)。

Windows PowerShell：
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:ZHIPUAI_API_KEY = "your-own-key"
python start.py --build-json examples/games.synthetic.json
python start.py
```

macOS / Linux：
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export ZHIPUAI_API_KEY="your-own-key"
python start.py --build-json examples/games.synthetic.json
python start.py
```

- `.env.example` 仅作为配置示例，程序不会自动加载 `.env`。
- 构建索引和生成回答会调用外部模型 API，可能产生费用；只提交有权使用和发送的数据。
- 仓库中的 JSON 是虚构示例，不是真实 Steam 游戏数据。实际使用时，请提供相同结构、具备使用权限的数据。
- 原始密钥未包含在仓库中，请使用自己的环境变量配置。

### 目录结构
| 路径 | 用途 |
| --- | --- |
| `agent/` | 模型适配、提示词与检索链 |
| `DataProcess/` | 文档整理、向量化与索引更新 |
| `webui/` | Streamlit 对话界面 |
| `steam_crawler/` | 可选的原始采集工具 |
| `examples/` | 虚构示例数据 |
| `tests/` | 离线测试 |
| `start.py` | 索引构建与应用启动入口 |

### 测试与验证
```bash
python -m unittest discover -s tests -v
```
已通过3项离线测试：示例数据转换、空输入处理和缺失密钥检查。整理期间未调用真实模型 API，完整在线交互与回答质量尚未验证。详见 [VERIFICATION.md](VERIFICATION.md)。

### 已知限制
- 当前为应用原型，未提供推荐准确率、问答质量或延迟的实测结论。
- 侧栏与回答链分别检索，侧栏内容不保证与回答实际使用的材料完全一致。
- 当前链路可能重复检索与生成，需进一步优化和评估。
- 可选采集工具需要本地提供 `data_base/steam_category.json`，并确认来源的采集及使用条件；示例演示不依赖它。
- 在线运行需要有效账号、模型访问权限和网络连接；离线测试不能替代端到端验证。



---

## English

### Overview
A Chinese-language game-information prototype built with retrieval-augmented generation (RAG). Game information is converted into documents, embedded with Zhipu AI, stored in Chroma, and retrieved to support conversational answers in a Streamlit interface.


### Features and architecture
- Document preparation, embeddings, and local index updates.
- Retrieval of relevant documents to ground generated answers.
- History-aware follow-up question rewriting, multi-turn chat, and streaming output.
- A sidebar displaying retrieved context.
- Optional original collection utilities; neither the default demo nor launcher runs collection.

```text
Game JSON → document preparation → embeddings → Chroma
Question + chat history → retrieval → prompt + chat model → Streamlit
```

### Installation and usage
Run from the repository root. The original project used Python 3.10; preparation-time offline checks used Windows / Python 3.12, as recorded in [VERIFICATION.md](VERIFICATION.md).

Windows PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:ZHIPUAI_API_KEY = "your-own-key"
python start.py --build-json examples/games.synthetic.json
python start.py
```

macOS / Linux:
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export ZHIPUAI_API_KEY="your-own-key"
python start.py --build-json examples/games.synthetic.json
python start.py
```

- `.env.example` is illustrative; the application does not automatically load `.env`.
- Indexing and chat call external APIs and may incur charges. Only submit data you are authorized to use and send.
- The included JSON is fictional demo content, not real Steam data. Supply authorized data with the same schema for practical use.
- The original credential is excluded. Configure your own key through the environment.

### Repository structure
| Path | Purpose |
| --- | --- |
| `agent/` | Model adapter, prompts, and retrieval chains |
| `DataProcess/` | Document preparation, embeddings, and indexing |
| `webui/` | Streamlit chat interface |
| `steam_crawler/` | Optional original collection utilities |
| `examples/` | Synthetic demo data |
| `tests/` | Offline tests |
| `start.py` | Index-building and application entry point |

### Tests and verification
```bash
python -m unittest discover -s tests -v
```
Three offline tests passed: synthetic document normalization, empty-input handling, and missing-key rejection. No live model API calls were made during preparation. Full online integration and answer quality remain unverified. See [VERIFICATION.md](VERIFICATION.md).

### Known limitations
- This is a prototype with no measured recommendation accuracy, answer-quality, or latency claims.
- The sidebar and answer chain retrieve separately; sidebar documents are not guaranteed exact answer citations.
- The current chain may repeat retrieval and generation; further optimization and evaluation are needed.
- Optional collection utilities require a locally supplied `data_base/steam_category.json` and compliance with the source's collection and usage conditions. The demo does not depend on them.
- Live execution requires a valid account, model access, and connectivity. Offline tests do not replace end-to-end validation.


