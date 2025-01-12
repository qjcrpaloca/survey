import streamlit as st
import sqlite3
from datetime import datetime

# Initialize database
conn = sqlite3.connect('survey_app.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS surveys (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, link TEXT, points INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, points INTEGER DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS completions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, survey_id INTEGER, completion_date TEXT)''')
conn.commit()

# Sidebar navigation
st.sidebar.title("Survey App")
page = st.sidebar.selectbox("Navigation", ["Home", "Admin Panel", "User Dashboard"])

if page == "Home":
    st.title("Welcome to the Survey App")
    st.write("Earn points by completing surveys!")

elif page == "Admin Panel":
    st.title("Admin Panel")
    
    # Add a new survey
    st.header("Add a New Survey")
    with st.form("add_survey_form"):
        title = st.text_input("Survey Title")
        link = st.text_input("Survey Link")
        points = st.number_input("Points", min_value=1, step=1)
        submit = st.form_submit_button("Add Survey")
        
        if submit:
            c.execute("INSERT INTO surveys (title, link, points) VALUES (?, ?, ?)", (title, link, points))
            conn.commit()
            st.success("Survey added successfully!")

    # View surveys
    st.header("Existing Surveys")
    surveys = c.execute("SELECT * FROM surveys").fetchall()
    for survey in surveys:
        st.write(f"**{survey[1]}** ({survey[3]} points)")
        st.write(f"[Go to survey]({survey[2]})")
        if st.button(f"Delete {survey[1]}", key=survey[0]):
            c.execute("DELETE FROM surveys WHERE id = ?", (survey[0],))
            conn.commit()
            st.experimental_rerun()

elif page == "User Dashboard":
    st.title("User Dashboard")
    
    # User authentication (simple example)
    st.header("Login or Register")
    username = st.text_input("Username")
    if st.button("Login/Register"):
        user = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not user:
            c.execute("INSERT INTO users (username) VALUES (?)", (username,))
            conn.commit()
            user = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        st.session_state["user_id"] = user[0]
        st.success(f"Welcome, {username}!")

    if "user_id" in st.session_state:
        user_id = st.session_state["user_id"]
        user = c.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        st.write(f"**Username**: {user[1]}")
        st.write(f"**Points**: {user[2]}")

        # List surveys
        st.header("Available Surveys")
        surveys = c.execute("SELECT * FROM surveys").fetchall()
        for survey in surveys:
            st.write(f"**{survey[1]}** ({survey[3]} points)")
            st.write(f"[Go to survey]({survey[2]})")
            if st.button(f"Mark as Completed {survey[1]}", key=f"complete_{survey[0]}"):
                completion = c.execute("SELECT * FROM completions WHERE user_id = ? AND survey_id = ?", (user_id, survey[0])).fetchone()
                if not completion:
                    c.execute("INSERT INTO completions (user_id, survey_id, completion_date) VALUES (?, ?, ?)", (user_id, survey[0], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    c.execute("UPDATE users SET points = points + ? WHERE id = ?", (survey[3], user_id))
                    conn.commit()
                    st.success("Survey marked as completed and points awarded!")
                else:
                    st.warning("You have already completed this survey.")

# Close database connection
conn.close()
