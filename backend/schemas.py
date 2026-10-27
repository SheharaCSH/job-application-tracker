from datetime import date
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

Status = Literal["Applied", "Interview", "Offer", "Rejected"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ApplicationCreate(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=200)
    location: str | None = None
    status: Status = "Applied"
    applied_date: date = Field(default_factory=date.today)
    job_link: str | None = None
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    company: str | None = None
    role: str | None = None
    location: str | None = None
    status: Status | None = None
    applied_date: date | None = None
    job_link: str | None = None
    notes: str | None = None


class ApplicationOut(ApplicationCreate):
    id: int

    model_config = {"from_attributes": True}