import React, { useState } from "react";
import axios from "axios";
import ChartBox from "./components/ChartBox"; // 상대 경로에 따라 조정


function App() {
  const [files, setFiles] = useState([]);  // 여러 개 파일
  const [resetVector, setResetVector] = useState(true);
  const [resetFolder, setResetFolder] = useState(true);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);  // { role: "user" | "ai", content: "..." }


  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };


  const handleUpload = async () => {
    if (!files) return alert("파일을 선택해주세요");

    const formData = new FormData();
    //formData.append("file", file);
    files.forEach((f) => formData.append("file", f));
    formData.append("reset_vector", resetVector);
    formData.append("reset_folder", resetFolder);  // ✅ 추가

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
      const aiResponse = res.data.answer || res.data.summary;

      // 기존 대화 메시지에 사용자 질문과 응답 추가
      setMessages(prev => [
        ...prev,
        { role: "user", content: question },
        {
          role: "ai",
          content: aiResponse,
          dataframe: res.data.dataframe || []  // 추가된 테이블 데이터
        }
      ]);

    // 질문창 초기화
    setQuestion("");

    } catch (err) {
      console.error(err);
      alert("질문 실패: 먼저 문서를 업로드했는지 확인해주세요.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {/* 왼쪽 사이드바 */}
      <div
        style={{
          width: 250,
          padding: 20,
          borderRight: "1px solid #ddd",
          background: "#fafafa",
          fontSize: "14px",
        }}
      >
        <h3>📄 문서 업로드</h3>

        {/* 파일 선택 + 체크박스들 수평 정렬 */}
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              type="file"
              multiple
              onChange={handleFileChange}
              style={{ flex: 1 }}
            />
          </div>

          {/* 체크박스 라인 */}
          <div style={{ display: "flex", gap: 6 }}>
            <label style={{ fontSize: "12px" }}>
              <input
                type="checkbox"
                checked={resetVector}
                onChange={() => setResetVector(!resetVector)}
              />{" "}
              벡터스토어 초기화
            </label>
            <label style={{ fontSize: "12px" }}>
              <input
                type="checkbox"
                checked={resetFolder}
                onChange={() => setResetFolder(!resetFolder)}
              />{" "}
              문서폴더 초기화
            </label>
          </div>
        </div>

        {/* ✅ 파일 목록을 별도 박스로 */}
        <div
          style={{
            marginTop: 12,
            padding: "10px",
            background: "#f3f3f3",
            border: "1px solid #ccc",
            borderRadius: "4px",
            fontSize: "12px",
            lineHeight: "1.5",
            minHeight: "80px",
          }}
        >
          {files.length === 0 && <i>선택된 파일 없음</i>}
          {files.slice(0, 10).map((f, idx) => (
            <div key={idx}>• {f.name}</div>
          ))}
          {files.length > 10 && (
            <div style={{ fontStyle: "italic" }}>
              + 외 {files.length - 10}개 파일...
            </div>
          )}
        </div>

        {/* ✅ 업로드 버튼을 아래로 이동 */}
        <div style={{ marginTop: 12 }}>
          <button onClick={handleUpload} disabled={loading} style={{ width: "100%" }}>
            {loading ? "업로드 중..." : "업로드"}
          </button>
        </div>
      </div>


      {/* 오른쪽 대화 영역 */}
      <div style={{ flex: 1, maxWidth: 900, margin: "0 auto", padding: "40px 20px 150px 20px", fontFamily: "sans-serif" }}>
        {/* 대화 메시지 출력 영역 */}
        <div style={{ marginBottom: "120px" }}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                textAlign: msg.role === "user" ? "right" : "left",
                margin: "10px 0",
                background: msg.role === "user" ? "#d9fdd3" : "#f1f0f0",
                padding: 10,
                borderRadius: 8
              }}
            >
              <div>{msg.content}</div>
              {msg.role === "ai" && msg.dataframe && msg.dataframe.length > 0 && (
                <div style={{ marginTop: 10 }}>
                  {/* ✅ 표: 전치해서 출력 */}
                  <table
                    border="1"
                    cellPadding="8"
                    cellSpacing="0"
                    style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}
                  >
                    <thead>
                      <tr>
                        <th>항목</th>
                        {msg.dataframe.map((row, idx) => (
                          <th key={idx}>{row["Date"]}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {["입고량", "출고량", "입출고차이"].map((metric) => (
                        <tr key={metric}>
                          <td>{metric}</td>
                          {msg.dataframe.map((row, idx) => (
                            <td key={idx}>{row[metric]}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>

                  {/*  아래에 그래프 추가 */}
                  <ChartBox data={msg.dataframe} />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    
      {/* 입력창 하단 고정 */}
      {/* 질문 영역 + 입력창 */}
      <div style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        width: "100%",
        background: "#fff",
        padding: "10px 0",
        boxShadow: "0 -2px 6px rgba(0,0,0,0.1)"
      }}>
      <div style={{ maxWidth: 600, margin: "0 auto", display: "flex", alignItems: "center", gap: 10, padding: "0 20px" }}>
        
        {/* 왼쪽 타이틀 */}
        <span style={{ whiteSpace: "nowrap", fontWeight: "bold", fontSize: "16px" }}>
          ❓ 질문하기
        </span>
            
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              style={{ flex: 1, padding: 8 }}
              placeholder="메시지를 입력하세요..."
            />
            <button onClick={handleAsk} disabled={loading} style={{ padding: "8px 16px" }}>
              {loading ? "..." : "전송"}
            </button>
          </div>
        </div>



    </div>
  );
}

export default App;