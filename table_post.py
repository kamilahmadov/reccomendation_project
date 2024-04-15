# This script retrieves the IDs of the ten most recent posts 
# in the "business" topic from a SQLAlchemy-managed database and prints them

from database import Base, SessionLocal
from sqlalchemy import Column, Integer, String

class Post(Base):
    __tablename__ = "post"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key = True)
    text = Column(String)
    topic = Column(String)


if __name__ == "__main__":
    session = SessionLocal()
    posts = (
        session.query(Post)
        .filter(Post.topic == "business")
        .order_by(Post.id.desc()).
        limit(10)
        .all()
    )

    post_list = [post.id for post in posts]
    print(post_list)