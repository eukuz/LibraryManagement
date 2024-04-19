import streamlit as st


def auth_page():
    personal_id = st.text_input(label="Personal Id", placeholder="Input your ID here...", type="password", key="user_id", label_visibility="hidden")
    login_button = st.button("Login")

    if login_button:
        if not personal_id:
            st.text("Please provide an ID")
        else:
            # do the id check on the backend
            st.text("You are logged in")
            st.switch_page("pages/1_My_books.py")


auth_page()
