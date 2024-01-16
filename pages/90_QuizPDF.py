import streamlit as st
import os, time
from streamlit_extras.switch_page_button import switch_page

def main():
    OPENAI_API_KEY = st.session_state.openai_api_key
    
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
    
    st.title(":red[QuizPDF2]")
    st.write("""
        Upload a multiple page PDF and generate a quiz with multiple options.
        """
    )


if __name__=="__main__":
    if "openai_api_key" not in st.session_state:
        st.error("Need a OPENAI_API_KEY! Go to the Home.", icon="🚨")
        time.sleep(2)
        switch_page('Home')

    main()