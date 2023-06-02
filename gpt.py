import concurrent.futures
import logging
from queue import Queue
import sys
import time
from dataclasses import dataclass

import dotenv
import openai

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger("openai").setLevel(level=logging.WARNING)

log = logging.getLogger(__name__)


@dataclass
class Chunk:
    text: str
    response: str
    id: int


class GPT:
    system_msg = {
        "role": "system",
        "content": "You are tasked with correcting the output of google tesseract. The \
        output comes from a handwritten document, so there are certain formatting \
        errors from the transcription. \
        You should remove these formatting errors and correct wrongly read words.\
        Do not change the wording or content or meaning of any sentence etc.\
        If there is a random string of characters for which you find no meaning, omit it. \
        Keep ALL of the text in german!",
    }
    total_tokens = 0
    count_requests = 0
    out_filename = ""

    def __init__(self, filename: str, model: str = "gpt-3.5-turbo", temperature: float = 0.1):
        # Load textfile
        with open(filename, "r", encoding="utf-8") as f:
            self.text = f.read()
        self.filename = filename
        # Set params
        self.model = model
        self.temperature = temperature
        # Load secrets
        dotenv.load_dotenv()
        openai.api_key = dotenv.get_key(".env", "openaiKey")
        openai.organization = dotenv.get_key(".env", "openaiOrg")

        log.info(f"{openai.api_key = } {openai.organization = }")

        # Building chunks
        self.chunks = self.split()
        log.info(f"Split into {len(self.chunks)} chunks")

    def build(self) -> None:
        log.info("Building ThreadPool")
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.chunks)
        ) as executor:
            chunk_futures = {
                executor.submit(self._req, chunk): chunk for chunk in self.chunks
            }
            log.info("Executing Threads...")
            for future in concurrent.futures.as_completed(chunk_futures):
                chunk = chunk_futures[future]
                try:
                    _ = future.result()
                except Exception as exc:
                    log.warn(f"{chunk.id} threw an exception: {exc}")
                    print(f"{chunk.id = } threw an exception: {exc}")
                else:
                    print(f"{chunk.id = } finished successfully")

    def _concatenate(self) -> None:
        self.output = ""
        for chunk in self.chunks:
            self.output += chunk.response + "\n\n"

    def write(self) -> None:
        self._concatenate()
        with open(
            f"{self.filename.split('.')[0]}-IMPR.txt", "w+", encoding="utf-8"
        ) as f:
            f.write(self.output)
            GPT.out_filename = str(f.name)

    def _req(self, chunk: Chunk) -> None:
        retries = 0
        id = GPT.count_requests
        GPT.count_requests += 1
        log.info(f"Sending request # {id}")
        # Get current time
        try:
            start = time.time()
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[GPT.system_msg, {"role": "user", "content": chunk.text}],
                temperature=self.temperature,
            )
            end = time.time()
            log.info(f"Received response # {id} in {end-start} seconds")
            log.info(f"{response.usage.total_tokens = }")  # type: ignore
            GPT.total_tokens += response.usage.total_tokens  # type: ignore
            log.info(f"{response.choices[0].finish_reason = }")  # type: ignore
            chunk.response = response.choices[0].message.content  # type: ignore

        except Exception as e:
            log.error(f"Request # {id} failed in with exception: {e}")
            log.error(e.__traceback__)
            log.error(f"Retrying request # {id}")
            retries += 1
            if retries > 3:
                log.error(f"Request # {id} failed 3 times, aborting")
                raise e
            else:
                self._req(chunk)

    def split(self) -> list[Chunk]:
        q: Queue = Queue()
        s = self.text.split("\n\n")

        for i in s:
            q.put(i)
        strings = []
        j = 0
        while q.qsize() > 0:
            c = Chunk("", "", id=j)
            while len(c.text) < 2000 and q.qsize() > 0:
                c.text += q.get()
            j += 1

            strings.append(c)

        return strings

    @property
    def stats(self) -> str:
        return f"""
    Total tokens used: {GPT.total_tokens}
    Estimated cost: {GPT.total_tokens*0.002 / 1000}$ (gpt-3.5-turbo)
    """


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except IndexError:
        filename = "test.txt"
    gpt = GPT(filename)

    gpt.build()
    gpt.write()
    print(gpt.stats)

    print(f"Total tokens used: {GPT.total_tokens}")
