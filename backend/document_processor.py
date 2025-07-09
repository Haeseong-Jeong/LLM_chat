# document_processor.py

import os
import logging
from typing import List, Optional
import pandas as pd
from langchain_core.documents import Document
#from langchain_community.document_loaders import CSVLoader, PyPDFLoader, TextLoader
#from langchain_community.document_loaders.word_document import Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.base import VectorStore

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """문서 처리 및 벡터스토어 구축 클래스"""

    def __init__(self, db_dir: str = "vector_db"):
        self.db_dir = db_dir
        os.makedirs(self.db_dir, exist_ok=True)

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        self.embeddings = HuggingFaceEmbeddings(
            model_name="intfloat/e5-small-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )


    def load_documents(self, file_path: str) -> List[Document]:
        try:
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.csv':
                return self._load_csv(file_path)
            elif file_extension == '.xlsx':
                return self._load_excel(file_path)

            else:
                raise ValueError(f"지원하지 않는 파일 형식: {file_extension}")

        except Exception as e:
            logger.error(f"문서 로드 오류: {str(e)}")
            raise

    def _load_csv(self, file_path: str) -> List[Document]:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp949')

        content = df.to_string(index=False)
        return [Document(page_content=content, metadata={"source": file_path})]
    
    def _load_excel(self, file_path: str) -> List[Document]:
        df = pd.read_excel(file_path)
        content = df.to_string(index=False)
        return [Document(page_content=content, metadata={"source": file_path})]

    def build_vector_store(self, documents: List[Document]) -> None:
        vectorstore = FAISS.from_documents(documents, self.embeddings)
        vectorstore.save_local(self.db_dir)

    def load_vector_store(self) -> Optional[VectorStore]:
        if not os.path.exists(self.db_dir):
            return None

        try:
            vectorstore = FAISS.load_local(
                self.db_dir,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            return vectorstore
        except Exception as e:
            logger.error(f"벡터스토어 로드 실패: {e}")
            return None

    def add_to_vector_store(self, documents: List[Document]) -> None:
        """벡터스토어에 문서를 추가하고 저장"""
        existing_vs = self.load_vector_store()
        if existing_vs:
            for doc in documents:
                existing_vs.add_documents([doc])
            existing_vs.save_local(self.db_dir)
        else:
            self.build_vector_store(documents)