# OAT-Chatbot

**OAT-Chatbot** is a retrieval-focused AI chatbot built upon approximately four years of blog content authored by the head of Ogawa Acupuncture Therapy.  
It answers user questions by combining vector and keyword search to reference relevant past blog posts and generate accurate, natural-sounding responses in Japanese.

---

## 📚 Features

- **RAG (Retrieval-Augmented Generation)** architecture using OpenAI's embedding model and ChromaDB for semantic search
- **High-precision answers** generated using GPT-4o-mini with top-ranked search results embedded in the prompt (140–170 characters per answer)
- **Hybrid search mechanism** combining vector and keyword search to enhance both precision and coverage
- **Citation display**: Sources retrieved via both search methods are shown alongside the answers
- **Chat history feature**: Stores and displays up to 10 previous messages per session
- **User interface features**: "Show more" option for keyword search results, and a history clear button

---

## 🛠 Technologies Used

- Python
- Flask
- OpenAI API (GPT-4o-mini)
- ChromaDB
- Janome (Japanese morphological analysis)
- HTML + CSS (minimalist web chat UI)

---

## 📂 Project Structure

| File/Folder                | Description                                           |
|---------------------------|-------------------------------------------------------|
| `app.py`                  | Core Flask application: handles routing and chat logic |
| `chatbot_prompt_module.py`| Handles question processing, vector search, keyword search, and prompt generation |
| `templates/index.html`    | Web chat UI for users, including result and history display |
| `chroma_db/`              | 🔒 Not included in this repo: vector database folder |

---

## 🔐 Note: `chroma_db/` is not included

This repository is provided for structural and implementation reference only.  
Actual blog content and vector database (`chroma_db/`) are **not** included, as they contain private information.

To rebuild the chatbot, you will need to prepare your own text dataset and convert it into a ChromaDB-compatible vector database.

---

## 🚀 Setup Instructions (Development)

```bash
pip install flask openai chromadb janome
```

Required environment variables (e.g., `.env`):

- `OPENAI_API_KEY`
- `FLASK_SECRET_KEY` (optional)

---

## 🧩 Challenges

While the RAG architecture is powerful, it requires careful design to ensure stable search accuracy and response quality.  
Through the development of this project, I realized the importance of:

- Designing appropriate chunking strategies for documents  
- Filtering out semantically irrelevant results from vector search

In light of these challenges, I plan to continue improving the system toward building a more flexible and general-purpose RAG chatbot by refining its data structure and retrieval strategy.
