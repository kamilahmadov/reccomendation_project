from fastapi import FastAPI, HTTPException
from typing import List
from datetime import datetime
import pandas as pd
from pydantic import BaseModel
import os
import pickle
from sqlalchemy import create_engine
from dotenv import load_dotenv

def get_model_path(path: str) -> str:
    if os.environ.get("IS_LMS") == "1":  # проверяем где выполняется код в лмс, или локально
        MODEL_PATH = '/workdir/user_input/model'
    else:
        MODEL_PATH = path
    return MODEL_PATH


def load_models():
    model_path = get_model_path("model_dl.pkl")
    model = pickle.load(open(model_path, 'rb'))
    return model


def batch_load_sql(query: str) -> pd.DataFrame:
    CHUNKSIZE = 200000
    engine = create_engine(
        os.environ.get('POSTGRES_CONNECTION')
    )
    conn = engine.connect().execution_options(stream_results=True)
    chunks = []
    for chunk_dataframe in pd.read_sql(query, conn, chunksize=CHUNKSIZE):
        chunks.append(chunk_dataframe)
    conn.close()
    return pd.concat(chunks, ignore_index=True)
 

def load_features() -> pd.DataFrame:
    return batch_load_sql(os.environ.get('POSTGRES_USER_DOWNLOAD'))


def load_features_post() -> pd.DataFrame:
    return batch_load_sql(os.environ.get('POSTGRES_POST_DOWNLOAD'))


def table_post() -> pd.DataFrame:
    return batch_load_sql(os.environ.get('POSTGRES_POST'))


loaded_model = load_models()
df_user_data = load_features()
df_post_mod = load_features_post()
df_post_all = table_post()


features = ['day_of_week', 'hour', 'gender', 'age', 'exp_group', 'os', 'source',
       'country_Azerbaijan', 'country_Belarus', 'country_Cyprus',
       'country_Estonia', 'country_Finland', 'country_Kazakhstan',
       'country_Latvia', 'country_Russia', 'country_Switzerland',
       'country_Turkey', 'country_Ukraine', 'pca_embeddings', 'topic_covid',
       'topic_entertainment', 'topic_movie', 'topic_politics', 'topic_sport',
       'topic_tech']


app = FastAPI()

class PostGet(BaseModel):
    id: int
    text: str
    topic: str

    class Config:
        orm_mode = True

# Getting top 5 recomendations for user based on user_id

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