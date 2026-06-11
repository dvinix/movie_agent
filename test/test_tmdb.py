# test_tmdb.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
TMDB_KEY = os.getenv("TMDB_API_KEY")

# Test 1: Raw API call with filters
params = {
    "api_key": TMDB_KEY,
    "with_genres": 27,  # Horror genre ID (hardcoded to bypass genre map)
    "primary_release_date.gte": "1990-01-01",
    "primary_release_date.lte": "1999-12-31",
    "sort_by": "vote_average.desc",
    "vote_count.gte": 100,
}

resp = requests.get("https://api.themoviedb.org/3/discover/movie", params=params)
data = resp.json()

print("Status code:", resp.status_code)
print("Total results:", data.get("total_results"))
print("\nFirst 3 movies:")
for m in data.get("results", [])[:3]:
    print(f"  - {m['title']} ({m.get('release_date','?')[:4]})")