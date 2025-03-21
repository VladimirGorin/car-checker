from pydantic import BaseModel


class AuthRequest(BaseModel):
    user_id: str
