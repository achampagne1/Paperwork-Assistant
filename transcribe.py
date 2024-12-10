import sys
sys.path.append('/mnt/efs/python')

import urllib.request
import http.client
import socket
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
from pydub import AudioSegment  
from pydub.utils import which

AudioSegment.converter = "/opt/bin/ffmpeg"
AudioSegment.ffprobe = "/opt/bin/ffprobe"

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

def getIOBytes(input, bucket):
    key = urllib.parse.unquote_plus(input, encoding='utf-8')
    fileResponse = s3.get_object(Bucket=bucket,Key=key)
    return io.BytesIO(fileResponse['Body'].read())

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

def transcribeAudio(audioData):
    audioSegment = AudioSegment.from_file(audioData)
    pcmStream = io.BytesIO()
    audioSegment.set_frame_rate(16000).set_channels(1).export(pcmStream, format="wav", codec="pcm_s16le")
    pcmStream.seek(0)

    r = sr.Recognizer()
    with sr.AudioFile(pcmStream) as source:
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
        if value:
            c.drawString(tagAndLocation[1][2]+rightShift,795-tagAndLocation[1][3],value[0]) 
            value.pop(0)
    c.save()

    overlay_reader = PdfReader(temp_pdf_path)
    if len(overlay_reader.pages)==0:
        return 0

    reader = PdfReader(fileStream)   
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
    expiration = 10

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
    fileStream = getIOBytes(body['file'], body['bucket'])
    audioStream = getIOBytes(body['audio'], body['bucket'])

    #nlp = spacy.load("en_core_web_sm_with_medical_terminology") fix this later
    nlp = spacy.load("en_core_web_sm")

    #add_text_to_pdf(userInput, "output_filled.pdf", transcribeAudio("transcript.mp3")) #for testing with audio
    #inputString = "my child's name is Aubrey Champagne, today is October 7th, and my name is Scott Champagne"
    transcript = transcribeAudio(audioStream)
    allInformation = extractAllInformation(transcript, nlp)
    output = add_text_to_pdf(fileStream, "/mnt/efs/lambda/python/temp_overlay.pdf", allInformation)
    if output == 0:
        return "NO INFORMATION GIVEN TO TRANSCRIBE"

    fileKey = fileKey[6:len(fileKey)-4]
    outputPath = "output/"+fileKey+"_output.pdf"
    s3.upload_fileobj(output,bucket,outputPath)
    return generateLink(bucket, outputPath)