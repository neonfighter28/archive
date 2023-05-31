import requests
import sys
import html

if sys.argv[1]:
    filename = sys.argv[1]
else:
    print("No filename given")
    sys.exit()

URL = (
    "https://translate.googleapis.com/language/translate/v2"
)

PARAMS = {
    "key" : "AIzaSyA9eZzr0CDXIYSoi5NmyC6UtApu_nDaekA",
    "source" : "de",
    "target": "en"
}

with open(filename, "r") as file:
    text = file.read()

DATA = {
    "q": text
}

response = requests.post(URL, params = PARAMS, json=DATA)
translated = response.json()["data"]["translations"][0]["translatedText"]
decoded_text = html.unescape(translated)
with open(f"{filename.split('.')[0]}-EN.txt", "w+", encoding="utf-8") as f:
    f.write(decoded_text)