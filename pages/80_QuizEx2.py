import streamlit as st
import os, time
from streamlit_extras.switch_page_button import switch_page

from openai import OpenAI
import os

def gen_Quiz(client, nb_questions, subject):

    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=f"Write {nb_questions} question Multiple choice quiz for the subject: {subject}.",
        temperature=0.8,
        max_tokens=4000,
        top_p=0.8,
        best_of=2,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    
    return response.choices[0].text

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
    
    st.markdown('Generate Quiz questionsrelated to a topic - powered by OpenAI using text-davinci-003 Model:sun_with_face:')
    st.write('\n')  # add spacing

    st.subheader('\nWhat is your Quiz is about?\n')

    quiz_text = ""  # initialize columns variables
    col1, space, col2, space, col3 = st.columns([10, 0.5, 5, 0.5, 5])
    with col1:
        input_topic = st.text_input('Tape a topic', value='tesla')
    with col2:
        input_number = st.text_input('number of questions', value=2)
    with col3:
        st.write("\n")
        st.write("\n")
        if st.button('Generate Quiz'):
            with st.spinner():
                quiz_text = gen_Quiz(client, input_number, input_topic)
    if quiz_text != "":
        st.write('\n')  # add spacing
        with st.expander("SECTION - Quiz Questions", expanded=True):
            st.markdown(quiz_text)  #output the results

if __name__=="__main__":
    if "openai_api_key" not in st.session_state:
        st.error("Need a OPENAI_API_KEY! Go to the Home.", icon="🚨")
        time.sleep(2)
        switch_page('Home')

    main()