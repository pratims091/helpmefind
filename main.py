"""Main module for the helpmefind app."""

from pprint import pprint

from dotenv import load_dotenv

from agents.places_search import search
from chains.custom_chains import get_summarized_review_chain
from output_parsers import Places

load_dotenv()


def helpmefind(query: str, location: str) -> Places:
    """Find places based on a query and location."""
    places = search(query=query, location=location)
    summarized_reviews = get_summarized_review_chain()

    res: Places = summarized_reviews.invoke(input={"information": places})

    return res


if __name__ == "__main__":
    res = helpmefind(query="coffee", location="37.7749,-122.4194")
    pprint(res)
