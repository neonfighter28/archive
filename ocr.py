import pytesseract
import pdf2image
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

log = logging.getLogger(__name__)


class OCR:
    out_filename: str = ""

    def __init__(self, filename: str):
        self.filename = filename
        log.info(f"Splitting {filename} into images")
        self.pages = pdf2image.convert_from_path(filename, 500)  # type: ignore
        log.info(f"Split {filename} into {len(self.pages)} images...")
        self.text = ""

    def build(self) -> None:
        log.info("Building text from images")
        for i, page in enumerate(self.pages):
            log.info(f"Processing page {i+1}/{len(self.pages)}")
            self.text += pytesseract.image_to_string(page, lang="deu")
        log.info("Finished building text")

    def write(self) -> None:
        log.info("Writing text to file")
        with open(f"{self.filename.split('.')[0]}.txt", "w+", encoding="utf-8") as f:
            f.write(self.text)
            OCR.out_filename = str(f.name)
            log.info(f"Text written to {f.name}")
