# tools.py

from langchain.tools import tool
from langchain.agents import Tool
from langchain_core.documents import Document
from langchain_ollama import OllamaLLM

from analyzer import InOutAnalyzer
from document_processor import DocumentProcessor
from config import UPLOAD_DIR, VECTOR_DB_DIR

llm = OllamaLLM(model="llama3", temperature=0.1, base_url="http://localhost:11434")

def query_with_context(question: str, custom_prompt_template: str = None, k: int = 3) -> str:
    """벡터스토어에서 문서 검색하고 LLM으로 답변 생성하는 공통 함수"""
    processor = DocumentProcessor(db_dir=VECTOR_DB_DIR)
    vectorstore = processor.load_vector_store()
    if vectorstore is None:
        return "벡터스토어를 사용할 수 없습니다."
    
    try:
        # 관련 문서 검색
        relevant_docs = vectorstore.similarity_search(question, k=k)
        
        if not relevant_docs:
            return "관련 정보를 찾을 수 없습니다."
        
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        # 기본 프롬프트 또는 커스텀 프롬프트 사용
        if custom_prompt_template:
            prompt = custom_prompt_template.format(context=context, question=question)
        else:
            prompt = f"""
            다음 문서를 참고하여 질문에 답해주세요:
            
            문서 내용:
            {context}
            
            질문: {question}
            
            답변:
            """
        
        response = llm.invoke(prompt)
        return response
        
    except Exception as e:
        return f"답변 생성 중 오류가 발생했습니다: {str(e)}"

@tool
def summarize_tool(question: str) -> str:
    """문서 요약 요청을 입력값으로 받아서 요약합니다."""
    if not question.strip():
        question = "이 문서를 요약해줘"
    
    prompt_template = """
    다음 문서들을 바탕으로 질문에 답해주세요:
    
    문서 내용:
    {context}
    
    질문: {question}
    
    답변:
    """
    
    return query_with_context(question, prompt_template, k=3)

@tool
def search_documents_tool(query: str) -> str:
    """문서에서 특정 정보를 검색합니다."""
    prompt_template = """
    다음 문서에서 '{question}'와 관련된 정보를 찾아 정리해주세요:
    
    {context}
    
    검색어: {question}
    답변:
    """
    
    return query_with_context(query, prompt_template, k=5)

@tool
def default_tool(question: str) -> str:
    """기본 응답을 위한 도구입니다."""
    return query_with_context(question)  # 기본 프롬프트 사용


@tool
def visualization(question: str) -> str:
    """문서 정보들을 시각화합니다."""   
    try:
        analyzer = InOutAnalyzer(UPLOAD_DIR)
        analyzer.load_all_data()
        daily_summary_df = analyzer.get_daily_summary()
        daily_summary_df["Date"] = daily_summary_df["Date"].astype(str)
        
        daily_summary_df = daily_summary_df.set_index("Date")
        daily_summary_df = daily_summary_df.T

        if daily_summary_df is None:
            return "시각화 할 데이터가 없습니다."
        
        # (1) 벡터 DB에 저장 (RAG가 이후 질문에서도 참조할 수 있도록)
        #text = f"이 문서의 수치 데이터는 다음과 같습니다:\n{daily_summary_df.to_string(index=False)}"
        # 프롬프트용 문서 텍스트
        text = daily_summary_df.to_markdown(index=True)

        processor = DocumentProcessor(db_dir=VECTOR_DB_DIR)
        processor.add_to_vector_store([Document(page_content=text, metadata={"source": "visualization_tool"})])

        # (2) RAG 응답 생성 (기존 문서 + 수치 데이터 결합)
        prompt_template = """
        다음 문서와 시각화 데이터를 참고하여 질문에 답해주세요:
        
        기존 문서 및 시각화 데이터:
        {context}
        
        새로운 시각화 데이터:
        {get_daily_summary}
        
        질문: {question}
        
        답변: (시각화 데이터를 활용하여 구체적으로 답변해주세요)
        """
        
        # 기존 문서에서 관련 정보 검색
        processor = DocumentProcessor(db_dir=VECTOR_DB_DIR)
        vectorstore = processor.load_vector_store()
        if vectorstore is not None:
            relevant_docs = vectorstore.similarity_search(question, k=2)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            prompt = prompt_template.format(
                context=context, 
                get_daily_summary=text,
                question=question
            )
        else:
            prompt = f"""
            다음 시각화 데이터를 참고하여 질문에 답해주세요:
            
            시각화 데이터:
            {text}
            
            질문: {question}
            
            답변:
            """
        
        response = llm.invoke(prompt)
        
        # (3) 프론트 전달용 JSON 추가 포함
        #json_data = daily_summary_df.to_json(orient="records", force_ascii=False)
        json_data = daily_summary_df.reset_index().to_json(orient="records", force_ascii=False)
        return f"{response}\n\n[DATAFRAME_JSON_START]{json_data}[DATAFRAME_JSON_END]"

    except Exception as e:
        return f"오류 발생: {e}"

visualization_tool = Tool(
    name="시각화 데이터 계산",
    func=visualization,
    description="문서의 시각화 데이터를 추출하고 시각화합니다."
)

TOOLS = {
    "summarize": summarize_tool,
    "visualization": visualization_tool,
    "search_documents": search_documents_tool,
    "default": default_tool
}