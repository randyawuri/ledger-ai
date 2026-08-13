from pydantic import BaseModel, EmailStr


class RegisterUserRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str