# lm-agent 渐进实施路线图

目标：从当前 `FastAPI + OpenAI SDK` 的最小后端，逐步演进为支持流式聊天、Agent 内容块、Function Calling、RAG、Memory、MCP 和多 Agent 协作的完整 AI Agent 后端。

## 总体技术栈

### 后端技术栈

| 技术 | 阶段 | 作用 |
|---|---|---|
| `Python 3.10+` | 基础 | 后端主开发语言，也是 AI / Agent / RAG 生态最成熟的语言基础。 |
| `uv` | 基础 | Python 项目依赖、虚拟环境和运行命令管理工具，用于替代传统 `pip + venv` 工作流。 |
| `FastAPI` | 基础 | 后端 Web 框架，用于提供聊天接口、流式接口、健康检查、运行控制等 HTTP API。 |
| `Uvicorn` | 基础 | ASGI 服务运行器，用于启动 FastAPI 应用并支持异步请求处理。 |
| `OpenAI SDK` | 基础 | 调用 OpenAI 兼容模型接口，例如 DeepSeek、OpenAI 或其他兼容大模型服务。 |
| `AsyncOpenAI` | 基础 | OpenAI SDK 的异步客户端，用于实现非阻塞聊天请求和流式响应。 |
| `DeepSeek API` | 基础 | 当前默认接入的大模型服务，使用 OpenAI 兼容协议调用。 |
| `SSE` | 阶段 1 | 服务端事件推送协议，用于将 AI 回复增量、阶段状态、工具调用和引用来源持续推送给前端。 |
| `sse-starlette` | 阶段 1 | FastAPI / Starlette 生态中的 SSE 响应库，用 `EventSourceResponse` 暴露标准 SSE 流。 |
| `Pydantic` | 基础 | 请求体、响应体、事件体和工具参数的数据建模与校验。 |
| `pydantic-settings` | 基础 | 从 `.env` 加载配置，例如 API Key、模型地址、应用名称等。 |
| `python-dotenv` | 基础 | 辅助加载本地 `.env` 环境变量。 |
| `CORS Middleware` | 基础 | 允许前端 `ai` 子应用跨端口访问 `lm-agent` 后端接口。 |
| `conversationId` / `runId` / `messageId` / `blockId` / `seq` | 阶段 2 | 聊天协议 ID 体系，用于多轮上下文、运行追踪、消息归属、内容块合并和事件排障。 |
| `Function Calling / Tool Calling` | 阶段 5 | 让模型输出结构化工具调用请求，由后端执行工具并将结果回填给模型。 |
| `LangChain` | 阶段 8 | 中后期可选的 LLM 应用框架，用于封装模型、工具、Prompt、Memory 和 RAG 链路。 |
| `LangGraph` | 阶段 8 | 中后期推荐的 Agent 图式编排框架，用于表达规划、检索、工具执行、回答生成等多节点流程。 |
| `MCP` | 阶段 9 | 模型上下文协议，用于让 `lm-agent` 调用外部 MCP Server 暴露的工具、资源和 Prompt。 |
| `MCP Client` | 阶段 9 | 后端侧 MCP 调用客户端，用于连接 MCP Server、发现工具、校验参数并执行工具调用。 |
| `SQLite` | 阶段 3 / 7 | 初期轻量数据库，用于本地保存会话历史、运行记录和记忆数据。 |
| `PostgreSQL` | 阶段 3 / 7 | 后期生产化数据库，用于持久化会话、用户、运行日志、记忆和知识库元数据。 |
| `FAISS` | 阶段 6 | 本地向量检索库，适合初期 RAG Demo 和本地知识库检索。 |
| `Chroma` | 阶段 6 | 轻量向量数据库，适合快速实现文档向量化、存储和检索。 |
| `pgvector` | 阶段 6 | PostgreSQL 向量扩展，适合后期把业务数据和向量检索统一放入 PostgreSQL。 |
| `sentence-transformers` | 阶段 6 | 本地 embedding 模型库，用于将 Markdown 文档和用户问题向量化。 |
| `OpenAI Embeddings` | 阶段 6 | 云端 embedding 服务，用于生成语义向量，可替代本地 embedding 模型。 |
| `Markdown 文档加载` | 阶段 6 | 读取 `lm-document`、`lm-project`、`lm-skill` 等目录中的知识文档，作为 RAG 数据源。 |
| `文本切分 / Chunking` | 阶段 6 | 把长文档切成适合向量化和召回的小片段。 |
| `RAG` | 阶段 6 | 检索增强生成，用本地知识库检索结果增强模型回答，并通过 `QUOTE` 事件返回引用来源。 |
| `Memory` | 阶段 7 | 记忆系统，用于保存短期上下文、中期摘要和长期用户偏好。 |
| `pytest` | 测试 | 后端测试框架，用于验证接口、SSE 事件、工具调用、RAG 检索和 Memory 行为。 |
| `httpx` | 测试 / 集成 | 异步 HTTP 客户端和测试客户端，用于接口调用、集成测试和外部服务请求。 |

