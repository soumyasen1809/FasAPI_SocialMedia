from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, List
from pydantic import BaseModel
from passlib.context import CryptContext
import psycopg2
from psycopg2.extras import RealDictCursor
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
# we get the schemas from the schemas.py file
# . represents our current directory
from .. import models, schemas, utils
from ..database import engine, get_db
from ..config import settings


router = APIRouter(
    # for grouping our documentation in FastAPI into categories
    tags=['Authentication']
)


@router.post("/login", response_model=schemas.Token)
async def login(user_creds: schemas.UserLoginStructure, db: Session = Depends(get_db)):
    user_db = db.query(models.User).filter(
        models.User.email == user_creds.email).first()
    if user_db:
        # Get the password and convert it to a hashed password and compare it with the db stored password for the user
        verification_status = utils.verify_password(
            user_creds.password, user_db.password)
        if verification_status:
            # the payload in the data is choosen by me (I chose to just encode the user email)
            access_token = create_access_token(data={"user_id": user_db.id})
            # we just add the "bearer" in the "token type" while returning, no reason whatsoever
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f'Invalid credentials for the email {user_creds.email}')
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Invalid credentials for the email {user_creds.email}')


# For the token, we need to provide:
# SECRET_KEY
# Algorithm
# Expiration date (if this is not given, then the user is logged in forever)
# These values are found in the documentation of FastAPI
# obtained from random website
# SECRET_KEY = "TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30    # in minutes
# Now we are using the .env file
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes    # in minutes


# access token needs to take the data (which is the payload)
def create_access_token(data: dict):
    to_encode = data.copy()     # this data needs to be encoded in the JWT token
    # the token needs to expire after 30 minutes from now
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # adding this extra information to the data
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Next we need to verify the access token
def verify_access_token(token: str, cred_exception):
    try:
        payload_data = jwt.decode(
            token, key=SECRET_KEY, algorithms=[ALGORITHM])
        # from the payload data we can get the elements that were decoded
        # I chose to just encode the user email in the login() method
        user_id: str = payload_data.get("user_id")
        if user_id is None:
            raise cred_exception
        token_data = schemas.TokenData(id=user_id)
    except JWTError:
        raise cred_exception

    return token_data


# get the path "/login and remove the slash (/) and put it here"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# We can pass this as a dependency
# This is going to take the token from the request automatically
# extract the ID for us
# verify that the token is correct by calling the verify_token_access() method
# automatically fetch the user and add as a parameter to the path operation function


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    creds_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail=f'Invalid credentials', headers={"WWW-Authenticate": "Bearer"})

    # return verify_access_token(token, creds_exception)
    token = verify_access_token(token, creds_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user
