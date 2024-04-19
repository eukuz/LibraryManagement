import streamlit as st

from model.book import Book


@st.cache_data
def get_books():
    books = [
        Book("Book name", "Author", 40),
        Book("Book name1", "Author1", 0),
        Book("Book name2", "Author2", 100),
        Book("Book name3", "Author3", 15)
    ]
    return books


def top_bar():
    with st.container(border=False):
        cols = st.columns([1, 4, 1])

        with cols[0]:
            find_books_button = st.button("Find books")
            if find_books_button:
                search_string = st.session_state["search_string"]
                books = get_books()
                st.session_state["filtered_books"] = [book for book in books if book.name.startswith(search_string)]

        with cols[1]:
            st.text_input(label="Search string", placeholder="Type a book's title...", key="search_string", label_visibility="collapsed")

        with cols[2]:
            logout_button = st.button("Logout")
            if logout_button:
               st.switch_page("Home.py")


def my_books_page():
    books = get_books()

    if "filtered_books" in st.session_state:
        books = st.session_state["filtered_books"]

    st.title("My books")

    top_bar()

    for book in books:
        with st.container(border=True):
            cols = st.columns(2)

            with cols[0]:
                st.write(book.name)
                st.write(book.author)

            with cols[1]:
                st.checkbox(label="In my books", value=True, key=book.name + str(books.index(book)))

            st.progress(book.progress)


my_books_page()
