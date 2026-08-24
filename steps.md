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
| 请求超时 / 取消 / 幂等 / 结构化日志 | 阶段 2.5 | 建立后续会话、Tools、RAG 和 MCP 共用的最小工程基线。 |
| `Function Calling / Tool Calling` | 阶段 5 | 让模型输出结构化工具调用请求，由后端执行工具并将结果回填给模型。 |
| `LangChain` | 阶段 7B | 完成手写 Tool Calling、RAG 和 Memory 后引入，用于封装模型、工具、Prompt 和检索链路。 |
| `LangGraph` | 阶段 8 | 在理解手写 Agent 循环后引入，用于表达规划、检索、工具执行、回答生成等有状态工作流。 |
| `MCP` | 阶段 9 | 模型上下文协议，用于让 `lm-agent` 调用外部 MCP Server 暴露的工具、资源和 Prompt。 |
| `MCP Client` | 阶段 9 | 后端侧 MCP 调用客户端，用于连接 MCP Server、发现工具、校验参数并执行工具调用。 |
| `SQLAlchemy 2.x` | 阶段 3.5 / 8.5 | 统一 SQLite 与 PostgreSQL 的异步数据访问和实体映射，降低后续数据库迁移成本。 |
| `Alembic` | 阶段 3.5 / 8.5 | 管理数据库 Schema 版本和迁移脚本。 |
| `SQLite` | 阶段 3.5 / 7A | 在内存版多轮会话跑通后引入，用于本地保存会话历史、运行记录和记忆数据。 |
| `PostgreSQL` | 可选阶段 8.5 | 有真实多用户或生产部署需求时迁移，用于持久化会话、用户、运行日志、记忆和知识库元数据。 |
| `FAISS` | 阶段 6 | 本地向量检索库，适合初期 RAG Demo 和本地知识库检索。 |
| `Chroma` | 阶段 6 | 轻量向量数据库，适合快速实现文档向量化、存储和检索。 |
| `pgvector` | 可选阶段 8.5 | PostgreSQL 向量扩展，用于按需把阶段 6 的本地向量检索迁移到生产数据库。 |
| `sentence-transformers` | 阶段 6 | 本地 embedding 模型库，用于将 Markdown 文档和用户问题向量化。 |
| `OpenAI Embeddings` | 阶段 6 | 云端 embedding 服务，用于生成语义向量，可替代本地 embedding 模型。 |
| `Markdown 文档加载` | 阶段 6 | 读取 `lm-document`、`lm-project`、`lm-skill` 等目录中的知识文档，作为 RAG 数据源。 |
| `文本切分 / Chunking` | 阶段 6 | 把长文档切成适合向量化和召回的小片段。 |
| `RAG` | 阶段 6 | 检索增强生成，用本地知识库检索结果增强模型回答，并通过 `QUOTE` 事件返回引用来源。 |
| `Memory` | 阶段 7A | 记忆系统，用于保存会话摘要、跨会话用户偏好和可语义召回的长期信息。 |
| `pytest` | 测试 | 后端测试框架，用于验证接口、SSE 事件、工具调用、RAG 检索和 Memory 行为。 |
| `httpx` | 测试 / 集成 | 异步 HTTP 客户端和测试客户端，用于接口调用、集成测试和外部服务请求。 |

### 前端技术栈

| 技术 | 阶段 | 作用 |
|---|---|---|
| `React` | 前端基础 | 前端聊天窗主框架，用于构建消息列表、输入框、模式按钮和内容块渲染。 |
| `TypeScript` | 前端基础 | 前端类型系统，用于定义统一消息模型、SSE 事件类型和内容块类型。 |
| `Vite` | 前端基础 | 前端开发和构建工具，用于运行 `ai` 子应用开发环境。 |
| `qiankun` | 前端 F1 | 微前端框架，用于将 `ai` 聊天窗作为子应用接入主应用。 |
| `@microsoft/fetch-event-source` | 前端 F1 | 前端 SSE 客户端库，用于发起 POST SSE 请求、接收事件、处理中断和错误。 |
| `markdown-it` | 前端 F1 / F3 | 前端 Markdown 渲染引擎，用于渲染 AI 回答和引用标记。 |
| `html-react-parser` | 前端 F1 / F3 | 将 Markdown 渲染后的 HTML 转换为 React 节点，并替换为自定义组件。 |
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
- `POST /api/v1/chat/stream` 已通过 `EventSourceResponse` 暴露 SSE 流。
- 已有 `STREAM_CREATED`、`MESSAGE_STARTED`、`ANSWER_DELTA`、`MESSAGE_COMPLETE`、`STREAM_COMPLETED`、`STREAM_FAILED` 事件。
- 已有 `conversationId`、`clientRequestId`、`runId`、`messageId`、`blockId`、`seq` ID 体系。
- `sse-starlette` 已在依赖中。

