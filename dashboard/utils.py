import pandas as pd
from tqdm import tqdm
from datetime import datetime
tqdm.pandas()

def is_related(row):
    return row['id'] in conversation_ids or any(p in row['text'].lower() for p in ['consejo', 'concejo', 'concejal'])

df = pd.read_csv('../data/search/JDOviedoAr_sentiment.csv')
df["date"] = pd.to_datetime(df["created_at"]).dt.date

conversation_ids = []
with open('../data/search/tweets_ids_video_oviedo.txt', 'r') as f:
    for line in f:
        if line.strip().isnumeric():
            conversation_ids.append(int(line.strip()))

df['related'] = df.apply(lambda row: is_related(row), axis=1)