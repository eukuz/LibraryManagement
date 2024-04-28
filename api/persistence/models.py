from datetime import datetime
from sqlalchemy import ForeignKey, func
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
    genre_name: Mapped[str] = mapped_column(ForeignKey("genre.name"))

    pages: Mapped[int]


class BookProgress(Base):
    __tablename__ = "book_progress"

    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"), primary_key=True)

    read_pages: Mapped[int] = mapped_column(default=0)


class Collection(Base):
    __tablename__ = "collection"

    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"), primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
