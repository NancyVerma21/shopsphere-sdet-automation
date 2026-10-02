import os

from dotenv import load_dotenv


load_dotenv()

BASE_URL = os.getenv("BASE_URL")

if not BASE_URL:
    raise ValueError("BASE_URL is not set in the environment configuration.")