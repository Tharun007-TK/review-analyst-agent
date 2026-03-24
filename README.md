# 🏨 Review Insight Agent

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

An AI-powered agentic system that fetches and analyzes Google Maps reviews for hotels and restaurants using **LangChain**, **Groq LLM**, and **SerpApi**.

## ✨ Features

- 🔍 Fetches the latest 10 Google Maps reviews via **SerpApi**
- 🏨 Automatically detects whether the place is a **hotel or restaurant**
- 🤖 Analyzes reviews using a **Groq LLM** (Llama 3 series)
- 📊 Returns a structured JSON report including:
  - Overall, Food, Ambiance, Cleanliness, and Service/Hospitality summaries
  - Pros & Cons lists
  - Calculated average Star Rating
- ✅ Output validated with **Pydantic**
- 🖥️ Clean **Streamlit** UI

## 🗂️ Project Structure

```
├── app.py            # Streamlit UI
├── agent.py          # LangChain agent orchestrator
├── analyzer.py       # LCEL chain for LLM analysis
├── tools.py          # SerpApi fetch_place_reviews tool
├── models.py         # Pydantic ReviewAnalysis model
├── test_agent.py     # Pytest test suite (with mocked SerpApi)
├── requirements.txt
├── .env.example
└── .gitignore
```

## 🚀 Getting Started

### 1. Clone the repo and create a virtual environment

```bash
git clone https://github.com/your-username/review-analyst.git
cd review-analyst
python -m venv venv
venv\Scripts\activate   # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

| Variable | Where to get it |
|---|---|
| `GROQ_API_KEY` | [console.groq.com/keys](https://console.groq.com/keys) |
| `SERPAPI_API_KEY` | [serpapi.com/manage-api-key](https://serpapi.com/manage-api-key) |
| `GROQ_MODEL` | e.g. `llama-3.1-8b-instant` or `llama-3.3-70b-versatile` |

### 4. Run the app

```bash
streamlit run app.py
```

## 🧪 Running Tests

```bash
pytest test_agent.py
```

Tests use mocked SerpApi responses so no API credits are consumed.

## 🛠️ Tech Stack

- [LangChain](https://python.langchain.com/) + [LangChain-Groq](https://github.com/langchain-ai/langchain-groq)
- [Groq](https://groq.com/) — ultra-fast LLM inference (Llama 3 series)
- [SerpApi](https://serpapi.com/) — Google Maps reviews
- [Streamlit](https://streamlit.io/) — UI
- [Pydantic](https://docs.pydantic.dev/) — output validation
