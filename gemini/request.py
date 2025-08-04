import os
from google.genai import Client, types
from dotenv import load_dotenv


def setup_gemini():
    """Initialize the Gemini API with API key from environment variables."""
    load_dotenv()  # Load environment variables from .env file

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")

    client = Client(api_key=api_key)
    return client


def upload_rulebook(client: Client):
    """Upload a file to the Gemini API."""
    file = client.files.upload(file="rulebooks/Rising_Sun_Rulebook.pdf")
    return client, file


def create_chat_session(client: Client, history: list):
    chat = client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction="Provide a concise and helpful response regarding the rules to the uploaded board game rulebook. Always consult the rulebook for the most accurate information.",
            temperature=0.1,
        ),
    )
    return chat


if __name__ == "__main__":
    # Example usage
    client = setup_gemini()
    client, file = upload_rulebook(client)

    model_content = types.ModelContent(
        parts=[
            types.Part.from_text(
                text="You are an expert at understanding board game rules and are able to answer questions about them."
            )
        ]
    )

    history = [file, model_content]

    chat = create_chat_session(client, history)

    while True:
        user_input = input("-------------------------------------\nYou: ")
        history.append(types.Part.from_text(text=user_input))

        # response = chat.generate_content(
        #     model="gemini-2.0-flash-001",
        #     history=history,
        #     config=types.GenerateContentConfig(
        #         system_instruction="Provide a concise and helpful response.",
        #         temperature=0.1,
        #     ),
        # )

        response = chat.send_message(user_input)
        history.append(response)

        print(response.text)
