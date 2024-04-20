from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, MappedAsDataclass


class Base(MappedAsDataclass, AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(primary_key=True)
    fullname: Mapped[str]


class Author(Base):
    __tablename__ = "author"
    fullname: Mapped[str] = mapped_column(primary_key=True)


class UserSession(Base):
    __tablename__ = "user_session"

    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship(init=False, lazy="selectin")
    session_id: Mapped[str] = mapped_column(unique=True, primary_key=True)


class Genre(Base):
    __tablename__ = "genre"

    name: Mapped[str] = mapped_column(primary_key=True)


class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(unique=True)

    author_id: Mapped[str] = mapped_column(ForeignKey('author.fullname'))
    author: Mapped[Author] = relationship(init=False, lazy='selectin')

    genre_name: Mapped[str] = mapped_column(ForeignKey("genre.name"))
    genre: Mapped[Genre] = relationship(init=False, lazy='selectin')

    pages: Mapped[int]


class BookProgress(Base):
    __tablename__ = "book_progress"

    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"), primary_key=True)
    book: Mapped[Book] = relationship(init=False, lazy='selectin')

    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"), primary_key=True)
    user: Mapped[User] = relationship(init=False, lazy='selectin')

    read_pages: Mapped[int]


class Collection(Base):
    __tablename__ = "collection"

    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"), primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"), primary_key=True)
    book: Mapped[Book] = relationship(init=False, lazy='selectin')