### 前端技术栈

| 技术 | 阶段 | 作用 |
|---|---|---|
| `React` | 前端基础 | 前端聊天窗主框架，用于构建消息列表、输入框、模式按钮和内容块渲染。 |
| `TypeScript` | 前端基础 | 前端类型系统，用于定义统一消息模型、SSE 事件类型和内容块类型。 |
| `Vite` | 前端基础 | 前端开发和构建工具，用于运行 `ai` 子应用开发环境。 |
| `qiankun` | 阶段 4 | 微前端框架，用于将 `ai` 聊天窗作为子应用接入主应用。 |
| `@microsoft/fetch-event-source` | 阶段 1 / 2 | 前端 SSE 客户端库，用于发起 POST SSE 请求、接收事件、处理中断和错误。 |
| `markdown-it` | 内容渲染 | 前端 Markdown 渲染引擎，用于渲染 AI 的回答内容。 |
| `html-react-parser` | 内容渲染 | 将 Markdown 渲染后的 HTML 转换为 React 节点，并替换为自定义组件。 |
| `highlight.js` | 内容渲染 | 代码块高亮库，用于展示 AI 回复中的代码片段。 |
| `markdown-it-katex` / `katex` | 内容渲染 | 数学公式渲染能力，用于支持行内公式和块级公式。 |
| `dompurify` | 安全 | HTML 清洗库，用于在需要开放 HTML 时防止 XSS。 |
| `ResizeObserver` | 交互体验 | 前端自动滚动辅助能力，用于在流式内容高度变化时保持聊天窗口滚动体验。 |

当前项目已有：

```text
FastAPI + OpenAI SDK + uv + pydantic-settings + sse-starlette
```

因此不需要推倒重来，直接在现有 `lm-agent` 上渐进扩展。

## 阶段 0：当前状态

当前能力：

- `FastAPI` 应用已搭好。
- `/api/v1/chat` 同步对话已存在。
- `services/agent.py` 已封装 `AsyncOpenAI`。
- `chat_stream()` 已有流式生成器，但还没有暴露成 SSE 接口。
- `sse-starlette` 已在依赖中。

当前不足：

- 前端还不能真正接后端流。
- 没有 `conversationId`。
- 没有 `runId`。
- 没有标准 SSE 事件。
- 没有 Agent 编排。
- 没有工具、RAG、记忆。

## 阶段 1：最小 SSE 聊天后端

目标：先让前端 `ai` 子应用能接上 `lm-agent` 的流式回答。

新增接口：

```text
POST /api/v1/chat/stream
```

推荐实现：

```text
sse-starlette.EventSourceResponse
```

最小事件：

```text
MESSAGE_STARTED
ANSWER_DELTA
STREAM_COMPLETED
```

最小返回示例：

```text
event: MESSAGE_STARTED
data: {
	"eventType": "MESSAGE_STARTED",
	"messageId": "msg_xxx"
}

event: ANSWER_DELTA
data: {
	"eventType": "ANSWER_DELTA",
	"messageId": "msg_xxx",
	"payload": {
		"blockId": "answer_xxx",
		"type": "answer",
		"content": "增量文本",
		"status": "streaming"
	}
}

event: STREAM_COMPLETED
data: {
	"eventType": "STREAM_COMPLETED",
	"messageId": "msg_xxx"
}
```

阶段产出：

```text
用户输入 -> 后端流式输出 -> 前端逐字展示
```

暂不做：

- RAG。
- Tool。
- Memory。
- 多 Agent。
- LangChain / LangGraph。

## 阶段 2：补齐标准 ID 体系

目标：让后端协议和前端聊天窗文档中的完整设计对齐。

增加字段：

```text
conversationId
clientRequestId
runId
messageId
blockId
seq
```

推荐关系：

```text
conversationId
	└── clientRequestId
			└── runId
					└── messageId
							└── blockId
									└── seq
```

新增事件：

```text
STREAM_CREATED
MESSAGE_STARTED
ANSWER_DELTA
MESSAGE_COMPLETE
STREAM_COMPLETED
STREAM_FAILED
```

