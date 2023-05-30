from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import Optional, List
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import func
# we get the schemas from the schemas.py file
# . represents our current directory
from .. import models, schemas, utils
from ..database import engine, get_db
from . import auth


# Create a router object
router = APIRouter(
    tags=['Posts']   # for grouping our documentation in FastAPI into categories
)


# Root path
@router.get("/")
async def root():
    return {"message": "Hello World, Welcome to FastAPI"}


# Get all posts
# @router.get("/posts", response_model=List[schemas.ResponseStructureBase])
@router.get("/posts", response_model=List[schemas.PostVoteStructure])
# 'limit' argument is the query parameter that will be used to limit the number of posts to be displayed
# default value added to limit is 5
# 'skip' argument is another query parameter to skip the given number of results (useful for pagination)
# default value added to skip is 2
# 'search_keyword' argument is added to search through the title
# It is optional. Using .contains(search_keyword) will search if the string is contained (substring) in the title
# For searching in Postman, if there is a space between two words we are searching, use %20 between the words
# In Postman, use the ? to add query parameters
# In Postman, to add more query parameters use &
async def get_posts(db: Session = Depends(get_db), limit: int = 5, skip: int = 2, search_keyword: Optional[str] = ""):
    # add all_posts query to the below query with inner join and couting votes
    # all_posts = db.query(models.Post).filter(models.Post.title.contains(
    #     search_keyword)).limit(limit).offset(skip).all()

    # SQLAlchemy by default makes an INNER LEFT JOIN, but we need an OUTER LEFT JOIN, so we pass flag isouter=True
    # Using .label() we can rename a column in the sql output (similar to AS in raw SQL)
    # We groupby post.id and count with post.id (the column needs to be passed to count instead of using * to disallow counting null)
    # This will give me the number of votes for each post id (excluding the posts with null votes)
    count_votes_query = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search_keyword)).limit(limit).offset(skip).all()
    # return {"get all posts": all_posts}
    # return all_posts
    return count_votes_query


# # Get latest post
# @router.get("/posts/latest")
# async def get_latest_post():
#     cursor.execute(""" SELECT * FROM posts ORDER BY id DESC LIMIT 1""")
#     lastest_post = cursor.fetchone()
#     # return {"get latest post": lastest_post}
#     return lastest_post


# Get post for an ID
# @router.get("/posts/{id}", response_model=schemas.ResponseStructureBase)
@router.get("/posts/{id}", response_model=schemas.PostVoteStructure)
async def get_post(id: int, db: Session = Depends(get_db)):
    # filter is similar to WHERE in SQL
    # .first() will find the first instance and return the results
    # add id_post query to the below query with inner join and couting votes
    # id_post = db.query(models.Post).filter(
    #     models.Post.id == id).first()
    id_post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.id == id).first()
    if id_post:
        # return {"get post with id": id_post}
        return id_post
    else:
        # return {"get post with ID" : f'Post with id {id} not found'}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} not found')


# Create a post
@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.ResponseStructureBase)
async def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(auth.get_current_user)):
    # We would now need user login authorization
    # In Postman, to send an authorization token, do the following:
    # 1. Go to http://127.0.0.1:8000/login (Post) and copy the access_token
    # 2. Go to http://127.0.0.1:8000/posts (Post) and select Headers
    # 3. In Headers, add a new field, with Key: Authorization and Value: Bearer <token> (note the space after Bearer)
    print(f'{current_user}')

    # first, we create a brand new post
    # new_post = models.Post(title=post.title, content=post.content, rating=post.rating, published=post.published)
    # the above method is inefficient, because what if we have 50 different parameters,
    # then every time we need to do xx = post.xx,...
    # so we use the below method, where we convert the post to a dictionary
    # and then using **, we unpack the dictionary
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    # We should be able to use this login information of the user to add it as the foreign key to the posts table
    # second, we add it to our database
    db.add(new_post)
    # next, we commit our changes to the database (so that we can see in PGAdmin now)
    db.commit()
    # and we retrieve the new post we created and store it back to the the variable new_post
    db.refresh(new_post)
    # return {"new post created": new_post}
    return new_post


# Delete a post
@router.delete("/posts/{id}")
async def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(auth.get_current_user)):
    deleted_post = db.query(models.Post).filter(models.Post.id == id)

    if deleted_post.first():
        # an user should be able to delete his own post only, not some other user's post
        if deleted_post.first().owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f'Not authorized to delete different user post')
        # no justification for synchronize_session=False, SQLAlchemy doc says so, thats why
        deleted_post.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        # return {"get post with ID" : f'Post with id {id} not found'}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} not found')


# Update a post (Edit)
@router.put("/posts/{id}", response_model=schemas.ResponseStructureBase)
async def update_post(id: int, edited_post: schemas.PostUpdate, db: Session = Depends(get_db), current_user: int = Depends(auth.get_current_user)):
    updated_post = db.query(models.Post).filter(models.Post.id == id)

    if updated_post.first():
        # an user should be able to update/edit his own post only, not some other user's post
        if updated_post.first().owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f'Not authorized to modify different user post')
        updated_post.update(edited_post.dict(), synchronize_session=False)
        db.commit()
        # return {"edited post": updated_post.first()}
        return updated_post.first()
    else:
        # return {"get post with ID" : f'Post with id {id} not found'}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} not found')


# # Testing sqlalchemy
# # Using SQLAlchemy so that we do not need to write any SQL command
# @router.get("/sqlalchemy")
# async def get_posts_sqlalchemy(db: Session = Depends(get_db)):
#     sql_post = db.query(models.Post).all()      # Post is a model defined in models.py
#     # Using models.Post we can access the table defined in the model Post
#     # i.e. the table "posts"
#     # .all() method will grab everything
#     return {"sql data" : sql_post}
