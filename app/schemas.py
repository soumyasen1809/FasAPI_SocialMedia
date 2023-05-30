from pydantic import BaseModel, EmailStr
from pydantic.types import conint
from typing import Optional
from datetime import datetime


# For the User class
class UserStructureBase(BaseModel):
    email: EmailStr     # this ensures this is a valid email and not some random text
    password: str
    name: str


class UserCreate(UserStructureBase):
    pass


class UserUpdate(UserStructureBase):
    pass


# For the response, I do not want to return the password
# If I extend it with UserStructureBase baseclass, then
# I will get the password as a return too, which I do not want
class UserResponseStructure(BaseModel):
    id: int
    email: EmailStr
    name: str
    created_at: datetime

    class Config:
        orm_mode = True


# For post class

# class PostStructure(BaseModel):
#     title: str
#     content: str
#     published: bool = True  # default value
#     rating: Optional[int]

# we create a Baseclass here of how the post structure should look like
# It is a pydantic model and extends the BaseModel


class PostStructureBase(BaseModel):
    title: str
    content: str
    published: bool = True  # default value
    rating: Optional[int]
    # Note we don't need to add the user_id column here, as we will let the logic to flow
    # We will let the login get the token and add the user_id automatically

# when we create a post it extends the Baseclass
# we now have the flexibility of choosing which
# fields to use for creating a post


class PostCreate(PostStructureBase):
    pass

# when we update a post it extends the Baseclass of the post structure


class PostUpdate(PostStructureBase):
    pass

# This provides a lot of flexibility
# E.g., I can just have the field id in this response class
# and we will just return the id only to the frontend/user


class ResponseStructureBase(PostStructureBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponseStructure

    # this (taken from documentation) is needed to let the pydantic model response work without dictionary
    class Config:
        orm_mode = True


# error in the video: should inherit from BaseModel
class PostVoteStructure(BaseModel):
    Post: ResponseStructureBase
    votes: int

    class Config:
        orm_mode = True


# For authentication (login)
class UserLoginStructure(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str]


# Schema for voting
class VoteStructureBase(BaseModel):
    post_id: int
    # conint: anything less than 1 is allowed (problem: allows negative numbers)
    dir: conint(le=1)   # dir: value of 1 means we want to like the post
