import streamlit as st


def auth_page():
    st.markdown("""
    <form action="https://sqr.webrtc-thesis.ru/api/yndx-oauth/authenticate">
        <input type="submit" value="Login with Yandex" />
    </form>
    """, unsafe_allow_html=True)


auth_page()
