import os
import sounddevice as sd
from kokoro_onnx import Kokoro
from openai import OpenAI

# 1. 配置路徑與模型
base_path = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_path, "kokoro-v1.0.onnx")
voices_path = os.path.join(base_path, "voices-v1.0.bin")

# 初始化 Kokoro 與 Ollama 客戶端
kokoro = Kokoro(model_path, voices_path)
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

def speak(text):
    """讓 HOODY 開口說話 (優化語氣與節奏)"""
    print(f"🎤 HOODY: {text}")
 
    text = text.replace("\n", " ").strip()
    
    # 使用 0.95 語速：這最能體現 Michael 的磁性與街頭感
    samples, sample_rate = kokoro.create(text, voice="am_michael", speed=0.95)
    
    sd.play(samples, sample_rate)
    sd.wait()

def get_ollama_response(user_input):
    """送去給 Ollama 思考 (使用 Gemma 3 或 Llama 3.1)"""
    try:
        response = client.chat.completions.create(
            model="gemma3", # 💡 請確保你執行過 'ollama pull gemma3'
            messages=[
                {
                    "role": "system", 
                    "content": """
                        You are HOODY, a street-smart black mentor from Brooklyn. 
                        Rules:
                        1. Use heavy AAVE (African American Vernacular English). 
                        2. Use words like 'fam', 'real talk', 'no cap', 'straight up', 'homie'.
                        3. Drop the 'g' at the end of words (e.g., 'workin', 'talkin').
                        4. Keep it short, blunt, and rhythmic. 
                        5. Don't be polite, be real. No emojis.
                        6. Always speak short and to the point, like a true OG mentor.
                    """
                },
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Yo, my brain just glitched. You might need to check if the model name is right, fam. Error: {e}"

# --- 測試對話循環 ---
if __name__ == "__main__":
    print("------------------------------------------")
    print("🔥 HOODY IS ONLINE. (輸入 'quit' 退出)")
    print("------------------------------------------")
    
    # 起手式
    speak("Yo, I'm listening. What's on your mind, homie?")
    
    while True:
        user_text = input("\n👉 You: ")
        if user_text.lower() in ['quit', 'exit', 'bye']:
            speak("Peace out, fam. Keep it real.")
            break
            
        # 1. 想
        reply = get_ollama_response(user_text)
        
        # 2. 說
        speak(reply)