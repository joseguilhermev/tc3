import requests

url = "http://localhost:8050/render.html"
params = {
    "url": "https://www.cashbackforex.com/chart?s=BTC.USD-1m",
    "wait": 2,
    "timeout": 10,  # Extend timeout if needed
}  # Wait for JavaScript to load
response = requests.get(url, params=params)
print(response.text)  # Rendered HTML
