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



def moveon(question, choices, info):
    question.empty()
    choices.empty()
    info.empty()
    

def quizzing(num, noq, pdf_text, time_limit):
    api_key = os.getenv("OPENAI_API_KEY")
    llm = OpenAI(openai_api_key=api_key)
    
    prompt_template = PromptTemplate.from_template(
        '''Provide a multiple-choice question with only ONE correct answer and the answer from this text: 
        {pdf_file}
        
        Follow this template:
            (Question)
            A. (multiple choice)
            B. (multiple choice)
            C. (multiple choice)
            D. (multiple choice)
            (Correct Answer)
        
        Example: 
            What run should you take to warm up on Blackcomb Mountain?
            A. Easy Out
            B. Countdown
            C. Big Easy
            D. Magic Castle
            C. Big Easy
        
        '''
    )
    quiz = prompt_template.format(noq=noq, pdf_file=pdf_text)
    generated = llm(quiz)
    
    # Only print out question portion
    question = generated.split('?')
    st.subheader('Question ' + str(num + 1))
    st.write (question[0] + '?')
    
    # Only print out multiple choice portion
    # [:-1] is used to omit 'A', 'B', 'C', 'D' in the end of each string
    mc = question[1].split('.')
    
    mc_choice = st.radio(
        "multiple choice",
        label_visibility="collapsed",
        options=(mc[1][:-1], mc[2][:-1], mc[3][:-1], mc[4][:-1]),
        index=None
    )
    
    # Correct answer
    correct_ans = mc[5]

    if mc_choice is not None:
        if correct_ans == mc_choice:
            st.markdown(f"You selected **{mc_choice}**")
            st.write("Correct 🟢")
            question.empty()
        else: 
            st.markdown(f"You selected **{mc_choice}**")
            st.write(f"Incorrect 🔴 \nCorrect answer is {correct_ans}. ")
            
    else:
        time.sleep(time_limit)
        st.write("You didn't answer in time!")
        st.write(f"Out of time! 🔴 \nCorrect answer is {correct_ans}. ")
    


def main():
    placeholder = st.empty()
    
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
        
    if pdf is not None:
        st.empty()
        pdf_reader = PdfReader(pdf)
        pdf_text = ""                       # Initialize a string to accumulate extracted text
        for page in pdf_reader.pages:       # Loop through each page in the PDF
            pdf_text += page.extract_text() 

            
        for i in range(noq):
            quizzing(i, noq, pdf_text, time_limit)
            i += 1
            
            # if mc_choice is not None:
            #     if correct_ans == mc_choice:
            #         st.markdown(f"You selected **{mc_choice}**")
            #         st.write("Correct 🟢")
            #     else: 
            #         st.markdown(f"You selected **{mc_choice}**")
            #         st.write(f"Incorrect 🔴 \nCorrect answer is {correct_ans}. ")
                    
            # else:
            #     time.sleep(time_limit)
            #     st.write("You didn't answer in time!")
            #     st.write(f"Out of time! 🔴 \nCorrect answer is {correct_ans}. ")
            




if __name__ == '__main__':
    main()