import streamlit as st
import os, time
from streamlit_extras.switch_page_button import switch_page
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import StrOutputParser

def create_quiz_prompt_template():
    template = """
You are an expert quiz maker for technical fields. Let's think step by step and
create a quiz with {num_questions} {quiz_type} questions about the following concept/content: {quiz_context}.

The format of the quiz could be one of the following:
- Multiple-choice: 
- Questions:
    <Question1>: <a. Answer 1>, <b. Answer 2>, <c. Answer 3>, <d. Answer 4>
    <Question2>: <a. Answer 1>, <b. Answer 2>, <c. Answer 3>, <d. Answer 4>
    ....
- Answers:
    <Answer1>: <a|b|c|d>
    <Answer2>: <a|b|c|d>
    ....
    Example:
    - Questions:
    - 1. What is the time complexity of a binary search tree?
        a. O(n)
        b. O(log n)
        c. O(n^2)
        d. O(1)
    - Answers:
        1. b
- True-false:
    - Questions:
        <Question1>: <True|False>
        <Question2>: <True|False>
        .....
    - Answers:
        <Answer1>: <True|False>
        <Answer2>: <True|False>
        .....
    Example:
    - Questions:
        - 1. What is a binary search tree?
        - 2. How are binary search trees implemented?
    - Answers:
        - 1. True
        - 2. False
- Open-ended:
- Questions:
    <Question1>: 
    <Question2>:
- Answers:    
    <Answer1>:
    <Answer2>:
Example:
    Questions:
    - 1. What is a binary search tree?
    - 2. How are binary search trees implemented?
    
    - Answers: 
        1. A binary search tree is a data structure that is used to store data in a sorted manner.
        2. Binary search trees are implemented using linked lists.
"""
    prompt = PromptTemplate.from_template(template)
    # prompt.format(
    #     num_questions=3, 
    #     quiz_type="multiple-choice", 
    #     quiz_context="Data Structures in Python Programming"
    # )
    print("-" * 50)
    print(prompt.format)
    return prompt

def create_quiz_chain(prompt_template, llm, openai_api_key):
    return prompt_template | llm |  StrOutputParser()
    # https://rfriend.tistory.com/822

def split_questions_answers(quiz_response):
    # splits the questions and answers from the quiz response
    if "Answers:" in quiz_response:     # num_questions >= 2
        splitString = "Answers:"
    elif "Answer:" in quiz_response:    # num_questions = 1
        splitString = "Answer:"
    else:
        st.error(f"An error occurred: {e}", icon="🚨")
        
    questions = quiz_response.split(splitString)[0]
    answers = quiz_response.split(splitString)[1]
    return questions, answers

def main():
    OPENAI_API_KEY = st.session_state.openai_api_key

    st.set_page_config(
        page_title="QuizText",
        page_icon="🧠",
        layout="centered"
    )

    with st.sidebar:
        st.header("👨‍💻 About the Author")
        st.write("""
        :orange[**Daniel**] is a tech enthusiast and coder. Driven by passion and a love for sharing knowledge, I'm created this platform to make learning more interactive and fun.
        """)
        
    st.title(":red[QuizText] - Context Quiz App")
    st.write("This app generates a quiz based on a given context.")
    
    context = st.text_area(
        "Enter the concept/context for the quiz",
        value = "the Mission: Impossible movie."
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        num_questions = st.number_input(
            "Enter the number of questions", 
            min_value=1, 
            max_value=10, 
            value=3
        )
        
    with col2:
        quiz_type = st.selectbox(
            "Select the quiz type",
            ["multiple-choice","true-false", "open-ended"]
        )

    with col3:
        num_temperature = st.slider(
            label = "Select the Temperature",
            min_value = 0.0,
            max_value = 1.0,
            step = 0.1,
            value = 0.2,    # Temperature Default = 0.7
            format="%.1f",
            label_visibility="visible",
        )

    try:
        if st.button("Generate Quiz"):
            llm = ChatOpenAI(temperature=num_temperature)
            prompt_template = create_quiz_prompt_template()
            chain = create_quiz_chain(prompt_template, llm, OPENAI_API_KEY)
            quiz_response = chain.invoke({"quiz_type":quiz_type, "num_questions":num_questions, "quiz_context":context})

            st.info("Quiz Generated! [num_questions: " + str(num_questions) + ", quiz_type: " + quiz_type + ", temperature:" + str(num_temperature) + "]", icon="ℹ️")       

            print(quiz_response)
            questions, answers = split_questions_answers(quiz_response)
            
            st.session_state.quiztext_answers = answers
            st.session_state.quiztext_questions = questions

            st.write(questions)
        
        if st.button("Show Answers"):
            st.markdown(st.session_state.quiztext_questions)
            st.write("----")
            st.markdown(st.session_state.quiztext_answers)

    except Exception as e:
        st.error(f"An error occurred: {e}", icon="🚨")

if __name__=="__main__":
    if "openai_api_key" not in st.session_state:
        st.error("Need a OPENAI_API_KEY! Go to the Home.", icon="🚨")
        time.sleep(2)
        switch_page('Home')

    main()
