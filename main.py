import streamlit as st
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import PyPDFLoader
from PyPDF2 import PdfReader
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
import time



def initialize():
    if 'loq' not in st.session_state:
        st.session_state.loq = []
    
    
def quizzer(pdf_text):
    api_key = os.getenv("OPENAI_API_KEY")
    llm = OpenAI(openai_api_key=api_key)
    
    prompt_template = PromptTemplate.from_template(
        '''Provide a multiple-choice question with only ONE correct answer and the answer from this text: 
        {pdf_file}
        
        Follow this template:
            Question: (Question)
            A. (multiple choice)
            B. (multiple choice)
            C. (multiple choice)
            D. (multiple choice)
            (Correct Answer)
        
        Example: 
            Question: What run should you take to warm up on Blackcomb Mountain?
            A. Easy Out
            B. Countdown
            C. Big Easy
            D. Magic Castle
            C. Big Easy
        
        '''
    )
    quiz = prompt_template.format(pdf_file=pdf_text)
    
    return llm(quiz)


def quizzing(i, noq, pdf_text, time_limit):
    
    global corrects
    
    # list of questions
    for k in range(noq):
        st.session_state.loq.append(quizzer(pdf_text))
    
    # Only print out question portion
    question = st.session_state.loq[i].split('?')
    
    st.subheader('Question ' + str(i + 1))
        
    st.write (question[0][10:] + '?')
    
    # Only print out multiple choice portion
    # [:-1] is used to omit 'A', 'B', 'C', 'D' in the end of each string
    mc = question[1].split('.')

    
    mc_choice = st.radio(
        "multiple choice",
        label_visibility="collapsed",
        options=(mc[1][:-1], mc[2][:-1], mc[3][:-1], mc[4][:-1]),
        index=None, 
    )
    
    # Correct answer
    correct_ans = mc[5]
    

    if mc_choice is not None:
        if str(correct_ans).strip() == str(mc_choice).strip():
            st.info(f"Correct 🟢 You selected '{mc_choice}'")
            corrects += 1
        else: 
            st.info(f"You selected '{mc_choice}'")
            st.error(f"Incorrect 🔴 Correct answer is '{correct_ans}'. ")
            
    else: 
        progress_bar = st.progress(0, text="Time is passing ...")
        for t in range(time_limit):
            time.sleep(1)
            progress_bar.progress(100//time_limit * t, text="Time is passing ...")

        progress_bar.empty()
        st.error(f"Out of time! 🔴 Correct answer is '{correct_ans}'. ")


def main():
    initialize()
    
    # load api_key
    if not load_dotenv():
        st.info("Could not load .env file or it is empty. Please check if it exists and is readable.")
        exit(1)
    
    # page style
    st.set_page_config(
        page_title="Quizzer❔",
        page_icon="❔" 
    )
    
    st.header('Quizzer❔')
    
    col1, col2 = st.columns(2)
    
    with col1:
        noq = st.selectbox(
            "Number of questions for your quiz:",
            key='number_of_questions',
            options=[5, 10, 15, 20, 25, 30]
        )
    with col2:
        time_limit = st.selectbox(
            "Time limit (in seconds) for each question",
            key='time_limit',
            options=[15, 30, 45, 60, 75, 90, 105, 120]
        )
    
    pdf = st.file_uploader("Upload your PDF", type="pdf")
    cancel_button = st.button('Cancel')
    
    
    if cancel_button:
        st.stop()
        
    global corrects
    corrects = 0
        
    if pdf is not None:
        st.empty()
        pdf_reader = PdfReader(pdf)
        pdf_text = ""                       # Initialize a string to accumulate extracted text
        for page in pdf_reader.pages:       # Loop through each page in the PDF
            pdf_text += page.extract_text()
        
        j = 0

        while j < noq:
            quizzing(j, noq, pdf_text, time_limit)
            j += 1
                
        st.subheader(f"Quiz Finsihed! Your score is {str(corrects)} / {noq}. ")




if __name__ == '__main__':
    main()