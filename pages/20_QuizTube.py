import streamlit as st
import os, time
from streamlit_extras.switch_page_button import switch_page
from helpers.youtube_utils import extract_video_id_from_url, get_transcript_text
from helpers.openai_utils import get_quiz_data
from helpers.quiz_utils import string_to_list, get_randomized_options
from helpers.toast_messages import get_random_toast

def main():
    OPENAI_API_KEY = st.session_state.openai_api_key
    
    st.set_page_config(
        page_title="QuizTube",
        page_icon="🧠",
        layout="centered"
    )

    # Check if user is new or returning using session state.
    # If user is new, show the toast message.
    # if 'first_time' not in st.session_state:
    #     message, icon = get_random_toast()
    #     st.toast(message, icon=icon)
    #     st.session_state.first_time = False

    with st.sidebar:
        st.header("👨‍💻 About the Author")
        st.write("""
        :orange[**Haena**] is a tech enthusiast and coder. Driven by passion and a love for sharing knowledge, I'm created this platform to make learning more interactive and fun.
        """)

    st.title(":red[QuizTube]")
    st.write("""
        Ever watched a YouTube video and wondered how well you understood its content?
        Here's a fun twist: Instead of just watching on YouTube,
        come to **QuizTube** and test your comprehension!
        """
    )

    with st.form("user_input"):
        YOUTUBE_URL = st.text_input(
            "Enter the YouTube video link: (under 10min)",
            value="https://www.youtube.com/watch?v=bcYwiwsDfGE"
        )
        submitted = st.form_submit_button("Generate Quiz")

    if submitted or ('quiz_data_list' in st.session_state):
        if not YOUTUBE_URL:
            st.warning("Please provide a valid YouTube video link.", icon="⚠️")
            st.stop()
        elif not OPENAI_API_KEY:
            st.error("Need a OPENAI_API_KEY!", icon="🚨")
            st.stop()
            
        with st.spinner("Generating your quiz...🤓"):
            if submitted:
                video_id = extract_video_id_from_url(YOUTUBE_URL)
                video_transcription = get_transcript_text(video_id)
                quiz_data_str = get_quiz_data(video_transcription, OPENAI_API_KEY)
                st.session_state.quiz_data_list = string_to_list(quiz_data_str)

                if 'quiztube_user_answers' not in st.session_state:
                    st.session_state.quiztube_user_answers = [None for _ in st.session_state.quiz_data_list]
                if 'quiztube_correct_answers' not in st.session_state:
                    st.session_state.quiztube_correct_answers = []
                if 'quiztube_randomized_options' not in st.session_state:
                    st.session_state.quiztube_randomized_options = []

                for q in st.session_state.quiz_data_list:
                    options, correct_answer = get_randomized_options(q[1:])
                    st.session_state.quiztube_randomized_options.append(options)
                    st.session_state.quiztube_correct_answers.append(correct_answer)

            with st.form(key='quiz_form'):
                st.subheader("🧠 Quiz Time: Test Your Knowledge!", anchor=False)
                for i, q in enumerate(st.session_state.quiz_data_list):
                    options = st.session_state.quiztube_randomized_options[i]
                    default_index = st.session_state.quiztube_user_answers[i] if st.session_state.quiztube_user_answers[i] is not None else 0
                    response = st.radio(q[0], options, index=default_index)
                    user_choice_index = options.index(response)
                    st.session_state.quiztube_user_answers[i] = user_choice_index  # Update the stored answer right after fetching it

                results_submitted = st.form_submit_button(label='Check My Score!')

                if results_submitted:
                    score = sum([ua == st.session_state.quiztube_randomized_options[i].index(ca) for i, (ua, ca) in enumerate(zip(st.session_state.quiztube_user_answers, st.session_state.quiztube_correct_answers))])
                    st.success(f"Your score: {score}/{len(st.session_state.quiz_data_list)}")

                    if score == len(st.session_state.quiz_data_list):  # Check if all answers are correct
                        st.balloons()
                    else:
                        incorrect_count = len(st.session_state.quiz_data_list) - score
                        if incorrect_count == 1:
                            st.warning(f"Almost perfect! You got 1 question wrong. Let's review it:", icon="⚠️")
                        else:
                            st.warning(f"Almost there! You got {incorrect_count} questions wrong. Let's review them:", icon="⚠️")

                    for i, (ua, ca, q, ro) in enumerate(zip(st.session_state.quiztube_user_answers, st.session_state.quiztube_correct_answers, st.session_state.quiz_data_list, st.session_state.quiztube_randomized_options)):
                        with st.expander(f"Question {i + 1}", expanded=False):
                            if ro[ua] != ca:
                                st.info(f"Question: {q[0]}", icon="ℹ️")
                                st.error(f"Your answer: {ro[ua]}", icon="🚨")
                                st.success(f"Correct answer: {ca}")

if __name__=="__main__":
    if "openai_api_key" not in st.session_state:
        st.error("Need a OPENAI_API_KEY! Go to the Home.", icon="🚨")
        time.sleep(2)
        switch_page('Home')

    main()