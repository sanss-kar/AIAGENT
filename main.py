import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool
from PyPDF2 import PdfReader
import mysql.connector
import bcrypt
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="sanskar",
    database="aiagent"
)
cursor = conn.cursor()

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
    
def login_user(username, password):
    cursor.execute(
        "SELECT password_hash FROM users WHERE username=%s", (username,)
    )
    result = cursor.fetchone()
    if result:
        return bcrypt.checkpw(password.encode(), result[0].encode())
    return False

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
                st.success("Registered succesfully!")
            else:
                st.error("Username or email already exists.")
    
    else:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("password")
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
        



class ResearchResponse(BaseModel):  
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

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



def create_agent():
    llm = ChatOpenAI(
        openai_api_key=GROQ_API_KEY,
        openai_api_base="https://api.groq.com/openai/v1",
        model="llama3-70b-8192",
        temperature=0,
    )

    parser = PydanticOutputParser(pydantic_object=ResearchResponse)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are a research assistant that helps summarize and analyze documents.

                If the user provides a query → answer it using ONLY the document content.
                If the user provides no query → summarize the document in ≤150 words.
                The summary should include clear sections if possible: Introduction, Key Points, Conclusion.

                If the user asks for 'Challenge Me', generate 3 logic or comprehension questions from the document,
                wait for user answers, then evaluate each response with justification (refer to document content).

                Wrap the output in this format and provide no other text:\n{format_instructions}
                """,
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{query}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    tools = [search_tool, wiki_tool, save_tool]

    agent = create_tool_calling_agent(
        llm=llm,
        prompt=prompt,
        tools=tools
    )

    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return executor, parser


#-----------------Streamlit began ----------------------
if st.session_state.logged_in:
    st.set_page_config(page_title="Research Assistant", layout="wide")
    st.title("Smart Research Assistant")

    upload_file = st.file_uploader("Upload a pdf or TXT document", type=["pdf", "txt"])

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
            agent_executor, parser = create_agent()

            if mode == "Challenge Me":
                full_query = f"Document Content:\n{document_text}\n\nChallenge Me: Generate 3 logic/comprehension from the doc"
            elif mode == "Query" and query:
                full_query = f"Document Content:\n{document_text}\n\nUser Question: {query}"
            else:
                full_query = f"Document Content:\n{document_text}\n\nSummarize the document in ≤150 words. Use sections like Introduction, Key Points, Conclusion if applicable."

            with st.spinner("Running research agent...."):
                raw_response = agent_executor.invoke({"query": full_query})
                output_text = raw_response.get("output") or raw_response.get("result")

                try:
                    structured_response = parser.parse(output_text)

                    st.subheader("Research Result")
                    st.markdown(f"**Topic:** {structured_response.topic}")
                    st.markdown(f"**Summary:**\n{structured_response.summary}")
                    st.markdown(f"**Sources:** {', '.join(structured_response.sources) if structured_response.sources else 'None'}")

                    if mode == "Challenge Me":
                        st.subheader("Please answer the 3 questions above:")
                        answers = []
                        for i in range(1, 4):
                            ans = st.text_input(f"Your answer to Question {i}: ")
                            answers.append(ans)

                        if st.button("Submit Answers"):
                            evaluation_query = (
                                f"Document Content:\n{document_text}\n\n"
                                f"User answered the Challenge Me questions as follows: \n"
                                f"Q1: {answers[0]}\nQ2: {answers[1]}\nQ3: {answers[2]}\n\n"
                                f"Please evaluate each response, justify correctness, and reference the document."
                            )

                            with st.spinner("Evaluating your answers..."):
                                raw_eval = agent_executor.invoke({"query": evaluation_query})
                                eval_output = raw_eval.get("output") or raw_eval.get("result")

                                st.subheader("Evaluation of your Answers")
                                st.write(eval_output)

                except Exception as e:
                    st.error(f"Error parsing response: {e}")
                    st.write("Raw Response: ", raw_response)
