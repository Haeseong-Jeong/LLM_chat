# main.py

import os
import shutil
import json
import re
import traceback  # 추가
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from document_processor import DocumentProcessor
from agent_graph import build_agent_graph

# config.py가 없다면 여기서 직접 정의
try:
    from config import UPLOAD_DIR, VECTOR_DB_DIR
except ImportError:
    # config.py가 없다면 기본값 사용
    UPLOAD_DIR = "./uploads"
    VECTOR_DB_DIR = "./vector_db"

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
async def upload_file(file: List[UploadFile] = File(...), reset_vector: bool = Form(False), reset_folder: bool = Form(False)):
    """
    - 문서 업로드 후 벡터스토어 구축
    - reset=True: 기존 벡터스토어 초기화 후 다시 생성
    """
    try:
        # 벡터 및 폴더 DB 초기화 여부 처리
        if reset_vector and os.path.exists(VECTOR_DB_DIR):
            shutil.rmtree(VECTOR_DB_DIR)
        if reset_folder and os.path.exists(UPLOAD_DIR):
            shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
            os.makedirs(UPLOAD_DIR, exist_ok=True)

        # 파일들 저장
        file_paths = []
        for f in file:
            file_path = os.path.join(UPLOAD_DIR, f.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(f.file, buffer)
            file_paths.append(file_path)

        # 문서 임베딩 수행
        processor = DocumentProcessor(db_dir=VECTOR_DB_DIR)
        all_docs = []
        for path in file_paths:
            docs = processor.load_documents(path)
            all_docs.extend(docs)
        processor.build_vector_store(all_docs)

        return JSONResponse(
            content={"message": f"총 {len(file_paths)}개 파일 벡터스토어 저장 완료."},
            status_code=200,
        )
    except Exception as e:
        print(f"업로드 에러: {e}")
        print(f"업로드 에러 상세: {traceback.format_exc()}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/ask/")
async def ask_question(question: str = Form(...)):
    """
    질문에 대한 답변을 생성
    """
    try:
        print(f"=== 질문 처리 시작 ===")
        print(f"질문: {question}")
        print(f"VECTOR_DB_DIR: {VECTOR_DB_DIR}")
        print(f"UPLOAD_DIR: {UPLOAD_DIR}")
        
        # 벡터 DB가 먼저 구축되어야 질문 가능
        if not os.path.exists(VECTOR_DB_DIR):
            print(f"벡터 DB 경로가 존재하지 않습니다: {VECTOR_DB_DIR}")
            raise HTTPException(status_code=400, detail="벡터 DB가 존재하지 않습니다. 먼저 문서를 업로드해주세요.")

        # 벡터 DB 폴더는 있지만 실제 파일들이 있는지 확인
        vector_files = os.listdir(VECTOR_DB_DIR)
        print(f"벡터 DB 폴더 내용: {vector_files}")
        
        if not vector_files:
            print(f"벡터 DB 폴더가 비어있습니다: {VECTOR_DB_DIR}")
            raise HTTPException(status_code=400, detail="벡터 DB가 비어있습니다. 먼저 문서를 업로드해주세요.")

        print("그래프 빌드 시작...")
        graph = build_agent_graph()
        print("그래프 빌드 완료")
        
        print("그래프 invoke 시작...")
        result = graph.invoke({"question": question})
        print("그래프 invoke 완료")
        print(f"결과 타입: {type(result)}")
        print(f"결과 키들: {result.keys() if isinstance(result, dict) else 'dict가 아님'}")
        
        obs = result.get("observation", "")
        final_answer = result.get("final_answer", "")
        
        print(f"observation 길이: {len(obs)}")
        print(f"final_answer 길이: {len(final_answer)}")
        print(f"observation 시작 부분: {obs[:200]}...")
        print(f"final_answer 시작 부분: {final_answer[:200]}...")

        # Observation에서 JSON이 있으면 추출
        match = re.search(r"\[DATAFRAME_JSON_START](.*?)\[DATAFRAME_JSON_END]", obs, re.DOTALL)
        if match:
            print("JSON 데이터 발견, 파싱 시작...")
            try:
                df_data = json.loads(match.group(1))
                print(f"JSON 파싱 성공, 데이터 길이: {len(df_data)}")
            except json.JSONDecodeError as je:
                print(f"JSON 파싱 실패: {je}")
                df_data = []
        else:
            print("JSON 데이터 없음")
            df_data = []

        print("응답 생성 완료")
        return JSONResponse(content={
            "answer": final_answer,
            "dataframe": df_data
        })
    
    except HTTPException:
        raise  # HTTPException은 그대로 전달
    except Exception as e:
        print(f"=== 질문 처리 에러 ===")
        print(f"에러 메시지: {str(e)}")
        print(f"에러 상세:")
        print(traceback.format_exc())
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/")
async def health_check():
    """
    ✅ 서버 헬스 체크 및 상태 확인용
    """
    return {"status": "ok", "message": "RAG API 서버가 실행 중입니다."}