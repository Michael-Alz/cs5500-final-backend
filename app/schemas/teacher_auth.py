from pydantic import BaseModel, EmailStr


class TeacherSignupIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class TeacherSignupOut(BaseModel):
    id: str
    email: str
    full_name: str


class TeacherLoginIn(BaseModel):
    email: EmailStr
    password: str


class TeacherLoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    teacher_email: str
    teacher_full_name: str
