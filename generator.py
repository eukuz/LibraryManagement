import csv
import random
import string

# Define the genres
genres = [
    "Mystery",
    "Science Fiction",
    "Fantasy",
    "Romance",
    "Horror",
    "Thriller",
    "Historical Fiction",
    "Adventure",
    "Literary Fiction",
    "Crime",
    "Young Adult",
    "Poetry",
    "Non-fiction",
    "Memoir",
    "Biography",
    "Satire",
    "Drama",
    "Comedy",
    "Fairy Tale",
    "Mythology",
]

authors = ["".join(random.choices(string.ascii_letters, k=8)) for _ in range(500)]

# Generate and write to CSV file
with open("books.csv", "w", newline="") as csvfile:
    fieldnames = ["book_id", "title", "author", "genre_name", "pages"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for i in range(10000):
        writer.writerow(
            {
                "book_id": i,
                "title": f"Book {i}",
                "author": random.choice(authors),
                "genre_name": random.choice(genres),
                "pages": random.randint(100, 1000),
            }
        )

print("CSV file generated successfully.")
