from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from .script_tools import *
from pydantic import BaseModel
from typing import List, Literal, Optional
import os
from dotenv import load_dotenv
from pathlib import Path

# This will work regardless of where the script is run from
env_path = Path(__file__).parent.parent / "configs" / ".env"
load_dotenv(dotenv_path=env_path)


class BeachFacilities(BaseModel):
    umbrella: Literal["Paid", "Free", "Not Exists", "No Info"]
    sunbed: Literal["Paid", "Free", "Not Exists", "No Info"]
    beach_towel: Literal["Paid", "Free", "Not Exists", "No Info"]
    shower: Literal["Paid", "Free", "Not Exists", "No Info"]
    food: Literal["Paid", "Free", "Not Exists", "No Info"]
    pavilion: Literal["Paid", "Free", "Not Exists", "No Info"]
    shuttle: Literal["Paid", "Free", "Not Exists", "No Info"]
    shuttle_info: Optional[str] = None


class AgentResponse(BaseModel):
    distance_to_beach: int
    private_beach: Literal["Exists", "Not Exists"]
    public_beach: Literal["Exists", "Not Exists"]
    beach_length: int
    beach_types: List[Literal["Sand", "Gravel", "Platform"]]
    sea_types: List[Literal["Sand", "Gravel"]]
    beach_facilities: BeachFacilities


llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

parser = PydanticOutputParser(pydantic_object=AgentResponse)


config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "prompt_config.json")
config_path = os.path.abspath(config_path)
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)


system_prompt = config["beachsea"]

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("user", "{text}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt_template,
    tools=[],
)

agent_executor = AgentExecutor(agent=agent, tools=[])

def beachsea(path):
    hotel_info = extract_hotel_info(
            agent_executor=agent_executor,
            text=extract_info_from_file(path)
            )

    return clean_hotel_info(hotel_info)