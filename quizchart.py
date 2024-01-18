import streamlit as st
from dotenv import load_dotenv
import pandas as pd

def main():
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
    st.write('Quiz Generating App')


if __name__ == '__main__':
    main()