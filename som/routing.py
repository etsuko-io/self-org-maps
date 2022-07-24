from fastapi.routing import APIRoute

from som.views.som import create_som, retrieve_som


routes = [
    APIRoute(
        path="/som",
        endpoint=retrieve_som,
        methods=["GET"],
        include_in_schema=True,
    ),
    APIRoute(
        path="/som",
        endpoint=create_som,
        methods=["POST"],
        include_in_schema=True,
    ),
]
