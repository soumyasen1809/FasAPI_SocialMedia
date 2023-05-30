from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import Optional, List
from pydantic import BaseModel
from passlib.context import CryptContext
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
# we get the schemas from the schemas.py file
from .. import models, schemas, utils        # . represents our current directory
from ..database import engine, get_db


# Create a router object
router = APIRouter(
    tags=['Users']  # for grouping our documentation in FastAPI into categories
)


# Create a new user
@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponseStructure)
async def create_users(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # hash the password before saving to the database
    hashed_pass = utils.hash_function(user.password)
    user.password = hashed_pass

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Get all users
@router.get("/users", response_model=List[schemas.UserResponseStructure])
async def get_users(db: Session = Depends(get_db)):
    all_users = db.query(models.User).all()
    return all_users


# Get user data for an id
@router.get("/users/{id}", response_model=schemas.UserResponseStructure)
async def get_user(id: int, db: Session = Depends(get_db)):
    id_user = db.query(models.User).filter(models.User.id == id).first()
    if id_user:
        return id_user
    else:
        # return {"get user with ID" : f'User with id {id} not found'}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with id {id} not found')
