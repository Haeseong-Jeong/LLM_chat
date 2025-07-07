# tools.py

from langchain.tools import tool
from rag_chain import RAGChain

rag = RAGChain()  # 전역 RAG 객체

@tool
def summarize_tool(question: str) -> str:
    """문서를 요약합니다."""
    return rag.get_answer("이 문서를 요약해줘")

#def summarize_tool(question: str) -> str:
#    """문서 요약 요청을 입력값으로 받아서 요약합니다."""
#    if not question.strip():
#        question = "이 문서를 요약해줘"
#    return rag.get_answer(question)

@tool
def kpi_tool(question: str) -> str:
    """문서에서 KPI 정보를 추출합니다."""
    if not question.strip():
        question = "이 문서의 KPI 정보를 알려줘"
    return rag.get_answer(question)
    #return rag.get_answer("이 문서의 KPI 정보를 알려줘")

@tool
def default_tool(question: str) -> str:
    """기본 응답을 위한 도구입니다. 질문을 이해하지 못할 경우 이 도구를 사용하세요."""
    return rag.get_answer(question)


TOOLS = [summarize_tool, kpi_tool, default_tool]
