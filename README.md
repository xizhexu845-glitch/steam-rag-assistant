# Steam RAG Assistant
A Chinese-language game-information assistant using retrieval-augmented generation (RAG).

## 项目概述
将游戏信息整理为文档，通过智谱 Embedding、Chroma 检索和聊天模型生成回答，使用 Streamlit 展示对话和检索信息。代码包含游戏信息采集模块，但默认演示不执行采集。

## Architecture
JSON → document normalization → embeddings → Chroma → retrieval → prompt + LLM → Streamlit.
Conversation history can be used to rewrite follow-up questions before retrieval.

## Quick start
Use Python 3.10 or 3.11. From the repository root:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:ZHIPUAI_API_KEY = "your-own-key"
python start.py --build-json examples/games.synthetic.json
python start.py
```
On macOS/Linux, activate with `source .venv/bin/activate` and set the key with `export ZHIPUAI_API_KEY=...`.
`.env.example` is documentation only; the application does not automatically load `.env` files.
Building an index and chatting call external model APIs and may incur charges. Only send data you are authorized to send. The original credential is not included.
The shipped JSON is invented demo content, not real Steam data. Use your own authorized JSON with the same schema for a useful knowledge base.

## Repository
- `agent/`: model adapter, prompts and retrieval chains
- `DataProcess/`: document preparation, embeddings and indexing
- `webui/`: conversational interface
- `steam_crawler/`: optional original collection utilities
- `examples/`: synthetic fixture

## Known limitations
- This is a prototype, not a production recommendation system; no measured accuracy or latency claim is made.
- The sidebar and answer chain retrieve separately; sidebar documents are retrieval context, not guaranteed exact answer citations.
- Retrieval and generation may be repeated in the current chain; optimize and evaluate before claiming efficiency gains.
- Original collection utilities need a locally supplied `data_base/steam_category.json` and permission to collect/use the source. They are not required by the demo and are not run by the launcher.
- Full live API behavior requires a compatible account, model access and connectivity. No real API calls were made during repository preparation.
- Packaging checks and offline tests do not prove model answer quality.

## Ownership
Personal project by 徐思哲 (xizhexu845-glitch). See OWNERSHIP.md for third-party material handling. Original datasets, binary index, avatars and bundled environment are excluded.

## Offline checks
```bash
python -m unittest discover -s tests -v
```
