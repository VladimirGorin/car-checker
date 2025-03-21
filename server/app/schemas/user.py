from pydantic import BaseModel

class UserBase(BaseModel):
    id: int
    user_id: str

class UserCreateResponse(UserBase):
    pass

class UserCreateRequest(BaseModel):
    pass

class UserCreate(UserBase):
    pass
