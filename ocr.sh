#!/bin/bash


# Source the python environment
source ./venv/bin/activate

# Make temporary folder and copy file into it
mkdir .temp
cp input.pdf .temp/input.pdf
cp main.py .temp/main.py
cd .temp

echo "Splitting PDF to PNGs"
pdftoppm -png input.pdf TEMP_PNG

echo "Done"
for i in TEMP_PNG-??.png; 
do 
    echo "Transcribing image $i"
    tesseract "$i" "TEMP_TEXT-$i" -l deu; 

done;
echo "Concatenating text files"
cat TEMP_TEXT* > input.txt

echo "Removing temporary files..."
rm TEMP*

echo "Translating"
python main.py

cd ..
cp .temp/translated.txt .
cp .temp/input.txt .
rm -r .temp
