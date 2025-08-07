import agent
from pprint import pprint

path = "C:/Users/DENIX/Desktop/FILES PDF/FILES/CASSIATOUR HOTELS 1/CASSIATOUR HOTELS/EFTALIA MARIN HOTEL+/EFTALIA MARIN HOTEL.pdf"

all = {
  "definition": agent.definition(path),
  "units": agent.units(path),
  "beach & sea": agent.beachsea(path),
  "pools": agent.pools(path),
  "rooms": agent.rooms(path),
  "services": agent.services(path),
  "restaurants": agent.restaurants(path)
}

pprint(all)