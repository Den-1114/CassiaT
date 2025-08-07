from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from enum import Enum
from typing import Dict, List
import os
from .script_tools import *

from dotenv import load_dotenv
from pathlib import Path

# This will work regardless of where the script is run from
env_path = Path(__file__).parent.parent / "configs" / ".env"
load_dotenv(dotenv_path=env_path)

class UnitType(str, Enum):
    main_building = "Main Building"
    anex_building = "Anex Building"
    club = "Club"
    deluxe_building = "Deluxe Building"
    additional_building = "Additional Building"
    bungalow = "Bungalow"
    lake_house = "Lake House"
    villa = "Villa"

class Building(BaseModel):
    name: UnitType
    number_of_blocks: int
    number_of_floors: int
    number_of_elevators: int

class AgentResponse(BaseModel):
    number_buildings: int
    buildings: Dict[str, List[Building]]
    restaurant_count: int
    bar_count: int
    meeting_room_count: int



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


system_prompt = config["units"]

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


def units(path):
    hotel_info = extract_hotel_info(
            agent_executor=agent_executor,
            text=extract_info_from_file(path)
            )

    return clean_hotel_info(hotel_info)
