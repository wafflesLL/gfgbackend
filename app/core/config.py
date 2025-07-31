from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    EXPECTED_API_KEY = os.getenv("EXPECTED_API_KEY")
    PROJECT_NAME = "Glasses for Good API"

settings = Settings()

