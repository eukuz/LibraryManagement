import csv
import random
import string


# Function to generate random strings
def random_string(length):
    letters = string.ascii_letters
    return "".join(random.choice(letters) for _ in range(length))


def generate_authors(num) -> list[str]:
    result = []
    for _ in range(num):
        result.append(random_string(10))
    return result


def generate_csv(filename, num_books, num_authors, num_genres):
    authors = generate_authors(num_authors)
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["book_id", "title", "author", "genre_name", "pages"])

        for i in range(1, num_books + 1):
            title = f"Book {i}"
            author = random.choice(authors)
            pages = random.randint(100, 2000)
            genre_name = f"Genre {random.randint(1, num_genres)}"
            writer.writerow([i, title, author, genre_name, pages])


# Generate the CSV file
generate_csv("books.csv", 1000, 100, 20)