阶段产出：

```text
工程化 SSE 聊天协议
```

简历表达：

> 设计并实现基于 SSE 的 AI 聊天流式协议，支持 `conversationId`、`runId`、`messageId`、`blockId`、`seq` 等多层 ID 追踪。

## 阶段 3：加入会话上下文

目标：支持多轮对话。

请求结构：

```json
{
	"conversationId": "conv_xxx",
	"clientRequestId": "req_xxx",
	"input": {
		"type": "TEXT",
		"text": "继续解释"
	}
}
```

后端维护：

```text
conversationId -> messages[]
```

存储演进：

```text
内存版 -> SQLite -> PostgreSQL
```

阶段能力：

- 多轮上下文。
- 对话历史管理。
- 消息裁剪。
- token 控制。
- 会话持久化。

## 阶段 4：加入 Agent 内容块

目标：让后端不只是返回 `answer`，还能返回过程块。

新增事件：

```text
PHASE
THINK_DELTA
PLAN
```

示例链路：

```text
STREAM_CREATED
MESSAGE_STARTED
PHASE
PLAN
ANSWER_DELTA
MESSAGE_COMPLETE
STREAM_COMPLETED
```

前端展示效果：

```text
正在分析问题...
回答计划：
1. 理解问题
2. 检索相关上下文
3. 生成回答

最终回答：
...
```

说明：这一阶段可以先由后端程序生成结构化过程，不必一开始就让模型真的执行复杂推理。

## 阶段 5：加入 Function Calling / Tools

目标：让模型可以调用工具。

推荐先做 3 个简单工具：

```text
get_current_time
calculate
search_local_docs
```

工具调用事件：

```text
TOOL_STARTED
TOOL_COMPLETED
```

示例：

```text
event: TOOL_STARTED
data: {
	"eventType": "TOOL_STARTED",
	"payload": {
		"blockId": "tool_001",
		"type": "tool",
		"title": "调用工具：search_local_docs",
		"status": "running",
		"data": {
			"toolName": "search_local_docs",
			"arguments": {
				"query": "Function Calling"
			}
		}
	}
}
```

完成后：

```text
event: TOOL_COMPLETED
data: {
	"eventType": "TOOL_COMPLETED",
	"payload": {
		"blockId": "tool_001",
		"type": "tool",
		"status": "success",
		"data": {
			"toolName": "search_local_docs",
			"result": "找到 3 条相关文档"
		}
	}
}
```

阶段能力：

- Tool Calling。
- Function Calling。
- 工具参数 schema。
- 工具执行结果回填模型。
- 工具调用过程可视化。

## 阶段 6：加入 RAG

目标：让 `lm-agent` 能基于本地文档回答问题。

适合接入的本地知识来源：

```text
lm-document/
lm-project/
lm-skill/
lm-ai-future/
```

技术链路：

```text
Markdown 文档
	-> 文档切分
	-> 向量化
	-> 向量库存储
	-> query 检索
	-> prompt 拼接
	-> LLM 回答
	-> QUOTE 引用返回前端
```

推荐依赖：

```text
sentence-transformers / OpenAI embeddings
FAISS / Chroma / pgvector
```

存储建议：

```text
初期：Chroma 或 FAISS
后期：PostgreSQL + pgvector
```

前端协议事件：

```text
QUOTE
```

阶段产出：

```text
基于本地 Markdown 文档的知识库问答
```

## 阶段 7：加入 Memory

目标：让 Agent 记住用户偏好、历史上下文和长期信息。

记忆分层：

```text
短期记忆：当前 conversation messages
中期记忆：最近 N 轮摘要
长期记忆：用户偏好 / 项目知识 / 常用上下文
```

存储建议：

```text
初期：SQLite
后期：PostgreSQL
长期记忆：memory_text -> embedding -> vector search
```

阶段产出：

```text
可持续对话的个人 AI 助手
```

## 阶段 8：引入 LangGraph / LangChain

目标：把手写 Agent 编排升级成图式工作流。

推荐顺序：

```text
先手写 Agent 流程
	-> 理解工具调用和 RAG
	-> 再迁移 LangGraph
```

适合表达的流程：

```text
用户输入
	-> 规划节点
	-> 检索节点
	-> 工具节点
	-> 回答节点
	-> 总结节点
```

说明：LangChain / LangGraph 是简历关键词，但更重要的是理解什么时候该用，什么时候不该用。

## 阶段 9：支持 MCP 工具生态

