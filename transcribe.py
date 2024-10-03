import speech_recognition as sr
from os import path
from pydub import AudioSegment
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox, LTChar
import spacy

nlp = spacy.load("en_core_web_sm")

def extractInformation(text, label):
    doc = nlp(text)
    info = [ent.text for ent in doc.ents if ent.label_ == label]
    return info

def transcribeAudio(audioFilePath):                                                 
    sound = AudioSegment.from_mp3(audioFilePath)
    sound.export("transcript.wav", format="wav")


    # transcribe audio file                                                         
    AUDIO_FILE = "transcript.wav"

    # use the audio file as the audio source                                        
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file                  

        return r.recognize_google(audio)


def add_text_to_pdf(inputPdfPath, output_pdf_path, transcript):
    # Create a temporary PDF with the text to overlay
    temp_pdf_path = "temp_overlay.pdf"
    c = canvas.Canvas(temp_pdf_path, pagesize=letter)
    
    # Write the data (coordinates need to be adjusted based on the PDF layout)
    c.setFont("Helvetica", 12)
    name = extractInformation(transcript,"PERSON")
    c.drawString(150, 700,name[0])  # Coordinates for Name

    places = extractInformation(transcript,"GPE")
    for place in places:
        c.drawString(500, 700,place)  # Coordinates for Name
    
    c.save()

    # Read the original PDF
    reader = PdfReader(inputPdfPath)
    writer = PdfWriter()

    # Read the overlay PDF
    overlay_reader = PdfReader(temp_pdf_path)

    # Merge the original PDF and the overlay PDF
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        overlay_page = overlay_reader.pages[i]

        page.merge_page(overlay_page)
        writer.add_page(page)

    # Save the result
    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

add_text_to_pdf("IntroductoryForm.pdf", "output_filled.pdf", transcribeAudio("transcript.mp3"))