当前不足：

- 阶段 2 的 SSE 序列化、事件顺序、断开和失败场景还需要完整验收。
- 缺少请求超时、取消传播、幂等、模型白名单和结构化日志等工程基线。
- `conversationId` 目前只用于请求追踪，还没有关联真实历史消息。
- 没有会话存储和服务重启恢复能力。
- 没有 Agent 编排。
- 没有工具、RAG、记忆。

当前里程碑：

```text
阶段 1：基本完成
阶段 2：实现完成，正在收尾验收
阶段 3：尚未开始
```

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

## 阶段 2.5：工程基线

目标：在加入会话、Tools 和 RAG 前，先建立所有后续能力共用的请求控制、幂等和可观测性基础。

请求控制：

```text
请求超时
客户端断开检测
停止生成
取消向上游模型传播
输入长度限制
上游异常转换
```

幂等与模型控制：

```text
clientRequestId 幂等
模型别名
模型白名单
Provider 配置
```

前端只传稳定别名，由后端映射具体模型：

```text
default -> 默认聊天模型
fast -> 快速模型
reasoning -> 推理模型
```

结构化日志统一携带：

```text
conversationId
clientRequestId
runId
messageId
model
duration
status
errorCode
inputTokens
outputTokens
```

新增终止事件：

```text
STREAM_CANCELLED
```

阶段验收：

```text
重复 clientRequestId 不会重复执行
客户端断开后停止上游生成
超时能够返回统一失败事件
模型名称不能任意透传
日志可以通过 runId 串联一次请求
```

## 阶段 3：加入会话上下文

目标：先使用内存仓库支持多轮对话，理解历史消息管理和上下文预算，不在这一阶段操作数据库。

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

推荐边界：

```text
Chat API
	-> ConversationService
	-> ConversationRepository
	-> AgentService
```

第一版实现：

```text
ConversationRepository
	-> InMemoryConversationRepository
```

推荐接口：

```text
get_conversation
list_messages
append_message
create_run
update_run
```

多轮执行链路：

```text
接收用户请求
	-> 根据 conversationId 获取历史消息
	-> 写入本轮 user message
	-> 裁剪历史上下文
	-> 调用模型并流式输出
	-> 聚合完整 assistant message
	-> 写入助手消息
	-> 更新 run 状态
```

第一版裁剪策略：

```text
始终保留 system message
始终保留当前用户消息
从最近消息向前截取
最多保留 N 轮
```

第二版再加入：

```text
token 估算
上下文预算
历史摘要
上下文溢出处理
```

阶段能力：

- 多轮上下文。
- 对话历史管理。
- 消息裁剪。
- token 控制。
- 会话隔离。
- 内存仓库抽象。

阶段验收：

```text
同一个 conversationId 可以连续多轮对话
不同 conversationId 不会共享历史
传给模型的消息角色和顺序正确
历史过长时能够裁剪
模型失败不会写入伪造的 assistant message
```

## 阶段 3.5：加入 SQLite 会话持久化

目标：在内存版会话通过验收后，将会话、消息和运行记录持久化，支持服务重启后恢复对话。

推荐依赖：

```text
SQLAlchemy 2.x
Alembic
SQLite
```

第一版数据表：

```text
conversations
	-> id / title / created_at / updated_at

messages
	-> id / conversation_id / role / content / status / seq / created_at

runs
	-> id / conversation_id / client_request_id / model / status
	-> error_code / input_tokens / output_tokens / created_at / completed_at
```

当前阶段暂不加入：

```text
users
memories
documents
document_chunks
tool_calls
message_blocks
```

存储执行链路：

```text
创建 run，状态为 running
	-> 保存 user message
	-> 查询历史消息
	-> 调用模型并流式输出
	-> 保存 assistant message
	-> 更新 run 为 completed
```

失败处理：

```text
保留 user message
不保存伪造的完整 assistant message
更新 run 为 failed
记录 error_code
```

仓库实现演进：

