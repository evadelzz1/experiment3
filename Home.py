import openai
import streamlit as st
from dotenv import load_dotenv
import os

def main():
    st.set_page_config(
        page_title = "QuizGPT Apps",
        page_icon = "",
    )

    with st.sidebar:
        # st.info("Select a page above.")
        st.write(
            "<small>**About.**  \n</small>",
            "<small>*blueholelabs*, Jan. 2024  \n</small>",
            unsafe_allow_html=True,
        )
    
    # main page
    st.title("Welcome to the QuizGPT Apps")
    st.divider()

    st.write("**OPENAI_API_KEY Selection**")
    choice_api = st.radio(
        label = "$\\hspace{0.25em}\\texttt{Choice of API}$",
        options = ("Your key", "My key"),
        label_visibility = "collapsed",
        horizontal = True,
    )

    st.session_state.openai = None
    
    authorized = False
    if choice_api == "Your key":
        st.write("**Your API Key**")
        inputOPENAIKEY = st.text_input(
            label = "Enter your OpenAI API Key:",
            type = "password",
            placeholder = "sk-",
            # value="",
            value = "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",
            label_visibility = "collapsed",
        )
        
        if inputOPENAIKEY == "":
            authorized = False
        else:
            st.session_state.openai_api_key = inputOPENAIKEY
            authorized = True

    else:

        if not load_dotenv():
            st.error(
                "Could not load .env file or it is empty. Please check if it exists and is readable.",
                icon="🚨"
            )
            exit(1)

        st.session_state.user_password = os.getenv("USER_PASSWORD")
        
        # st.session_state.openai_api_key = st.secrets["openai_api_key"]
        # user_password = st.secrets["user_PIN"]

        st.write("**Password**")
        inputPassword = st.text_input(
            label = "Enter password", 
            type = "password", 
            label_visibility = "collapsed"
        )
        if (inputPassword == st.session_state.user_password):
            st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY")
            authorized = True        

    # st.session_state.openai = openai.OpenAI(
    #     api_key=st.session_state.openai_api_key
    # )
    
    if authorized == True:
        st.info("Successed Login!", icon="ℹ️")   

if __name__ == "__main__":
    main()
