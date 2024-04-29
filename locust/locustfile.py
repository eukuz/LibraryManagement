import os
from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def list_books(self):
        for offset in range(0, 13000, 50):
            self.client.get("/api/books/", params={'limit': 20, 'offset': offset})

    @task
    def get_collection(self):
        self.client.get("/api/collection")

    @task
    def get_book_details(self):
        book_id = 123  # Replace with a valid book ID
        self.client.get(f"/api/books/{book_id}")

    @task
    def suggest_books(self):
        self.client.get("/api/books/suggest")

    @task
    def get_root_books(self):
        self.client.get("/api/books/")

    def on_start(self):
        session_id = os.environ['SESSION_ID']
        self.client.headers = {'Authorization': f'Bearer {session_id}'}
