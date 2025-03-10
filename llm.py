"""Module for getting the LLM."""

import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

load_dotenv()


def get_llm():
    """Get the LLM to use."""
    llm_to_use = os.getenv("LLM_TO_USE", "google")
    model = os.getenv("LLM_MODEL", "gemini-2.0-flash")

    match llm_to_use:
        case "google":
            return ChatGoogleGenerativeAI(model=model, temperature=0)
        case "groq":
            return ChatGroq(model=model, temperature=0)
        case "ollama":
            return ChatOllama(model=model, temperature=0)
        case _:
            raise ValueError(f"Unsupported LLM_TO_USE value: {llm_to_use}")
    return ChatGoogleGenerativeAI(temperature=0, model=model)
