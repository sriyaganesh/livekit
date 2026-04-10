import os
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

SERP_API_KEY = os.getenv("SERP_API_KEY")


def search_web(query):
    params = {
        "q": query,
        "api_key": SERP_API_KEY,
        "engine": "google"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    output = []

    for r in results.get("organic_results", [])[:5]:
        output.append({
            "title": r.get("title"),
            "link": r.get("link"),
            "snippet": r.get("snippet")
        })

    return output