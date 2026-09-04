from langchain.tools import tool
import requests 
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from rich import print

load_dotenv()

_key = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key=_key) if _key else None

#RESULTS DEPTH
_DEPTH_RESULTS = {"quick": 3, "standard": 5, "deep": 7}
_max_results = 5  # default

#SOURCE CITATION
_last_sources = []


#ACCEPT API KEYS
def init_tavily(tavily_api_key: str | None = None, depth: str = "standard"):
    global tavily, _max_results
    key = tavily_api_key or os.getenv("TAVILY_API_KEY")
    if not key:
        raise ValueError("Tavily API key required. Set TAVILY_API_KEY in .env or pass it explicitly.")
    tavily = TavilyClient(api_key=key)
    _max_results = _DEPTH_RESULTS.get(depth, 5)


@tool
def web_search(query: str) -> str:
    """Search the web for relevant information on a topic. Returns Titles, URLs and snippets."""
    global _last_sources
    results = tavily.search(query=query, max_results=_max_results)
    
    _last_sources = [{"title": r["title"], "url": r["url"]} for r in results.get("results", [])]
    
    out = []
    for i, r in enumerate(results.get("results", []), start=1):
        out.append(
            f"[{i}] Title: {r['title']}\n    URL: {r['url']}\n    Snippet: {r['content'][:300]}\n"
        )
    
    return "\n---\n".join(out)


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout = 10, headers = {"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.content, "html.parser")
        for tag in soup (["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator="", strip = True) [:3000]
    except Exception as e:
        return f"Could not scrape the URL: {str(e)}"

def get_sources() -> list[dict]:
    """Returns the list of sources found during the last search."""
    return _last_sources
