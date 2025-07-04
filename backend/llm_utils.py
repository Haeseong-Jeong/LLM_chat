import requests

def generate_response(message):
    try:
        system_prompt = "너는 똑똑한 한국어 도우미야. 모든 답변은 가능한 한국어로 해줘."
        full_prompt = f"{system_prompt}\n\n사용자: {message}"

        response = requests.post(
            url="http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": message,
                "stream": False
            }
        )
        data = response.json()
        return data.get("response", "응답 생성 실패")
    except Exception as e:
        return f"Error: {str(e)}"
