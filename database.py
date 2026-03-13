import sqlite3

def create():

    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS history(
        name TEXT,
        score INT,
        mail TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert(name, score, mail):

    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO history VALUES (?,?,?)",
        (name, score, mail)
    )

    conn.commit()
    conn.close()


def get():

    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    c.execute("SELECT * FROM history")

    data = c.fetchall()

    conn.close()

    return data