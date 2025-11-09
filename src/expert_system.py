from experta import *
from collections.abc import Mapping
from typing import List, Dict

class PetHealth(KnowledgeEngine):
    # Common pet symptoms
    symptoms_list = [
        "vomiting", "diarrhea", "lethargy", "loss of appetite", "coughing",
        "sneezing", "limping", "excessive thirst", "frequent urination",
        "scratching", "hair loss", "bad breath", "weight loss", "fever",
        "difficulty breathing"
    ]

    # Knowledge base facts and rules
    @DefFacts()
    def _initial_facts(self):
        yield Fact(action="start_diagnosis")

    @Rule(Fact(action="start_diagnosis"))
    def init_diagnosis(self):
        self.declared_symptoms = []
        self.questions_asked = []
        self.diagnosis = None
        self.confidence = 0.0

    @Rule(Fact(symptom=MATCH.s))
    def record_symptom(self, s):
        if s not in self.declared_symptoms:
            self.declared_symptoms.append(s)

    # Example diagnostic rules
    @Rule(
        AND(
            Fact(symptom="vomiting"),
            Fact(symptom="diarrhea")
        )
    )
    def possible_gastroenteritis(self):
        self.diagnosis = "Gastroenteritis"
        self.confidence = 0.7
        if "blood_in_stool" not in self.questions_asked:
            self.questions_to_ask = ["Is there blood in the stool?", "When was the last meal?"]

    @Rule(
        AND(
            Fact(symptom="coughing"),
            Fact(symptom="sneezing"),
            Fact(symptom="lethargy")
        )
    )
    def possible_respiratory_infection(self):
        self.diagnosis = "Respiratory Infection"
        self.confidence = 0.6
        if "temperature" not in self.questions_asked:
            self.questions_to_ask = ["Does your pet have a fever?", "How long has the coughing persisted?"]

    # Add more rules based on symptoms combinations...

    def get_next_questions(self) -> List[str]:
        """Return follow-up questions based on current symptoms."""
        self.run()
        questions = getattr(self, 'questions_to_ask', [])
        self.questions_to_ask = []
        return questions

    def get_diagnosis(self) -> Dict:
        """Return current diagnosis and confidence level."""
        return {
            'diagnosis': self.diagnosis,
            'confidence': self.confidence,
            'symptoms': self.declared_symptoms
        }