import streamlit as st


def title():

    st.markdown(
        """
        <h1 style='text-align:center;
        color:#00BFFF;
        font-size:40px;
        font-weight:bold;'>
        AI RESUME SCREENING SYSTEM
        </h1>
        """,
        unsafe_allow_html=True
    )


def card(text):

    st.markdown(
        f"""
        <div style="
        background-color:#111;
        padding:10px;
        border-radius:10px;
        margin:5px;
        ">
        {text}
        </div>
        """,
        unsafe_allow_html=True
    )