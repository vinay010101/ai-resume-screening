import streamlit as st
import pandas as pd
import sqlite3
import smtplib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------- DB ----------------

def create_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute(
        "CREATE TABLE IF NOT EXISTS data(resume TEXT, score INT, mail TEXT)"
    )

    conn.commit()
    conn.close()


def insert_db(r, s, m):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO data VALUES(?,?,?)",
        (r, s, m),
    )

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute("SELECT * FROM data")

    data = c.fetchall()

    conn.close()

    return data


create_db()


# ---------------- CONFIG ----------------

st.set_page_config(
    page_title="AI Resume Screening",
    layout="wide"
)


# ---------------- LOGIN ----------------

USER = "admin"
PASS = "123"


if "login" not in st.session_state:
    st.session_state.login = False


if not st.session_state.login:

    st.title("AI RESUME SCREENING")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):

        if u == USER and p == PASS:
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

    st.header("Dashboard")

    data = get_db()

    if data:

        df = pd.DataFrame(
            data,
            columns=["Resume", "Score", "Mail"]
        )

        st.dataframe(df)

        st.write("Total:", len(df))
        st.write("Selected:", len(st.session_state.selected))
        st.write("Rejected:", len(st.session_state.rejected))


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

            mail = f.name

            insert_db(
                f.name,
                int(score),
                mail,
            )

            row = {
                "Resume": f.name,
                "Score": int(score),
                "Mail": mail,
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

    st.dataframe(df)

    select_all = st.checkbox("Select All")

    mails = []

    for i, r in df.iterrows():

        if select_all:
            mails.append(r["Mail"])

    if st.button("Send Mail"):

        for m in mails:
            print("send to", m)

        st.success("Mail sent")


# ---------------- SELECTED ----------------

if menu == "Selected":

    show(
        st.session_state.selected,
        st.session_state.get("msg1", ""),
    )


# ---------------- REJECTED ----------------

if menu == "Rejected":

    show(
        st.session_state.rejected,
        st.session_state.get("msg2", ""),
    )