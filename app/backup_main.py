from fastapi import FastAPI, Response, status, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from . import models        # . represents our current directory
from .database import engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class PostStructure(BaseModel):
    title: str
    content: str
    published: bool = True  # default value
    rating: Optional[int]


# my_posts = [{"id": 1, "title": "Post1", "content": "This is my post #1", "published": True},
#             {"id": 2, "title": "Post2", "content": "This is my post #2"},
#             {"id": 3, "title": "Post3", "content": "This is my post #3", "published": False}]


# Connect the database
try:
    conn = psycopg2.connect(host='localhost', database='fastapi',
                            user='postgres', password='test123', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print(f'Database connection is successful')
except Exception as err:
    print(f'Error connecting to database: {err}')


# Root path
@app.get("/")
async def root():
    return {"message": "Hello World, Welcome to FastAPI"}

# Get operation


@app.get("/posts")
async def get_posts():
    # Note that the name of the table in the database needs to be in small.
    # Use of any capital letter will cause an error, since psycopg2 converts the name to all lower
    cursor.execute(""" SELECT * FROM posts """)
    all_posts = cursor.fetchall()
    return {"get all posts": all_posts}

# Get latest post


@app.get("/posts/latest")
async def get_latest_post():
    cursor.execute(""" SELECT * FROM posts ORDER BY id DESC LIMIT 1""")
    lastest_post = cursor.fetchone()
    return {"get latest post": lastest_post}

# Get post for an ID


@app.get("/posts/{id}")
async def get_post(id: int):
    # the below code is to get data for a given ID when the data is stored in the list my_posts
    # for post in my_posts:
    #     if post["id"] == int(id):
    #         return {"get post with ID": post}

    # the below code is to get data for a given ID when the data is stored in a database
    cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id),)
                   )      # the id here is a path parameter, and hence needs to be a string
    # note: this (str(id)), syntax is used (i.e. this weird brackets and extra comma) to fix certain issues
    # there is no explanation to that (just weird hack to work)
    id_post = cursor.fetchone()     # there is only 1 post with given id
    if id_post:
        return {"get post with ID": id_post}
    if not id_post:
        # return {"get post with ID" : f'Post with id {id} not found'}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} not found')

# Create a post


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(post: PostStructure):
    # this is the code to post data in the list my_post
    # to_post = post.dict()
    # my_post_latest = my_posts[len(my_posts) - 1]
    # latest_post_id = my_post_latest["id"]
    # to_post_id = latest_post_id + 1
    # to_post["id"] = to_post_id
    # my_posts.append(to_post)
    # return {"new post created": to_post}

    # this is the code to post data to the database
    # %s denotes a variable. the variables sent later are replaced into the %s placeholders.
    # This method is used to prevent SQL Injections
    # also, using RETURNING * will return the entry that has been added
    cursor.execute(""" INSERT INTO posts (title, content, published, rating) VALUES (%s, %s, %s, %s) RETURNING * """,
                   (post.title, post.content, post.published, post.rating))
    new_post = cursor.fetchone()
    # just doing steps till above will not update the values in the postgres database, although you can see it in Postman
    # so, we need to commit the changes to make them visible in Pgadmin
    conn.commit()
    return {"new post created": new_post}

# Delete a post


@app.delete("/posts/{id}")
async def delete_post(id):
    # the below code is to delete data for a given ID when the data is stored in the list my_posts
    # for index, post in enumerate(my_posts):
    #     if post["id"] == int(id):
    #         # to_delete = post
    #         my_posts.pop(index)
    #         # return {"post deleted" : to_delete}
    #         # for deleting operation, we are not supposed to return any data (FASTAPI guidelines)
    #         # hence we return the status
    #         return Response(status_code=status.HTTP_204_NO_CONTENT)

    # the below code is to get data for a given ID when the data is stored in a database
    # we need to return the post that is deleted, so the RETURNING * keyword
    cursor.execute(
        """ DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()       # we need to commit since we are making a change to the database

    if deleted_post:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        # return {"get post with ID" : f'Post with id {id} not found'}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} not found')


# Update a post (Edit)
@app.put("/posts/{id}")
async def update_post(id: int, edited_post: PostStructure):
    # the below code is to update data for a given ID when the data is stored in the list my_posts
    # to_edit_post = edited_post.dict()
    # for post in my_posts:
    #     if post["id"] == int(id):
    #         post["title"] = to_edit_post["title"]
    #         post["content"] = to_edit_post["content"]
    #         post["published"] = to_edit_post["published"]
    #         return {"edited post": post}

    # the below code is to update data for a given ID when the data is stored in a database
    cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
                   (edited_post.title, edited_post.content, edited_post.published, (str(id),)))
    # again note, in curson.execute, the entire list of variables need to be inside a () bracket
    # else, we get an error - TypeError: execute() takes from 2 to 3 positional arguments
    updated_post = cursor.fetchone()
    conn.commit()   # need to commit to reflect changes to PGadmin

    if updated_post:
        return {"edited post": updated_post}
    else:
        # return {"get post with ID" : f'Post with id {id} not found'}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} not found')


# # Testing sqlalchemy
# # Using SQLAlchemy so that we do not need to write any SQL command
# @app.get("/sqlalchemy")
# async def get_posts_sqlalchemy(db: Session = Depends(get_db)):
#     sql_post = db.query(models.Post).all()      # Post is a model defined in models.py
#     # Using models.Post we can access the table defined in the model Post
#     # i.e. the table "posts"
#     # .all() method will grab everything
#     return {"sql data" : sql_post}
