
# 📄 AI-Powered Research Assistant

An **AI-powered web application** that reads PDF or TXT documents, summarizes them clearly, answers your questions, and even challenges you — all through an easy-to-use web interface with user login & registration.

---

## 🚀 Features

✅ Upload a PDF or TXT file.  
✅ Get a clear, short summary of the document (with sections: *Introduction, Key Points, Conclusion*).  
✅ Ask any question about the document and get an answer.  
✅ Choose **Challenge Me** mode — it asks you 3 questions about the document and checks your answers.  
✅ All answers are based **only on the document** (no made-up content).  
✅ User authentication (Register & Login) with MySQL backend.  

---

## 🛠️ Tech Stack

| Tool / Library            | Purpose                                   |
|----------------------------|-------------------------------------------|
| **Streamlit**             | Web interface                            |
| **LangChain**             | AI agent                    |
| **Anthropic Claude 3.5 Sonnet / LLM** | Understand & process documents |
| **PyPDF2**                | Extract text from PDF files              |
| **Pydantic**              | Validate & structure outputs            |
| **MySQL + bcrypt**        | Store and authenticate users             |
| **dotenv**                | Manage secrets like API keys            |

---

## 📂 Setup & Run

### 1️⃣ Clone the repo

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2️⃣ Install dependencies

You can use the provided `requirements.txt` or manually install:

```bash
pip install -r requirements.txt
```

or manually:

```bash
pip install streamlit langchain anthropic python-dotenv pydantic PyPDF2 mysql-connector-python bcrypt
```

---

### 3️⃣ Set up environment variables

Create a `.env` file in the project folder and add:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
```

---

### 4️⃣ Set up MySQL

Create a database and a table for users:

```sql
CREATE DATABASE research_app;

USE research_app;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);
```

Update your MySQL credentials in the Python code where it connects to the database.

---

### 5️⃣ Run the app

```bash
streamlit run app.py
```

The app will open automatically in your browser.

---

## 🌟 How to use the app?

1️⃣ Open the app in your browser.  
2️⃣ Register or login to access the features.  
3️⃣ Upload your PDF or TXT file.  
4️⃣ Choose a mode:
- **Query** → Ask any question about the document.
- **Just Summarize** → Get a summary of the document.
- **Challenge Me** → Answer 3 questions based on the document.
5️⃣ View results directly on the page.

---

## 🔗 API Endpoints (optional)

If you prefer to interact via API instead of UI, here are some sample endpoints you can implement and test with Postman:

| Endpoint         | Method | Description              |
|------------------|--------|--------------------------|
| `/register`      | POST   | Register a new user      |
| `/login`         | POST   | Login existing user      |
| `/summary`       | POST   | Upload document & get summary / Q&A |

### 📥 Postman Collection

A ready-to-use Postman collection file:  
[`postman_collection.json`](postman_collection.json)  

You can import it in Postman:  
**Postman → Import → Upload JSON file**

---

## 📄 Sample Postman Request

### Register
```http
POST /register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

### Login
```http
POST /login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

### Summary
```http
POST /summary
Content-Type: application/json

{
  "document_text": "Your document text here...",
  "query": "Summarize the document"
}
```

---

## 🧩 Workflow Architecture

Below is the architecture and flow of the application:

```
              ┌────────────────────────────┐
              │         User               │
              │  (Browser, Streamlit UI)  │
              └────────────┬──────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │          Streamlit Frontend         │
        │  (app.py + session state + forms)  │
        └──────────────────┬──────────────────┘
                           │
       ┌───────────────────┼────────────────────┐
       │                   │                    │
       │                   │                    │
 ┌───────────────┐   ┌──────────────┐    ┌──────────────────┐
 │  Login/Regist │   │  File Upload │    │  Mode Selection  │
 │ (username/pwd)│   │ (PDF/TXT)    │    │ (Query/Summary/  │
 │               │   │              │    │  Challenge Me)   │
 └───────────────┘   └──────────────┘    └──────────────────┘
       │                   │                    │
       │                   │                    │
       │                   │                    │
       ▼                   ▼                    ▼

  ┌────────────────────────────────────────────────────────────┐
  │                      Backend Logic                         │
  │  - Validate user with MySQL (login/register)               │
  │  - Extract text from uploaded document using PyPDF2        │
  │  - Build query based on mode & document text               │
  │  - Pass query to LangChain agent with Anthropic Claude LLM │
  │  - Use tools (Search, Wiki, Save) if needed                │
  │  - Parse & structure response using Pydantic               │
  └────────────────────────────────────────────────────────────┘
                           │
                           ▼

                 ┌──────────────────────────────┐
                 │         Response             │
                 │  - Summary / Answer         │
                 │  - Challenge Questions      │
                 │  - Evaluation of answers    │
                 │  - Shown on Streamlit UI    │
                 └──────────────────────────────┘

                           │
                           ▼
              ┌────────────────────────────┐
              │        Optional:           │
              │  API endpoints + Postman   │
              │  (Register, Login, Q&A)    │
              └────────────────────────────┘
```

---

## 🙋‍♀️ Contributions

Feel free to fork and submit PRs.  
If you have suggestions or find issues, please open an Issue or Discussion.

---


