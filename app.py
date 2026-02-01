from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Fixes "CORSMiddleware not defined"
from pydantic import BaseModel
import pickle
import pandas as pd  # Fixes "NameError: name 'pd' or 'movies_df' logic"
from rapidfuzz import process, fuzz

app = FastAPI(title="Movie Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

movies_df = pickle.load(open("movies_df.pkl", "rb"))
cosine_sim = pickle.load(open("cosine_sim.pkl", "rb"))
indices = pickle.load(open("indices.pkl", "rb"))

# Keep list of titles for fuzzy search
all_titles = movies_df["original_title"].dropna().tolist()

@app.get("/")
def home():
    return {"message": "Movie Recommender API running 😄"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ✅ Fuzzy search endpoint
@app.get("/search")
def search_movies(query: str, limit: int = 10):
    query = query.strip()
    if not query:
        return {"results": []}

    matches = process.extract(
        query,
        all_titles,
        scorer=fuzz.WRatio,
        limit=limit
    )

    # return as clean json
    results = [{"title": title, "score": score} for title, score, _ in matches]
    return {"query": query, "results": results}


class RecommendRequest(BaseModel):
    title: str
    top_k: int = 10
    min_rating: float = 6.5
    min_votes: int = 200


@app.post("/recommend")
def recommend(req: RecommendRequest):
    title = req.title.strip()

    # ✅ if exact title not found -> fuzzy match
    if title not in indices:
        best = process.extractOne(title, all_titles, scorer=fuzz.WRatio)
        if not best:
            return {"error": "Movie not found"}

        best_title, score, _ = best

        # If similarity is too low, don't auto-correct
        if score < 70:
            return {
                "error": "Movie not found",
                "hint": "Try using /search endpoint",
                "best_guess": best_title,
                "match_score": score
            }

        title = best_title  # auto-correct

    idx = indices[title]

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    recs = []
    for i, score in sim_scores[1:]:
        row = movies_df.iloc[i]

        # ✅ top-rated filter
        rating = row.get("vote_average", 0) if row.get("vote_average") else 0
        votes = row.get("vote_count", 0) if row.get("vote_count") else 0

        if rating >= req.min_rating and votes >= req.min_votes:
            recs.append({
                "title": row["original_title"],
                "rating": float(rating),
                "votes": int(votes),
                "similarity": float(score)
            })

        if len(recs) >= req.top_k:
            break

    return {
        "input": req.title,
        "resolved_title": title,
        "filters": {
            "min_rating": req.min_rating,
            "min_votes": req.min_votes
        },
        "recommendations": recs
    }

class FilterRequest(BaseModel):
    runtime: int | None = None
    director: str | None = None
    cast: str | None = None
    language: str | None = None
    genre: str | None = None
    limit: int = 10


@app.post("/filter")
def filter_movies(req: FilterRequest):
    df = movies_df.copy()

    # runtime filter: +- 10 minutes
    if req.runtime is not None:
        min_rt, max_rt = req.runtime - 10, req.runtime + 10
        df = df[(df["runtime"] >= min_rt) & (df["runtime"] <= max_rt)]

    # director filter (stored cleaned: lowercase and no spaces)
    if req.director:
        d = req.director.lower().replace(" ", "")
        df = df[df["director"] == d]

    # cast filter (cast column is list of cleaned names)
    if req.cast:
        c = req.cast.lower().replace(" ", "")
        df = df[df["cast"].apply(lambda x: any(c in str(name).lower().replace(" ", "") for name in x) if isinstance(x, list) else False)]

    # Change this for Genre:
    if req.genre:
        g = req.genre.lower().replace(" ", "")
        df = df[df["genres"].apply(lambda x: any(g in str(genre).lower().replace(" ", "") for genre in x) if isinstance(x, list) else False)]

    # original_language filter
    if req.language:
        lang = req.language.lower().strip()
        df = df[df["original_language"].astype(str).str.lower() == lang]

    results = df[["original_title", "vote_average", "vote_count", "runtime"]].head(req.limit).to_dict(orient="records")

    return {
        "filters_applied": {
            "runtime": req.runtime,
            "director": req.director,
            "cast": req.cast,
            "language": req.language,
            "genre": req.genre
        },
        "count": len(results),
        "results": results
    }
