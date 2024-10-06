import spacy
from spacy.training.example import Example
import random

trainingData = [
    ("The patient was diagnosed with diabetes.", {"entities": [(30, 38, "CONDITION")]}),
    ("She has been suffering from hypertension for years.", {"entities": [(25, 37, "CONDITION")]}),
    ("John was admitted due to a severe asthma attack.", {"entities": [(28, 34, "CONDITION")]}),
    ("She was treated for pneumonia last month.", {"entities": [(20, 29, "CONDITION")]}),
    ("The patient has a history of heart disease.", {"entities": [(31, 43, "CONDITION")]}),
    ("He is taking medication for depression.", {"entities": [(30, 40, "CONDITION")]}),
    ("The primary symptom is chronic fatigue syndrome.", {"entities": [(24, 49, "CONDITION")]}),
    ("She was diagnosed with arthritis last year.", {"entities": [(24, 33, "CONDITION")]}),
    ("He has experienced severe migraines recently.", {"entities": [(25, 34, "CONDITION")]}),
    ("The doctor prescribed medication for epilepsy.", {"entities": [(34, 42, "CONDITION")]}),
    ("She was treated for a common cold.", {"entities": [(23, 34, "CONDITION")]}),
    ("He has a history of chronic obstructive pulmonary disease.", {"entities": [(22, 61, "CONDITION")]}),
    ("She developed symptoms of hypothyroidism.", {"entities": [(28, 42, "CONDITION")]}),
    ("The patient suffers from irritable bowel syndrome.", {"entities": [(25, 49, "CONDITION")]}),
    ("He was diagnosed with Alzheimer's disease last year.", {"entities": [(22, 40, "CONDITION")]}),
    ("John Doe was diagnosed with diabetes.", {"entities": [(0, 8, "PERSON"), (30, 38, "CONDITION")]}),
    ("Jane Smith has been suffering from hypertension for years.", {"entities": [(0, 10, "PERSON"), (25, 37, "CONDITION")]}),
    ("Dr. Brown was admitted due to a severe asthma attack.", {"entities": [(0, 10, "PERSON"), (36, 42, "CONDITION")]}),
    ("She was treated for pneumonia last month.", {"entities": [(20, 29, "CONDITION")]}),
    ("The patient has a history of heart disease.", {"entities": [(31, 43, "CONDITION")]}),
    ("John Doe was diagnosed with diabetes.", {"entities": [(0, 8, "PERSON"), (30, 38, "CONDITION")]}),
    ("Jane Smith has been suffering from hypertension for years.", {"entities": [(0, 10, "PERSON"), (25, 37, "CONDITION")]}),
    ("Dr. Brown was admitted due to a severe asthma attack.", {"entities": [(0, 10, "PERSON"), (36, 42, "CONDITION")]}),
    ("The patient was treated for pneumonia last month.", {"entities": [(20, 29, "CONDITION")]}),
    ("The doctor diagnosed Amy with heart disease.", {"entities": [(21, 24, "PERSON"), (38, 50, "CONDITION")]}),
    ("Elena Martinez is recovering from a mild stroke.", {"entities": [(0, 15, "PERSON"), (32, 37, "CONDITION")]}),
    ("Michael's chronic bronchitis requires regular treatment.", {"entities": [(0, 7, "PERSON"), (10, 29, "CONDITION")]}),
    ("He has been struggling with anxiety for months.", {"entities": [(8, 14, "CONDITION")]}),
    ("Dr. Lee specializes in treating arthritis.", {"entities": [(0, 7, "PERSON"), (28, 36, "CONDITION")]}),
    ("Linda is managing her symptoms of depression.", {"entities": [(0, 5, "PERSON"), (30, 40, "CONDITION")]}),
    
    # Medical conditions
    ("He was treated for a urinary tract infection.", {"entities": [(20, 45, "CONDITION")]}),
    ("The patient exhibits symptoms of chronic fatigue syndrome.", {"entities": [(38, 66, "CONDITION")]}),
    ("She was diagnosed with multiple sclerosis last year.", {"entities": [(24, 43, "CONDITION")]}),
    ("The patient has a history of rheumatoid arthritis.", {"entities": [(31, 55, "CONDITION")]}),
    ("John had a serious case of meningitis.", {"entities": [(10, 19, "CONDITION")]}),
    ("She experiences regular episodes of vertigo.", {"entities": [(30, 36, "CONDITION")]}),
    ("He was treated for kidney stones last summer.", {"entities": [(20, 32, "CONDITION")]}),
    ("Chronic obstructive pulmonary disease is common among smokers.", {"entities": [(0, 40, "CONDITION")]}),
    ("They are researching the effects of Alzheimer's disease.", {"entities": [(36, 54, "CONDITION")]}),
    ("Her diagnosis included hypertension and hyperlipidemia.", {"entities": [(18, 30, "CONDITION"), (35, 50, "CONDITION")]}),

    # Mixed entities
    ("Dr. Patel noted that Michael's asthma was getting worse.", {"entities": [(0, 6, "PERSON"), (15, 21, "PERSON"), (31, 37, "CONDITION")]}),
    ("The study included patients suffering from fibromyalgia.", {"entities": [(34, 48, "CONDITION")]}),
    ("Emily has been diagnosed with lupus.", {"entities": [(0, 5, "PERSON"), (22, 27, "CONDITION")]}),
    ("John Doe works at TechCorp and suffers from depression.", {"entities": [(0, 8, "PERSON"), (26, 34, "ORG"), (41, 51, "CONDITION")]}),
    ("Sara experienced a mild concussion during the game.", {"entities": [(0, 4, "PERSON"), (28, 38, "CONDITION")]}),
    ("The hospital treats various conditions, including PTSD.", {"entities": [(35, 39, "CONDITION")]}),
    ("He went to see Dr. Wong for his chronic migraines.", {"entities": [(27, 32, "PERSON"), (38, 46, "CONDITION")]}),
    
    # More examples for CONDITIONS
    ("Chronic pain can often lead to depression.", {"entities": [(0, 13, "CONDITION"), (31, 40, "CONDITION")]}),
    ("She has been diagnosed with bipolar disorder.", {"entities": [(33, 50, "CONDITION")]}),
    ("Asthma can be triggered by allergens.", {"entities": [(0, 6, "CONDITION")]}),
    ("He was treated for pancreatitis after his surgery.", {"entities": [(20, 34, "CONDITION")]}),
    ("The patient is suffering from sleep apnea.", {"entities": [(32, 42, "CONDITION")]}),
    ("She has a family history of breast cancer.", {"entities": [(36, 42, "CONDITION")]}),
    ("His chronic kidney disease requires regular monitoring.", {"entities": [(0, 33, "CONDITION")]}),
    ("Patients with schizophrenia may need lifelong treatment.", {"entities": [(17, 30, "CONDITION")]}),
    ("He has been managing his hypertension with medication.", {"entities": [(36, 48, "CONDITION")]}),
    ("She underwent surgery for ovarian cysts.", {"entities": [(29, 43, "CONDITION")]}),
    
    # More variations
    ("Diabetes can lead to various complications.", {"entities": [(0, 7, "CONDITION")]}),
    ("He suffers from chronic sinusitis.", {"entities": [(19, 32, "CONDITION")]}),
    ("Her treatment plan includes therapy for PTSD.", {"entities": [(32, 36, "CONDITION")]}),
    ("The doctor warned about the risks of heart failure.", {"entities": [(42, 55, "CONDITION")]}),
    ("He is undergoing treatment for skin eczema.", {"entities": [(33, 39, "CONDITION")]}),
    ("Patients diagnosed with depression often require therapy.", {"entities": [(25, 34, "CONDITION")]}),
    ("He is allergic to penicillin, which can cause anaphylaxis.", {"entities": [(33, 43, "CONDITION")]}),
    ("She has been feeling unwell due to chronic fatigue.", {"entities": [(30, 47, "CONDITION")]}),

]

nlp = spacy.load("en_core_web_sm_with_medical_terminology")

# Get the NER component
ner = nlp.get_pipe("ner")

# Add new label for medical conditions
ner.add_label("CONDITION")

# Disable all other pipeline components except NER
pipe_exceptions = ["ner"]
other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]

# Train the model
with nlp.disable_pipes(*other_pipes):  # Only train NER
    optimizer = nlp.resume_training()

    for itn in range(30):
        random.shuffle(trainingData)  # Shuffle the training data
        losses = {}
        for text, annotations in trainingData:
            doc = nlp.make_doc(text)  # Create a Doc object
            example = Example.from_dict(doc, annotations)  # Create an Example object
            nlp.update([example], losses=losses, drop=0.35)  # Update the model
        print(f"Iteration {itn}, Losses: {losses}")

# Save the updated model
nlp.to_disk("en_core_web_sm_with_medical_terminology")