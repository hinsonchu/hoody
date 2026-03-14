import os
import re
import queue
import threading
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

def _split_sentences(text):
    """將文字切成句子，以 . ! ? 為分界"""
    parts = re.split(r'(?<=[.!?,])\s+', text)
    return [s.strip() for s in parts if s.strip()]

def speak(text):
    """讓 HOODY 開口說話 — 分句生成，邊生成邊播放，降低延遲"""
    print(f"🎤 HOODY: {text}")

    text = text.replace("\n", " ").strip()
    sentences = _split_sentences(text)
    if not sentences:
        return

    audio_queue = queue.Queue()

    def generate():
        for sentence in sentences:
            samples, sample_rate = kokoro.create(sentence, voice="am_michael", speed=0.95)
            audio_queue.put((samples, sample_rate))
        audio_queue.put(None)  # 結束哨兵

    def playback():
        while True:
            item = audio_queue.get()
            if item is None:
                break
            samples, sample_rate = item
            sd.play(samples, sample_rate)
            sd.wait()

    gen_thread = threading.Thread(target=generate, daemon=True)
    play_thread = threading.Thread(target=playback, daemon=True)
    gen_thread.start()
    play_thread.start()
    gen_thread.join()
    play_thread.join()

SYSTEM_PROMPT = """
You are HOODY, a street-smart black mentor from Brooklyn.
Rules:
1. Use heavy AAVE (African American Vernacular English).
2. Use words like 'fam', 'real talk', 'no cap', 'straight up', 'homie'.
3. Drop the 'g' at the end of words (e.g., 'workin', 'talkin').
4. Keep it short, blunt, and rhythmic.
5. Don't be polite, be real. No emojis.
6. Always speak short and to the point, like a true OG mentor.
"""

# 句子邊界：.!? 後接空白或字串結尾
SENTENCE_END = re.compile(r'[.!?][)\'"]*(\s|$)')

def chat_and_speak(user_input):
    """串流接收 LLM 回覆，逐句即時生成音頻，大幅降低首字延遲"""
    audio_queue = queue.Queue()

    def playback():
        while True:
            item = audio_queue.get()
            if item is None:
                break
            samples, sample_rate = item
            sd.play(samples, sample_rate)
            sd.wait()

    play_thread = threading.Thread(target=playback, daemon=True)
    play_thread.start()

    try:
        stream = client.chat.completions.create(
            model="gemma3",  # 💡 請確保你執行過 'ollama pull gemma3'
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            stream=True
        )
    except Exception as e:
        audio_queue.put(None)
        play_thread.join()
        speak(f"Yo, my brain just glitched. Error: {e}")
        return

    # 合成執行緒：從 tts_queue 取句子，合成後放進 audio_queue
    tts_queue = queue.Queue()

    def synthesize():
        while True:
            sentence = tts_queue.get()
            if sentence is None:
                break
            samples, sample_rate = kokoro.create(sentence, voice="am_michael", speed=0.95)
            audio_queue.put((samples, sample_rate))
        audio_queue.put(None)  # 通知播放執行緒結束

    tts_thread = threading.Thread(target=synthesize, daemon=True)
    tts_thread.start()

    buffer = ""
    print("🎤 HOODY: ", end="", flush=True)

    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        print(delta, end="", flush=True)
        buffer += delta.replace("\n", " ")

        # 每湊成一個完整句子就立刻入隊合成
        while True:
            match = SENTENCE_END.search(buffer)
            if not match:
                break
            sentence = buffer[:match.end()].strip()
            buffer = buffer[match.end():]
            if sentence:
                tts_queue.put(sentence)

    print()  # 換行

    # 處理剩餘未結尾片段
    if buffer.strip():
        tts_queue.put(buffer.strip())

    tts_queue.put(None)   # 通知合成執行緒結束
    tts_thread.join()
    play_thread.join()

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
            
        # 串流思考 + 邊說邊播
        chat_and_speak(user_text)