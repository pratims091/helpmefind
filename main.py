"""Main module for the helpmefind app."""

import asyncio
from pprint import pprint

from dotenv import load_dotenv

from agents.places_search import search
from chains.custom_chains import get_summarized_review_chain_async
from output_parsers import Places

load_dotenv()


async def helpmefind(query: str, location: str) -> Places:
    """Find places based on a query and location."""
    places = await search(query=query, location=location)
    summarized_reviews = await get_summarized_review_chain_async(
        {"information": places}
    )

    res: Places = summarized_reviews

    return res


if __name__ == "__main__":
    res = asyncio.run(helpmefind(query="coffee", location="37.7749,-122.4194"))
    pprint(res)
