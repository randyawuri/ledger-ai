from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------------------------------------------------------
# Register
# ---------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr

    first_name: str = Field(
        min_length=2,
        max_length=100,
    )

    last_name: str = Field(
        min_length=2,
        max_length=100,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

class LoginRequest(BaseModel):
    email: EmailStr

    password: str


# ---------------------------------------------------------
# JWT Response
# ---------------------------------------------------------

class TokenResponse(BaseModel):
    access_token: str

    token_type: str = "bearer"


# ---------------------------------------------------------
# Current User
# ---------------------------------------------------------

class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    email: EmailStr

    first_name: str

    last_name: str

    created_at: datetime