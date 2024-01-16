import streamlit as st
import os, time
from streamlit_extras.switch_page_button import switch_page
from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain.prompts import PromptTemplate
from langchain_community.callbacks import get_openai_callback
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.chains.summarize import load_summarize_chain

import traceback
import json
import pandas as pd
from helpers.quizpdf_utils import parse_file, get_table_data, RESPONSE_JSON

def main():
    OPENAI_API_KEY = st.session_state.openai_api_key

    st.set_page_config(
        page_title="QuizPDF",
        page_icon="🧠",
        layout="centered"
    )
    
    with st.sidebar:
        st.header("👨‍💻 About the Author")
        st.write("""
        :orange[**Mathilda**] is a tech enthusiast and coder. Driven by passion and a love for sharing knowledge, I'm created this platform to make learning more interactive and fun.
        """)
        st.info(OPENAI_API_KEY)

    st.title(":red[QuizPDF]")
    st.write("""
        Upload a multiple page PDF and generate a quiz with multiple options.
        """
    )
    
    # This is an LLMChain to create 10-20 multiple choice questions from a given piece of text.
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
    # llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0, max_tokens=-1)
    template = """
        Text: {text}
        You are an expert MCQ maker. Given the above text, it is your job to\
        create a quiz of {number} multiple choice questions for grade {grade} students in {tone} tone.
        Make sure that questions are not repeated and check all the questions to be conforming to the text as well.
        Make sure to format your response like the RESPONSE_JSON below and use it as a guide.\
        Ensure to make the {number} MCQs.
        Ensure to summarize so that there are no more than 50000 tokens.
        
        ### RESPONSE_JSON
        {response_json}
    """
    
    quiz_generation_prompt = ChatPromptTemplate.from_template(template)
    # quiz_generation_prompt = PromptTemplate(
    #     input_variables=["text", "number", "grade", "tone", "response_json"],
    #     template=template,
    # )
    
    quiz_chain = LLMChain(
        llm=llm, prompt=quiz_generation_prompt, output_key="quiz", verbose=True
    )

    # https://medium.com/@johnidouglasmarangon/how-to-summarize-text-with-openai-and-langchain-e038fc922af
    
    # This is an LLMChain to evaluate the multiple choice questions created by the above chain
    # llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0)
    # llm = ChatOpenAI(model_name="gpt-4-1106-preview")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)
    template = """
        You are an expert english grammarian and writer. Given a multiple choice quiz for {grade} grade students.\
        You need to evaluate complexity of the questions and give a complete analysis of the quiz if the students 
        will be able to understand the questions and answer them. Only use at max 50 words for complexity analysis.
        If quiz is not at par with the cognitive and analytical abilities of the students,\
        update the quiz questions which need to be changed and change the tone such that it perfectly fits the students abilities. 
        Quiz MCQs:
        {quiz}
        Critique from an expert english writer of the above quiz:
    """

    quiz_evaluation_prompt = ChatPromptTemplate.from_template(template)
    # quiz_evaluation_prompt = PromptTemplate(
    #     input_variables=["grade", "quiz"], 
    #     template=template,
    # )
    
    review_chain = LLMChain(
        llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True
    )

    # This is the overall chain where we run these two chains in sequence.
    generate_evaluate_chain = SequentialChain(
        chains=[quiz_chain, review_chain],
        input_variables=["text", "number", "grade", "tone", "response_json"],
        # Here we return multiple variables
        output_variables=["quiz", "review"],
        verbose=True,
    )

    # Create a form using st.form
    with st.form("user_inputs"):
        # File upload
        uploaded_file = st.file_uploader("Upload a pdf or text file", type=["pdf", "txt"])

        # Input fields
        col1, col2 = st.columns(2)
        with col1:
            mcq_count = st.number_input("No of MCQs", min_value=2, max_value=5)
        with col2:
            grade = st.number_input("Insert Grade", min_value=1, max_value=5)
        tone = st.text_input("Insert Quiz tone", value="simple", max_chars=50, placeholder="simple")
        submitted = st.form_submit_button("Generate Quiz")

    # Check if the submitted button is clicked and all fields have inputs
    if submitted and mcq_count and grade and tone:
        if uploaded_file is None:
            st.warning("Please upload a file.", icon="⚠️")
            st.stop()

        with st.spinner("Loading...🤓"):
            try:
                text = parse_file(uploaded_file)

                # count tokens and cost of api call
                with get_openai_callback() as cb:
                    response = generate_evaluate_chain(
                        {
                            "text": text,
                            "number": mcq_count,
                            "grade": grade,
                            "tone": tone,
                            "response_json": json.dumps(RESPONSE_JSON),
                        }
                    )
                print(2)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error", icon="🚨")
            else:
                print(f"Total Tokens: {cb.total_tokens}")
                print(f"Prompt Tokens: {cb.prompt_tokens}")
                print(f"Completion Tokens: {cb.completion_tokens}")
                print(f"Total Cost (USD): ${cb.total_cost}")

                if isinstance(response, dict):
                    # Extract quiz data from the response
                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.table(df)
                            # Display the review in a text box
                            st.text_area(label="Review", value=response["review"])
                        else:
                            st.error("Error in table data", icon="🚨")
                else:
                    st.write(response)

if __name__=="__main__":
    if "openai_api_key" not in st.session_state:
        st.error("Need a OPENAI_API_KEY! Go to the Home.", icon="🚨")
        time.sleep(2)
        switch_page('Home')

    main()