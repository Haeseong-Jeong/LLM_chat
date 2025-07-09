# agent_graph.py

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnableLambda
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3", temperature=0.1, base_url="http://localhost:11434")

# 상태 정의
class AgentState(dict):
    question: str
    tool_input: str
    observation: str
    final_answer: str

# Tool 선택 노드
def select_tool(state):
    return {"tool_input": state["question"]}

# Tool 실행 노드
# def run_tool(state):
#     for tool in TOOLS:
#         if tool.name in state["question"]:
#             result = tool.func(state["question"])
#             return {"observation": result}
#     # fallback
#     return {"observation": TOOLS[-1].func(state["question"])}

# Tool 실행 노드
# def run_tool(state):
#     # tools.py에서 TOOLS import (circular import 방지)
#     from tools import TOOLS
    
#     question = state["question"].lower()
    
#     # 키워드 기반 tool 선택
#     if any(keyword in question for keyword in ["요약", "정리", "요약해"]):
#         result = TOOLS[0].func(state["question"])  # summarize_tool
#     elif any(keyword in question for keyword in ["수치", "숫자", "데이터", "통계"]):
#         result = TOOLS[1].invoke(state["question"])  # numerical_tool
#     elif any(keyword in question for keyword in ["검색", "찾아", "찾기"]):
#         result = TOOLS[2].func(state["question"])  # search_documents_tool
#     else:
#         result = TOOLS[3].func(state["question"])  # default_tool
#     return {"observation": result}

KEYWORD_TOOL_MAP = {
    ("요약", "정리", "요약해"): "summarize",
    ("수치", "숫자", "데이터", "통계"): "numerical",
    ("검색", "찾아", "찾기"): "search_documents"
}

def run_tool(state):
    from tools import TOOLS
    question = state["question"].lower()

    for keywords, tool_name in KEYWORD_TOOL_MAP.items():
        if any(kw in question for kw in keywords):
            return {"observation": TOOLS[tool_name].func(state["question"])}

    return {"observation": TOOLS["default"].func(state["question"])}



# Final Answer 요약 노드
def generate_final_answer(state):
    obs = state["observation"]
    prompt = f"""당신은 한국어 응답을 생성하는 응답기입니다.
아래 관찰 결과를 자연스럽고 구체적인 최종 답변을 한국말로 정리해주세요.

관찰 결과:
{obs}

답변:"""
    answer = llm.invoke(prompt)
    return {"final_answer": answer}

# Graph 구성
def build_agent_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("select_tool", RunnableLambda(select_tool))
    workflow.add_node("run_tool", RunnableLambda(run_tool))
    workflow.add_node("generate_final_answer", RunnableLambda(generate_final_answer))

    workflow.set_entry_point("select_tool")
    workflow.add_edge("select_tool", "run_tool")
    workflow.add_edge("run_tool", "generate_final_answer")
    workflow.add_edge("generate_final_answer", END)

    return workflow.compile()
