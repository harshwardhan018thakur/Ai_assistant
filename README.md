# 🧠 NexusAI Assistant

A full-featured, production-quality AI Assistant built with **Streamlit** and **Groq API (LLaMA-3 70B)**.

---

## ✨ Features

| Module | Description |
|---|---|
| 🔍 **Question Answering** | Domain-aware Q&A with detail-level control |
| 📄 **Text Summarization** | Multi-style summaries with compression stats |
| ✍️ **Creative Writing** | Stories, poems, emails, scripts, and more |
| 💬 **Feedback System** | Rating collection with AI-generated acknowledgements |
| 📊 **Dashboard** | Live usage analytics, history, and export |

---

## 🚀 Quick Start

### 1. Clone / extract the project
```bash
cd nexusai_assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your API key
```bash
cp .env.example .env
# Edit .env and add your key:
# GROQ_API_KEY=gsk_xxxxxxxxxxxx
```
> Get a **free** Groq API key at [console.groq.com](https://console.groq.com)

### 4. Run
```bash
streamlit run app.py
```
The app opens at `http://localhost:8501`

---

## 📁 Project Structure

```
nexusai_assistant/
├── app.py                  ← Main Streamlit application
├── requirements.txt        ← Python dependencies
├── .env.example            ← API key template
├── README.md               ← This file
└── data/                   ← Auto-created at runtime
    ├── history.json        ← Query history (auto-saved)
    └── feedback.json       ← User feedback (auto-saved)
```

---

## 🏗️ Architecture

```
User Input
    │
    ▼
Streamlit UI  ──→  Mode Router
                       │
          ┌────────────┼───────────────┐
          ▼            ▼               ▼
    Question QA   Summarization   Creative Writing
          │            │               │
          └────────────┴───────────────┘
                       │
                  Groq API (LLaMA-3 70B)
                       │
                  JSON Response
                       │
              ┌────────┴────────┐
              ▼                 ▼
         Display UI        data/*.json
                         (history + feedback)
```

---

## 🔑 Key Technologies

- **Streamlit** — Python-native web UI
- **Groq API** — Ultra-fast LLaMA-3 70B inference
- **python-dotenv** — Secure environment variable management
- **JSON** — Lightweight persistent storage (no DB needed)

---

## 🎨 Design

- Deep navy + electric violet palette (`#0d0f14` + `#6c63ff`)
- Space Grotesk display + Inter body typography
- Responsive layout with sidebar navigation
- Live stat chips (response time, word count, compression ratio)
- Animated button hover effects

---

## 📊 Assignment Requirements Checklist

- [x] Question Answering
- [x] Text Summarization
- [x] Creative Writing
- [x] Feedback Storage (JSON-persisted, with ratings)
- [x] Attractive UI (custom CSS, dark theme, gradient accents)
- [x] Groq API integration
- [x] Modular, well-commented code
- [x] README with setup instructions

---

## 👤 Author

**Harshwardhan Thakur**  
B.Tech CSE — KIIT University  
GitHub: [harshwardhan018thakur](https://github.com/harshhhhhh8168)

---

## 📄 License

MIT — free to use and modify.
