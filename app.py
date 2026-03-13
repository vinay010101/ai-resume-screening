import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- CONFIG ----------------

st.set_page_config(
    page_title="AI Resume Screening",
    page_icon="🤖",
    layout="wide"
)

# ---------------- STYLE ----------------

st.markdown("""
<style>

.big-title {
text-align:center;
font-size:40px;
font-weight:bold;
color:#00BFFF;
}

.login-box {
background-color:#111;
padding:20px;
border-radius:10px;
}

</style>
""", unsafe_allow_html=True)


# ---------------- TITLE ----------------

st.markdown(
'<div class="big-title">AI RESUME SCREENING SYSTEM</div>',
unsafe_allow_html=True
)


# ---------------- LOGIN ----------------

if "login" not in st.session_state:
    st.session_state.login = False

def login():

    col1,col2,col3 = st.columns([2,2,2])

    with col2:

        st.subheader("Login")

        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):

            if user=="admin" and pwd=="admin":
                st.session_state.login=True
            else:
                st.error("Wrong")

if not st.session_state.login:
    login()
    st.stop()


# ---------------- SIDEBAR ----------------

menu = st.sidebar.radio(
"Menu",
["Home","Screening","Selected","Rejected"]
)


# ---------------- STORAGE ----------------

if "data" not in st.session_state:
    st.session_state.data=[]

if "selected" not in st.session_state:
    st.session_state.selected=[]

if "rejected" not in st.session_state:
    st.session_state.rejected=[]


# ---------------- HOME ----------------

if menu=="Home":

    st.subheader("History")

    if st.session_state.data:
        df=pd.DataFrame(st.session_state.data)
        st.dataframe(df,use_container_width=True)
    else:
        st.info("No data")


# ---------------- SCREENING ----------------

if menu=="Screening":

    st.subheader("Upload resumes")

    job=st.text_area("Job description")

    files=st.file_uploader(
        "Upload",
        accept_multiple_files=True
    )

    limit=st.slider(
        "Cutoff",
        0,100,50
    )

    msg1=st.text_area("Selected mail")
    msg2=st.text_area("Rejected mail")


    if st.button("Start"):

        st.session_state.selected=[]
        st.session_state.rejected=[]

        for f in files:

            text=f.read().decode("latin1")

            vec=TfidfVectorizer()

            tfidf=vec.fit_transform(
                [job,text]
            )

            score=cosine_similarity(
                tfidf[0:1],
                tfidf[1:2]
            )[0][0]*100

            mail=f.name

            row={
                "Resume":f.name,
                "Score":int(score),
                "Mail":mail
            }

            st.session_state.data.append(row)

            if score>=limit:
                st.session_state.selected.append(row)
            else:
                st.session_state.rejected.append(row)

        st.success("Done")


# ---------------- MAIL ----------------

def send_mail(to,msg):

    sender="youremail@gmail.com"
    password="app_password"

    m=MIMEText(msg)

    m["Subject"]="Result"
    m["From"]=sender
    m["To"]=to

    s=smtplib.SMTP("smtp.gmail.com",587)
    s.starttls()
    s.login(sender,password)

    s.sendmail(sender,to,m.as_string())
    s.quit()


# ---------------- TABLE ----------------

def show(data,msg):

    if not data:
        st.info("No data")
        return

    df=pd.DataFrame(data)

    df=df.sort_values(
        by="Score",
        ascending=False
    )

    df.insert(
        0,
        "S.No",
        range(1,len(df)+1)
    )

    mails=df["Mail"].tolist()

    select=st.multiselect(
        "Select",
        mails
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    c1,c2=st.columns(2)

    with c1:
        if st.button("Send Mail"):
            for m in select:
                send_mail(m,msg)
            st.success("Sent")

    with c2:
        if st.button("Send Mail All"):
            for m in mails:
                send_mail(m,msg)
            st.success("Sent all")


# ---------------- SELECTED ----------------

if menu=="Selected":

    st.subheader("Selected")

    msg=st.text_area("Mail")

    show(
        st.session_state.selected,
        msg
    )


# ---------------- REJECTED ----------------

if menu=="Rejected":

    st.subheader("Rejected")

    msg=st.text_area("Mail")

    show(
        st.session_state.rejected,
        msg
    )