import streamlit as st
import requests
from model.book import parse_books_response, Book
import extra_streamlit_components as stx

books_list_key = "books_list"
search_string_key = "search_string"
token_key = "token"
cookies_key = "cookies"


def update_cookies():
    stx.CookieManager(cookies_key)


def get_cookies():
    return st.session_state[cookies_key]


def get_random_books() -> list[Book]:
    token = st.session_state[token_key]
    response_books = requests.get(
        "https://sqr.webrtc-thesis.ru/api/books/suggest",
        headers={'Authorization': f'Bearer {token}'}
    )

    books = parse_books_response(response_books)

    return books


def find_books(search_string: str):
    token = st.session_state[token_key]
    headers = {'Authorization': f'Bearer {token}'}
    request_url = "https://sqr.webrtc-thesis.ru/api/books/"
    if not search_string:
        response = requests.get(request_url,
                                headers=headers)
    else:
        response = requests.get(request_url,
                                headers=headers,
                                params={"title_like": search_string})
    books = parse_books_response(response)

    return books


def top_bar():
    if search_string_key not in st.session_state:
        st.session_state[search_string_key] = ""

    with st.container(border=False):
        cols = st.columns([1, 4, 1])

        with cols[0]:
            my_books_button = st.button("My books")
            if my_books_button:
                st.session_state.pop(books_list_key)
                st.switch_page("pages/1_My_books.py")

        with cols[1]:
            current_search_string = st.text_input(
                label="Search string",
                placeholder="Type a book's title...",
                label_visibility="collapsed"
            )
            if current_search_string is None:
                current_search_string = ""

            if current_search_string != st.session_state[search_string_key]:
                print(current_search_string)
                print(st.session_state[search_string_key])
                st.session_state[books_list_key] = find_books(current_search_string)

        with cols[2]:
            suggest_button = st.button("Suggest")
            if suggest_button:
                st.session_state[books_list_key] = get_random_books()


def update_in_collection():
    books = st.session_state[books_list_key]
    for book in books:
        in_collection = st.session_state[f"in_collection_{book.id}"]
        if book.in_my_collection != in_collection:
            book.in_my_collection = in_collection
            token = st.session_state[token_key]
            requests.post(
                f"https://sqr.webrtc-thesis.ru/api/books/{book.id}/collection",
                headers={'Authorization': f'Bearer {token}'},
                params={"add": in_collection}
            )


def find_books_page():
    if token_key not in st.session_state:
        update_cookies()
        cookies = get_cookies()
        if "SESSION_ID" in cookies:
            session_id = cookies["SESSION_ID"]
        else:
            st.switch_page("Home.py")
        if session_id:
            st.session_state[token_key] = session_id
        else:
            st.switch_page("Home.py")

    if books_list_key not in st.session_state:
        st.session_state[books_list_key] = find_books("")

    st.title("Find books")

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
                st.checkbox(label="In my books",
                            value=book.in_my_collection,
                            key=f'in_collection_{book.id}',
                            on_change=update_in_collection
                            )

            st.progress(book.progress)


find_books_page()
