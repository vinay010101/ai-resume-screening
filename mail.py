import yagmail

def send(to, msg):

    sender = "youremail@gmail.com"
    password = "app_password"

    yag = yagmail.SMTP(
        sender,
        password
    )

    yag.send(
        to=to,
        subject="Screening Result",
        contents=msg
    )