import speech_recognition as sr
from os import path
from pydub import AudioSegment
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter

# convert mp3 file to wav      

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


def add_text_to_pdf(input_pdf_path, output_pdf_path, data_dict, transcript):
    # Create a temporary PDF with the text to overlay
    temp_pdf_path = "temp_overlay.pdf"
    c = canvas.Canvas(temp_pdf_path, pagesize=letter)
    
    # Write the data (coordinates need to be adjusted based on the PDF layout)
    c.setFont("Helvetica", 12)
    c.drawString(150, 700,transcript)  # Coordinates for Name
    c.drawString(150, 650, data_dict.get("email", ""))  # Coordinates for Email
    c.drawString(150, 600, data_dict.get("date", ""))   # Coordinates for Date
    
    c.save()

    # Read the original PDF
    reader = PdfReader(input_pdf_path)
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

# Example usage
data = {
    "name": "John Doe",
    "email": "john@example.com",
    "date": "2024-09-30"
}
add_text_to_pdf("input_form.pdf", "output_filled.pdf", data, transcribeAudio("transcript.wav"))