```text
ConversationRepository
	├── InMemoryConversationRepository
	└── SQLiteConversationRepository
```

阶段验收：

```text
服务重启后能够恢复会话
历史消息顺序稳定
重复 clientRequestId 不产生重复 run
消息与 conversation 正确关联
数据库异常能够转换为统一失败事件
业务层可以在内存与 SQLite 实现之间切换
```

## 阶段 4：预留内容块协议

目标：先稳定统一内容块模型和前端适配边界，不在没有真实执行过程时主动发送装饰性的阶段事件。

当前阶段实现：

```text
UnifiedContentBlock
Event Adapter
AnswerBlock
PlanBlock（可选）
未知 block 降级渲染
```

后端事件策略：

```text
STREAM_CREATED
MESSAGE_STARTED
PLAN（可选）
ANSWER_DELTA
MESSAGE_COMPLETE
STREAM_COMPLETED
```

暂不主动发送：

```text
PHASE
PROGRESS
```

说明：协议可以提前支持多种 block，但只有存在真实 Tool、RAG 或工作流节点时，才展示可验证的执行状态。

## 阶段 5：加入 Function Calling / Tools

目标：让模型可以调用工具。

推荐先做 3 个简单工具：

```text
get_current_time
calculate
query_fixed_data
```

工具调用与执行过程事件：

```text
PHASE
PROGRESS
PLAN
TOOL_STARTED
TOOL_COMPLETED
```

真实执行链路：

```text
PHASE：正在选择工具
	-> PROGRESS：参数校验完成
	-> TOOL_STARTED：开始执行工具
	-> TOOL_COMPLETED：工具执行完成
	-> PHASE：正在整理最终回答
	-> ANSWER_DELTA
```

示例：

```text
event: TOOL_STARTED
data: {
	"eventType": "TOOL_STARTED",
	"payload": {
		"blockId": "tool_001",
		"type": "tool",
		"title": "调用工具：query_fixed_data",
		"status": "running",
		"data": {
			"toolName": "query_fixed_data",
			"arguments": {
				"key": "demo"
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
			"toolName": "query_fixed_data",
			"result": "返回固定测试数据"
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
- 工具超时、参数错误和最大调用轮数控制。

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
FAISS / Chroma
```

存储建议：

```text
阶段 6：Chroma 或 FAISS
可选阶段 8.5：PostgreSQL + pgvector
```

说明：阶段 6 先手写完成文档加载、切分、Embedding、Top-K 检索和 Prompt 拼接；完成后开始学习 LangChain 的模型、工具和 Retriever 抽象，但暂不立即重构全部代码。

在这一阶段加入 `search_local_docs` 工具，将本地检索能力接入阶段 5 已完成的 Tool Calling 循环。

检索评估：

```text
准备固定测试问题集
	-> 检查正确文档是否进入 Top-K
	-> 检查引用是否来自真实检索结果
	-> 调整 chunk size / overlap / Top-K
	-> 验证无相关文档时不会编造引用
```

前端协议事件：

```text
QUOTE
```

阶段产出：

```text
基于本地 Markdown 文档的知识库问答
```

## 阶段 7A：手写 Memory

目标：继续使用 OpenAI SDK 和 SQLite，手写完成跨会话记忆链路，先验证业务规则再引入框架抽象。

记忆分层：

```text
会话历史：阶段 3 的 conversation messages
会话摘要：当前会话过长后的压缩结果
跨会话记忆：用户偏好 / 项目背景 / 长期事实
语义记忆：通过 embedding 召回的长期信息
```

存储建议：

```text
当前阶段：SQLite
可选阶段 8.5：PostgreSQL
跨会话记忆：memory_text -> embedding -> vector search
```

Memory 执行链路：

```text
对话完成
	-> 提取候选记忆
	-> 校验和去重
	-> 保存或更新
	-> 新请求按相关性召回
	-> 注入模型上下文
```

阶段能力：

```text
记忆提取
记忆去重
记忆更新
记忆召回
记忆删除
用户隔离
```

阶段验收：

```text
不同用户的记忆不会串联
重复偏好不会持续新增
过期记忆能够被更新
用户可以查看和删除记忆
召回内容与当前问题相关
```

阶段产出：

```text
SQLite 持久化的个人 AI 助手
```

## 阶段 7B：引入 LangChain 抽象层

目标：在手写 Tools、RAG 和 Memory 通过验收后，引入 LangChain 统一模型、消息、工具和 Retriever 适配。

