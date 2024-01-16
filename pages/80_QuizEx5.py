import streamlit as st
import os, time
from streamlit_extras.switch_page_button import switch_page

from openai import OpenAI
import os

def create_test_prompt(topic, num_questions, num_possible_answers):
    prompt = f"Create a multiple choice quiz on the topic of {topic} consisting of {num_questions} questions. " \
                 + f"Each question should have {num_possible_answers} options. "\
                 + f"Also include the correct answer for each question using the starting string 'Correct Answer: '."
    return prompt

def create_student_view(test, num_questions):
    student_view = {1 : ""}
    question_number = 1
    for line in test.split("\n"):
        if not line.startswith("Correct Answer:"):
            student_view[question_number] += line+"\n"
        else:
            if question_number < num_questions:
                question_number+=1
                student_view[question_number] = ""
    return student_view

def extract_answers(test, num_questions):
    answers = {1 : ""}
    question_number = 1
    for line in test.split("\n"):
        if line.startswith("Correct Answer:"):
            answers[question_number] += line+"\n"

            if question_number < num_questions:
                question_number+=1
                answers[question_number] = ""
    return answers

def take(student_view):
    answers = {}
    for question, question_view in student_view.items():
        print(question_view)
        answer = input("Enter your answer: ")
        answers[question] = answer
    return answers

def grade(correct_answer_dict, answers):
    correct_answers = 0
    for question, answer in answers.items():
        if answer.upper() == correct_answer_dict[question].upper()[16]:
            correct_answers+=1
    grade = 100 * correct_answers / len(answers)

    if grade < 60:
        passed = "Not passed!"
    else:
        passed = "Passed!"
    return f"{correct_answers} out of {len(answers)} correct! You achieved: {grade} % : {passed}"

def main():
    OPENAI_API_KEY = st.session_state.openai_api_key
    client = OpenAI(api_key=OPENAI_API_KEY)

    st.set_page_config(
        page_title="QuizText",
        page_icon="🧠",
        layout="centered"
    )

    with st.sidebar:
        st.header("👨‍💻 About the Author")
        st.write("""
        :orange[**?**] is a tech enthusiast and coder. Driven by passion and a love for sharing knowledge, I'm created this platform to make learning more interactive and fun.
        """)
    
    st.title(":red[Quiz Generator]")
    st.write(":red[See your command windows (iTerm) and solve quiz]")

    st.write('🎃 https://github.com/hdksrma/OpenAI-Quiz-Generator')
    st.write('🎃 https://github.com/Lee-Terrell/Quiz_Generator/tree/main')

    st.divider()
    st.write("1) Prompt :")
    prompt = create_test_prompt("Python", 3, 4)
    st.write(prompt)

    # input_number = st.text_input('number of questions', value=3)
    
    if st.button('Generate Quiz'):
        with st.spinner():
            # quiz_text = gen_Quiz(client, input_number, input_topic)

            response = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=4000
            )
            
            st.write("2) Quiz create :")
            created_answer = response.choices[0].text
            st.write(created_answer)
            
            st.write("3) Disp for Student :")
            st.write(create_student_view(created_answer, 3))
            
            st.write("4) Disp only Answer :")
            st.write(extract_answers(created_answer, 3))
        
            st.write("5) See your command windows (iTerm) and solve quiz.")
            student_answers = take(create_student_view(created_answer, 3))

            st.write("6) Check Score.")             
            st.write(grade(extract_answers(created_answer, 3), student_answers))
            
if __name__=="__main__":
    if "openai_api_key" not in st.session_state:
        st.error("Need a OPENAI_API_KEY! Go to the Home.", icon="🚨")
        time.sleep(2)
        switch_page('Home')

    main()