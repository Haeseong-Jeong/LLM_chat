# 📊 문서 기반 Q&A + 시각화 웹 서비스 (LLM + RAG + Chart.js)

이 프로젝트는 PDF/문서 기반 데이터를 업로드하고,  
LLM 기반 자연어 질의 응답 + 표 + 차트 시각화를 동시에 제공하는 인터랙티브 대시보드입니다.

---

## 🧠 작동 방식

1. 사용자가 문서를 업로드하면 Vectorstore로 임베딩
2. 사용자가 질문하면:
   - 관련 문서 context를 검색 (RAG)
   - LLM이 응답 생성
3. 시각화 요청 경우:
   - 📋 표로 출력  
   - 📈 Chart.js로 시각화

---

## ⚙️ 실행 방법

### 1. 저장소 클론

### 2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 프론트엔드 의존성 설치

```bash
cd frontend
npm install
```

---

## 🚀 실행 방법

### 1. Ollama 설치 및 모델 실행

- [Ollama 설치](https://ollama.com/)
- LLaMA3 모델 다운로드 및 실행:

```bash
ollama run llama3
```

> 또는 필요시: `ollama pull llama3`

---

### 2. FastAPI 서버 실행

루트 디렉토리에서:

```bash
uvicorn main:app --reload
```

→ 백엔드 서버가 `http://localhost:8000`에서 실행됩니다.

---

### 3. React 프론트엔드 실행

```bash
cd frontend
npm start
```

→ 프론트 서버가 `http://localhost:3000`에서 실행됩니다.

---

## 📦 주요 기술 스택

- 📚 LangChain + Ollama + LLaMA3 (LLM)
- 🧠 FAISS (Vectorstore)
- 🖼️ React + Chart.js (프론트 시각화)
- 🐍 FastAPI (백엔드 API)

---

## ✅ 기능 요약

- 문서 업로드 + 벡터 저장
- 자연어 질의 응답 (RAG 기반)
- 표 + 차트 자동 시각화

---

## 🗂️ 폴더 구조 예시

```
.
├── main.py             # FastAPI entry
├── tools.py            # LangChain tool 정의
├── agent_graph.py      # Agent + Graph 정의
├── analyzer.py         # 데이터 가공
├── document_processor.py
├── config.py
├── frontend/           # React 프론트엔드
│   ├── App.js
│   └── components/
│       └── ChartBox.jsx
```

---

## 🙋 사용 시 주의

- Ollama가 반드시 켜져 있어야 LLM 응답이 동작합니다.
- 문서를 업로드하지 않으면 질문 시 벡터스토어 오류가 발생할 수 있습니다.

---

