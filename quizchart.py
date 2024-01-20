import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
from langchain_openai import OpenAI
from PyPDF2 import PdfReader
from langchain.prompts import PromptTemplate

def initialize():
    if 'q' not in st.session_state:
        st.session_state.q = []

def quizzer(pdf_text, loq):
    api_key = os.getenv("OPENAI_API_KEY")
    llm = OpenAI(openai_api_key=api_key)
    
    prev_questions = ""
    
    for i in enumerate(loq):
        prev_questions += str(i) + ", "
    
    prompt_template = PromptTemplate.from_template(
        '''{pdf_file}
        Provide a multiple-choice question with only ONE correct answer and the answer from the text above. However, questions 
        MUST DIFFER from these: {prev_questions}. That is, questions shouldn't ask the same thing as those questions. 
        
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
    quiz = prompt_template.format(pdf_file=pdf_text, prev_questions=prev_questions)
    
    return llm(quiz)


def quizzing(pdf_text, loq): # Takes care of a single question
    
    mcq = quizzer(pdf_text, loq)
    quiz = mcq.split('?')
    
    question = quiz[0][10:] + "?"
    
    # Only print out multiple choice portion
    # [:-1] is used to omit 'A', 'B', 'C', 'D' in the end of each string
    mc = quiz[1].split('.')
    
    mco = f'''A. {mc[1][:-1]} \nB.{mc[2][:-1]} \nC.{mc[3][:-1]} \nD.{mc[4][:-1]}'''
    
    # Correct answer
    correct_ans = mc[4][-1] + "." + mc[5]
    
    return question, mco, correct_ans




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
    
    st.header("Quizzer ❔")
    st.write('Quiz Generating App')
    
    noq = st.selectbox(
            "Number of questions for your quiz:",
            key='number_of_questions',
            options=[5, 10, 15, 20, 25, 30]
        )
    
    pdf = st.file_uploader("Upload your PDF", type="pdf")
    cancel_button = st.button('Cancel')

    
    if cancel_button:
        st.stop()
        
    # List Of Questions, List of Multiple Choice Options, List of Correct Answers, List Of Index
    loq, lmco, lca, loi = [], [], [], []
        
    if pdf is not None:
        st.empty()
        pdf_reader = PdfReader(pdf)
        pdf_text = ""                       # Initialize a string to accumulate extracted text
        for page in pdf_reader.pages:       # Loop through each page in the PDF
            pdf_text += page.extract_text()
            
        for i in range(noq):
            question, mco, correct_ans = quizzing(pdf_text, loq)
            i += 1
            loq.append(question)
            lmco.append(mco)
            lca.append(correct_ans)
            loi.append(i)
            
    quizzes = {
        "Question": loq,
        "Multiple Choice Options": lmco,
        "Correct Answer": lca
    }
    
    quizchart = pd.DataFrame(quizzes, index = loi) # loi: list of i + 1
    
    st.dataframe(quizchart)


if __name__ == '__main__':
    main()