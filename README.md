# 🎫 Ticket Known Issue Classifier using Sentence Transformers

## 📘 Overview
An AI-powered ticket classification system that automatically maps user-reported issues to predefined known issues using semantic similarity and Sentence Transformers.

The system generates text embeddings from incoming ticket descriptions and compares them against stored known issues using cosine similarity to identify the closest match with high accuracy.

This solution was developed during my internship and is currently deployed within the company’s internal ticketing platform to automate issue categorization, reduce manual effort, and improve ticket resolution efficiency.

---

## 🧠 Key Features

- 🤖 Semantic similarity matching using Sentence Transformers (`all-MiniLM-L6-v2`)
- ⚡ Fast issue classification using cosine similarity
- 🧩 Modular backend architecture with separated routes, services, and utilities
- 💾 Database integration for issue storage and retrieval
- 🚀 Dedicated development and production execution modes
- 📜 Logging system for prediction tracking and monitoring
- 🔍 Scalable NLP-based issue recommendation pipeline

---

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| Language | Python |
| Backend Framework | Flask / FastAPI |
| NLP Model | Sentence Transformers |
| Embedding Model | all-MiniLM-L6-v2 |
| Similarity Method | Cosine Similarity |
| Database | SQLite / MySQL |
| Libraries | Transformers, Sentence-Transformers, NumPy, Pandas, Scikit-learn |
| Deployment | Gunicorn / Uvicorn / Docker |

---

## ⚙️ How It Works

```text
User Ticket → Text Embedding Generation → Semantic Similarity Matching → Known Issue Prediction
