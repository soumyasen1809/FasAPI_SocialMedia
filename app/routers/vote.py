from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import Optional, List
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
# we get the schemas from the schemas.py file
# . represents our current directory
from .. import models, schemas, utils
from ..database import engine, get_db
from . import auth

# Create a router object
router = APIRouter(
    tags=['Votes']   # for grouping our documentation in FastAPI into categories
)


@router.post("/votes", status_code=status.HTTP_201_CREATED)
async def cast_vote(vote: schemas.VoteStructureBase, db: Session = Depends(get_db), current_user: int = Depends(auth.get_current_user)):
    post_query = db.query(models.Post).filter(
        models.Post.id == vote.post_id).first()
    if not post_query:  # user is trying to vote a post that does not exist
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post {vote.post_id} does not exist')

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    if vote.dir == 1:
        if vote_query.first():  # user has already voted, hence there is a record in the db
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f'User {current_user.id} has already voted the post {vote.post_id}')
        # else:   # user has not liked/voted the post before
            # add the vote to the database
        new_vote = models.Vote(
            user_id=current_user.id, post_id=vote.post_id)
        db.add(new_vote)
        db.commit()
        return {"vote message": "successfully voted"}
    else:
        if not vote_query.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f'Vote does not exist')   # trying to delete a vote/like that does not exist
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"vote message": "successfully deleted vote"}
