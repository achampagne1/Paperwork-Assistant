import sys
sys.path.append('/mnt/efs/python')

import io
import json
import urllib.parse
import boto3
from botocore.exceptions import ClientError
import speech_recognition as sr
import os
import spacy
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox, LTChar
import fitz  # PyMuPDF
import time

labelLookUpTable = {
        "name": "PERSON",
        "location": "GPE",
        "age": "CARDINAL",
        "nationality": "NORP",
        "food": "PRODUCT",
        "date": "DATE"
    }

rightShift = 5

s3 = boto3.client('s3')

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

def extractAllInformation(text, nlp):
    allInformation = {}
    doc = nlp(text)
    ner = nlp.get_pipe("ner")
    for label in ner.labels:
        allInformation[label] = ([ent.text for ent in doc.ents if ent.label_ == label])
    return allInformation

def transcribeAudio(audioFilePath):                                                 
    sound = AudioSegment.from_mp3(audioFilePath)
    sound.export("transcript.wav", format="wav")                                                    
    AUDIO_FILE = "transcript.wav"
                                      
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)                 

        return r.recognize_google(audio)

def findLocationOfAllText(fileStream):
    allWords = []
    pdfDocument = fitz.open("pdf", fileStream)
    page = pdfDocument.load_page(0)
    textInstances = page.get_text("dict")

    for block in textInstances['blocks']:
        if 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    tempList = (span['text'],span['bbox'])
                    allWords.append(tempList)
    return allWords

def add_text_to_pdf(fileStream, output_pdf_path, allInformation):

    tagsAndLocations = findLocationOfAllText(fileStream)
    temp_pdf_path = "/mnt/efs/lambda/python/temp_overlay.pdf"
    c = canvas.Canvas(temp_pdf_path, pagesize=letter)
    
    for tagAndLocation in tagsAndLocations:
        value = allInformation.get(labelLookUpTableWrapper(tagAndLocation[0]))
        if value is not None:
import sys
sys.path.append('/mnt/efs/python')

import io
import json
import urllib.parse
import boto3
from botocore.exceptions import ClientError
import speech_recognition as sr
import os
import spacy
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox, LTChar
import fitz  # PyMuPDF
import time

labelLookUpTable = {
        "name": "PERSON",
        "location": "GPE",
        "age": "CARDINAL",
        "nationality": "NORP",
        "food": "PRODUCT",
        "date": "DATE"
    }

rightShift = 5

s3 = boto3.client('s3')
start = time.time()

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

def extractAllInformation(text, nlp):
    allInformation = {}
    doc = nlp(text)
    ner = nlp.get_pipe("ner")
    for label in ner.labels:
        allInformation[label] = ([ent.text for ent in doc.ents if ent.label_ == label])
    return allInformation

def transcribeAudio(audioFilePath):                                                 
    sound = AudioSegment.from_mp3(audioFilePath)
    sound.export("transcript.wav", format="wav")                                                    
    AUDIO_FILE = "transcript.wav"
                                      
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)                 

        return r.recognize_google(audio)

def findLocationOfAllText(fileStream):
    allWords = []
    pdfDocument = fitz.open("pdf", fileStream)
    page = pdfDocument.load_page(0)
    textInstances = page.get_text("dict")

    for block in textInstances['blocks']:
        if 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    tempList = (span['text'],span['bbox'])
                    allWords.append(tempList)
    return allWords

def add_text_to_pdf(fileStream, output_pdf_path, allInformation):

    tagsAndLocations = findLocationOfAllText(fileStream)
    temp_pdf_path = "/mnt/efs/lambda/python/temp_overlay.pdf"
    c = canvas.Canvas(temp_pdf_path, pagesize=letter)
    
    for tagAndLocation in tagsAndLocations:
        value = allInformation.get(labelLookUpTableWrapper(tagAndLocation[0]))
        if value is not None:
            c.drawString(tagAndLocation[1][2]+rightShift,795-tagAndLocation[1][3],value[0]) 
            value.pop(0)
    c.save()

    reader = PdfReader(fileStream)
    overlay_reader = PdfReader(temp_pdf_path)
    writer = PdfWriter()

    for i in range(len(reader.pages)):
        page = reader.pages[i]
        overlay_page = overlay_reader.pages[i]

        # Merge overlay page onto the main page
        page.merge_page(overlay_page)
        writer.add_page(page)

    outputBuffer = io.BytesIO()
    writer.write(outputBuffer)
    outputBuffer.seek(0)
    return outputBuffer

def generateLink(bucket, key):
    expiration = 60 

    try:
        # Generate a pre-signed URL
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration
        )
        
        # Return the URL
        return {
            'statusCode': 200,
            'body': json.dumps({'url': url})
        }
        
    except Exception as e:
        print(f"Error generating pre-signed URL: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to generate URL'})
        }

def lambda_handler(event, context):
    body = json.loads(event.get("body"))
    bucket = body['bucket']
    key = urllib.parse.unquote_plus(body['object'], encoding='utf-8')
    response = s3.get_object(Bucket=bucket,Key=key)
    fileStream = io.BytesIO(response['Body'].read())
    #nlp = spacy.load("en_core_web_sm_with_medical_terminology") fix this later
    nlp = spacy.load("en_core_web_sm")

    #userInput = input("Enter file input file name: ")
    #if userInput == "":
    #    userInput = "testForm1.pdf"
    #add_text_to_pdf(userInput, "output_filled.pdf", transcribeAudio("transcript.mp3")) #for testing with audio
    inputString = "my child's name is Aubrey Champagne, today is October 7th, and my name is Scott Champagne"
    allInformation = extractAllInformation(inputString, nlp)
    output = add_text_to_pdf(fileStream, "/mnt/efs/lambda/python/temp_overlay.pdf", allInformation)
    
    key = key[6:len(key)-4]
    outputPath = "output/"+key+"_output.pdf"
    s3.upload_fileobj(output,bucket,outputPath)
    return generateLink(bucket, outputPath)
    end = time.time()
    return (end - start)