import pandas as pd
import numpy as np
import pickle
from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df1 = pd.read_csv("tmdb_5000_credits.csv")
df2 = pd.read_csv("tmdb_5000_movies.csv")

df1.columns = ["id","title","cast","crew"]
df2 = df2.merge(df1 , on="id")

# Parse json-like strings
features = ['cast', 'crew', 'keywords', 'genres']
for f in features:
    df2[f] = df2[f].apply(literal_eval)

def get_director(x):
    for i in x:
        if i.get('job') == 'Director':
            return i.get('name')
    return np.nan

df2['director'] = df2['crew'].apply(get_director)

def get_list(x):
    if isinstance(x, list):
        return [i.get('name', '') for i in x]
    return []

for f in ['cast', 'keywords', 'genres']:
    df2[f] = df2[f].apply(get_list)

def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    if isinstance(x, str):
        return str.lower(x.replace(" ", ""))
    return ""

for f in ['cast', 'keywords', 'director', 'genres']:
    df2[f] = df2[f].apply(clean_data)

def create_soup(x):
    return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + x['director'] + ' ' + ' '.join(x['genres'])

df2['soup'] = df2.apply(create_soup, axis=1)

# Similarity
count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(df2['soup'])
cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

# Reset index + indices
df2 = df2.reset_index(drop=True)
indices = pd.Series(df2.index, index=df2['original_title']).drop_duplicates()

# Save artifacts
pickle.dump(df2, open("movies_df.pkl", "wb"))
pickle.dump(cosine_sim2, open("cosine_sim.pkl", "wb"))
pickle.dump(indices, open("indices.pkl", "wb"))

print("✅ Saved: movies_df.pkl, cosine_sim.pkl, indices.pkl")
