# This script queries and prints the countries and operating systems of users in experimental group 3, 
# grouping them by country and OS, filtering those with counts greater than 100,
# and ordering them by count in descending order.

from database import Base, SessionLocal
from sqlalchemy import Column, Integer, String, func

class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True)
    gender = Column(Integer)
    age = Column(Integer)
    country = Column(String) 
    city = Column(String) 
    exp_group = Column(Integer)
    os = Column(String)
    source = Column(String)


if __name__ == "__main__":
    session = SessionLocal()
    users = (
        session.query(User.country, User.os, func.count().label('count'))
        .filter(User.exp_group == 3)
        .group_by(User.country, User.os)
        .having(func.count() > 100)
        .order_by(func.count().desc())
        .all()
    )

    result = [(user.country, user.os, user.count) for user in users]
    print(result)