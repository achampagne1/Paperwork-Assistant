import spacy

# Load the fine-tuned model
nlp = spacy.load("en_core_web_sm_with_medical_terminology")

# Test with various inputs
test_texts = [
    "John Doe was diagnosed with diabetes.",
    "Jane Smith has hypertension.",
    "The patient was treated for pneumonia.",
    "Dr. Green prescribes medication for heart disease.",
    "today is October 7th"
    "I like Amazon"
]

for text in test_texts:
    doc = nlp(text)
    for ent in doc.ents:
        print(ent.text, ent.label_)