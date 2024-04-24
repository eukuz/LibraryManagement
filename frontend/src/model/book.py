class Book:
    def __init__(self, book_id: int, name: str, author: str, genre: str, pages_read: int, pages_total: int, in_my_collection: bool):
        self.id = book_id
        self.name = name
        self.author = author
        self.genre = genre
        self.pages_read = pages_read
        self.pages_total = pages_total
        self.in_my_collection = in_my_collection


def parse_book(json_book) -> Book:

    return Book(
        json_book["id"],
        json_book["title"],
        json_book["author"],
        json_book["genre"],
        int(json_book["read_pages"]),
        int(json_book["total_pages"]),
        json_book["in_collection"] if "in_collection" in json_book else True
    )


def parse_books(json_books) -> list[Book]:
    return [parse_book(json_book) for json_book in json_books]


def parse_books_response(response) -> list[Book]:
    return parse_books(response.json()['books'])
