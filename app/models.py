# Every model represents a table in our database
from .database import Base
# this is to use the server_default = text
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey


# Post is a model here
class Post(Base):       # all the model classes need to extend Base class
    __tablename__ = "posts"     # name of the table we want
    # if we already have a table present named "posts", sqlalchemy will not touch it
    # it is a limitation of SQLAlchemy.

    # now we add columns to the table we created
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    rating = Column(Integer, nullable=True)
    published = Column(Boolean, nullable=False, server_default='True')
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    # Note in writing a foreign key, we pass the tablename (users) and not the class name (User)
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)

    # Automatically create another property for our post so that when we retireve a post,
    # it will fetch the user based on the owner_id
    # here I am referencing the class and not the table
    owner = relationship("User")


# User is another model here
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    # using unique flag tells that there can't be two users with the same email
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))


# Model for our votes
class Vote(Base):
    __tablename__ = "votes"

    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    post_id = Column(Integer, ForeignKey(
        "posts.id", ondelete="CASCADE"), primary_key=True, nullable=False)
