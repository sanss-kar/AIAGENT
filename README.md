An AI-powered web application that reads PDF or TXT documents, summarizes them clearly, answers your questions, and even challenges you with questions — all through an easy-to-use web interface.


# What does it do?

1. Upload a PDF or TXT file.

2. Get a clear, short summary of the document (with sections: Introduction, Key Points, Conclusion).

3. Ask any question about the document and get an answer.

4. Choose Challenge Me mode — it asks you 3 questions about the document and checks your answers.

5. All answers are based only on the document (no made-up content).



# What is it built with?

1. Streamlit → for the web interface.

2. LangChain → for managing the AI agent and tools.

3. Anthropic Claude 3.5 Sonnet → the AI model that reads and understands your document.

4. PyPDF2 → to read text from PDF files.

5. Pydantic → to make sure the output is structured and correct.



# How to run it?

1. Install the required libraries or You can also looks requirements.txt for required libraries:
   
   * pip install streamlit langchain anthropic python-dotenv pydantic PyPDF2

2.  Add your Anthropic API key:

    * Create a file named .env in the project folder.
    * Add this line to it:

   ----- ANTHROPIC_API_KEY=your_api_key_here -----

3.  Run the app:
    * streamlit run app.py



# How to use the app?

* Open the app in your browser (it will open automatically).
* Upload your PDF or TXT file.
* Choose a mode:
  -> Query → ask any question.
  -> Just Summarize → get a summary of the document.
  -> Challenge Me → answer 3 questions asked by the assistant.
* See your results directly on the page.