# Agent Basics

Agent 是一种能够基于目标进行推理、规划并调用工具完成任务的智能系统。

在 LLM 应用中，Agent 通常由以下部分组成：

1. LLM：负责理解用户问题、生成推理过程、决定是否调用工具。
2. Tools：外部能力，例如计算器、搜索、数据库查询、RAG 检索、API 调用。
3. Memory：保存对话历史或长期用户偏好。
4. Planner：将复杂任务拆解为多个步骤。
5. Executor：执行工具调用并整合结果。

LangGraph 是一个适合构建 Agent 工作流的框架。它使用图结构表达 Agent 的执行流程，例如：

START -> agent -> tools -> agent -> END

RAG 是 Retrieval-Augmented Generation 的缩写，即检索增强生成。它通常先从知识库中检索相关内容，再把检索结果提供给 LLM 生成回答。

RAG 的核心流程包括：

1. 文档加载
2. 文本切分
3. 索引构建
4. 查询检索
5. 上下文增强生成

在工程项目中，RAG 通常被封装成一个工具，让 Agent 在需要外部知识时主动调用。