# These Pydantic models define structures for fetching user,
# post, and feed data with associated details and timestamps.

from pydantic import BaseModel
import datetime

class UserGet(BaseModel):
    id: int
    gender: int
    age: int
    country: str
    city: str
    exp_group: int
    os: str
    source: str
    
    class Config:
        from_attributes = True

class PostGet(BaseModel):
    id: int
    text: str
    topic: str

    class Config:
        from_attributes = True

class FeedGet(BaseModel):
    user_id: int
    post_id: int
    user: UserGet
    post: PostGet
    action: str
    time: datetime.datetime

    class Config:
        from_attributes = True