# 🎫 Ticket Known Issue Classifier using Sentence Transformers

## 📘 Overview
This project is an **AI-powered ticket classification system** that automatically maps **user-entered issues** to a set of **predefined known issues**.  
It leverages **Sentence Transformers** to generate text embeddings and calculates **semantic similarity** to find the closest matching issue.

Developed with a modular architecture for scalability and maintainability, the project can easily integrate into real-world ticketing systems or IT support tools.

---

## 🧠 Key Features
- 🤖 **Semantic similarity matching** using Sentence Transformers (e.g., `all-MiniLM-L6-v2`).
- ⚡ **Fast classification** using cosine similarity between embeddings.
- 🧩 **Modular architecture** — routes, services, and utilities neatly separated.
- 💾 Integrated with a database service for issue storage and retrieval.
- 🚀 **Production and development modes** supported (`run_dev.py`, `run_prod.py`).
- 📜 Logging system for tracking predictions and performance.

---

## 🧑‍💻 Tech Stack
| Category | Tools / Frameworks |
|-----------|--------------------|
| Language | Python |
| Framework | Flask / FastAPI |
| NLP | Sentence Transformers (Hugging Face) |
| Database | SQLite / MySQL (via `database.py`) |
| Libraries | Transformers, Sentence-Transformers, NumPy, Pandas, Scikit-learn |
| Deployment | Gunicorn / Uvicorn / Docker (optional) |

---

## 📂 Project Structure
app/
├── routes/ # API endpoints and views
│ ├── init.py
│ ├── api.py # Core API routes
│ └── views.py # UI or frontend endpoints (if any)
│
├── services/ # Business logic and model services
│ ├── database.py # Database connection and queries
│ └── similarity_service.py # Core NLP logic using Sentence Transformers
│
├── utils/ # Helper utilities
│ └── init.py
│
├── data/ # Dataset or CSV files (known issues, etc.)
│
├── logs/ # Log files for activity tracking
│
├── requirements.txt # Dependencies
├── run_dev.py # Development server runner
└── run_prod.py # Production server runner
