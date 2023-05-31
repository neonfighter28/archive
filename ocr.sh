#!/bin/bash

# Check if argument is supplied and set filename
if [ $# -eq 0 ]
  then
    echo "Supply a PDF file as argument"
    exit 1
fi
r_filename=$1
filename="${r_filename%.*}"

# Check if python environment exists
if [ ! -d "./venv" ]
  then
    echo "Python environment not found. Creating..."
    python3 -m venv venv
    source ./venv/bin/activate
    pip3 install -r requirements.txt
fi

# Source the python environment
source ./venv/bin/activate

# Check if tesseract is installed
if ! command -v tesseract &> /dev/null
then
    echo "tesseract could not be found. Installing..."
    sudo apt install tesseract-ocr
    sudo apt install tesseract-ocr-deu
fi

# Check if pdftoppm is installed
if ! command -v pdftoppm &> /dev/null
then
    echo "pdftoppm could not be found. Installing..."
    sudo apt install poppler-utils
fi

# Make temporary folder and copy file into it
mkdir .temp
cp $1 .temp/$1
cp main.py .temp/main.py
cd .temp

echo "Splitting PDF to PNGs"
pdftoppm -png $1 TEMP_PNG

echo "Done"
for i in TEMP_PNG-??.png; 
do 
    echo "Transcribing image $i"
    tesseract "$i" "TEMP_TEXT-$i" -l deu; 

done;

echo "Concatenating text files"


cat *.txt > $filename.txt

echo "Removing temporary files..."
rm TEMP*

echo "Translating"
python3 main.py $filename.txt

cd ..

cp .temp/$filename-EN.txt .
cp .temp/$filename.txt .
rm -r .temp

echo "Done"