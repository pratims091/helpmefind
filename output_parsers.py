"""Module for parsing the output of the LLM."""

from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class Place(BaseModel):
    """A place with name, address, rating, and other details."""

    name: str = Field(description="The name of the place.")
    address: str = Field(description="The address of the place.")
    rating: float = Field(description="The rating of the place.")
    place_id: str = Field(description="The Google Maps place ID.")
    reviewSummary: str = Field(description="A summary of the reviews for the place.")
    images: List[str] = Field(description="A list of unique image URLs associated with the place.")
    ratingCount: int = Field(description="User review count.")


class Places(BaseModel):
    """A list of places."""

    places: List[Place] = Field(description="A list of places.")

    def dump(self) -> str:
        """Dump the model to a string."""
        return self.model_dump()


places_parser = PydanticOutputParser(pydantic_object=Places)
