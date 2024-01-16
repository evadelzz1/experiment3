import streamlit as st
import os, time
from streamlit_extras.switch_page_button import switch_page

from openai import OpenAI
import os

def initialize_session_state():
    if 'quiz' not in st.session_state:
        st.session_state.quiz = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'player_score' not in st.session_state:
        st.session_state.player_score = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'quiz_finished' not in st.session_state:
        st.session_state.quiz_finished = False

def generate_quiz(client, topic, num_questions):
    quiz = []
    for _ in range(num_questions):
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Create a multiple choice question about {topic} with four options and indicate the correct answer.",
            max_tokens=150
        )
        content = response.choices[0].text.strip().split('\n')
        if len(content) >= 6:
            question = content[0]
            options = content[1:5]
            correct_answer = content[-1].split(': ')[-1].strip()
            quiz.append({'question': question, 'options': options, 'correct_answer': correct_answer})
    return quiz

def display_question(question_idx):
    question = st.session_state.quiz[question_idx]
    st.write(question["question"])
    option_indices = {option: idx for idx, option in enumerate(question['options'])}
    selected_option = st.radio("Select your answer:", question['options'], key=f"question_{question_idx}")
    return option_indices[selected_option]

def main():
    OPENAI_API_KEY = st.session_state.openai_api_key
    client = OpenAI(api_key=OPENAI_API_KEY)

    st.set_page_config(
        page_title="QuizPDF2",
        page_icon="🧠",
        layout="centered"
    )

    with st.sidebar:
        st.header("👨‍💻 About the Author")
        st.write("""
        :orange[**?**] is a tech enthusiast and coder. Driven by passion and a love for sharing knowledge, I'm created this platform to make learning more interactive and fun.
        """)
    
    st.title(":red[Dynamic Quiz Generator]")
    st.write("""
        This application is a dynamic quiz generator using OpenAI's GPT-3 model to create questions and answers on specified topics. 
        Users can select a topic, the number of questions, and then take the quiz.
        The application records responses and calculates scores.
        """
    )
    st.write('🎃 https://github.com/Gaurang3355/AI-quiz-generator')
    
    initialize_session_state()

    topic = st.text_input("Enter the topic for your quiz:", value = "tesla")
    num_questions = st.number_input("How many questions do you want?", min_value=1, max_value=10, value=2)

    if st.button('Generate Quiz'):
        if topic and num_questions > 0:
            st.session_state.quiz = generate_quiz(client, topic, num_questions)
            st.session_state.current_question = 0
            st.session_state.player_score = 0
            st.session_state.user_answers = [None] * num_questions
            st.session_state.quiz_finished = False
        else:
            st.error("Please enter a topic for your quiz and the number of questions.")

    if st.session_state.quiz and not st.session_state.quiz_finished:
        selected_option_index = display_question(st.session_state.current_question)
        if st.button("Save and Next"):
            st.session_state.user_answers[st.session_state.current_question] = selected_option_index
            if st.session_state.quiz[st.session_state.current_question]['options'][selected_option_index] == st.session_state.quiz[st.session_state.current_question]['correct_answer']:
                st.session_state.player_score += 1
            if st.session_state.current_question < len(st.session_state.quiz) - 1:
                st.session_state.current_question += 1
            else:
                st.session_state.quiz_finished = True

    if st.session_state.quiz_finished:
        st.write("Quiz Finished!")
        st.write(f"Your Score: {st.session_state.player_score}/{len(st.session_state.quiz)}")
        for i, question in enumerate(st.session_state.quiz):
            user_answer_index = st.session_state.user_answers[i]
            user_answer = question['options'][user_answer_index]
            correct_answer = question['correct_answer']
            answer_status = "Correct" if user_answer == correct_answer else "Incorrect"
            st.write(f"Q{i+1}: {question['question']}")
            st.write(f"Your answer: {user_answer} - {answer_status}")
            st.write(f"Correct answer: {correct_answer}")
            st.write("")

if __name__=="__main__":
    if "openai_api_key" not in st.session_state:
        st.error("Need a OPENAI_API_KEY! Go to the Home.", icon="🚨")
        time.sleep(2)
        switch_page('Home')

    main()