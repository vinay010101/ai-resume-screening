import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import database
import mail
import config
import ui


database.create()

st.set_page_config(layout="wide")

ui.title()


# ---------------- LOGIN ----------------

if "login" not in st.session_state:
    st.session_state.login = False


if not st.session_state.login:

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):

        if user == config.USER and pwd == config.PASS:
            st.session_state.login = True
        else:
            st.error("Wrong")

    st.stop()


# ---------------- MENU ----------------

menu = st.sidebar.radio(
    "Menu",
    ["Home", "Screening", "Selected", "Rejected"]
)


if "data" not in st.session_state:
    st.session_state.data = []

if "selected" not in st.session_state:
    st.session_state.selected = []

if "rejected" not in st.session_state:
    st.session_state.rejected = []


# ---------------- HOME ----------------

if menu == "Home":

    st.subheader("History")

    data = database.get()

    if data:

        df = pd.DataFrame(
            data,
            columns=["Resume", "Score", "Mail"]
        )

        st.dataframe(df)


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

    if st.button("Start"):

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

            mail_id = f.name

            database.insert(
                f.name,
                int(score),
                mail_id
            )

            row = {
                "Resume": f.name,
                "Score": int(score),
                "Mail": mail_id
            }

            if score >= cutoff:
                st.session_state.selected.append(row)
            else:
                st.session_state.rejected.append(row)

        st.session_state.msg1 = msg1
        st.session_state.msg2 = msg2

        st.success("Done")


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

    select_all = st.checkbox("Select All")

    selected = []

    for i, row in df.iterrows():

        c1, c2, c3, c4, c5 = st.columns(
            [1, 3, 1, 3, 1]
        )

        with c1:
            if select_all:
                tick = True
            else:
                tick = False

            check = st.checkbox(
                "",
                key=i,
                value=tick
            )

        with c2:
            st.write(row["Resume"])

        with c3:
            st.write(row["Score"])

        with c4:
            st.write(row["Mail"])

        if check:
            selected.append(row["Mail"])

    if st.button("Send Mail"):

        for m in selected:
            mail.send(m, msg)

        st.success("Sent")


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