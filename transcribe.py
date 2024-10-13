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
import time

start = time.time()

nlp = spacy.load("en_core_web_sm_with_medical_terminology")
rightShift = 5

labelLookUpTable = {
    "name": "PERSON",
    "location": "GPE",
    "age": "CARDINAL",
    "nationality": "NORP",
    "food": "PRODUCT",
    "date": "DATE"
}

def labelLookUpTableWrapper(inputString):
    inputString = inputString.lower()
    label = ""
    try:
        for word in labelLookUpTable.keys():
            if word in inputString:
                label = labelLookUpTable[word]
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

def extractAllInformation(text):
    allInformation = []
    doc = nlp(text)
    ner = nlp.get_pipe("ner")
    for label in ner.labels:
        info = (label,[ent.text for ent in doc.ents if ent.label_ == label])
        allInformation.append(info)
    return allInformation

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
        if 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    tempList = (span['text'],span['bbox'])
                    allWords.append(tempList)
    return allWords



def add_text_to_pdf(inputPdfPath, output_pdf_path, transcript):
    tagsAndLocations = findLocationOfAllText(inputPdfPath)
    temp_pdf_path = "temp_overlay.pdf"
    c = canvas.Canvas(temp_pdf_path, pagesize=letter)
    allInformation = extractAllInformation(transcript)

    #currently it will be implemented using double loop of lists. Will move to dicts some day
    for tagAndLocation in tagsAndLocations:
        for information in allInformation:
            if information[0] == labelLookUpTableWrapper(tagAndLocation[0]):
                c.drawString(tagAndLocation[1][2]+rightShift,795-tagAndLocation[1][3],information[1][0]) 
                print(information[1])
                information[1].pop(0)
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

#userInput = input("Enter file input file name: ")
#if userInput == "":
#    userInput = "testForm1.pdf"
#add_text_to_pdf(userInput, "output_filled.pdf", transcribeAudio("transcript.mp3")) #for testing with audio
inputString = "my child's name is Aubrey Champagne, today is October 7th, and my name is Scott Champagne"
add_text_to_pdf("testForm5.pdf", "output_filled.pdf", inputString)
end = time.time()

print(end - start)