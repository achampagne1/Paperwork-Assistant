import spacy
import random
from spacy import util
from spacy.tokens import Doc
from spacy.training import Example
from spacy.language import Language

def customizing_pipeline_component(nlp: Language):
    # NOTE: Starting from Spacy 3.0, training via Python API was changed. For information see - https://spacy.io/usage/v3#migrating-training-python
    train_data = [
        ("John Doe was diagnosed with diabetes.",[(0, 8, "PERSON"), (28, 36, "CONDITION")]),
        ("Jane Smith has been suffering from hypertension for years.", [(0, 10, "PERSON"), (35, 47, "CONDITION")]),
        ("Dr. Brown was admitted due to a severe asthma attack.", [(0, 9, "PERSON"), (32, 52, "CONDITION")]),
        ("The patient was treated for pneumonia last month.", [(28, 37, "CONDITION")]),
        ("The doctor diagnosed Amy with heart disease.", [(21, 24, "PERSON"), (30, 43, "CONDITION")]),
        ("Elena Martinez is recovering from a mild stroke.", [(0, 14, "PERSON"), (36, 47, "CONDITION")]),
        ("Michael's chronic bronchitis requires regular treatment.", [(0, 7, "PERSON"), (10, 28, "CONDITION")]),
        ("He has been struggling with anxiety for months.", [(28, 35, "CONDITION")]),
        ("Dr. Lee specializes in treating arthritis.", [(0, 7, "PERSON"), (32, 41, "CONDITION")]),
        ("Linda is managing her symptoms of depression.", [(0, 5, "PERSON"), (34, 44, "CONDITION")]),
        ("He was treated for a urinary tract infection.", [(21, 44, "CONDITION")]),
        ("The patient exhibits symptoms of chronic fatigue syndrome.", [(33, 57, "CONDITION")]),
        ("She was diagnosed with multiple sclerosis last year.", [(23, 41, "CONDITION")]),
        ("The patient has a history of rheumatoid arthritis.", [(29, 49, "CONDITION")]),
        ("he had a serious case of meningitis.", [(25, 35, "CONDITION")]),
        ("She experiences regular episodes of vertigo.", [(36, 43, "CONDITION")]),
        ("He was treated for kidney stones last summer.", [(19, 32, "CONDITION")]),
        ("Chronic obstructive pulmonary disease is common among smokers.", [(0, 37, "CONDITION")]),
        ("They are researching the effects of Alzheimer's disease.", [(36, 55, "CONDITION")]),
        ("Her diagnosis included hypertension and hyperlipidemia.", [(23, 35, "CONDITION"), (40, 54, "CONDITION")]),
        ("We have a meeting on 25th August 2022.",[(21, 37, "DATE")]),
        ("My appointment is on March 5th, 2021.",[(21, 36, "DATE")]),
        ("Google hired James Earl Jones last year.",[(0, 6, "ORG"), (13, 29, "PERSON")]),
        ("Mary Hannover started working at Microsoft in 2019.",[(0, 13, "PERSON"), (33, 42, "ORG"), (46, 50, "DATE")]),
        ("I live in New York City.",[(10, 23, "GPE")]),
        ("The conference is being held in London.",[(32, 38, "GPE")]),
        ("Joseph Beck is the CEO of the company.", [(0, 11, "PERSON")]),
        ("Barack Obama was the 44th president.", [(0, 12, "PERSON")]),
        ("Google is a multinational technology company.", [(0, 6, "ORG")]),
        ("She works for Microsoft.", [(14, 23, "ORG")]),
        ("He lives in New York City.", [(12, 25, "GPE")]),
        ("She is from France.", [(12, 18, "GPE")]),
        ("The meeting is on March 5th, 2021.", [(18, 33, "DATE")]),
        ("The date of today is June 12th", [(21, 30, "DATE")]),
        ("The event starts at 8:00 PM.", [(20, 27, "TIME")]),
        ("I will arrive by 6:30 AM tomorrow.", [(17, 33, "TIME")]),
        ("The car costs $40,000.", [(14, 21, "MONEY")]),
        ("They made a donation of $1,000,000.", [(24, 34, "MONEY")]),
        ("Mount Everest is the highest mountain in the world.", [(0, 13, "LOC")]),
        ("They sailed across the Atlantic Ocean.", [(23, 37, "LOC")]),
        ("The company is hosting the Super Bowl.", [(27, 37, "EVENT")]),
        ("The Olympic Games are held every four years.", [(4, 17, "EVENT")]),
        ("He just bought a new iPhone.", [(21, 27, "PRODUCT")]),
        ("I love my Tesla Model 3.", [(10, 23, "PRODUCT")]),
        ("She is fluent in French.", [(17, 23, "LANGUAGE")]),
        ("He speaks English and Spanish.", [(10, 17, "LANGUAGE"), (22, 29, "LANGUAGE")]),
        ("He was treated for a urinary tract infection.", [(21, 44, "CONDITION")]),
        ("The patient suffers from chronic fatigue syndrome.", [(25, 49, "CONDITION")]),
        ("The new GDPR regulation is in effect.", [(8, 12, "LAW")]),
        ("He violated the California Privacy Act.", [(16, 38, "LAW")]),
        ("I love The Great Gatsby.", [(7, 23, "WORK_OF_ART")]),
        ("We went to see Hamilton.", [(15, 23, "WORK_OF_ART")]),
        ("The Eiffel Tower is a famous landmark.", [(4, 16, "FAC")]),
        ("They arrived at Heathrow Airport.", [(16, 32, "FAC")]),
        ("The jar holds 500 milliliters of water.", [(14, 29, "QUANTITY")]),
        ("There are 200 grams of flour in the recipe.", [(10, 19, "QUANTITY")]),
        ("The interest rate is 5%.", [(21, 23, "PERCENT")]),
        ("He scored 95% on his final exam.", [(10, 13, "PERCENT")]),
        #("She finished in 2nd place.", [(16, 19, "ORDINAL")]),
        #("This is the 3rd time he has called.", [(12, 15, "ORDINAL")]),
        ("There were 200 people at the event.", [(11, 14, "CARDINAL")]),
        ("They sold 1,000 tickets in one day.", [(10, 15, "CARDINAL")]),

        #for recognizing pdf fields
        #("name:",[(0, 4, "PERSON")]),
        #("write your name:",[(6, 15, "PERSON")]),
        #("what is your name?",[(8, 17, "PERSON")]),
        #("1. your name",[(3, 12, "PERSON")]),
        #("Where are you from:",[(0, 18, "GPE")]),
        #("What is your address",[(13, 20, "GPE")]),
        #("address",[(0, 7, "GPE")]),
        #("Date:",[(0, 4, "DATE")]),
        #("what is your birthday",[(13, 21, "DATE")]),
        #("location",[(0, 8, "GPE")]),
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
    doc = nlp("my name is John Doe")
    for ent in doc.ents:
        print(ent.text, ent.label_)
    doc = nlp("Today is October 7th")
    for ent in doc.ents:
        print(ent.text, ent.label_)
    
    nlp.to_disk("en_core_web_sm_with_medical_terminology")

def main():
    nlp = spacy.load('en_core_web_sm')
    customizing_pipeline_component(nlp)


if __name__ == '__main__':
    main()