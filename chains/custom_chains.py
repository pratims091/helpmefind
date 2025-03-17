"""Custom chains for place summarization."""

import asyncio

import nest_asyncio
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableSequence

from llm import get_llm
from output_parsers import places_parser
from tools.search_google_maps import inject_images_to_places

load_dotenv()
nest_asyncio.apply()


def extract_content(output):
    """Extract content from AIMessage."""
    if isinstance(output, AIMessage):
        return output.content
    return output


def get_summarized_review_chain() -> RunnableSequence:
    """Get summarized review chain."""
    llm = get_llm()

    template = """
        You will be given information about several places

        Information: {information}

        For each place, generate a summary that includes:
        1. Overall sentiment (positive, negative, or mixed)
        2. Top 3 positive aspects mentioned by reviewers
        3. Top 3 negative aspects or concerns (if any)
        4. Standout features or unique selling points
        5. A one-sentence overall assessment
        Make sure these points are separated with a html break tag, so that they come in new lines
        \n{format_instructions}
    """

    prompt_template = PromptTemplate(
        input_variables=["information"],
        template=template,
        partial_variables={"format_instructions": places_parser.get_format_instructions()},
    )

    chain = prompt_template | llm
    chain = chain | RunnableLambda(extract_content)

    # Create a synchronous wrapper for inject_images_to_places
    def inject_images_sync(content):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(inject_images_to_places(content))

    chain = chain | RunnableLambda(inject_images_sync)
    chain = chain | places_parser
    return chain


async def call_llm(prompt):
    llm = get_llm()
    return llm.invoke(prompt)


async def get_summarized_review_chain_async(input_data):
    """Get summarized review chain."""
    template = """
        You will be given information about several places

        Information: {information}

        For each place, generate a summary that includes:
        1. Overall sentiment (positive, negative, or mixed)
        2. Top 3 positive aspects mentioned by reviewers
        3. Top 3 negative aspects or concerns (if any)
        4. Standout features or unique selling points
        5. A one-sentence overall assessment
        Make sure these points are separated with a html break tag, so that they come in new lines
        \n{format_instructions}
    """

    prompt_template = PromptTemplate(
        input_variables=["information"],
        template=template,
        partial_variables={"format_instructions": places_parser.get_format_instructions()},
    )

    prompt = prompt_template.format(information=input_data["information"])
    output = await call_llm(prompt)
    content = extract_content(output)
    injected_images = await inject_images_to_places(content)
    parsed_places = places_parser.parse(injected_images)
    return parsed_places
