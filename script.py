import pandas as pd
import requests

print("inicio script")

# ejemplo base
data = [
    {"keyword": "pool service indio"}
]

for row in data:
    keyword = row["keyword"]

    url = "https://serpapi.com/search.json"
    params = {
        "q": keyword,
        "api_key": "b42c2dc107e6b2487a8ec59fb482c65392ec8dd841829e0e3588b08e93d7bcfd"
    }

    response = requests.get(url, params=params)
    result = response.json()

    print(result.get("organic_results", [])[:1])

print("fin script")
