import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai
from PyPDF2 import PdfReader
import mysql.connector
import bcrypt
import os

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sanskar",
    database="aiagent"
)
cursor = conn.cursor()

# User registration
def register_user(username, email, password):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash)
        )
        conn.commit()
        return True
    except mysql.connector.IntegrityError:
        return False
    
# User login
def login_user(username, password):
    cursor.execute(
        "SELECT password_hash FROM users WHERE username=%s", (username,)
    )
    result = cursor.fetchone()
    if result:
        return bcrypt.checkpw(password.encode(), result[0].encode())
    return False

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    choice = st.radio("Choose:", ["Login", "Register"])

    if choice == "Register":
        st.subheader("Register")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Register"):
            if register_user(username, email, password):
                st.success("Registered successfully!")
            else:
                st.error("Username or email already exists.")
    
    else:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome {username}")
            else:
                st.error("Invalid credentials.")
else:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False

# Pydantic model for response
class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

# Extract text from PDF or TXT
def extract_text_from_document(file) -> str:
    text = "" 
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    elif file.name.endswith(".txt"):
        text = file.read().decode("utf-8")
    else:
        st.error("Unsupported file format: Please use PDF or TXT.")
        st.stop()
    if not text.strip():
        st.error("No text found in document.")
        st.stop()
    return text

# Create Gemini agent function
def create_agent():
    client = genai.Client(api_key=GEMINI_API_KEY)

    def run_gemini(prompt):
        response = client.models.generate_content(
            model="gemini-1.5-flash",  # You can use gemini-1.5-pro for better quality
            contents=prompt
        )
        return response.text.strip()
    
    return run_gemini

# ----------------- Streamlit main app ----------------------
if st.session_state.logged_in:
    st.set_page_config(page_title="Research Assistant", layout="wide")
    st.title("Smart Research Assistant (Gemini)")

    upload_file = st.file_uploader("Upload a PDF or TXT document", type=["pdf", "txt"])

    if upload_file:
        document_text = extract_text_from_document(upload_file)

        st.subheader("Document Preview")
        st.text_area("Preview", document_text[:1000], height=200)

        mode = st.radio(
            "Choose a mode:",
            options=["Query", "Just Summarize", "Challenge Me"]
        )

        query = ""
        if mode == "Query":
            query = st.text_input("Enter your question about the document:")

        if st.button("Run"):
            gemini_runner = create_agent()

            if mode == "Challenge Me":
                full_query = f"Document Content:\n{document_text}\n\nChallenge Me: Generate 3 logic/comprehension questions from the document."
            elif mode == "Query" and query:
                full_query = f"Document Content:\n{document_text}\n\nUser Question: {query}"
            else:
                full_query = f"Document Content:\n{document_text}\n\nSummarize the document in ≤150 words. Use sections like Introduction, Key Points, Conclusion if applicable."

            with st.spinner("Running Gemini research agent..."):
                output_text = gemini_runner(full_query)

                st.subheader("Research Result")
                st.write(output_text)

                if mode == "Challenge Me":
                    st.subheader("Please answer the 3 questions above:")
                    answers = []
                    for i in range(1, 4):
                        ans = st.text_input(f"Your answer to Question {i}: ")
                        answers.append(ans)

                    if st.button("Submit Answers"):
                        evaluation_query = (
                            f"Document Content:\n{document_text}\n\n"
                            f"User answered the Challenge Me questions as follows:\n"
                            f"Q1: {answers[0]}\nQ2: {answers[1]}\nQ3: {answers[2]}\n\n"
                            f"Please evaluate each response, justify correctness, and reference the document."
                        )

                        with st.spinner("Evaluating your answers..."):
                            eval_output = gemini_runner(evaluation_query)
                            st.subheader("Evaluation of your Answers")
                            st.write(eval_output)
