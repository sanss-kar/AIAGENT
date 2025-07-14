# import streamlit as st

# st.write("Hello world")


from langchain.chat_models import ChatOpenAI

# 👇 Replace this with the actual model name from LM Studio
model_name = "llama3"  

# 🪄 Create the LLM client
llm = ChatOpenAI(
    openai_api_key="dummy-key",  # LM Studio ignores the key
    openai_api_base="http://localhost:1234/v1",  # LM Studio endpoint
    model=model_name,
    temperature=0
)

# 🧪 Run a simple query
response = llm.predict("What is AI?")

print("Response:", response)
