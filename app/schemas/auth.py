from pydantic import BaseModel, EmailStr


class AuthSignupIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class AuthSignupOut(BaseModel):
    id: str
    email: str
    full_name: str


class AuthLoginIn(BaseModel):
    email: EmailStr
    password: str


class AuthLoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
