<div align="center">

# ⚡ E.D.I.T.H.
### *Even Dead, I'm The Hero*

**A Production-Grade Agentic Voice Assistant powered by LangChain, LLMs & Autonomous AI Orchestration**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-Agentic_AI-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active_Development-brightgreen?style=for-the-badge)]()

<br/>

> *"Edith isn't just a voice assistant — it's an autonomous AI agent that thinks, plans, and acts."*

<br/>

</div>

---

## 🧠 What is Edith?

**Edith** is a fully agentic, voice-driven AI assistant built from the ground up to explore the frontiers of **LangChain**, **Agentic AI orchestration**, **LLM tool use**, and **real-time speech pipelines**. Inspired by Iron Man's always-on AI companion, Edith doesn't just answer questions — she **reasons through tasks**, **selects and invokes tools autonomously**, and **maintains conversational memory** across sessions.

This project goes well beyond a basic chatbot wrapper. It is a hands-on engineering deep-dive into:

- 🔗 **LangChain Agents & Chains** — building custom agent executors with dynamic tool selection
- 🤖 **Agentic AI Orchestration** — multi-step reasoning loops with ReAct (Reason + Act) paradigm
- 🎤 **Full Voice Pipeline** — real-time Speech-to-Text → LLM Reasoning → Text-to-Speech
- 🧩 **Tool-Augmented LLMs** — custom tools that let the AI interact with the real world
- 🗂️ **Persistent Memory** — conversation history that survives across sessions

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Voice                            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Speech-to-Text (STT) │
                    │        Whisper        │
                    └───────────┬───────────┘
                                │ text input
                    ┌───────────▼───────────┐
                    │    LangChain Agent    │
                    │  (ReAct Orchestrator) │
                    │                       │
                    │  ┌─────────────────┐  │
                    │  │  Prompt + Memory│  │
                    │  └────────┬────────┘  │
                    │           │           │
                    │  ┌────────▼────────┐  │
                    │  │    LLM (Llama)  │  │
                    │  └────────┬────────┘  │
                    │           │           │
                    │  ┌────────▼────────┐  │
                    │  │  Tool Selector  │  │
                    │  └────────┬────────┘  │
                    └───────────┼───────────┘
                                │
          ┌─────────────────────┼───────────────────────┐
          │                     │                       │
  ┌───────▼──────┐   ┌──────────▼──────┐   ┌──────────▼──────┐
  │Terminal Exec.│   │  System Config. │   │  Custom Tools   │
  │    Tool      │   │                 │   │  (Extensible)   │
  └──────────────┘   └─────────────────┘   └─────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Text-to-Speech (TTS) │
                    │    pyttsx3 / gTTS     │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │    Spoken Response    │
                    └───────────────────────┘
```

---

## ✨ Key Features

### 🤖 Agentic AI Core
- Implements the **ReAct (Reasoning + Acting)** agent loop — Edith doesn't just respond, she *thinks step by step* before answering
- Uses **LangChain Agent Executor** to dynamically pick the right tool for the right task
- Supports **multi-step task completion**: e.g., *"Search for the weather in Delhi and convert the temperature to Fahrenheit"* — Edith chains multiple tools autonomously

### 🎙️ Full-Duplex Voice Pipeline
- **Speech-to-Text**: Captures microphone input and transcribes in real-time using Whisper or Google Speech Recognition
- **Text-to-Speech**: Converts LLM responses back to natural-sounding speech using `pyttsx3` / `gTTS`
- Handles ambient noise calibration for robust real-world use

### 🗂️ Persistent Conversational Memory
- Powered by **LangChain's ConversationBufferMemory** (or window/summary memory variants)
- Edith *remembers* what was said earlier in the conversation and maintains context naturally
- Memory is injected into every prompt to ensure coherent multi-turn dialogue

### 🔧 Extensible Tool Ecosystem
Edith ships with a set of built-in tools and is designed to be infinitely extensible:

| Tool | Description |
|------|-------------|
| 🌐 Web Search | Real-time internet search via SerpAPI / DuckDuckGo |
| 🧮 Calculator | Handles complex mathematical queries |
| 🐍 Python REPL | Executes Python code for data tasks on-the-fly |
| 📅 Date & Time | Answers time-aware queries |
| *(Your tool here)* | Easily register any custom tool with LangChain's `@tool` decorator |

### 🔐 Secure & Configurable
- All API keys managed via `.env` + `python-dotenv` — no hardcoded secrets
- Modular configuration: swap models, tools, or memory backends without touching core logic

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Groq Llama 3.3-70b versatile / Llama 3.1-8b instant |
| **Orchestration** | LangChain (Agents, Chains, Tools, Memory) |
| **Speech-to-Text** | OpenAI Whisper / SpeechRecognition |
| **Text-to-Speech** | pyttsx3 / gTTS |
| **Environment** | Python 3.12+, python-dotenv |
| **Vector Store** *(optional)* | Chroma for document memory |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Groq API Key
- A working microphone
- uv Installed

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/aman-yadav-ds/Edith.git
cd Edith

# 2. Activate a virtual environment and Install dependencies
uv sync

# 5. Set up your environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY and other keys
```

