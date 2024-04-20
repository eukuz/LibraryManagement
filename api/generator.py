import string
import httpx


def get_authors() -> set[str]:
    result = set()
    for letter in string.ascii_lowercase:
        resp = httpx.get(f'https://openlibrary.org/search/authors.json?q="{letter}"&limit=10')
        resp.raise_for_status()
        docs = resp.json()['docs']
        for doc in docs:
            result.add(doc["name"])
            print(doc["name"])
    return result


print(get_authors())
