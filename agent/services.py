from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from enum import Enum
from .script_tools import *
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, List
# This will work regardless of where the script is run from
env_path = Path(__file__).parent.parent / "configs" / ".env"
load_dotenv(dotenv_path=env_path)


class Status(str, Enum):
    paid = "paid"
    free = "free"
    not_exists = "not_exists"
    no_info = "no_info"

class ServiceType(str, Enum):
    general_services = "General Services"
    spa = "SPA"
    sport = "Sport"
    water_activities = "Water Activities"
    entertainment = "Entertainment"
    for_children = "For Children"
    ski_services = "Ski Services"
    honeymoon_services = "Honeymoon Services"
    mini_club = "Mini Club"

# Category Models
class EntertainmentServices(BaseModel):
    boccia: Status = Status.no_info
    dart: Status = Status.no_info
    cinema: Status = Status.no_info
    game_centre: Status = Status.no_info
    playstation: Status = Status.no_info
    card_games: Status = Status.no_info
    disco: Status = Status.no_info
    animation: Status = Status.no_info
    billiards: Status = Status.no_info
    backgammon: Status = Status.no_info
    tennis_court_lighting: Status = Status.no_info
    bowling: Status = Status.no_info

class ForChildrenServices(BaseModel):
    mini_disco: Status = Status.no_info
    aupair: Status = Status.no_info
    playground_outdoor: Status = Status.no_info
    entertainment_programs_for_children: Status = Status.no_info
    childrens_menu_in_the_restaurant: Status = Status.no_info
    babysitter: Status = Status.no_info
    baby_car: Status = Status.no_info
    baby_bed: Status = Status.no_info
    game_centre: Status = Status.no_info
    kids_cinema: Status = Status.no_info
    childrens_chair_in_the_restaurant: Status = Status.no_info
    childrens_area_in_the_restaurant: Status = Status.no_info

class GeneralServices(BaseModel):
    wifi_in_the_lobby: Status = Status.no_info
    airport_transfer_services: Status = Status.no_info
    electric_vehicle_charging_station: Status = Status.no_info
    supermarket: Status = Status.no_info
    luggage_room: Status = Status.no_info
    exchange_money: Status = Status.no_info
    reception_24h: Status = Status.no_info
    casino: Status = Status.no_info
    safe_box_in_reception: Status = Status.no_info
    parking: Status = Status.no_info
    parking_indoor: Status = Status.no_info
    iron_service: Status = Status.no_info
    room_service: Status = Status.no_info
    autopark: Status = Status.no_info
    laundry_service: Status = Status.no_info
    wifi_in_all_areas: Status = Status.no_info
    doctor_service: Status = Status.no_info

class HoneymoonServices(BaseModel):
    free_alacart_restaurant_usage: Status = Status.no_info
    breakfast_service_into_room_first_day: Status = Status.no_info
    vine_and_fruites_table: Status = Status.no_info
    special_room_honeymoon_decoration: Status = Status.no_info
    discount_in_spa_centre: Status = Status.no_info
    live_frozen_in_the_room: Status = Status.no_info
    room_upgrade: Status = Status.no_info
    breakfast_service_in_the_room: Status = Status.no_info
    vine_and_fruites_in_the_room: Status = Status.no_info
    alacarte_restaurant_free_1_time: Status = Status.no_info
    discount_for_spa_services: Status = Status.no_info

class MiniClubServices(BaseModel):
    youth_club: Status = Status.no_info
    child_club: Status = Status.no_info

class SkiServices(BaseModel):
    ski_gardrope: Status = Status.no_info
    ski_equipment_rental: Status = Status.no_info
    shuttle_to_ski_centre: Status = Status.no_info

class SpaServices(BaseModel):
    spa_center: Status = Status.no_info
    beauty_center: Status = Status.no_info
    sauna: Status = Status.no_info
    hammam: Status = Status.no_info
    massage: Status = Status.no_info
    jacuzzi: Status = Status.no_info
    steam_room: Status = Status.no_info

class SportServices(BaseModel):
    aerobics: Status = Status.no_info
    fitness_center: Status = Status.no_info
    tennis_court: Status = Status.no_info
    parachute: Status = Status.no_info
    mini_golf: Status = Status.no_info
    table_tennis: Status = Status.no_info
    badminton: Status = Status.no_info
    beach_volley: Status = Status.no_info
    mini_football: Status = Status.no_info

class WaterActivitiesServices(BaseModel):
    canoe: Status = Status.no_info
    pedalo: Status = Status.no_info
    aquapark: Status = Status.no_info
    diving: Status = Status.no_info
    parasailing: Status = Status.no_info
    banana: Status = Status.no_info
    jet_ski: Status = Status.no_info
    paddle_boat: Status = Status.no_info
    surfing: Status = Status.no_info
    water_skiing: Status = Status.no_info


class AgentResponse(BaseModel):
    entertainment: Optional[EntertainmentServices] = None
    for_children: Optional[ForChildrenServices] = None
    general_services: Optional[GeneralServices] = None
    honeymoon_services: Optional[HoneymoonServices] = None
    mini_club: Optional[MiniClubServices] = None
    ski_services: Optional[SkiServices] = None
    spa: Optional[SpaServices] = None
    sport: Optional[SportServices] = None
    water_activities: Optional[WaterActivitiesServices] = None

class MiniClubService(BaseModel):
    status: Status = Status.no_info
    hours: Optional[List[str]] = None  # e.g. ["10:00", "23:00"]
    ages: Optional[List[int]] = None   # e.g. [4, 12]
    languages: Optional[List[str]] = None  # e.g. ["English", "Russian", ...]

class MiniClubServices(BaseModel):
    youth_club: MiniClubService = MiniClubService()
    child_club: MiniClubService = MiniClubService()


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

system_prompt = config["services"]

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



def services(path):
    hotel_info = extract_hotel_info(
            agent_executor=agent_executor,
            text=extract_info_from_file(path)
            )



    return clean_hotel_info(hotel_info)
