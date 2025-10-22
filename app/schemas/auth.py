from pydantic import BaseModel, EmailStr


class AuthSignupIn(BaseModel):
    email: EmailStr
    password: str


class AuthSignupOut(BaseModel):
    id: str
    email: str


class AuthLoginIn(BaseModel):
    email: EmailStr
    password: str


class AuthLoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
