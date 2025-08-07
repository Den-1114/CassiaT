from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
import os
import json
from .script_tools import *

# Room View Enum
class RoomView(str, Enum):
    sea = "Sea"
    land = "Land"

# Room model
class Room(BaseModel):
    room_type: str = Field(..., description="Official name of the room type")
    slug: str = Field(..., description="Unique slug identifier for the room")
    total_room_count: Optional[int] = Field(None, description="Total number of rooms available for this type")
    room_size_m2: int = Field(..., description="Size of the room in square meters")
    view: RoomView = Field(..., description="Type of view from the room")

# Agent response model
class RoomAgentResponse(BaseModel):
    number_of_room_types: int = Field(..., description="Total number of distinct room types")
    rooms: List[Room] = Field(..., description="List of all available room types")

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Load prompt configuration
config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "prompt_config.json")
config_path = os.path.abspath(config_path)
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

# Room-specific prompt
system_prompt_rooms = config["rooms"]

# Create parser for room data
parser_rooms = PydanticOutputParser(pydantic_object=RoomAgentResponse)

# Create prompt template
prompt_template_rooms = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt_rooms),
        ("user", "{text}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser_rooms.get_format_instructions())

# Create agent for rooms
agent_rooms = create_tool_calling_agent(
    llm=llm,
    prompt=prompt_template_rooms,
    tools=[],
)

agent_executor_rooms = AgentExecutor(agent=agent_rooms, tools=[])

def rooms(path):
    hotel_info = extract_hotel_info(
        agent_executor=agent_executor_rooms,
        text=extract_info_from_file(path)
    )
    return clean_hotel_info(hotel_info)