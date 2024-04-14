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
    for row in rows:
        async with sessionmaker() as session:
            session.add(Genre(name=row.genre_name))
            try:
                await session.commit()
            except IntegrityError as e:
                print(e)
                pass


async def fill_authors(sessionmaker: async_sessionmaker[AsyncSession], rows: list[Row]):
    for row in rows:
        async with sessionmaker() as session:
            session.add(Author(fullname=row.author))
            try:
                await session.commit()
            except IntegrityError as e:
                print(e)
                pass


async def fill_books(sessionmaker: async_sessionmaker[AsyncSession], rows: list[Row]):
    for row in rows:
        try:
            await books.add_book(
                row.title,
                row.author,
                row.genre_name,
                row.pages,
                sessionmaker,
            )
        except IntegrityError as e:
            print(e)
            pass


async def main():
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