### Running Edith

```bash
python main.py
```

Edith will greet you and start listening. Just speak naturally!

---

## 💡 Example Interactions

```
You:   "Edith, what's the weather like in Mumbai today?"
Edith: [Uses Web Search Tool → Fetches live data → Responds via TTS]
       "Currently in Mumbai it's 32 degrees with partly cloudy skies..."

You:   "Now convert that to Fahrenheit."
Edith: [Remembers previous context + Uses Calculator Tool]
       "32 degrees Celsius is equal to 89.6 degrees Fahrenheit."

You:   "Write a Python function to calculate compound interest."
Edith: [Uses Python REPL Tool → Generates and validates code]
       "Here's a function for compound interest: ..."
```

---

## 📚 What I Learned Building This

This project was a deliberate, structured learning journey through modern AI engineering. Here's what it taught me:

**LangChain Internals**
- How **prompt templates** inject memory and context into LLM calls
- The difference between **Chains** (deterministic) vs **Agents** (dynamic, reasoning-based)
- How **tool schemas** work — LangChain passes tool signatures to the LLM so it can decide when and how to invoke them

**Agentic AI Design Patterns**
- The **ReAct loop**: Thought → Action → Observation → Thought → ... → Final Answer
- How to prevent **agent hallucination** by grounding outputs through tool use
- Managing **token budgets** in long multi-turn conversations using memory summarization

**Production Considerations**
- Designing for **graceful degradation** (e.g., fallback when STT fails)
- Keeping secrets out of code with environment variable best practices
- Writing **modular, extensible code** so new tools can be added without refactoring

---

## 🗺️ Roadmap

- [ ] **RAG Integration** — Let Edith answer questions from your own documents using Chroma + LangChain retrievers
- [ ] **Persistent Long-Term Memory** — Store conversation history to a database (SQLite)
- [ ] **Wake Word Detection** — Always-on listening mode triggered by a custom wake phrase
- [ ] **Streaming Responses** — Start speaking before the full response is generated
- [ ] **Multi-Agent System** — Edith delegates specialized sub-tasks to purpose-built sub-agents

---

## 📁 Project Structure

```
Edith/
├── main.py                        # Entry point — boots the assistant & starts the voice loop
│
├── src/                           # Core application modules
│   ├── audio_input.py             # Speech-to-Text pipeline (microphone capture & transcription)
│   ├── audio_output.py            # Text-to-Speech pipeline (synthesizes and speaks responses)
│   ├── llm_engine.py              # LangChain Agent executor — orchestrates reasoning & tool use
│   ├── memory_manager.py          # High-level memory interface (read/write conversation context)
│   ├── memory_store.py            # Persistent memory storage backend
│   └── memory_supervisor.py       # Supervises memory lifecycle (pruning, summarization, retrieval)
│
├── utils/                         # Shared utilities & tools
│   ├── __init__.py
│   ├── helpers.py                 # General-purpose helper functions
│   ├── logger.py                  # Centralized logging setup
│   └── tools/                     # LangChain-registered tools (what Edith can *do*)
│       ├── __init__.py
│       ├── tools.py               # Core tool definitions (search, calculator, etc.)
│       └── os_tools.py            # OS-level tools (file system, system commands)
│
├── config/                        # YAML-based configuration files
│   ├── audio_config.yaml          # STT/TTS engine settings (model, voice, rate)
│   ├── brain_config.yaml          # LLM & agent config (model name, temperature, max tokens)
│   └── memory_config.yaml         # Memory backend config (type, buffer size, persistence)
│
├── pyproject.toml                 # Project metadata & dependency management (uv/pip)
├── uv.lock                        # Locked dependency versions for reproducible installs
└── README.md
```

---

## 🤝 Contributing

Contributions, ideas, and feedback are very welcome! If you want to add a new tool, improve the agent loop, or fix a bug:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/CoolNewTool`)
3. Commit your changes (`git commit -m 'Add CoolNewTool'`)
4. Push to the branch (`git push origin feature/CoolNewTool`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with curiosity, caffeine, and a lot of LangChain docs** ☕

*If this project helped you learn something, drop a ⭐ — it means a lot!*

[![GitHub stars](https://img.shields.io/github/stars/aman-yadav-ds/Edith?style=social)](https://github.com/aman-yadav-ds/Edith)

</div>