# test_genre.py
import os, requests
from dotenv import load_dotenv
load_dotenv()

TMDB_KEY = os.getenv("TMDB_API_KEY")

r = requests.get(
    "https://api.themoviedb.org/3/genre/movie/list",
    params={"api_key": TMDB_KEY, "language": "en-US"}
)
for g in r.json()["genres"]:
    print(g["id"], g["name"])