引入顺序：

```text
保留手写 SSE 协议和业务存储
	-> 统一模型与消息抽象
	-> 接入工具定义和结构化输出
	-> 封装 Retriever 与 RAG 链路
	-> 对比迁移前后的行为和测试结果
```

继续保留：

```text
FastAPI 接口
SSE 事件协议
数据库表和 Repository
Memory 提取与更新规则
前端内容块协议
```

阶段产出：

```text
可复用的 LangChain 模型、工具和检索适配层
```

## 阶段 8：引入 LangGraph

目标：把手写 Agent 编排升级成有状态、可中断和可恢复的图式工作流，当前阶段继续使用本地存储。

推荐顺序：

```text
阶段 5～7A：手写 Agent、Tool Calling、RAG 和 Memory
	-> 使用 LangChain 抽象模型、工具和检索层
	-> 使用 LangGraph 编排有状态工作流
	-> 使用 SQLite Checkpoint 验证状态恢复
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

阶段能力：

```text
Agent State
节点与条件路由
Checkpoint
失败重试
中断与恢复
人工审批
```

说明：LangChain / LangGraph 是简历关键词，但更重要的是理解它们封装了什么；先在 SQLite 上验证编排行为，再进行生产数据库迁移。

## 可选阶段 8.5：迁移 PostgreSQL 与 pgvector

目标：当项目出现真实多用户、多实例或生产部署需求时，将业务数据和向量数据迁移到生产级数据库；作品集最低版本不强制完成。

作品集最低存储方案：

```text
SQLite + Chroma / FAISS
```

适合迁移的场景：

```text
真实多用户
多实例部署
高并发写入
复杂查询与统计
独立备份和云端托管
大量向量数据
```

迁移顺序：

```text
SQLite -> PostgreSQL
	-> 验证会话、消息、运行和记忆数据
	-> 迁移 LangGraph Checkpoint

Chroma / FAISS -> pgvector
	-> 迁移文档块和向量
	-> 重新验证 Top-K 和引用结果
```

PostgreSQL 数据范围：

```text
users
conversations
messages
runs
tool_calls
memories
documents
document_chunks + vector
```

阶段验收：

```text
SQLite 与 PostgreSQL 仓库行为一致
迁移后历史会话可以正常恢复
LangGraph Checkpoint 可以中断恢复
pgvector 检索结果通过阶段 6 的固定评估集
```

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

安全边界：

```text
工具白名单
参数校验
调用超时与取消
输出大小限制
用户授权
敏感参数处理
审计日志
并发限制
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

## 前端并行里程碑

前端不等待后端全部完成，而是按协议能力分阶段并行开发。

### 前端 F1：聊天窗 MVP

触发时机：后端阶段 1～2 完成后。

```text
空态与输入框
用户消息和 AnswerBlock
POST SSE 接入
增量消息展示
停止生成与错误提示
自动滚动
Markdown 基础渲染
Event Adapter + UnifiedMessage
```

阶段产出：

```text
用户输入 -> 后端 SSE -> 前端逐字展示
```

### 前端 F2：Agent 执行内容块

触发时机：后端阶段 5 完成后。

```text
PlanBlock
PhaseBlock
ProgressBlock
ToolBlock
工具运行、成功和失败状态
内容块折叠与展开
```

### 前端 F3：RAG 引用展示

触发时机：后端阶段 6 完成后。

```text
QuoteBlock
引用编号
文档标题和路径
命中片段
点击定位
无引用降级
```

### 前端 F4：会话与运行控制

触发时机：后端阶段 7A～8 完成后。

```text
历史会话列表
会话恢复
记忆查看与删除
运行状态
人工审批
中断恢复
```

并行关系：

```text
后端：1 -> 2 -> 2.5 -> 3 -> 3.5 -> 4 -> 5 -> 6 -> 7A -> 7B -> 8
前端：     F1 ---------------------------> F2 -> F3 -------> F4
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
│   ├── logging.py
│   └── sse.py
├── db/
│   ├── models.py
│   ├── session.py
│   ├── repositories.py
│   └── migrations/
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
│   ├── fixed_data.py
│   └── local_docs_search.py
├── rag/
│   ├── loader.py
│   ├── splitter.py
│   ├── embeddings.py
│   └── vector_store.py
└── main.py
```

## 学习与实现顺序

