import requests


class Embeddings:

    def __init__(self):
        self.model = "nomic-embed-text:latest"
        self.url = "http://localhost:11434/api/embed"

    def generate(self, text):
        print("[Embeddings] generating")

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "input": text
            }
        )

        response.raise_for_status()

        data = response.json()

        return data["embeddings"][0]