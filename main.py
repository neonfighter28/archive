import requests

URL = (
    "https://translate.googleapis.com/language/translate/v2"
)

PARAMS = {
    "key" : "AIzaSyA9eZzr0CDXIYSoi5NmyC6UtApu_nDaekA",
    "source" : "de",
    "target": "en"
}

with open("input.txt", "r") as file:
    text = file.read()

DATA = {
    "q": text
}

response = requests.post(URL, params = PARAMS, json=DATA)
translated = response.json()["data"]["translations"][0]["translatedText"]

with open("translated.txt", "w+", encoding="utf-8") as f:
    f.write(translated)