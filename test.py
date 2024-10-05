import spacy

# Load the pre-trained spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to get the NER label for a string
def get_ner_label(text):
    # Process the text
    doc = nlp(text)
    
    # Check if any named entity is detected
    if doc.ents:
        # Return the first entity's text and label
        ent = doc.ents[0]
        return ent.text, ent.label_
    else:
        # Return None for both values if no entity is found
        return None, None

# Example usage
text = "Alabama"
entity, label = get_ner_label(text)
if entity:
    print(f"Entity: {entity}, Label: {label}")
else:
    print("No entity found")