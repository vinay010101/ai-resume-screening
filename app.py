import streamlit as st
import pandas as pd
import re
import smtplib
from email.mime.text import MIMEText
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from streamlit_option_menu import option_menu


st.set_page_config(
    page_title="AI Resume Screening",
    layout="wide"
)

# ---------------- SESSION ----------------

if "login" not in st.session_state:
    st.session_state.login = False

if "history" not in st.session_state:
    st.session_state.history = []


# ---------------- LOGIN ----------------

def login():

    st.markdown(
        "<h1 style='text-align:center;color:green;'>AI RESUME SCREENING</h1>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([2, 2, 2])

    with c2:

        st.markdown("### Login")

        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):

            if user == "admin" and pwd == "1234":
                st.session_state.login = True
            else:
                st.error("Wrong login")


if not st.session_state.login:
    login()
    st.stop()


# ---------------- SIDEBAR ----------------

with st.sidebar:

    selected = option_menu(
        "Menu",
        ["Home", "Screening", "About"],
        icons=["house", "robot", "info"],
        default_index=0,
    )


# ---------------- FUNCTIONS ----------------

def read_file(file):

    if file.type == "application/pdf":
        pdf = PdfReader(file)
        text = ""

        for page in pdf.pages:
            text += page.extract_text()

        return text

    else:
        return file.read().decode()


def get_email(text):

    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

    match = re.findall(pattern, text)

    if match:
        return match[0]

    return "Not found"


# ---------------- HOME ----------------

if selected == "Home":

    st.title("Previous History")

    if st.session_state.history:

        for h in st.session_state.history:
            st.write(h)

    else:
        st.write("No history yet")


# ---------------- SCREENING ----------------

if selected == "Screening":

    st.title("Resume Screening")

    keywords = st.text_input(
        "Skills",
        "python, java, sql, ai, aws, cloud, devops"
    )

    keyword_list = [
        k.strip().lower()
        for k in keywords.split(",")
    ]

    col1, col2 = st.columns(2)

    with col1:
        resumes = st.file_uploader(
            "Upload Resumes",
            type=["txt", "pdf"],
            accept_multiple_files=True
        )

    with col2:
        job_file = st.file_uploader(
            "Upload Job Description",
            type=["txt", "pdf"]
        )

    if resumes and job_file:

        job = read_file(job_file)

        scores = []

        for file in resumes:

            resume = read_file(file)

            email = get_email(resume)

            texts = [resume, job]

            vectorizer = TfidfVectorizer()
            tfidf = vectorizer.fit_transform(texts)

            score = cosine_similarity(
                tfidf[0], tfidf[1]
            )[0][0]

            final_score = score * 100

            scores.append(
                {
                    "Resume": file.name,
                    "Email": email,
                    "Score": round(final_score, 2),
                }
            )

        df = pd.DataFrame(scores)

        df = df.sort_values(
            by="Score",
            ascending=False
        )

        st.dataframe(df)

        st.write("----")

        cutoff = st.number_input(
            "Cutoff Score",
            value=50
        )

        selected_df = df[df["Score"] >= cutoff]
        rejected_df = df[df["Score"] < cutoff]

        selected_df = selected_df.sort_values(
            by="Score",
            ascending=False
        )

        rejected_df = rejected_df.sort_values(
            by="Score",
            ascending=False
        )

        selected_df.insert(
            0,
            "S.No",
            range(1, len(selected_df) + 1),
        )

        rejected_df.insert(
            0,
            "S.No",
            range(1, len(rejected_df) + 1),
        )

        st.subheader("Selected Candidates")
        st.dataframe(selected_df)

        st.subheader("Rejected Candidates")
        st.dataframe(rejected_df)

        st.session_state.history.append(
            f"{len(selected_df)} selected / {len(rejected_df)} rejected"
        )

        st.write("----")

        select_mail = st.text_area(
            "Mail for Selected",
            "You are selected for next round"
        )

        reject_mail = st.text_area(
            "Mail for Rejected",
            "Thank you for applying"
        )

        sender_email = st.text_input(
            "Sender Gmail"
        )

        app_password = st.text_input(
            "App Password",
            type="password"
        )

        if st.button("Send Mail"):

            server = smtplib.SMTP(
                "smtp.gmail.com",
                587
            )

            server.starttls()

            server.login(
                sender_email,
                app_password
            )

            for i in selected_df["Email"]:

                msg = MIMEText(select_mail)

                msg["Subject"] = "Interview Update"
                msg["From"] = sender_email
                msg["To"] = i

                server.sendmail(
                    sender_email,
                    i,
                    msg.as_string()
                )

            for i in rejected_df["Email"]:

                msg = MIMEText(reject_mail)

                msg["Subject"] = "Application Update"
                msg["From"] = sender_email
                msg["To"] = i

                server.sendmail(
                    sender_email,
                    i,
                    msg.as_string()
                )

            server.quit()

            st.success("Mails Sent")


# ---------------- ABOUT ----------------

if selected == "About":

    st.title("About")

    st.write(
        "AI Resume Screening System using NLP and Machine Learning"
    )