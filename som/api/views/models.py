from fastapi_utils.api_model import APIModel


class SomMessage(APIModel):
    task_id: str
