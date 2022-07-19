from dotenv import load_dotenv
from fastapi import FastAPI

from som.routing import routes


def create_app():
    load_dotenv()
    return FastAPI(routes=routes)
