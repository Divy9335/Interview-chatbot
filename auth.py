# D:\Ai interview chatbot\auth.py
import streamlit as st
import sqlite3
import hashlib

# Persistent SQLite connection for the Streamlit process
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
    """
)
conn.commit()

def _hash(p: str) -> str:
    # SHA-256 hex of trimmed password
    return hashlib.sha256((p or "").strip().encode()).hexdigest()

def _norm(u: str) -> str:
    # Trim username for consistent storage/lookup
    return (u or "").strip()

def _login(u: str, p: str) -> bool:
    u = _norm(u)
    p = (p or "").strip()
    # Case-insensitive username match; parameterized query
    cursor.execute(
        "SELECT password FROM users WHERE username = ? COLLATE NOCASE",
        (u,),
    )
    row = cursor.fetchone()
    # fetchone returns a tuple; compare against its first element
    if row and row[0] == _hash(p):
        st.session_state["logged_in"] = True
        st.session_state["username"] = u
        return True
    return False

def _signup(u: str, p: str) -> bool:
    u = _norm(u)
    p = (p or "").strip()
    # Basic validation
    if not u or len(p) < 6:
        return False
    # Enforce unique username case-insensitively
    cursor.execute(
        "SELECT 1 FROM users WHERE username = ? COLLATE NOCASE",
        (u,),
    )
    if cursor.fetchone():
        return False
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (u, _hash(p)),
    )
    conn.commit()
    return True

def show_login_signup() -> bool:
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = ""

    if not st.session_state["logged_in"]:
        st.header("🔐 Please Login or Sign Up")

        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

        with tab_login:
            u = st.text_input("Username", key="login_username")
            p = st.text_input("Password", type="password", key="login_password")
            if st.button("Log In"):
                if u and p:
                    if _login(u, p):
                        st.success(f"Welcome back, {st.session_state['username']}!")
                        st.rerun()  # render logged-in view
                    else:
                        st.error("Invalid username or password.")
                else:
                    st.warning("Please enter both fields")

        with tab_signup:
            su = st.text_input("Choose Username", key="signup_username")
            sp = st.text_input(
                "Choose Password (min 6 chars)",
                type="password",
                key="signup_password",
            )
            if st.button("Create Account"):
                if su and sp and len(sp) >= 6:
                    if _signup(su, sp):
                        st.success("Account created! Please log in.")
                    else:
                        st.error("Username exists or invalid input.")
                else:
                    st.warning("Enter username and password (≥6 chars)")

        return False
    else:
        st.sidebar.success(f"Logged in as {st.session_state['username']}")
        if st.sidebar.button("Log Out"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.rerun()
        return True
