import React, { useState } from "react";
import axios from "axios";

function App() {
  const [file, setFile] = useState(null);
  const [reset, setReset] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return alert("파일을 선택해주세요");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("reset", reset);

    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/upload/", formData);
      alert(res.data.message);
    } catch (err) {
      console.error(err);
      alert("업로드 실패");
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async () => {
    if (!question) return alert("질문을 입력해주세요");

    const formData = new FormData();
    formData.append("question", question);

    setLoading(true);
    try {
      const res = await axios.post("http://localhost:8000/ask/", formData);
      setAnswer(res.data.answer);
    } catch (err) {
      console.error(err);
      alert("질문 실패: 먼저 문서를 업로드했는지 확인해주세요.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "50px auto", padding: 20, fontFamily: "sans-serif" }}>
      <h2>📄 문서 업로드</h2>
      <input type="file" onChange={handleFileChange} />
      <label>
        <input
          type="checkbox"
          checked={reset}
          onChange={() => setReset(!reset)}
        />{" "}
        기존 벡터스토어 초기화
      </label>
      <br />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "업로드 중..." : "업로드"}
      </button>

      <hr />

      <h2>❓ 질문하기</h2>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        style={{ width: "100%", marginBottom: 10 }}
        placeholder="예: 이 문서 요약해줘"
      />
      <button onClick={handleAsk} disabled={loading}>
        {loading ? "답변 중..." : "질문"}
      </button>

      {answer && (
        <div style={{ marginTop: 20, background: "#f7f7f7", padding: 10 }}>
          <h3>🧠 답변</h3>
          <pre>{answer}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
