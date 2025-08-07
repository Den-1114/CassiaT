from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional, Tuple
import os
import json
from .script_tools import *

class MealType(str, Enum):
    BREAKFAST = "Breakfast"
    LATE_BREAKFAST = "Late Breakfast"
    LUNCH = "Lunch"
    DINNER = "Dinner"
    SNACKS = "Snacks"
    FIVE_OCLOCK_TEA = "Five O'Clock Tea"
    LATE_DINNER = "Late Dinner"
    MIDNIGHT_SNACKS = "Midnight Snacks"
    OTHER = "Other"

class BuffetMenuType(str, Enum):
    BUFFET = "Buffet"
    MENU = "Menu"

class BoardType(str, Enum):
    ULTRA_ALL_INCLUSIVE = "ULTRA ALL INCLUSIVE"
    ALL_INCLUSIVE = "ALL INCLUSIVE"
    BED_BREAKFAST = "BED & BREAKFAST"
    HALF_BOARD = "HALF BOARD"
    HALF_BOARD_PREMIUM_DINNER = "HALF BOARD PREMIUM DINNER"
    PALACE_ALL_INCLUSIVE = "PALACE ALL INCLUSIVE"
    LUXURY_ULTRA_ALL_INCLUSIVE = "LUXURY ULTRA ALL INCLUSIVE"
    SPECIAL_ALL_INCLUSIVE = "SPECIAL ALL INCLUSIVE"
    ALL_INCLUSIVE_LIGHT = "ALL INCLUSIVE LIGHT"
    ALL_INCLUSIVE_PLUS = "ALL INCLUSIVE PLUS"
    FULL_BOARD = "FULL BOARD"
    FULL_BOARD_PLUS = "FULL BOARD PLUS"

class FreePaidType(str, Enum):
    FREE = "Free"
    PAID = "Paid"
    NO_INFO = "No Info"

class RestaurantHours(BaseModel):
    opening: str  # Format: "HH:MM"
    closing: str  # Format: "HH:MM"

class Restaurant(BaseModel):
    meal_type: MealType
    restaurant_name: str
    hours: RestaurantHours
    buffet_or_menu: BuffetMenuType
    board_type: BoardType
    free_or_paid: FreePaidType


class NeedReservationType(str, Enum):
    YES = "Yes"
    NO = "No"
    NO_INFO = "No Info"

class KitchenType(str, Enum):
    ITALIAN = "Italian"
    MEDITERRANEAN = "Mediterranean"
    MEXICAN = "Mexican"
    SEAFOOD = "Seafood"
    GREEK = "Greek"
    TURKISH = "Turkish"
    JAPANESE = "Japan"
    CHINESE = "Chinese"
    LOCAL = "Local Kitchen"
    INTERNATIONAL = "International Cuisine"
    SPANISH = "Spanish"
    EUROPEAN = "European"
    ASIAN = "Asian"
    GRILL_BBQ = "Grill & BBQ"
    SOUTH_AMERICAN = "South American"
    FAR_EAST = "Far East"
    NO_INFO = "No Info"

class MinNightAccomodationType(str, Enum):
    YES = "Yes"
    NO = "No"
    NO_INFO = "No Info"

class UsageLimitType(str, Enum):
    ONCE = "One Time"
    TWICE = "Two Times"
    THREE_TIMES = "Three Times"
    ONCE_A_WEEK = "One Time A Week"
    TWICE_A_WEEK = "Two Times A Week"
    LIMITLESS = "Limitless"
    NO_INFO = "No Info"

class ALACarteRestaurant(BaseModel):
    restaurant_name: str
    hours: RestaurantHours
    need_reservation: NeedReservationType
    kitchen: KitchenType
    min_night_accomodation: MinNightAccomodationType
    usage_limit: UsageLimitType
    board_type: BoardType
    free_or_paid: FreePaidType


class DrinkType(str, Enum):
    LOCAL_DRINKS = "Local Drinks"
    IMPORTED_DRINKS = "Imported Drinks"
    NON_ALCOHOLIC_DRINKS = "Non-Alcoholic Drinks"

class Bar(BaseModel):
    restaurant_name: str
    hours: RestaurantHours  # Reusing the same hours model from restaurants
    drink_types: List[DrinkType]
    board_type: BoardType  # Reusing the same BoardType enum
    free_or_paid: FreePaidType  # Reusing the same FreePaidType enum

class AgentResponse(BaseModel):
    meals: List[Restaurant]
    a_la_carte_restaurants: List[ALACarteRestaurant]
    bars: List[Bar]  # Adding bars to the main response model


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
system_prompt_rooms = config["restaurants"]

# Create parser for room data
parser_rooms = PydanticOutputParser(pydantic_object=AgentResponse)

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

def restaurants(path):
    hotel_info = extract_hotel_info(
        agent_executor=agent_executor_rooms,
        text=extract_info_from_file(path)
    )
    return clean_hotel_info(hotel_info)