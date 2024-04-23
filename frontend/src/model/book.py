class Book:
    def __init__(self, book_id: int, name: str, author: str, genre: str, progress: int, in_my_collection: bool):
        self.id = book_id
        self.name = name
        self.author = author
        self.genre = genre
        self.progress = progress
        self.in_my_collection = in_my_collection


def parse_book(json_book) -> Book:
    pages_total = int(json_book["total_pages"])
    pages_read = int(json_book["read_pages"])

    progress = int(pages_read / pages_total * 100)

    return Book(
        json_book["id"],
        json_book["title"],
        json_book["author"],
        json_book["genre"],
        progress,
        json_book["in_collection"] if "in_collection" in json_book else True
    )


def parse_books(json_books) -> list[Book]:
    return [parse_book(json_book) for json_book in json_books]


def parse_books_response(response) -> list[Book]:
    return parse_books(response.json()['books'])
