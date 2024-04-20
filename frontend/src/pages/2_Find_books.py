import random

import streamlit as st
import requests
from model.book import Book

books_list_key = "books_list"
search_string_key = "search_string"


@st.cache_data
def books_storage():
    # TODO: add a query to backend here
    books = [
        Book("A Tale of Two Cities", "Charles Dickens", "Historical fiction", 40, True),
        Book("The Little Prince", "Antoine de Saint-Exupéry", "Fantasy, Children's fiction", 0, False),
        Book("The Alchemist", "Paulo Coelho", "Fantasy", 100, True),
        Book("Harry Potter and the Philosopher's Stone", "J. K. Rowling", "Fantasy, Children's fiction", 15, True),
    ]
    return books


def get_random_book():
    books = books_storage()
    index = random.Random().randint(0, len(books) - 1)
    return books[index]


@st.cache_data
def find_books(search_string: str):
    books = books_storage()

    if not search_string:
        return []

    # TODO: add a query to backend here
    return [book for book in books if book.name.startswith(search_string)]


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
                st.session_state[search_string_key] = current_search_string
                st.session_state[books_list_key] = find_books(current_search_string)

        with cols[2]:
            suggest_button = st.button("Suggest")
            if suggest_button:
                st.session_state[books_list_key] = [get_random_book()]


def find_books_page():
    if books_list_key not in st.session_state:
        st.session_state[books_list_key] = []

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
                st.checkbox(label="In my books", value=book.in_my_collection, key=book.name + str(books.index(book)))

            st.progress(book.progress)


find_books_page()
