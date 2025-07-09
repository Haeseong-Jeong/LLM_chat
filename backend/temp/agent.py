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

    # 기존 코드에서 이 부분만 수정
    agent = initialize_agent(
        tools=TOOLS,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=2,  # 주석 해제하고 2로 설정
        early_stopping_method="generate",  # 추가
        agent_kwargs={
            "prefix": (
                "당신은 효율적인 한국어 AI 어시스턴트입니다.\n"
                "각 도구는 정확히 한 번만 사용하고 바로 완전한 답변을 제공합니다.\n"
                "도구 결과가 부족해도 추가 사용하지 않고 가능한 범위에서 답변합니다.\n"
            ),
            "suffix": (
                "질문: {input}\n\n"
                "진행 순서:\n"
                "Thought: 질문 분석 후 적절한 도구 선택\n"
                "Action: [도구명]\n"
                "Action Input: {input}\n"
                "Observation: [결과]\n"
                "Final Answer: 관찰 결과를 바탕으로 한국어로 상세한 최종 답변\n\n"
                "중요: 도구는 한 번만 사용, Final Answer는 구체적으로 작성\n"
                "{agent_scratchpad}"
            )
        }
    )

    return agent

