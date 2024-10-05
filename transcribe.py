import speech_recognition as sr
from os import path
from pydub import AudioSegment
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox, LTChar
import spacy
import fitz  # PyMuPDF

nlp = spacy.load("en_core_web_sm")
rightShift = 5

labelLookUpTable = {
    "name:": "PERSON",
    "name": "PERSON",
    "location:": "PERSON",
    "location": "PERSON",
    "age:": "PERSON",
    "age": "PERSON",
}

def labelLookUpTableWrapper(inputString):
    inputString = inputString.lower()
    label = ""
    try:
        label = labelLookUpTable[inputString]
    except KeyError:
        label = getNerLabel(inputString)
    return label

def getNerLabel(text):
    doc = nlp(text)
    
    if doc.ents:
        for ent in doc.ents:
            return ent.label_
    else:
        return "No entity found"

def getLocationOfText(textToFind, listOfText):
    for textAndLocation in listOfText:
        if textAndLocation[0] == textToFind:
            return (textAndLocation[1][2],textAndLocation[1][3])

def extractInformation(text, label):
    doc = nlp(text)
    info = [ent.text for ent in doc.ents if ent.label_ == label]
    return info

def transcribeAudio(audioFilePath):                                                 
    sound = AudioSegment.from_mp3(audioFilePath)
    sound.export("transcript.wav", format="wav")                                                    
    AUDIO_FILE = "transcript.wav"
                                      
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)                 

        return r.recognize_google(audio)

def findLocationOfAllText(filePath):
    allWords = []
    pdfDocument = fitz.open(filePath)
    page = pdfDocument.load_page(0)
    textInstances = page.get_text("dict")

    for block in textInstances['blocks']:
        for line in block['lines']:
            for span in line['spans']:
                tempList = (span['text'],span['bbox'])
                allWords.append(tempList)
    return allWords



def add_text_to_pdf(inputPdfPath, output_pdf_path, transcript):
    tagsAndLocations = findLocationOfAllText(inputPdfPath)
    temp_pdf_path = "temp_overlay.pdf"
    c = canvas.Canvas(temp_pdf_path, pagesize=letter)
    

    c.setFont("Helvetica", 12)
    name = extractInformation(transcript,labelLookUpTableWrapper(tagsAndLocations[1][0]))
    if name:
        tempList = getLocationOfText("Name:",tagsAndLocations)
        c.drawString(tempList[0]+rightShift,795-tempList[1],name[0]) 

    age = extractInformation(transcript,"CARDINAL")
    if age:
        tempList = getLocationOfText("Age:",tagsAndLocations)
        c.drawString(tempList[0]+rightShift,795-tempList[1],age[0]) 

    places = extractInformation(transcript,"GPE")
    fullPlace = ""
    if places:
        for place in places:
            fullPlace = fullPlace + place + " "
        tempList = getLocationOfText("Location:",tagsAndLocations)
        c.drawString(tempList[0]+rightShift,795-tempList[1],fullPlace) 
    
    c.save()


    reader = PdfReader(inputPdfPath)
    writer = PdfWriter()


    overlay_reader = PdfReader(temp_pdf_path)


    for i in range(len(reader.pages)):
        page = reader.pages[i]
        overlay_page = overlay_reader.pages[i]

        page.merge_page(overlay_page)
        writer.add_page(page)


    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

userInput = input("Enter file input file name: ")
add_text_to_pdf(userInput, "output_filled.pdf", transcribeAudio("transcript.mp3"))