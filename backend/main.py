# main.py

import os
import shutil
import json
import re
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from document_processor import DocumentProcessor
from agent_graph import build_agent_graph

from config import UPLOAD_DIR, VECTOR_DB_DIR


app = FastAPI(
    title="RAG 기반 문서 질의응답 API",
    description="문서 업로드 → 임베딩 → 질문/응답까지 수행하는 API입니다.",
    version="1.0.0"
)

# CORS 설정 (프론트엔드와 연동 시 필수)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포 시 도메인 제한 가능
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), reset: bool = Form(False)):
    """
    - 문서 업로드 후 벡터스토어 구축
    - reset=True: 기존 벡터스토어 초기화 후 다시 생성
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 벡터 DB 초기화 여부 처리
        if reset and os.path.exists(VECTOR_DB_DIR):
            shutil.rmtree(VECTOR_DB_DIR)

        # 문서 임베딩 수행
        processor = DocumentProcessor(db_dir=VECTOR_DB_DIR)
        docs = processor.load_documents(file_path)
        processor.build_vector_store(docs)

        return JSONResponse(content={"message": f"벡터스토어 저장 완료 ({file.filename})"}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/ask/")
async def ask_question(question: str = Form(...)):
    """
    질문에 대한 답변을 생성
    """
    try:
        # 벡터 DB가 먼저 구축되어야 질문 가능
        if not os.path.exists(VECTOR_DB_DIR):
            raise HTTPException(status_code=400, detail="벡터 DB가 존재하지 않습니다. 먼저 문서를 업로드해주세요.")

        graph = build_agent_graph()
        result = graph.invoke({"question": question})
        obs = result.get("observation", "")
        final_answer = result.get("final_answer", "")

        # Observation에서 JSON이 있으면 추출
        match = re.search(r"\[DATAFRAME_JSON_START](.*?)\[DATAFRAME_JSON_END]", obs, re.DOTALL)
        if match:
            df_data = json.loads(match.group(1))
        else:
            df_data = []

        return JSONResponse(content={
            "answer": final_answer,
            "dataframe": df_data
        })
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)



@app.get("/")
async def health_check():
    """
    ✅ 서버 헬스 체크 및 상태 확인용
    """
    return {"status": "ok", "message": "RAG API 서버가 실행 중입니다."}
