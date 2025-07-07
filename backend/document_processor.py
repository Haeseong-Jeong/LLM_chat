# document_processor.py

import os
import logging
from typing import List
import pandas as pd
from langchain_core.documents import Document
from langchain_community.document_loaders import CSVLoader, PyPDFLoader, TextLoader
from langchain_community.document_loaders.word_document import Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

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

    def load_documents(self, file_path: str) -> List[Document]:
        try:
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.csv':
                return self._load_csv(file_path)
            elif file_extension == '.pdf':
                return self._load_pdf(file_path)
            elif file_extension == '.txt':
                return self._load_text(file_path)
            elif file_extension == '.docx':
                return self._load_docx(file_path)
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
            csv_content = df.to_string(index=False)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp949')
            csv_content = df.to_string(index=False)

        documents = [Document(page_content=csv_content, metadata={"source": file_path})]
        return self.text_splitter.split_documents(documents)

    def _load_pdf(self, file_path: str) -> List[Document]:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return self.text_splitter.split_documents(documents)

    def _load_text(self, file_path: str) -> List[Document]:
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        return self.text_splitter.split_documents(documents)

    def _load_docx(self, file_path: str) -> List[Document]:
        loader = Docx2txtLoader(file_path)
        documents = loader.load()
        return self.text_splitter.split_documents(documents)

    def _load_excel(self, file_path: str) -> List[Document]:
        df = pd.read_excel(file_path)
        content = df.to_string(index=False)
        documents = [Document(page_content=content, metadata={"source": file_path})]
        return self.text_splitter.split_documents(documents)

    def build_vector_store(self, documents: List[Document]) -> None:
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name="intfloat/e5-small-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            vectorstore = FAISS.from_documents(documents, embeddings)
            vectorstore.save_local(self.db_dir)
            logger.info(f"벡터스토어 구축 완료: {len(documents)}개 문서")
        except Exception as e:
            logger.error(f"벡터스토어 구축 오류: {str(e)}")
            raise
