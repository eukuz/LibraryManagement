import streamlit as st

from model.book import Book

books_list_key = "books_list"
search_string_key = "search_string"


@st.cache_data
def get_books():
    # TODO: add a query to backend here
    books = [
        Book("A Tale of Two Cities", "Charles Dickens", "Historical fiction", 40, True),
        Book("The Little Prince", "Antoine de Saint-Exupéry", "Fantasy, Children's fiction", 0, True),
        Book("The Alchemist", "Paulo Coelho", "Fantasy", 100, True),
        Book("Harry Potter and the Philosopher's Stone", "J. K. Rowling", "Fantasy, Children's fiction", 15, True),
        Book("A Tale of Two Cities", "Charles Dickens", "Historical fiction", 40, True),
        Book("The Little Prince", "Antoine de Saint-Exupéry", "Fantasy, Children's fiction", 0, True),
        Book("The Alchemist", "Paulo Coelho", "Fantasy", 100, True),
        Book("Harry Potter and the Philosopher's Stone", "J. K. Rowling", "Fantasy, Children's fiction", 15, True),
        Book("A Tale of Two Cities", "Charles Dickens", "Historical fiction", 40, True),
        Book("The Little Prince", "Antoine de Saint-Exupéry", "Fantasy, Children's fiction", 0, True),
        Book("The Alchemist", "Paulo Coelho", "Fantasy", 100, True),
        Book("Harry Potter and the Philosopher's Stone", "J. K. Rowling", "Fantasy, Children's fiction", 15, True),
    ]
    return books


@st.cache_data
def get_filtered_books(search_string: str):
    books = get_books()

    if not search_string:
        return books

    # TODO: add a query to backend here
    return [book for book in books if book.name.startswith(search_string)]


def top_bar():
    if search_string_key not in st.session_state:
        st.session_state[search_string_key] = ""

    with st.container(border=False):
        cols = st.columns([1, 4, 1])

        with cols[0]:
            find_books_button = st.button("Find books")
            if find_books_button:
                st.session_state.pop(books_list_key)
                st.switch_page("pages/2_Find_books.py")

        with cols[1]:
            current_search_string = st.text_input(
                label="Search string",
                placeholder="Type a book's title...",
                key="current_search_string",
                label_visibility="collapsed"
            )

            if current_search_string is None:
                current_search_string = ""

            if current_search_string != st.session_state[search_string_key]:
                st.session_state[search_string_key] = current_search_string
                st.session_state[books_list_key] = get_filtered_books(current_search_string)

        with cols[2]:
            logout_button = st.button("Logout")
            if logout_button:
                st.switch_page("Home.py")


def my_books_page():
    if books_list_key not in st.session_state:
        st.session_state[books_list_key] = get_books()

    st.title("My books")

    top_bar()

    books = st.session_state[books_list_key]

    for book in books:
        with st.container(border=True):
            cols = st.columns(3)

            with cols[0]:
                st.write(book.name)
                st.write(book.author)

            with cols[1]:
                st.write(book.genre)

            with cols[2]:
                st.checkbox(label="In my books", value=book.in_my_collection, key=book.name + str(books.index(book)))

            st.progress(book.progress)


my_books_page()
