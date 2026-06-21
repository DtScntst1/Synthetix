# 🌌 Synthetix

> **Synthetix** is a powerful, node-based Visual AI Pipeline Orchestrator. It allows you to build, wire, and execute complex LLM (Large Language Model) workflows in a completely code-free, drag-and-drop canvas.

![Synthetix Canvas](https://img.shields.io/badge/Status-Live-emerald?style=for-the-badge) ![Tech Stack](https://img.shields.io/badge/Stack-Next.js%20%7C%20FastAPI%20%7C%20React%20Flow-indigo?style=for-the-badge)

## 🚀 Features

- **Infinite Drag & Drop Canvas**: Built with React Flow. Drag AI nodes (LLMs, Inputs, Prompts) onto the canvas.
- **Dynamic LangChain Compiler**: The FastAPI backend parses your visual graph and instantly compiles it into an executable LangChain pipeline.
- **Real-Time Execution**: Watch your data flow from User Input $\rightarrow$ Prompt $\rightarrow$ Llama-3.1 LLM $\rightarrow$ Output Result.
- **Premium Glassmorphism UI**: Beautiful, fully responsive frontend with glowing nodes and animated connecting wires.

## 🛠️ Architecture

Synthetix completely breaks away from the traditional "Chatbot" or "Dashboard" mold. It acts as an **Infrastructure Platform**:

1. **Frontend (Next.js + React Flow)**: Manages the node state and edge connections. When "Run Pipeline" is clicked, it serializes the graph into a JSON payload.
2. **Backend (FastAPI)**: Receives the graph payload via the `/execute` endpoint.
3. **Execution Engine (LangChain + Groq)**: Maps the JSON nodes to LangChain primitives (`ChatPromptTemplate`, `ChatGroq`), chains them together using LCEL (LangChain Expression Language), and executes the pipeline concurrently.

## 📦 Tech Stack

- **Frontend**: Next.js 14, React Flow, TailwindCSS, Framer Motion, Lucide Icons.
- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic.
- **AI / LLM**: LangChain, Groq API (Llama-3.1-8b-Instant).

## 🚦 Getting Started

### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Create a `.env` file in the `backend` folder:
```env
GROQ_API_KEY=your_groq_api_key_here
```
Run the server:
```bash
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Usage
- Open `http://localhost:3000`.
- Drag an **Input**, **Prompt**, **Groq LLM**, and **Output** node onto the canvas.
- Wire them together by dragging from the right dots to the left dots.
- Type your input and click **Run Pipeline**.
- Alternatively, click the **✨ Load Example Template** button for a pre-wired demo!

---
*Built to demonstrate Advanced Agentic Architecture and Visual Node-Based Programming.*
