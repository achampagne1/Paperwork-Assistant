import spacy
import random
from spacy import util
from spacy.tokens import Doc
from spacy.training import Example
from spacy.language import Language

def customizing_pipeline_component(nlp: Language):
    # NOTE: Starting from Spacy 3.0, training via Python API was changed. For information see - https://spacy.io/usage/v3#migrating-training-python
    train_data = [
        ("I have diabetes.",[(7, 15, "CONDITION")]),
        ("The patient was diagnosed with diabetes.", [(31, 39, "CONDITION")]),
        ("She has been suffering from hypertension for years.", [(28, 40, "CONDITION")]),
        ("He was admitted due to a severe asthma attack.", [(25, 45, "CONDITION")]),
        ("She was treated for pneumonia last month.",[(20, 29, "CONDITION")]),
        ("The patient has a history of heart disease.",[(29, 42, "CONDITION")]),
        ("He is taking medication for depression.",[(28, 38, "CONDITION")]),
        ("The primary symptom is chronic fatigue syndrome.",[(23, 47, "CONDITION")]),
        ("She was diagnosed with arthritis last year.",[(23, 32, "CONDITION")]),
        ("He has experienced severe migraines recently.",[(26, 35, "CONDITION")]),
        ("The doctor prescribed medication for epilepsy.",[(37, 45, "CONDITION")]),
        ("She was treated for a common cold.",[(22, 33, "CONDITION")]),
        ("He has a history of chronic obstructive pulmonary disease.",[(20, 57, "CONDITION")]),
        ("She developed symptoms of hypothyroidism.",[(26, 40, "CONDITION")]),
        ("The patient suffers from irritable bowel syndrome.",[(25, 49, "CONDITION")]),
        ("He was diagnosed with Alzheimer's disease last year.",[(22, 41, "CONDITION")]),
        ("John Doe was diagnosed with diabetes.",[(0, 8, "PERSON"), (28, 36, "CONDITION")]),
        ("Jane Smith has been suffering from hypertension for years.",[(0, 10, "PERSON"), (35, 47, "CONDITION")]),
        ("Dr. Brown was admitted due to a severe asthma attack.",[(0, 9, "PERSON"), (32, 52, "CONDITION")]),
        ("She was treated for pneumonia last month.",[(20, 29, "CONDITION")]),
        ("The patient has a history of heart disease.",[(29, 42, "CONDITION")]),

        #for recognizing pdf fields
        ("name:",[(0, 4, "PERSON")]),
        ("write your name:",[(6, 15, "PERSON")]),
        ("what is your name?",[(8, 17, "PERSON")]),
        ("1. your name",[(3, 12, "PERSON")]),
        ("Where are you from:",[(0, 18, "GPE")]),
        ("What is your address",[(13, 20, "GPE")]),
        ("address",[(0, 7, "GPE")]),
        ("Date:",[(0, 4, "DATE")]),
        ("what is your birthday",[(13, 21, "DATE")]),
        ("location",[(0, 8, "GPE")]),
        ('I like red oranges', [])
    ]

    # Result before training
    print("\nResult BEFORE training:")
    doc = nlp("I have diabetes.")
    for ent in doc.ents:
        print(ent.text, ent.label_)

    # Disable all pipe components except 'ner'
    disabled_pipes = []
    for pipe_name in nlp.pipe_names:
        if pipe_name != 'ner':
            nlp.disable_pipes(pipe_name)
            disabled_pipes.append(pipe_name)

    print("   Training ...")
    optimizer = nlp.resume_training()
    for _ in range(25):
        random.shuffle(train_data)
        for raw_text, entity_offsets in train_data:
            doc = nlp.make_doc(raw_text)
            example = Example.from_dict(doc, {"entities": entity_offsets})
            nlp.update([example], sgd=optimizer)
        print(_)

    # Enable all previously disabled pipe components
    for pipe_name in disabled_pipes:
        nlp.enable_pipe(pipe_name)

    # Result after training
    print(f"Result AFTER training:")
    doc = nlp("i have diabetes")
    for ent in doc.ents:
        print(ent.text, ent.label_)
    doc = nlp("John Doe")
    for ent in doc.ents:
        print(ent.text, ent.label_)
    
    nlp.to_disk("en_core_web_sm_with_medical_terminology")

def main():
    nlp = spacy.load('en_core_web_sm')
    customizing_pipeline_component(nlp)


if __name__ == '__main__':
    main()