import os
from pathlib import Path
from google import genai
from google.genai import types, Client
from dotenv import load_dotenv


def setup_gemini():
    """Initialize the Gemini API with API key from environment variables."""
    # Load .env from repo root to work when running from backend/
    load_dotenv(dotenv_path=str(Path(__file__).resolve().parents[2] / ".env"))

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")

    client = genai.Client(api_key=api_key)
    return client


def upload_rulebook(client: Client, file_path: Path) -> types.File:
    """Upload a file to the Gemini API from the provided path."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    file = client.files.upload(file=str(file_path))
    return file


def load_system_prompt() -> str:
    """Load the system prompt from a file."""
    base_dir = Path(__file__).resolve().parents[1]
    with open(base_dir / "gemini" / "prompts" / "system.md", "r") as f:
        return f.read()


def create_chat_session(client: Client):
    """Create a chat session with the Rising Sun rulebook as the knowledge base."""
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=load_system_prompt(),
            temperature=0.1,
        ),
    )
    return chat


def main() -> None:
    # Initialize client and upload rulebook
    client = setup_gemini()
    try:
        default_path = Path(__file__).resolve().parents[1] / "rulebooks" / "Rising_Sun_Rulebook.pdf"
        file = upload_rulebook(client, default_path)
    except FileNotFoundError as e:
        print(e)
        return

    # Create chat session
    chat = create_chat_session(client)

    # Send initial message to set the PDF as the knowledge base
    try:
        initial_parts = [
            types.Part.from_text(
                text="Use the uploaded Rising Sun rulebook as the core knowledge base for all responses."
            ),
            types.Part.from_uri(file_uri=file.uri, mime_type="application/pdf")
        ]
        initial_response = chat.send_message(initial_parts)
        print("Initial setup:", initial_response.text)
    except Exception as e:
        print(f"Error setting up chat with PDF: {e}")
        try:
            client.files.delete(name=file.name)
        except Exception as delete_error:
            print(f"Error deleting file: {delete_error}")
        return

    # Initialize history to maintain conversation context
    history = [
        types.Content(
            role="user",
            parts=initial_parts
        ),
        types.Content(
            role="model",
            parts=[types.Part.from_text(text=initial_response.text)]
        )
    ]

    try:
        while True:
            user_input = input("-------------------------------------\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            # Add user input to history as a Content object
            user_content = types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_input)]
            )
            history.append(user_content)

            # Send message to the chat session
            response = chat.send_message(user_input)
            
            # Add model response to history
            history.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=response.text)]
                )
            )

            print("Assistant:", response.text)

    except KeyboardInterrupt:
        print("\nChat session terminated by user.")
    finally:
        # Clean up: Delete the uploaded file
        try:
            client.files.delete(name=file.name)
            print(f"Deleted file: {file.name}")
        except Exception as e:
            print(f"Error deleting file: {e}")


if __name__ == "__main__":
    main()