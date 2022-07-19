from fastapi.routing import APIRoute

from som.views.som import retrieve_som, create_som

routes = [
    APIRoute(
        path="/som",
        endpoint=retrieve_som,
        methods=["GET"],
        include_in_schema=True
    ),
    APIRoute(
        path="/som",
        endpoint=create_som,
        methods=["POST"],
        include_in_schema=True
    )
]
