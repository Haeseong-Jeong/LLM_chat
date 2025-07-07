# rag_chain.py

import logging
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class RAGChain:
    """RAG 체인 클래스"""

    def __init__(self, db_dir: str = "vector_db"):
        self.db_dir = db_dir
        self.chain = self._build_chain()

    def _build_chain(self) -> RetrievalQA:
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name="intfloat/e5-small-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )

            vectorstore = FAISS.load_local(
                self.db_dir,
                embeddings,
                allow_dangerous_deserialization=True
            )

            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )

            llm = OllamaLLM(
                model="llama3",
                temperature=0.1,
                base_url="http://localhost:11434"
            )

            prompt_template = """
            당신은 문서 분석 전문가입니다. 주어진 문서 내용을 바탕으로 질문에 답변해주세요.

            문서 내용:
            {context}

            질문: {question}

            답변 시 다음 규칙을 따르세요:
            1. 문서 내용을 기반으로 정확하게 답변하세요
            2. 답변은 한국어로 작성하세요
            3. 문서에 없는 내용은 추측하지 말고 모른다고 하세요
            4. 답변은 명확하고 구체적으로 작성하세요

            답변:
            """

            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )

            chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True
            )

            return chain

        except Exception as e:
            logger.error(f"RAG 체인 구축 오류: {str(e)}")
            raise

    def get_answer(self, question: str) -> str:
        try:
            result = self.chain.invoke({"query": question})
            answer = result.get("result", "답변을 생성할 수 없습니다.")
            source_docs = result.get("source_documents", [])
            if source_docs:
                sources = list(set([doc.metadata.get("source", "Unknown") for doc in source_docs]))
                answer += f"\n\n[참고 문서: {', '.join(sources)}]"
            return answer
        except Exception as e:
            logger.error(f"답변 생성 오류: {str(e)}")
            return f"답변 생성 중 오류가 발생했습니다: {str(e)}"
