import requests
import streamlit as st

from model.book import parse_books_response, Book
from operations.token_ops import set_token

books_list_key = "books_list"
search_string_key = "search_string"
token_key = "token"
cookies_key = "cookies"


def get_books():
    token = st.session_state[token_key]
    response = requests.get("https://sqr.webrtc-thesis.ru/api/collection/",
                            headers={'Authorization': f'Bearer {token}'})
    books = parse_books_response(response)

    return books


@st.cache_data
def get_filtered_books(search_string: str):
    books = get_books()

    if not search_string:
        return books

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


def update_in_collection():
    books: list[Book] = st.session_state[books_list_key]
    for book in books:
        in_collection = st.session_state[f"in_collection_{book.id}"]
        if not in_collection:
            token = st.session_state[token_key]
            requests.post(
                f"https://sqr.webrtc-thesis.ru/api/books/{book.id}/collection",
                headers={'Authorization': f'Bearer {token}'},
                params={"add": in_collection}
            )
            books.remove(book)


def update_pages_read():
    books: list[Book] = st.session_state[books_list_key]
    for book in books:
        pages_read = int(st.session_state[f"slider_{book.id}"])
        if pages_read != book.pages_read:
            print(book.id)
            print(pages_read)
            print(book.pages_read)
            token = st.session_state[token_key]
            requests.post(
                f"https://sqr.webrtc-thesis.ru/api/books/{book.id}/progress",
                headers={'Authorization': f'Bearer {token}'},
                json={"pages_read": pages_read},
            )


def display_books(books: list[Book]) -> ():
    with st.container(height=600):
        for book in books:
            with st.container(border=True):
                cols = st.columns(3)

                with cols[0]:
                    st.write(book.name)
                    st.write(book.author)

                with cols[1]:
                    st.write(book.genre)

                with cols[2]:
                    st.checkbox(label="In my books", value=True, key=f"in_collection_{book.id}",
                                on_change=update_in_collection)

                st.slider(
                    label="Reading progress",
                    key=f"slider_{book.id}",
                    min_value=0,
                    max_value=book.pages_total,
                    value=book.pages_read,
                    on_change=update_pages_read
                )


def my_books_page():
    set_token()

    if books_list_key not in st.session_state:
        st.session_state[books_list_key] = get_books()

    st.title("My books")

    top_bar()

    books = st.session_state[books_list_key]

    display_books(books)


my_books_page()
