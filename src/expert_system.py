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

    def __init__(self):
        super().__init__()
        # Manually initialize all state variables to prevent crashes
        self.declared_symptoms = []
        self.questions_asked = []
        self.diagnosis = None
        self.confidence = 0.0
        self.questions_to_ask = []

    # Knowledge base facts and rules
    @DefFacts()
    def _initial_facts(self):
        yield Fact(action="start_diagnosis")

    # High priority rule to reset the engine
    @Rule(Fact(action="start_diagnosis"),
          salience=100) 
    def init_diagnosis(self):
        self.declared_symptoms = []
        self.questions_asked = []
        self.diagnosis = None
        self.confidence = 0.0
        self.questions_to_ask = []

    @Rule(Fact(symptom=MATCH.s))
    def record_symptom(self, s):
        if s not in self.declared_symptoms:
            self.declared_symptoms.append(s)

    # --- NEW SINGLE-SYMPTOM RULES (DECISION TREE LOGIC) ---
    # These have low priority (salience=5) and run if no other rule matches.
    # They ask the *next logical question* to move down the decision tree.

    @Rule(Fact(symptom="vomiting"),
          NOT(Fact(symptom="diarrhea")),
          salience=5)
    def ask_about_vomiting(self):
        self._add_question("Is the pet also experiencing diarrhea?")

    @Rule(Fact(symptom="diarrhea"),
          NOT(Fact(symptom="vomiting")),
          salience=5)
    def ask_about_diarrhea(self):
        self._add_question("Is the pet also vomiting?")

    @Rule(Fact(symptom="coughing"),
          NOT(Fact(symptom="sneezing")),
          NOT(Fact(symptom="harsh_cough")),
          salience=5)
    def ask_about_coughing(self):
        self._add_question("Is the cough persistent and harsh?")
        self._add_question("Is the pet also sneezing or lethargic?")

    @Rule(Fact(symptom="lethargy"),
          NOT(Fact(symptom="vomiting")),
          NOT(Fact(symptom="coughing")),
          salience=5)
    def ask_about_lethargy(self):
        self._add_question("Is the pet also vomiting or experiencing diarrhea?")
        self._add_question("Is the pet also coughing or sneezing?")

    @Rule(Fact(symptom="scratching"),
          NOT(Fact(symptom="hair_loss")),
          salience=5)
    def ask_about_scratching(self):
        self._add_question("Are you seeing any hair loss or red skin patches?")

    # --- DIAGNOSIS RULES (HIGHER PRIORITY) ---

    # Rule 1: Base Gastroenteritis
    @Rule(
        AND(
            Fact(symptom="vomiting"),
            Fact(symptom="diarrhea"),
            NOT(Fact(symptom="blood_in_stool")) 
        ),
        salience=10 
    )
    def possible_gastroenteritis(self):
        self.diagnosis = "Gastroenteritis"
        self.confidence = 0.7
        self._add_question("Is there blood in the stool?")

    # Rule 2: More specific HGE
    @Rule(
        AND(
            Fact(symptom="vomiting"),
            Fact(symptom="diarrhea"),
            Fact(symptom="blood_in_stool") 
        ),
        salience=20 
    )
    def possible_hemorrhagic_gastroenteritis(self):
        self.diagnosis = "Hemorrhagic Gastroenteritis (HGE)"
        self.confidence = 0.9
        self._remove_question("Is there blood in the stool?")

    # Rule 3: Base Respiratory Infection
    @Rule(
        AND(
            Fact(symptom="coughing"),
            Fact(symptom="sneezing"),
            Fact(symptom="lethargy"),
            NOT(Fact(symptom="harsh_cough"))
        ),
        salience=10
    )
    def possible_respiratory_infection(self):
        self.diagnosis = "Respiratory Infection"
        self.confidence = 0.6
        self._add_question("Is the cough persistent and harsh?")

    # Rule 4: More specific Kennel Cough
    @Rule(
        AND(
            Fact(symptom="coughing"),
            Fact(symptom="harsh_cough")
        ),
        salience=20
    )
    def possible_kennel_cough(self):
        self.diagnosis = "Kennel Cough (Infectious Tracheobronchitis)"
        self.confidence = 0.85
        self._remove_question("Is the cough persistent and harsh?")
        self._remove_question("Is the pet also sneezing or lethargic?")

    # Rule 5: Skin issue
    @Rule(
        AND(
            Fact(symptom="scratching"),
            Fact(symptom="hair_loss")
        ),
        salience=10
    )
    def possible_skin_allergy(self):
        self.diagnosis = "Skin Allergy or Parasites"
        self.confidence = 0.6
        self._remove_question("Are you seeing any hair loss or red skin patches?")


    # --- HELPER METHODS ---
    
    def _add_question(self, question: str):
        """Helper to add a question if it hasn't been asked."""
        if question not in self.questions_asked and question not in self.questions_to_ask:
            self.questions_to_ask.append(question)

    def _remove_question(self, question: str):
        """Helper to remove a question if it's now irrelevant."""
        if question in self.questions_to_ask:
            self.questions_to_ask.remove(question)
            
    def get_next_questions(self) -> List[str]:
        """Return follow-up questions based on current symptoms."""
        self.run()
        # Return a copy of the list and clear the original
        questions = list(set(self.questions_to_ask)) # Use set to remove duplicates
        self.questions_to_ask.clear()
        return questions

    def get_diagnosis(self) -> Dict:
        """Return current diagnosis and confidence level."""
        self.run() # Run the engine one last time
        return {
            'diagnosis': self.diagnosis,
            'confidence': self.confidence,
            'symptoms': self.declared_symptoms
        }