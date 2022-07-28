from dotenv import load_dotenv
from fastapi import FastAPI

from som.api.routing import routes


def create_app():
    # Load a .env file, primarily for local usage.
    # there's no harm if the file is not present.
    load_dotenv()
    return FastAPI(routes=routes)
