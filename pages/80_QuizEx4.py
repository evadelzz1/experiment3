import streamlit as st
import os, time, json, base64, requests, re
from streamlit_extras.switch_page_button import switch_page

from cgitb import text
from io import BytesIO
from tempfile import NamedTemporaryFile

from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_community.document_loaders import CSVLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models.openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA

class LLMChainConfig:
  def __init__(self):
    self._load_embeddings()
    self._load_llm()
  
  def _load_embeddings(self):
    self._embedding = OpenAIEmbeddings()
  
  def _load_llm(self):
    self._llm = ChatOpenAI(temperature=0.6, verbose=True)
  
  def run(self, uploaded_file, label = "PdfDataChunk", n_questions=1):
    if uploaded_file is None:
        return None

    file_bytes = BytesIO(uploaded_file.read())
    
    # Create a temporary file within the "files/" directory
    with NamedTemporaryFile(dir="files/", delete=False) as file:
        filepath = file.name
        file.write(file_bytes.read())
    
    # Determine the loader based on the file extension.
    if uploaded_file.name.lower().endswith(".pdf"):
        loader = PyPDFLoader(filepath)
    elif uploaded_file.name.lower().endswith(".txt"):
        loader = TextLoader(filepath)
    elif uploaded_file.name.lower().endswith(".docx"):
        loader = Docx2txtLoader(filepath)
    elif uploaded_file.name.lower().endswith(".csv"):
        loader = CSVLoader(filepath)
    elif uploaded_file.name.lower().endswith(".html"):
        loader = UnstructuredHTMLLoader(filepath)
    elif uploaded_file.name.lower().endswith(".pptx"):
        loader = UnstructuredPowerPointLoader(filepath)
    else:
        st.error("Please load a file", icon="🚨")
        if os.path.exists(filepath):
            os.remove(filepath)
        return None

    # Load the document using the selected loader.
    document = loader.load()

    try:
        with st.spinner("Vector store in preparation..."):
            # Split the loaded text into smaller chunks for processing.
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=50,
                separators=["\n", "\n\n", "(?<=\. )", "", " "],
                length_function=len
            )
            chunks = text_splitter.split_documents(document)
            
            # Create a FAISS vector database.
            embeddings = OpenAIEmbeddings(
                openai_api_key=st.session_state.openai_api_key
            )
            
            vector_store = FAISS.from_documents(chunks, embeddings)
    except Exception as e:
        vector_store = None
        st.error(f"An error occurred: {e}", icon="🚨")
    finally:
        # Ensure the temporary file is deleted after processing
        if os.path.exists(filepath):
            os.remove(filepath)

    vector_store = FAISS.from_documents(chunks, embedding=self._embedding)
    
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=False)

    qa = RetrievalQA.from_chain_type(llm=self._llm, retriever=vector_store.as_retriever(), memory=memory)

    st.divider()
    st.write("[Running] QA")
    result = qa({
        "query": f"""
            You are a assistant to a teacher. Using the context
            create questions, and provide the teacher with questions and the answers in JSON format.
            Make unique questions and answers using the context and also make sure that the answers are either one word or one line.
            Also make sure that you are using the whole context and not partially using the context.
            sMake {n_questions} number of unique questions.
          """
      })
    
    st.write(json.loads(result["result"])["questions"])
    return json.loads(result["result"])["questions"]
  
def main():
    OPENAI_API_KEY = st.session_state.openai_api_key

    st.set_page_config(
        page_title="QuizMe",
        page_icon="🧠",
        layout="centered"
    )

    with st.sidebar:
        st.header("👨‍💻 About the Author")
        st.write("""
        :orange[**?**] is a tech enthusiast and coder. Driven by passion and a love for sharing knowledge, I'm created this platform to make learning more interactive and fun.
        """)
    
    st.title(":red[QuizMe]")
    
    st.write('🎃 https://github.com/subhroacharjee/quizme-cli/tree/main/lib')

    uploaded_file = st.file_uploader("Upload a pdf or text file", type=["pdf", "txt"])

    if uploaded_file:
        llmconfig = LLMChainConfig()
        llmconfig.run(uploaded_file)

if __name__=="__main__":
    if "openai_api_key" not in st.session_state:
        st.error("Need a OPENAI_API_KEY! Go to the Home.", icon="🚨")
        time.sleep(2)
        switch_page('Home')

    main()