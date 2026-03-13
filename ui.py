import streamlit as st


def title():

    st.image("logo.png", width=80)

    st.markdown(
        """
        <h1 style='text-align:center;
        color:#00BFFF;
        font-size:38px;
        font-weight:bold;'>
        AI RESUME SCREENING SYSTEM
        </h1>
        """,
        unsafe_allow_html=True
    )


def card(label, value):

    st.markdown(
        f"""
        <div style="
        background:#111;
        padding:10px;
        border-radius:10px;
        text-align:center;
        ">
        <h3>{label}</h3>
        <h2>{value}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )