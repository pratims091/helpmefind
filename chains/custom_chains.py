"""Custom chains for place summarization."""

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableSequence

from llm import get_llm
from output_parsers import places_parser
from tools.search_google_maps import inject_images_to_places

load_dotenv()


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
    chain = chain | RunnableLambda(inject_images_to_places)
    chain = chain | places_parser
    return chain
