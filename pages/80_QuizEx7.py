import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import os, time

from openai import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain import PromptTemplate

def create_the_quiz_prompt_template():
    """Create the prompt template for the quiz app."""
    
    template = """
You are an expert quiz maker for technical fields. Let's think step by step and
create an MCQ quiz with {num_questions} questions about the following concept/content: {quiz_context}.

The format of the quiz is the following:
- Multiple-choice: 
- Questions:
    <Question1>: 
    <a. Answer 1>, 
    <b. Answer 2>, 
    <c. Answer 3>,
     <d. Answer 4>
    <Question2>: 
    <a. Answer 1>, 
    <b. Answer 2>, 
    <c. Answer 3>, 
    <d. Answer 4>
    ....
- Answers:
    <Answer1>: <a|b|c|d>
    <Answer2>: <a|b|c|d>
    ....
    Example:
    - Questions:
    What does the SQL acronym "DDL" stand for?

    a. Data Definition Language

    b. Data Description Language

    c. Data Design Language

    d. Database Design Language
    - Answers: 
        1. a
"""
    prompt = PromptTemplate.from_template(template)
    prompt.format(num_questions=3, quiz_context="Data Structures in Python Programming")
    
    return prompt

def quiz_gen_with_chain(client, prompt_question):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful research and programming assistant"},
            {"role": "user", "content": prompt_question},
        ]
    )

    return response.choices[0].message.content

def main():
    OPENAI_API_KEY = st.session_state.openai_api_key
    client = OpenAI(api_key=OPENAI_API_KEY)

    st.set_page_config(
        page_title="Quiz App",
        page_icon="🧠",
        layout="centered"
    )

    with st.sidebar:
        st.header("👨‍💻 About the Author")
        st.write("""
        :orange[**?**] is a tech enthusiast and coder. Driven by passion and a love for sharing knowledge, I'm created this platform to make learning more interactive and fun.
        """)
    
    st.title(":red[Quiz App]")
    st.write("This app generates a quiz based on a given context.")
    
    prompt_template = create_the_quiz_prompt_template()
    context = st.text_area("Enter the concept/context for the quiz", "telsa")
    if st.button("Generate Quiz"):
        quiz_response = quiz_gen_with_chain(client, context)
        st.write("Quiz Generated!")        
        st.write(quiz_response)
    if st.button("Show Answers"):
        st.write("-Scroll to above mentioned answers for self evalutaion-")
        

if __name__=="__main__":
    if "openai_api_key" not in st.session_state:
        st.error("Need a OPENAI_API_KEY! Go to the Home.", icon="🚨")
        time.sleep(2)
        switch_page('Home')

    main()