from fastapi.routing import APIRoute

from som.api.views.som import create_som, retrieve_som


def get_routes():
    return [
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
