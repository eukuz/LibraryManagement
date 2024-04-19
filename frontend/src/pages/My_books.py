import streamlit as st
from model.book import Book


books = [
    Book("Book name", "Author"),
    Book("Book name1", "Author1"),
    Book("Book name2", "Author2"),
    Book("Book name3", "Author3")
]

st.title("My books")

for book in books:
    with st.container(border=True):
        cols = st.columns(2)

        with cols[0]:
            st.write(book.name)
            st.write(book.author)

        with cols[1]:
            st.checkbox(label="In my books", value=True, key=book.name + str(books.index(book)))

        st.progress(40)
