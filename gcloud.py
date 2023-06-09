"""
Author: Elias Csuka, 2023
Description: Translates a text file from German to English using the Google Cloud API

"""
import html
import logging

import dotenv
import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.getLogger("requests").setLevel(logging.WARNING)
log = logging.getLogger(__name__)


class GCloud:
    """
    Translates a text file from German to English using the Google Cloud API
    """

    URL = "https://translate.googleapis.com/language/translate/v2"
    PARAMS = {"key": None, "source": "de", "target": "en"}

    def __init__(self, filepath: str):
        # Load API Key
        dotenv.load_dotenv()
        GCloud.PARAMS["key"] = dotenv.get_key(".env", "gCloudKey")
        self.filename = filepath

        # Open file
        with open(self.filename, "r", encoding="utf-8") as file:
            self.text = file.read()
        log.info(f"Loaded {self.filename} for translation")

    def build(self) -> None:
        log.info("Sending request to Google Cloud API")
        DATA = {"q": self.text}
        response = requests.post(GCloud.URL, params=GCloud.PARAMS, json=DATA)
        translated = response.json()["data"]["translations"][0]["translatedText"]
        self.decoded_text = html.unescape(translated)
        log.info("Received response")

    def write(self) -> None:
        with open(f"{self.filename.split('.')[0]}-EN.txt", "w+", encoding="utf-8") as f:
            f.write(self.decoded_text)

        log.info(f"Translated text written to {self.filename.split('.')[0]}-EN.txt")


if __name__ == "__main__":
    pass
