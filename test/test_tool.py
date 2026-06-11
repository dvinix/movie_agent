# test_tool.py
import os
from dotenv import load_dotenv
load_dotenv()

from tools import search_movies

# Simulate exactly how LangChain calls your tool
result = search_movies.invoke({
    "genre": "horror",
    "year_from": 1990,
    "year_to": 1999,
    "certification": "R",
    "min_rating": 0.0,
    "keyword": ""
})

print(result)