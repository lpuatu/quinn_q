import os
from google.genai import Client, types
from dotenv import load_dotenv


class GameAgent:
    def __init__(self):
        self.client = setup_gemini()
        self.client = upload_rulebook(self.client)
        self.file = self.client.files.upload(file="rulebooks/Rising_Sun_Rulebook.pdf")
