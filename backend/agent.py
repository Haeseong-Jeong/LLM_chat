# agent.py

from langchain.agents import initialize_agent, AgentType
from langchain_ollama import OllamaLLM
from tools import TOOLS

def get_agent():
    llm = OllamaLLM(
        model="llama3",
        temperature=0.1,
        base_url="http://localhost:11434"
    )

    agent = initialize_agent(
        tools=TOOLS,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        agent_kwargs = {
            "prefix": (
                "당신은 도우미 AI입니다. 사용자 질문에 따라 아래 도구 중 하나를 사용해야 합니다.\n"
                "도구 없이 직접 답변하지 마세요.\n"
                "모든 대답은 반드시 **한국어로 작성**해야 합니다.\n"
                "각 도구는 고품질 결과를 제공하므로 한 번만 사용하고 바로 최종 답변을 제공하세요."
            ),
            "suffix": (
                "질문: {input}\n\n"
                "다음 형식으로 한 번만 도구를 실행하고 바로 Final Answer를 제공합니다:\n\n"
                "Thought: 사용자 질문을 분석하여 가장 적절한 도구를 선택합니다.\n"
                "Action: tool_name\n"
                "Action Input: {input}\n"
                "Observation: 도구 실행 결과가 여기에 표시됩니다.\n"
                "Final Answer: 도구 결과를 바탕으로 사용자에게 명확하고 완성된 한국어 답변을 제공합니다.\n\n"
                "중요사항:\n"
                "- 도구는 반드시 한 번만 사용\n"
                "- Final Answer는 한국어로 작성\n"
                "- 반드시 Final Answer로 응답 종료"
            )
        },
        #max_iterations=3
    )
    return agent

