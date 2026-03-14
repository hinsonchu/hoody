
# 🕶️ HOODY - The Street-Smart AI Mentor

Check demo: https://github.com/hinsonchu/hoody/raw/refs/heads/main/Hoody%20Demo.mp4

## 📖 Introduction / 簡介

**HOODY** is a localized AI assistant with a soul. Inspired by the raw energy of Brooklyn, HOODY doesn't just answer questions—he gives it to you straight. Combining the power of **Ollama (Gemma 3)** for brains and **Kokoro-82M** for a gritty, authentic AAVE (African American Vernacular English) voice, HOODY is your street-smart mentor living right on your Mac.

**HOODY** 是一個有靈魂的本地化 AI 助手。深受布魯克林街頭文化啟發，HOODY 不僅僅是回答問題，他會直白地告訴你真相。透過 **Ollama (Gemma 3)** 作為大腦，並結合 **Kokoro-82M** 打造道地的 AAVE（非裔美國人英語）語音，HOODY 就是住在你 Mac 裡的街頭導師。

---

## 🛠️ Features / 功能特點

* **Authentic Voice / 地道嗓音**: Uses Kokoro-82M `am_michael` with custom prosody to deliver a rhythmic, black-accented voice.
* **Street-Smart Brain / 街頭大腦**: Custom System Prompt to ensure responses are blunt, rhythmic, and full of Brooklyn slang.
* **Private & Local / 隱私與本地化**: Everything runs locally on your machine using Ollama and ONNX Runtime.
* **STT Ready / 語音輸入就緒**: Designed to work seamlessly with Whisper (Handy) for hands-free interaction.

---

## 🚀 Installation / 安裝步驟

### 1. Prerequisites / 前置需求

* **Mac** (M1/M2/M3 recommended)
* **Ollama** (Running with `gemma3` or `llama3.1`)
* **Python 3.10+**

### 2. Environment Setup / 環境設定

```zsh
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install kokoro-onnx onnxruntime sounddevice soundfile openai
brew install portaudio

```

### 3. Model Files / 模型檔案

Ensure the following files are in the root directory:
確保資料夾內包含以下檔案：

* `kokoro-v1.0.onnx`
* `voices-v1.0.bin`

---

## 🎮 Usage / 使用方法

```zsh
python3 hoody_chat.py

```

Type your message and listen to HOODY's real-talk response.
輸入訊息，聽聽 HOODY 的「大實話」回覆。

---

## 📜 License / 授權協議

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**.

**本專案採用 CC BY-NC-SA 4.0 授權：**

* **Attribution (姓名標示)**: You must give appropriate credit. / 必須標示原作者。
* **NonCommercial (非商業性)**: You may NOT use this for commercial purposes. / 不得用於商業用途。
* **ShareAlike (相同方式分享)**: Modified works must use the same license. / 衍生作品必須採用相同授權。

---

## 🤝 Acknowledgments / 鳴謝

* **Kokoro-82M** for the amazing TTS engine.
* **Ollama** for the local LLM power.
