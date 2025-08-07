import pandas as pd
import json

df = pd.read_excel("services.xlsx")
df.to_json("services.json")