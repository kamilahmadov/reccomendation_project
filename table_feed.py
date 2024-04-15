# This code defines a SQLAlchemy model for recording user 
# actions on posts within a feed, including user and post identifiers, 
# action types, and timestamps

from database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from table_user import User
from table_post import Post

class Feed(Base):
    __tablename__ = "feed_action"
    __table_args__ = {"schema": "public"}
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True, name="user_id")
    post_id = Column(Integer, ForeignKey(Post.id), primary_key=True, name="post_id")
    user = relationship(User)
    post = relationship(Post)
    action = Column(String)
    time = Column(TIMESTAMP, name="time")