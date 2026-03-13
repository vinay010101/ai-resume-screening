import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import database
import mail
import config
import ui


# ---------------- CONFIG ----------------

st.set_page_config(
    layout="wide",
    page_title="AI Resume Screening",
    page_icon="🤖"
)

st.markdown("""
<style>

body {
background-color:#0e1117;
color:white;
}

.stButton>button {
background-color:#00BFFF;
color:white;
border-radius:6px;
}

</style>
""", unsafe_allow_html=True)


database.create()

ui.title()


# ---------------- LOGIN ----------------

if "login" not in st.session_state:
    st.session_state.login = False


if not st.session_state.login:

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):

        if user in config.USERS and pwd == config.USERS[user]:
            st.session_state.login = True
        else:
            st.error("Wrong login")

    st.stop()


# ---------------- MENU ----------------

menu = st.sidebar.radio(
    "Menu",
    ["Home", "Screening", "Selected", "Rejected"]
)


if "selected" not in st.session_state:
    st.session_state.selected = []

if "rejected" not in st.session_state:
    st.session_state.rejected = []


# ---------------- HOME ----------------

if menu == "Home":

    st.subheader("Dashboard")

    data = database.get()

    if data:

        df = pd.DataFrame(
            data,
            columns=["Resume", "Score", "Mail"]
        )

        st.dataframe(df)

        ui.card("Total", len(df))
        ui.card("Selected", len(st.session_state.selected))
        ui.card("Rejected", len(st.session_state.rejected))

        fig = plt.figure()
        plt.hist(df["Score"])
        st.pyplot(fig)

        csv = df.to_csv(index=False)

        st.download_button(
            "Download Excel",
            csv,
            "data.csv"
        )


# ---------------- SCREENING ----------------

if menu == "Screening":

    job = st.text_area("Job Description")

    files = st.file_uploader(
        "Upload resumes",
        accept_multiple_files=True
    )

    cutoff = st.slider(
        "Cutoff",
        0, 100, 50
    )

    msg1 = st.text_area("Mail for selected")
    msg2 = st.text_area("Mail for rejected")

    if st.button("Start Screening"):

        st.session_state.selected = []
        st.session_state.rejected = []

        for f in files:

            text = f.read().decode("latin1")

            vec = TfidfVectorizer()

            tfidf = vec.fit_transform(
                [job, text]
            )

            score = cosine_similarity(
                tfidf[0:1],
                tfidf[1:2]
            )[0][0] * 100

            skills = ["python","sql","java","ai","ml","aws"]

            found = []

            for s in skills:
                if s in text.lower():
                    found.append(s)

            skill_text = ",".join(found)

            mail_id = f.name

            database.insert(
                f.name,
                int(score),
                mail_id
            )

            row = {
                "Resume": f.name,
                "Score": int(score),
                "Mail": mail_id,
                "Skills": skill_text
            }

            if score >= cutoff:
                st.session_state.selected.append(row)
            else:
                st.session_state.rejected.append(row)

        st.session_state.msg1 = msg1
        st.session_state.msg2 = msg2

        st.success("Screening Done")


# ---------------- TABLE ----------------

def show(data, msg):

    if not data:
        st.info("No data")
        return

    df = pd.DataFrame(data)

    df = df.sort_values(
        by="Score",
        ascending=False
    )

    df.insert(
        0,
        "S.No",
        range(1, len(df) + 1)
    )

    st.write(df)

    select_all = st.checkbox("Select All")

    selected = []

    for i, row in df.iterrows():

        if select_all:
            selected.append(row["Mail"])

    if st.button("Send Mail"):

        for m in selected:
            mail.send(m, msg)

        st.success("Mail Sent")


# ---------------- SELECTED ----------------

if menu == "Selected":

    show(
        st.session_state.selected,
        st.session_state.get("msg1", "")
    )


# ---------------- REJECTED ----------------

if menu == "Rejected":

    show(
        st.session_state.rejected,
        st.session_state.get("msg2", "")
    )