"""
Author: Elias Csuka
Date: 02/06/2023

Description:

"""

import logging
import os
from tkinter.filedialog import askopenfilename

from gcloud import GCloud
from gpt import GPT
from ocr import OCR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

log = logging.getLogger(__name__)

if __name__ == "__main__":
    filename = askopenfilename()  # type: ignore
    # if textfile already exists, skip OCR
    txtfile = f"{filename.split('.')[0]}.txt"
    if not os.path.isfile(txtfile):
        ocr = OCR(filename)
        ocr.build()
        ocr.write()
        filename = ocr.out_filename
    else:
        log.warn(f"{txtfile} already exists, skipping OCR")
        filename = txtfile
    gcloud = GCloud(filename)
    gcloud.build()
    gcloud.write()
    gpt = GPT(filename)
    gpt.build()
    gpt.write()
    filename = gpt.out_filename
    gcloud = GCloud(filename)
    gcloud.build()
    gcloud.write()