目标：让 `lm-agent` 可以调用 MCP Server 提供的工具。

调用链路：

```text
Agent
	-> MCP Client
	-> MCP Server
	-> tools/resources/prompts
```

可扩展能力：

```text
文件搜索
代码分析
Swagger 查询
数据库查询
浏览器操作
知识库检索
```

简历表达：

> 实现 Agent 与 MCP Server 的工具调用集成，支持动态发现工具、参数校验、调用结果回填和前端工具调用过程展示。

## 阶段 10：多 Agent 协作

目标：从单 Agent 升级到多角色协作。

推荐角色：

```text
PlannerAgent：拆解任务
ResearchAgent：检索资料
ToolAgent：调用工具
AnswerAgent：生成回答
ReviewAgent：检查结果
```

前端展示方式一：每个 Agent 独立消息。

```text
runId
	├── msg_planner
	├── msg_researcher
	├── msg_tool
	└── msg_summary
```

前端展示方式二：多个 Agent 作为同一条消息里的 block。

```text
runId
	└── msg_ai
			├── planner_block
			├── researcher_block
			├── tool_block
			└── answer_block
```

初期推荐：

```text
一个 runId -> 一个 messageId -> 多个 blockId
```

## 推荐最终架构

```text
lm-agent
├── api/
│   └── routes/
│       ├── chat.py
│       ├── runs.py
│       └── health.py
├── core/
│   ├── config.py
│   ├── ids.py
│   └── sse.py
├── models/
│   ├── schemas.py
│   ├── chat.py
│   └── events.py
├── services/
│   ├── agent.py
│   ├── chat_stream.py
│   ├── conversation.py
│   ├── tool_service.py
│   ├── rag_service.py
│   └── memory_service.py
├── tools/
│   ├── time_tool.py
│   ├── calculator.py
│   └── local_docs_search.py
├── rag/
│   ├── loader.py
│   ├── splitter.py
│   ├── embeddings.py
│   └── vector_store.py
└── main.py
```

## 学习与实现顺序

### 第 1 个月：AI 后端基础

学习：

```text
FastAPI
Pydantic
uv
AsyncOpenAI
SSE
流式响应
```

产出：

```text
lm-agent 支持 /chat/stream
```

### 第 2 个月：聊天协议工程化

学习：

```text
conversationId
runId
messageId
blockId
seq
错误事件
停止生成
重试机制
```

产出：

```text
前端 ai 子应用可完整消费 lm-agent SSE
```

### 第 3 个月：Tools / Function Calling

学习：

```text
Function Calling
工具 schema
工具执行
TOOL_STARTED / TOOL_COMPLETED
```

产出：

```text
Agent 能调用 2-3 个工具
```

### 第 4 个月：RAG

学习：

```text
文档加载
文本切片
向量化
向量检索
引用来源
QUOTE 事件
```

产出：

```text
基于本地 Markdown 文档的知识库问答
```

### 第 5 个月：Memory + 持久化

学习：

```text
SQLite / PostgreSQL
会话历史
短期记忆
长期记忆
用户偏好
```

产出：

```text
可持续对话的个人 AI 助手
```

### 第 6 个月：LangGraph + MCP + 多 Agent

学习：

```text
LangGraph
MCP Client
多 Agent 编排
任务拆解
结果审查
```

产出：

```text
完整 Agent 平台 Demo
```

## 最小作品集目标

项目名：

```text
LM Agent：面向企业知识库的可视化 Agent 聊天平台
```

核心卖点：

```text
FastAPI + SSE 流式聊天
React + TypeScript 前端聊天窗
统一 Agent 事件协议
Function Calling 工具调用
RAG 文档问答
QUOTE 引用来源
Memory 会话记忆
MCP 工具生态扩展
```

简历描述：

> 设计并实现一套基于 `FastAPI + React + SSE` 的 AI Agent 聊天平台，后端基于 `OpenAI SDK` 实现流式对话、Function Calling、RAG 检索和 Memory 记忆能力；前端通过统一消息模型渲染 `think / plan / tool / answer / quote` 等结构化内容块，支持多轮会话、停止生成、引用来源展示和 Agent 执行过程可视化。

## 最推荐路线总结

```text
1. FastAPI SSE 流式聊天
2. 标准事件协议和 ID 体系
3. 多轮会话
4. Agent 内容块
5. Function Calling / Tools
6. RAG 知识库
7. Memory 记忆
8. LangGraph 编排
9. MCP 工具生态
10. 多 Agent 协作
```
