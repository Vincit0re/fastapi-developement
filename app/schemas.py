from datetime import datetime
from venv import create
from pydantic import BaseModel, EmailStr, conint
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    pass


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PostBase(BaseModel):
    title: str
    content: str
    published: Optional[bool] = True


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    published = bool


class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponse

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: PostResponse
    votes: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class VoteBase(BaseModel):
    post_id: int
    value: conint(ge=0, le=1)


class VoteCreate(VoteBase):
    pass


class VoteResponse(VoteBase):
    voted_at: datetime

    class Config:
        orm_mode = True
