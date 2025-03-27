"""Module for searching Google Maps."""

import asyncio
import json
import os
from typing import Any, Dict, List

import aiohttp
from diskcache import Cache
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

cache = Cache("cache")


async def api_request(
    endpoint: str,
    method: str,
    body: Dict[str, Any] = None,
    params: Dict[str, Any] = None,
    response_keys: str = "*",
) -> Dict[str, Any]:
    """Make a request to the Google Places API."""
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.environ.get("GOOGLE_PLACES_API_KEY"),
        "X-Goog-FieldMask": response_keys,
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.request(
            method,
            url=f"{os.environ.get('GOOGLE_PLACES_BASE_URL')}{endpoint}",
            json=body,
            params=params,
        ) as response:
            if response.status != 200:
                print(f"Error: Received status code {response.status}")
                print(f"Response: {await response.text()}")
                response.raise_for_status()

            return await response.json()


async def fetch_images_for_place(place_id: str) -> List[str]:
    """Fetch images for a place using its place_id."""
    mock = os.environ.get("MOCK_API_REQUESTS", "True").lower() in ("true", "1", "t")

    images = []

    if mock:
        with open("mock_data/places_images.json", "r") as f:
            results = json.loads(f.read())
            return results
    else:
        params = {"maxWidthPx": 600, "maxHeightPx": 600, "skipHttpRedirect": "true"}
        photo_references = cache.get(f"photos_{place_id}", [])

        for photo_reference in photo_references:
            photo = await api_request(
                endpoint=f"{photo_reference}/media", method="GET", params=params
            )
            images.append(photo["photoUri"])

        with open("mock_data/places_images.json", "w") as f:
            json.dump(list(set(images)), f, indent=4)

    return list(set(images))


async def inject_images_to_places(content: str) -> str:
    """Middleware function to inject images."""
    try:
        # If content is already a dict, use it directly
        if isinstance(content, dict):
            data = content
        else:
            # Remove markdown code blocks if present
            clean_content = content
            if "```json" in content:
                clean_content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                clean_content = content.split("```")[1].split("```")[0].strip()

            data = json.loads(clean_content)

        # Process each place
        if "places" in data:
            for place in data["places"]:
                if "place_id" in place:
                    place_id = place["place_id"]
                    # Fetch images for this place
                    images = await fetch_images_for_place(place_id)
                    place["images"] = images

        return json.dumps(data)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error processing JSON: {e}")
        print(f"Content was: {content}")
        # Return original content if parsing fails
        return content


async def _search_google_maps_async(search: str) -> List[Dict[str, Any]]:
    """Search for places on Google Maps based on a query and location."""
    # Handle different input formats
    if "|" in search:
        # Format: "search query | location"
        query, location = search.split("|", 1)
    else:
        # Try to extract query and location from the input
        print(f"Warning: Input format not as expected. Input: {search}")
        # Default to empty query and location if we can't parse
        query, location = "", ""

    # Clean up query and location
    query = query.strip()
    location = location.strip()

    # Split location into lat and lng if it contains a comma
    if "," in location:
        try:
            lat, lng = location.split(",", 1)
            lat = lat.strip()
            lng = lng.strip()
        except ValueError:
            print(
                f"Error: Could not split location into lat and lng. Location: {location}"
            )
            raise ValueError(f"Invalid location format: {location}")
    else:
        print(f"Error: Location does not contain a comma. Location: {location}")
        raise ValueError(f"Invalid location format: {location}")

    mock = os.environ.get("MOCK_API_REQUESTS", "True").lower() in ("true", "1", "t")

    if mock:
        with open("mock_data/places.json", "r") as f:
            return json.loads(f.read())[:5]

    places = []
    payload = {
        "textQuery": query,
        "pageSize": 10,
        "locationBias": {
            "circle": {
                "center": {"latitude": float(lat), "longitude": float(lng)},
                "radius": 500,
            }
        },
        "rankPreference": "RELEVANCE",
        "minRating": 3,
    }
    result = await api_request(
        endpoint="places:searchText",
        method="POST",
        body=payload,
        response_keys="places.id,places.formattedAddress,places.location,places.rating,places.reviews,places.photos,places.displayName,places.userRatingCount",  # noqa: E501
    )
    for place in result["places"]:
        place_id = place["id"]
        reviews = list(
            set(
                [
                    review.get("text", {}).get("text", "")
                    for review in place["reviews"]
                    if "text" in review
                ]
            )
        )

        photos = list(set([photo.get("name", "") for photo in place.get("photos", [])]))
        cache[f"photos_{place_id}"] = photos

        if reviews:
            place = {
                "name": place["displayName"]["text"],
                "place_id": place_id,
                "address": place["formattedAddress"],
                "rating": place["rating"],
                "reviews": reviews,
                "rating_count": place["userRatingCount"],
            }
            places.append(place)
    places.sort(key=lambda x: x["rating"], reverse=True)

    with open("mock_data/places.json", "w") as f:
        json.dump(places, f, indent=4)

    return places


@tool
def search_google_maps(search: str) -> List[Dict[str, Any]]:
    """Search for places on Google Maps based on a query and location."""
    import nest_asyncio

    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_search_google_maps_async(search))
