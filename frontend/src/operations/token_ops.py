import streamlit as st
import extra_streamlit_components as stx
import time


token_key = "token"
cookies_key = "cookies"


def update_cookies():
    stx.CookieManager(cookies_key)


def get_cookies():
    return st.session_state[cookies_key]


def set_token():
    if token_key not in st.session_state:
        update_cookies()
        cookies = get_cookies()

        print("TRY")

        if not cookies:
            time.sleep(0.2)
            st.switch_page("pages/1_My_books.py")

        if "SESSION_ID" in cookies:
            session_id = cookies["SESSION_ID"]
        else:
            st.switch_page("Home.py")
        if session_id:
            st.session_state[token_key] = session_id
        else:
            st.switch_page("Home.py")