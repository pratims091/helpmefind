"""Agent for searching place details."""

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool

from llm import get_llm
from tools.search_google_maps import search_google_maps

load_dotenv()


def search(query: str, location: str) -> str:
    """Search places based on a query and location."""
    template = """
        You are a location search specialist focused on providing comprehensive structured data.

        When given a location: {loc} and query: {q}, your goal is to use the right tool to find matching places.

        Return ALL available results with COMPLETE data including:
        - name
        - place_id
        - address
        - rating
        - reviews
        - rating_count
    """  # noqa: E501
    llm = get_llm()
    prompt_template = PromptTemplate(template=template, input_variables=["q", "loc"])

    tools_for_agent = [
        Tool(
            name="Searches for places on Google Maps based on a query and location.",
            func=search_google_maps,
            description="Useful when you want to find places based on a query and location. "
            "Input should be in format: 'search query | location'",
        )
    ]

    react_prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm, tools=tools_for_agent, prompt=react_prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools_for_agent,
        handle_parsing_errors=True,
        verbose=True,
    )

    result = agent_executor.invoke(
        input={"input": prompt_template.format_prompt(q=query, loc=location)}
    )

    return result["output"]
