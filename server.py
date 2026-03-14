import asyncio
import base64
import functools
import io
import os
import re
import wave
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from kokoro_onnx import Kokoro
from openai import AsyncOpenAI

# ── Models ────────────────────────────────────────────────────────────────────
base_path = os.path.dirname(os.path.abspath(__file__))
kokoro = Kokoro(
    os.path.join(base_path, "kokoro-v1.0.onnx"),
    os.path.join(base_path, "voices-v1.0.bin"),
)
client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
tts_executor = ThreadPoolExecutor(max_workers=2)

# ── Prompt ────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are HOODY, a street-smart black mentor from Brooklyn.
Rules:
1. Use heavy AAVE (African American Vernacular English).
2. Use words like 'fam', 'real talk', 'no cap', 'straight up', 'homie'.
3. Drop the 'g' at the end of words (e.g., 'workin', 'talkin').
4. Keep it short, blunt, and rhythmic.
5. Don't be polite, be real. No emojis.
6. Always speak short and to the point, like a true OG mentor.
"""

SENTENCE_END = re.compile(r'[.!?][)\'"]*(\s|$)')

# ── Helpers ───────────────────────────────────────────────────────────────────
def _to_wav(samples: np.ndarray, sample_rate: int) -> bytes:
    s16 = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(s16.tobytes())
    return buf.getvalue()


async def _synthesize(text: str) -> str:
    """Synthesize text → base64-encoded WAV string."""
    loop = asyncio.get_running_loop()
    fn = functools.partial(kokoro.create, text, voice="am_michael", speed=0.95)
    samples, sr = await loop.run_in_executor(tts_executor, fn)
    return base64.b64encode(_to_wav(samples, sr)).decode()


# ── FastAPI ───────────────────────────────────────────────────────────────────
app = FastAPI()


@app.websocket("/ws")
async def ws_chat(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            user_input = await ws.receive_text()
            await _respond(ws, user_input.strip())
    except WebSocketDisconnect:
        pass


async def _respond(ws: WebSocket, user_input: str):
    if not user_input:
        return

    try:
        stream = await client.chat.completions.create(
            model="gemma3",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            stream=True,
        )
    except Exception as exc:
        await ws.send_json({"type": "error", "content": str(exc)})
        await ws.send_json({"type": "done"})
        return

    buffer = ""
    async for chunk in stream:
        delta = (chunk.choices[0].delta.content or "").replace("\n", " ")
        if not delta:
            continue

        await ws.send_json({"type": "text", "content": delta})
        buffer += delta

        # Drain completed sentences
        while m := SENTENCE_END.search(buffer):
            sentence = buffer[: m.end()].strip()
            buffer = buffer[m.end():]
            if sentence:
                audio = await _synthesize(sentence)
                await ws.send_json({"type": "audio", "data": audio})

    # Remaining fragment (no terminal punctuation)
    if buffer.strip():
        audio = await _synthesize(buffer.strip())
        await ws.send_json({"type": "audio", "data": audio})

    await ws.send_json({"type": "done"})


# Static files — must be mounted last
app.mount("/", StaticFiles(directory=os.path.join(base_path, "static"), html=True), name="static")