### 第 1 个月：SSE 与标准事件协议

学习：

```text
FastAPI
Pydantic
uv
AsyncOpenAI
SSE
流式响应
标准事件与 ID 体系
```

产出：

```text
完成阶段 1，收尾验收阶段 2，并启动前端 F1
```

### 第 2 个月：工程基线与内存会话

学习：

```text
请求超时与取消
clientRequestId 幂等
模型别名与白名单
结构化日志
会话历史拼接
上下文裁剪
token 预算
```

产出：

```text
完成阶段 2.5 和阶段 3，支持可靠的内存版多轮会话，并完成前端 F1
```

### 第 3 个月：SQLite 与内容块协议

学习：

```text
SQLAlchemy 2.x
Alembic
SQLite
Repository 模式
统一内容块模型
Event Adapter
AnswerBlock / PlanBlock
未知 block 降级渲染
```

产出：

```text
完成阶段 3.5 和阶段 4
```

### 第 4 个月：Tools 与执行内容块

学习：

```text
Function Calling
工具参数 schema
工具执行循环
PHASE / PROGRESS
TOOL_STARTED / TOOL_COMPLETED
工具超时与最大调用轮数
```

产出：

```text
Agent 稳定调用 2～3 个确定性工具，并完成前端 F2
```

### 第 5～6 个月：RAG 与检索评估

学习：

```text
文档加载
文本切片
Embedding
Chroma / FAISS
Top-K 检索
引用来源
检索评估集
LangChain 基础概念
```

产出：

```text
完成前端 F3，形成可验证检索和引用质量的本地知识库问答
```

### 第 7 个月：手写 Memory

学习：

```text
会话摘要
跨会话记忆
记忆提取、去重和召回
记忆更新和删除
用户隔离
```

产出：

```text
完成阶段 7A 和前端 F4，形成 SQLite 持久化的个人 AI 助手
```

### 第 8 个月：LangChain 抽象层

学习：

```text
LangChain 模型与消息抽象
Tool 封装
Retriever 封装
结构化输出
迁移前后行为对比
```

产出：

```text
完成阶段 7B，形成可复用的 LangChain 适配层
```

### 第 9 个月：LangGraph

学习：

```text
Agent State
节点与条件路由
Checkpoint
失败重试
中断恢复
人工审批
```

产出：

```text
基于 SQLite Checkpoint 的有状态 Agent 工作流
```

### 可选扩展：PostgreSQL 与 pgvector

学习：

```text
PostgreSQL
数据迁移
事务与索引
LangGraph PostgreSQL Checkpoint
pgvector
向量数据迁移与回归评估
```

产出：

```text
基于 PostgreSQL + pgvector 的生产化存储层
```

该阶段不占用作品集主线固定月份，可在出现真实生产需求或核心能力完成后补充。

### 第 10 个月：MCP 与作品集验收

学习：

```text
MCP Client
工具动态发现
参数校验
调用授权
超时、取消和审计日志
端到端测试
项目部署与演示
多 Agent 可选扩展
```

产出：

```text
完成 MCP 集成、项目验收和作品集演示；多 Agent 根据剩余时间选择实现
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

> 设计并实现一套基于 `FastAPI + React + SSE` 的 AI Agent 聊天平台，后端基于 `OpenAI SDK` 实现流式对话、Function Calling、RAG 检索和 Memory 记忆能力；前端通过统一消息模型渲染 `phase / progress / plan / tool / answer / quote` 等结构化内容块，支持多轮会话、停止生成、引用来源展示和 Agent 执行过程可视化。

## 最推荐路线总结

```text
1. FastAPI SSE 流式聊天
2. 标准事件协议和 ID 体系
2.5 工程基线：超时 / 取消 / 幂等 / 日志
3. 多轮会话：内存版上下文
3.5 SQLite 会话持久化
4. 内容块协议预留，PLAN 可选
5. Function Calling / Tools + PHASE / PROGRESS
6. RAG 知识库与检索评估：Chroma / FAISS
7A. 手写 Memory 记忆
7B. LangChain 抽象层
8. LangGraph 编排：SQLite Checkpoint
8.5 可选：PostgreSQL / pgvector 生产化迁移
9. MCP 工具生态
10. 多 Agent 协作（可选扩展）

前端 F1：聊天窗 MVP
前端 F2：Agent 执行内容块
前端 F3：RAG 引用展示
前端 F4：会话与运行控制
```
