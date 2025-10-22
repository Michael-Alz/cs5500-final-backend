from typing import List

from pydantic import BaseModel


class CourseCreate(BaseModel):
    title: str


class CourseOut(BaseModel):
    id: str
    title: str

    class Config:
        from_attributes = True


class CourseListOut(BaseModel):
    courses: List[CourseOut]
