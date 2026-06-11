# test_filters.py
import os, requests
from dotenv import load_dotenv
load_dotenv()

TMDB_KEY = os.getenv("TMDB_API_KEY")

# Test 1: sci-fi 2000s NO certification
r = requests.get("https://api.themoviedb.org/3/discover/movie", params={
    "api_key": TMDB_KEY,
    "with_genres": 878,
    "primary_release_date.gte": "2000-01-01",
    "primary_release_date.lte": "2009-12-31",
    "vote_count.gte": 200,
    "sort_by": "vote_average.desc",
})
print("Sci-fi 2000s (no cert):", r.json().get("total_results"))

# Test 2: WITH certification
r2 = requests.get("https://api.themoviedb.org/3/discover/movie", params={
    "api_key": TMDB_KEY,
    "with_genres": 878,
    "primary_release_date.gte": "2000-01-01",
    "primary_release_date.lte": "2009-12-31",
    "vote_count.gte": 200,
    "sort_by": "vote_average.desc",
    "certification_country": "US",
    "certification": "PG-13",
    "certification.lte": "PG-13",
})
print("Sci-fi 2000s (PG-13):", r2.json().get("total_results"))