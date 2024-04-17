import streamlit as st


def main():
    st.text_input(label="", placeholder="Input your ID here...", type="password", key="user_id")

    if st.button("Login"):
        if not st.session_state["user_id"]:
            st.text("Please provide an ID")
        else:
            st.text("You are logged in")


if __name__ == "__main__":
    main()
