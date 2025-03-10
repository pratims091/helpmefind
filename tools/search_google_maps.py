"""Module for searching Google Maps."""

import json
import os
from typing import Any, Dict, List

import requests
from diskcache import Cache
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

cache = Cache("cache")


def api_request(
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

    response = requests.request(
        method,
        url=f"{os.environ.get('GOOGLE_PLACES_BASE_URL')}{endpoint}",
        headers=headers,
        json=body,
        params=params,
    )

    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        print(f"Response: {response.text}")
        response.raise_for_status()

    return response.json()


def fetch_images_for_place(place_id: str) -> List[str]:
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
            photo = api_request(endpoint=f"{photo_reference}/media", method="GET", params=params)
            images.append(photo["photoUri"])

        with open("mock_data/places_images.json", "w") as f:
            json.dump(list(set(images)), f, indent=4)

    return list(set(images))


def inject_images_to_places(content: str) -> str:
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
                    images = fetch_images_for_place(place_id)
                    place["images"] = images

        return json.dumps(data)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error processing JSON: {e}")
        print(f"Content was: {content}")
        # Return original content if parsing fails
        return content


@tool
def search_google_maps(search: str) -> List[Dict[str, Any]]:
    """Search for places on Google Maps based on a query and location."""
    query, location = search.split("|")
    lat, long = location.split(",")

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
                "center": {"latitude": float(lat), "longitude": float(long)},
                "radius": 500,
            }
        },
        "rankPreference": "RELEVANCE",
        "minRating": 3,
    }
    result = api_request(
        endpoint="places:searchText",
        method="POST",
        body=payload,
        response_keys="places.id,places.formattedAddress,places.location,places.rating,places.reviews,places.photos,places.displayName,places.userRatingCount",  # noqa: E501
    )
    for place in result["places"]:
        place_id = place["id"]
        reviews = list(set([review["text"]["text"] for review in place["reviews"]]))

        photos = list(set([photo["name"] for photo in place["photos"]]))
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
