import os
from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def list_books(self):
        for offset in range(0, 10000, 50):
            self.client.get("/api/books/", params={'limit': 50, 'offset': offset})

    def on_start(self):
        session_id = os.environ['SESSION_ID']
        self.client.headers = {'Authorization': f'Bearer {session_id}'}
