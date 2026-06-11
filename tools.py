import os
import requests
from dotenv import load_dotenv
from langchain.tools import tool

# Load .env before reading any env vars
load_dotenv()

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_KEY = os.getenv("TMDB_API_KEY")

_GENRE_MAP = {}

def _get_genre_map():
    global _GENRE_MAP
    if not _GENRE_MAP:
        r = requests.get(
            f"{TMDB_BASE}/genre/movie/list",
            params={"api_key": TMDB_KEY, "language": "en-US"}
        )
        _GENRE_MAP = {g["name"].lower(): g["id"] for g in r.json().get("genres", [])}
    return _GENRE_MAP


@tool
def search_movies(query: str) -> str:
    """
    Search TMDB for movies. Input must be a JSON string with these optional fields:
    - genre (str): e.g. 'horror', 'science fiction', 'action', 'comedy', 'thriller'
    - year_from (int): start year e.g. 1990
    - year_to (int): end year e.g. 1999
    - min_rating (float): minimum rating e.g. 7.0
    - keyword (str): extra keyword e.g. 'vampire', 'space', 'robot'

    NOTE: Do NOT include certification in the JSON — it is not supported.
    Mention certification preference in Final Answer instead.

    Example input: {"genre": "horror", "year_from": 1990, "year_to": 1999, "min_rating": 7.0}
    """
    import json

    try:
        params_input = query if isinstance(query, dict) else json.loads(query)
    except (json.JSONDecodeError, TypeError):
        return "Invalid input. Please provide a valid JSON string."

    genre      = params_input.get("genre", "")
    year_from  = params_input.get("year_from")
    year_to    = params_input.get("year_to")
    min_rating = params_input.get("min_rating", 0.0)
    keyword    = params_input.get("keyword", "")

    # Hardcoded genre map — no API call needed
    GENRE_MAP = {
        "action": 28, "adventure": 12, "animation": 16, "comedy": 35,
        "crime": 80, "documentary": 99, "drama": 18, "family": 10751,
        "fantasy": 14, "history": 36, "horror": 27, "music": 10402,
        "mystery": 9648, "romance": 10749, "science fiction": 878,
        "sci-fi": 878, "scifi": 878, "thriller": 53, "war": 10752, "western": 37,
    }

    params = {
        "api_key": TMDB_KEY,
        "language": "en-US",
        "sort_by": "vote_average.desc",
        "vote_count.gte": 200,
        "page": 1,
        "include_adult": False,
    }

    if genre:
        genre_id = GENRE_MAP.get(genre.lower().strip())
        if genre_id:
            params["with_genres"] = genre_id

    if year_from:
        params["primary_release_date.gte"] = f"{year_from}-01-01"
    if year_to:
        params["primary_release_date.lte"] = f"{year_to}-12-31"

    if min_rating and float(min_rating) > 0:
        params["vote_average.gte"] = float(min_rating)

    if keyword:
        kw_resp = requests.get(
            f"{TMDB_BASE}/search/keyword",
            params={"api_key": TMDB_KEY, "query": keyword}
        )
        kw_results = kw_resp.json().get("results", [])
        if kw_results:
            params["with_keywords"] = kw_results[0]["id"]

    resp = requests.get(f"{TMDB_BASE}/discover/movie", params=params)
    data = resp.json()

    # Surface API errors clearly instead of silently returning empty
    if "status_message" in data:
        return f"TMDB API error: {data['status_message']} (code {data.get('status_code')})"

    movies = data.get("results", [])

    if not movies:
        return "No movies found. Try removing min_rating or widening the year range."

    out = []
    for m in movies[:5]:
        title   = m.get("title", "Unknown")
        year    = m.get("release_date", "????")[:4]
        rating  = m.get("vote_average", "N/A")
        overview = m.get("overview", "")[:200]
        out.append(f"🎬 {title} ({year}) | ⭐ {rating}/10\n   {overview}")

    return "\n\n".join(out)


@tool
def search_movie_by_title(query: str) -> str:
    """
    Search for a specific movie by its title.
    Input is a JSON string with field:
    - title (str): the movie name to search e.g. 'Obsession' or 'The Matrix'

    Example input: {"title": "Obsession"}
    """
    import json

    try:
        if isinstance(query, dict):
            data = query
        else:
            data = json.loads(query)
        title = data.get("title", query)
    except (json.JSONDecodeError, TypeError):
        title = query  # fallback: treat raw string as title

    resp = requests.get(
        f"{TMDB_BASE}/search/movie",
        params={"api_key": TMDB_KEY, "query": title, "language": "en-US"}
    )
    results = resp.json().get("results", [])

    if not results:
        return f"No movies found with title '{title}'."

    out = []
    for m in results[:5]:
        t       = m.get("title", "Unknown")
        year    = m.get("release_date", "????")[:4]
        rating  = m.get("vote_average", "N/A")
        overview = m.get("overview", "")[:200]
        out.append(f"🎬 {t} ({year}) | ⭐ {rating}/10\n   {overview}")

    return "\n\n".join(out)


@tool
def get_streaming_availability(query: str) -> str:
    """
    Check streaming platforms for a movie.
    Input is a JSON string with fields:
    - title (str): movie title e.g. 'Inception'
    - region (str): country code e.g. 'IN', 'US', 'GB' (default: 'IN')

    Example input: {"title": "Inception", "region": "IN"}
    """
    import json

    try:
        if isinstance(query, dict):
            data = query
        else:
            data = json.loads(query)
        title  = data.get("title", "")
        region = data.get("region", "IN")
    except (json.JSONDecodeError, TypeError):
        return "Invalid input. Provide JSON with 'title' and optional 'region'."

    search = requests.get(
        f"{TMDB_BASE}/search/movie",
        params={"api_key": TMDB_KEY, "query": title}
    )
    results = search.json().get("results", [])
    if not results:
        return f"Could not find '{title}' on TMDB."

    movie_id     = results[0]["id"]
    actual_title = results[0]["title"]

    providers = requests.get(
        f"{TMDB_BASE}/movie/{movie_id}/watch/providers",
        params={"api_key": TMDB_KEY}
    ).json().get("results", {}).get(region, {})

    if not providers:
        return f"No streaming data for '{actual_title}' in region {region}."

    out = [f"📺 '{actual_title}' streaming in {region}:"]
    for category, provider_list in providers.items():
        if category == "link":
            continue
        names = [p["provider_name"] for p in provider_list]
        out.append(f"  {category.capitalize()}: {', '.join(names)}")

    return "\n".join(out)