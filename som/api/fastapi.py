from fastapi import FastAPI

from som.api.routing import get_routes


def create_app():
    return FastAPI(routes=get_routes())
