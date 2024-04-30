from pathlib import Path
from api import di
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
import asyncio
import csv

from api.persistence.models import Book, Genre, Author
from api.services import books


class Row(BaseModel):
    title: str
    author: str
    genre_name: str
    pages: int


async def fill_genres(sessionmaker: async_sessionmaker[AsyncSession], rows: list[Row]):
    print("fill genres")
    async with sessionmaker() as session:
        genres = set()
        for row in rows:
            genres.add(row.genre_name)
        for genre in genres:
            session.add(Genre(name=genre))
        try:
            await session.commit()
        except IntegrityError as e:
            print(e)
            pass


async def fill_authors(sessionmaker: async_sessionmaker[AsyncSession], rows: list[Row]):
    async with sessionmaker() as session:
        authors = set()
        for row in rows:
            authors.add(row.author)
        for author in authors:
            session.add(Author(fullname=author))
        try:
            await session.commit()
        except IntegrityError as e:
            print(e)
            pass


async def fill_books(sessionmaker: async_sessionmaker[AsyncSession], rows: list[Row]):
    async with sessionmaker() as session:
        for row in rows:
            b = Book(
                title=row.title,
                author_id=row.author,
                genre_name=row.genre_name,
                pages=row.pages,
            )
            session.add(b)
        try:
            await session.commit()
        except IntegrityError as e:
            print(e)
            pass


async def main():
    await di.init_db("api/store/db.sqlite")
    sessionmaker = await di.sessionmaker()
    path = Path("books.csv")
    rows = csv.DictReader(path.read_text().splitlines())
    rows = [
        Row.model_validate(row)
        for row in rows
    ]
    await fill_genres(sessionmaker, rows)
    await fill_authors(sessionmaker, rows)
    await fill_books(sessionmaker, rows)


if __name__ == "__main__":
    asyncio.run(main())
