import datetime
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import List
from sqlalchemy import func

from table_user import User
from table_post import Post
from table_feed import Feed 
from schema import UserGet, PostGet, FeedGet
from connenction import loaded_model, df_user_data, df_post_mod, df_post_all, features

app = FastAPI()

def get_db():
    with SessionLocal() as db:
        return db

@app.get("/user/{id}", response_model=UserGet)
def get_user(id: int, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(User.id == id)
        .first()
    )
    if user is None:
        raise HTTPException(404, "No user with such id")
    else:
        return user
    

@app.get("/post/{id}", response_model=PostGet)
def get_post(id: int, db:Session = Depends(get_db)):
    post = (
        db.query(Post)
        .filter(Post.id == id)
        .first()
    )
    if post is None:
        raise HTTPException(404, "No post with such id")
    else:
        return post
    

@app.get("/user/{id}/feed", response_model=List[FeedGet])
def get_feed_user(id: int, limit: int = 10, db:Session = Depends(get_db)):
    actions = (
        db.query(Feed)
        .filter(Feed.user_id == id)
        .order_by(Feed.time.desc())
        .limit(limit)
        .all()
    )
    return actions


@app.get("/post/{id}/feed", response_model=List[FeedGet])
def get_feed_post(id: int, limit: int = 10, db:Session = Depends(get_db)):
    actions = (
        db.query(Feed)
        .filter(Feed.post_id == id)
        .order_by(Feed.time.desc())
        .limit(limit)
        .all()
    )
    return actions


@app.get("/post/recommendations/", response_model=List[PostGet])
def get_recommended_feed(limit: int = 10, db: Session = Depends(get_db)):
    rec_posts = (
    db.query(Post.id, Post.text, Post.topic, func.count(Feed.post_id).label("like_count"))
    .filter(Feed.action == "like")
    .join(Feed, Post.id == Feed.post_id)
    .group_by(Post.id)
    .order_by(func.count(Post.id).desc())
    .limit(limit)
    .all()
    )
    return rec_posts


@app.get("/post/recommendations/", response_model=List[PostGet])
def recommended_posts(id: int, time: datetime, limit: int = 5) -> List[PostGet]:
    user_table = df_user_data[df_user_data['user_id'] == id].reset_index(drop=True)
    
    user_table['timestamp'] = time
    user_table['day_of_week'] = user_table['timestamp'].dt.dayofweek
    user_table['hour'] = user_table['timestamp'].dt.hour
    user_table = user_table.drop('timestamp', axis=1)
    
    X = pd.merge(user_table, df_post_mod, how='cross', suffixes=('_user', '_post'))
    
    post_id = pd.concat([X['post_id'], pd.DataFrame(loaded_model.predict_proba(X[features]).T[1],
                                                     columns=['prediction'])], axis=1).sort_values(by=['prediction'], 
                                                                                                   ascending=False).head(limit)['post_id'].values

    result_table = df_post_all[df_post_all['post_id'].isin(post_id)].reset_index(drop=True)
    

    result = []
    for i in range(5):
        result.append(PostGet(id=result_table['post_id'].iloc[i],
                              text=result_table['text'].iloc[i],
                              topic=result_table['topic'].iloc[i]))

    if not result:
        raise HTTPException(404, "posts not found")
    return result