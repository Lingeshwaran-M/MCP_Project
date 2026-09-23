# 🚀 MCP Project  
AI + MCP + MySQL CRUD System

---

## 📌 Overview

MCP Project is an AI-powered database assistant that allows users to perform CRUD operations using natural language.

The system converts user prompts into structured tool calls using an LLM and executes them through an MCP server connected to MySQL.

---

## 🧠 How It Works

1. User enters a message in Streamlit UI  
2. Message is sent to Ollama (LLM)  
3. LLM generates a tool call  
4. MCP server executes the tool  
5. MySQL performs the operation  
6. Result is returned to the UI  

**Flow:**  
User → LLM → MCP Server → Database → Response

---

## 🛠 Features

- Natural language database interaction  
- Create, Read, Update, Delete operations  
- Secure parameterized queries  
- Connection pooling  
- Clean architecture separation (UI / Server / DB)

---

## ▶️ How To Run

### 1️⃣ Start MCP Server

```
python db_mcp_server.py --sse
```

### 2️⃣ Start Streamlit App (New Terminal)

```
streamlit run chat.py
```

---

## 📂 Project Structure

```
chat.py              → Streamlit UI  
db_mcp_server.py     → MCP Server  
db_tools.py          → Database logic  
```

---

## 👨‍💻 Author

Lingeshwaran-M  
https://github.com/Lingeshwaran-M
