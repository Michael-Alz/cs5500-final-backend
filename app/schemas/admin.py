from pydantic import BaseModel


class AdminActionRequest(BaseModel):
    password: str
