"""知识库搜索工具 - 供内部话术培训助手检索业务知识"""

from langchain.tools import tool
from coze_coding_dev_sdk import KnowledgeClient, Config
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context

DATASET_NAME = "training_knowledge"


def _search_knowledge(query: str, top_k: int = 5) -> str:
    """搜索知识库的公共逻辑（普通函数，供 tool 调用）"""
    ctx = request_context.get() or new_context(method="knowledge_search")
    client = KnowledgeClient(config=Config(), ctx=ctx)

    response = client.search(
        query=query,
        table_names=[DATASET_NAME],
        top_k=top_k,
        min_score=0.5,
    )

    if response.code != 0:
        return f"知识库搜索失败: {response.msg}"

    if not response.chunks:
        return "未在知识库中找到相关内容，请根据自身经验回答，并提醒新人以门店实际规则为准。"

    results = []
    for i, chunk in enumerate(response.chunks, 1):
        results.append(f"[知识片段{i}] (相关度: {chunk.score:.2f})\n{chunk.content}")

    return "\n\n---\n\n".join(results)


@tool
def knowledge_search(query: str) -> str:
    """搜索内部话术培训知识库，获取业务话术、报价规则、异议处理、到店流程等相关知识。当用户询问具体业务操作、话术模板、报价逻辑、异议处理方式等问题时，使用此工具检索相关知识。"""
    return _search_knowledge(query, top_k=5)
