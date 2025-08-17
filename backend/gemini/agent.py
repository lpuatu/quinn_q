import os
from google.genai import Client, types
from dotenv import load_dotenv
from gemini.request import setup_gemini, upload_rulebook


class GameAgent:
    def __init__(self):
        self.client = setup_gemini()
        self.file = upload_rulebook(self.client)
