# This main function contains all the queries using SQLAlchemy
# To see the way SQL queries can be directly embedded in the python code,
# see main backup file

from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
# we get the schemas from the schemas.py file
# . represents our current directory
from . import models, schemas, utils
from .database import engine, get_db
from .routers import post, user, auth, vote
from .config import settings


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# To allows CORS
# these domains are allowed to talk to us
origins = ["https://www.google.com",
           "https://www.bing.com", "https://www.youtube.com"]
# if you want all domains to talk to your API, your origins will be ["*"] (a wildcard)
app.add_middleware(
    CORSMiddleware,     # middleware is a function that runs before every request
    # specify the origins or domains our API can talk to
    allow_origins=origins,
    allow_credentials=True,
    # allow specific HTTP methods, like a domain can only do get request and not post or delete requests to our API
    allow_methods=["*"],
    allow_headers=["*"],
)


# This class is now written in schemas.py file
# class PostStructure(BaseModel):
#     title: str
#     content: str
#     published: bool = True  # default value
#     rating: Optional[int]


# # Connect the database: Not using anymore, We are using SQLALCHEMY (see database.py)
# try:
#     conn = psycopg2.connect(host='localhost', database='fastapi',
#                             user='postgres', password='test123', cursor_factory=RealDictCursor)
#     cursor = conn.cursor()
#     print(f'Database connection is successful')
# except Exception as err:
#     print(f'Error connecting to database: {err}')


# We use these router objects to break our code
# into seperate python files
# When we get a HTTP request, we go down the list like we normally do
# and this app object we first reference is app.include_router(...)
# and in here it says to include everything from post.router
# and so this request will go into the post.py file in router directory
# and check for all the matches
# and if it finds a match, it will respond like it normally does
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
