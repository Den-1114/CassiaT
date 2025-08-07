from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from .script_tools import *
import os
from dotenv import load_dotenv
from pathlib import Path

# This will work regardless of where the script is run from
env_path = Path(__file__).parent.parent / "configs" / ".env"
load_dotenv(dotenv_path=env_path)

class AgentResponse(BaseModel):
    hotel_name: str
    country: str
    address: str
    phone: str
    website: str
    foundation: str
    last_renovation: str
    total_area: str
    distance_to_nearest_city_center: str
    distance_to_nearest_airport: str
    distance_to_nearest_atm: str
    distance_to_nearest_mall: str
    distance_to_nearest_bus_or_metro: str
    distance_to_ski_center: str
    distance_to_ski_room: str


llm = ChatOpenAI(
    model="gpt-4o-mini",
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

system_prompt = config["definition"]

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



def definition(path):
    hotel_info = extract_hotel_info(
            agent_executor=agent_executor,
            text=extract_info_from_file(path)
            )



    return clean_hotel_info(hotel_info)
