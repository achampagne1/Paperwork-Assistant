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
                text = span['text']  # The actual text
                bbox = span['bbox']  # The bounding box (x0, y0, x1, y1)
                tempList = (text,bbox)
                allWords.append(tempList)
    return allWords



def add_text_to_pdf(inputPdfPath, output_pdf_path, transcript):
    print(findLocationOfAllText(inputPdfPath))
    temp_pdf_path = "temp_overlay.pdf"
    c = canvas.Canvas(temp_pdf_path, pagesize=letter)
    

    c.setFont("Helvetica", 12)
    c.drawString(107, 795-141.339111328125,"name[0]") 
    name = extractInformation(transcript,"PERSON")
    if name:
        c.drawString(150, 200,name[0]) 

    age = extractInformation(transcript,"CARDINAL")
    if age:
        c.drawString(150, 300,age[0]) 

    places = extractInformation(transcript,"GPE")
    fullPlace = ""
    if places:
        for place in places:
            fullPlace = fullPlace + place + " "
        c.drawString(150, 400,fullPlace) 
    
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

add_text_to_pdf("IntroductoryForm.pdf", "output_filled.pdf", transcribeAudio("transcript.mp3"))