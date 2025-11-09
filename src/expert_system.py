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
        # --- CHANGED TO A LIST ---
        self.diagnoses = [] 
        # -------------------------
        self.declared_symptoms = []
        self.questions_asked = []
        self.questions_to_ask = []

    # Knowledge base facts and rules
    @DefFacts()
    def _initial_facts(self):
        yield Fact(action="start_diagnosis")

    # High priority rule to reset the engine
    @Rule(Fact(action="start_diagnosis"),
          salience=100) 
    def init_diagnosis(self):
        # --- CHANGED TO A LIST ---
        self.diagnoses = []
        # -------------------------
        self.declared_symptoms = []
        self.questions_asked = []
        self.questions_to_ask = []

    @Rule(Fact(symptom=MATCH.s))
    def record_symptom(self, s):
        if s not in self.declared_symptoms:
            self.declared_symptoms.append(s)

    # --- COMPREHENSIVE SINGLE-SYMPTOM RULES (DECISION TREE LOGIC) ---
    # (These are unchanged, they just add questions)
    
    @Rule(Fact(symptom="vomiting"), NOT(Fact(symptom="diarrhea")), salience=5)
    def ask_about_vomiting(self):
        self._add_question("Is the pet also experiencing diarrhea?")

    @Rule(Fact(symptom="diarrhea"), NOT(Fact(symptom="vomiting")), salience=5)
    def ask_about_diarrhea(self):
        self._add_question("Is the pet also vomiting?")
        
    @Rule(Fact(symptom="coughing"), NOT(Fact(symptom="sneezing")), NOT(Fact(symptom="harsh_cough")), salience=5)
    def ask_about_coughing(self):
        self._add_question("Is the cough persistent and harsh?")
        self._add_question("Is the pet also sneezing?")

    @Rule(Fact(symptom="lethargy"), NOT(Fact(symptom="vomiting")), NOT(Fact(symptom="coughing")), NOT(Fact(symptom="fever")), salience=5)
    def ask_about_lethargy(self):
        self._add_question("Is the pet also experiencing loss of appetite?")
        self._add_question("Is the pet also vomiting?")

    @Rule(Fact(symptom="scratching"), NOT(Fact(symptom="hair_loss")), salience=5)
    def ask_about_scratching(self):
        self._add_question("Are you seeing any hair loss or red skin patches?")

    @Rule(Fact(symptom="loss of appetite"), NOT(Fact(symptom="vomiting")), NOT(Fact(symptom="lethargy")), salience=5)
    def ask_about_appetite(self):
        self._add_question("Is the pet also vomiting?")
        self._add_question("Is the pet also lethargic?")

    @Rule(Fact(symptom="sneezing"), NOT(Fact(symptom="coughing")), salience=5)
    def ask_about_sneezing(self):
        self._add_question("Is the pet also coughing?")

    @Rule(Fact(symptom="limping"), NOT(Fact(symptom="visible_injury")), salience=5)
    def ask_about_limping(self):
        self._add_question("Is there any visible injury or swelling on the leg?")

    @Rule(Fact(symptom="excessive thirst"), NOT(Fact(symptom="frequent_urination")), salience=5)
    def ask_about_thirst(self):
        self._add_question("Is the pet also urinating more than usual?")

    @Rule(Fact(symptom="frequent urination"), NOT(Fact(symptom="excessive_thirst")), salience=5)
    def ask_about_urination(self):
        self._add_question("Is the pet also drinking more water than usual?")
    
    @Rule(Fact(symptom="hair loss"), NOT(Fact(symptom="scratching")), salience=5)
    def ask_about_hair_loss(self):
        self._add_question("Is the pet also scratching a lot?")

    @Rule(Fact(symptom="bad breath"), NOT(Fact(symptom="dental_issue")), NOT(Fact(symptom="vomiting")), salience=5)
    def ask_about_bad_breath(self):
        self._add_question("Is this accompanied by vomiting?")

    @Rule(Fact(symptom="weight loss"), NOT(Fact(symptom="loss_of_appetite")), NOT(Fact(symptom="diarrhea")), salience=5)
    def ask_about_weight_loss(self):
        self._add_question("Is the pet also experiencing loss of appetite?")

    @Rule(Fact(symptom="fever"), NOT(Fact(symptom="lethargy")), NOT(Fact(symptom="coughing")), salience=5)
    def ask_about_fever(self):
        self._add_question("Is the pet also lethargic?")

    @Rule(Fact(symptom="difficulty breathing"), NOT(Fact(symptom="coughing")), NOT(Fact(symptom="lethargy")), salience=5)
    def ask_about_breathing(self):
        self._add_question("Is this accompanied by coughing or severe lethargy?")
        # --- LOGIC CHANGED: APPEND TO LIST ---
        self.diagnoses.append({
            "diagnosis": "Severe Respiratory Distress",
            "confidence": 0.8
        })

    # --- DIAGNOSIS RULES (HIGHER PRIORITY) ---
    # --- ALL RULES NOW APPEND TO THE LIST ---

    # Rule 1: Base Gastroenteritis
    @Rule(AND(Fact(symptom="vomiting"), Fact(symptom="diarrhea"), NOT(Fact(symptom="blood_in_stool"))), salience=10)
    def possible_gastroenteritis(self):
        self.diagnoses.append({
            "diagnosis": "Gastroenteritis",
            "confidence": 0.7
        })
        self._add_question("Is there blood in the stool?")
        self._remove_question("Is the pet also experiencing diarrhea?")

    # Rule 2: More specific HGE
    @Rule(AND(Fact(symptom="vomiting"), Fact(symptom="diarrhea"), Fact(symptom="blood_in_stool")), salience=20)
    def possible_hemorrhagic_gastroenteritis(self):
        self.diagnoses.append({
            "diagnosis": "Hemorrhagic Gastroenteritis (HGE)",
            "confidence": 0.9
        })
        self._remove_question("Is there blood in the stool?")
        self._remove_question("Is the pet also experiencing diarrhea?")

    # Rule 3: Base Respiratory Infection
    @Rule(AND(Fact(symptom="coughing"), Fact(symptom="sneezing"), NOT(Fact(symptom="harsh_cough"))), salience=10)
    def possible_respiratory_infection(self):
        self.diagnoses.append({
            "diagnosis": "Respiratory Infection",
            "confidence": 0.6
        })
        self._add_question("Is the cough persistent and harsh?")
        self._remove_question("Is the pet also sneezing?")

    # Rule 4: More specific Kennel Cough
    @Rule(AND(Fact(symptom="coughing"), Fact(symptom="harsh_cough")), salience=20)
    def possible_kennel_cough(self):
        self.diagnoses.append({
            "diagnosis": "Kennel Cough (Infectious Tracheobronchitis)",
            "confidence": 0.85
        })
        self._remove_question("Is the cough persistent and harsh?")
        self._remove_question("Is the pet also sneezing?")

    # Rule 5: Skin issue
    @Rule(AND(Fact(symptom="scratching"), Fact(symptom="hair_loss")), salience=10)
    def possible_skin_allergy(self):
        self.diagnoses.append({
            "diagnosis": "Skin Allergy or Parasites",
            "confidence": 0.6
        })
        self._remove_question("Are you seeing any hair loss or red skin patches?")

    # Rule 6: Diabetes/Kidney Issue
    @Rule(AND(Fact(symptom="excessive thirst"), Fact(symptom="frequent_urination")), salience=10)
    def possible_diabetes_kidney(self):
        self.diagnoses.append({
            "diagnosis": "Possible Diabetes or Kidney Issue",
            "confidence": 0.7
        })
        self._add_question("Is the pet also experiencing loss of appetite?")
        self._remove_question("Is the pet also drinking more water than usual?")

    # Rule 7: Physical Injury
    @Rule(AND(Fact(symptom="limping"), Fact(symptom="visible_injury")), salience=20)
    def possible_injury(self):
        self.diagnoses.append({
            "diagnosis": "Physical Injury (Sprain or Fracture)",
            "confidence": 0.9
        })
        self._remove_question("Is there any visible injury or swelling on the leg?")

    # --- HELPER METHODS ---
    
    def _add_question(self, question: str):
        if question not in self.questions_asked and question not in self.questions_to_ask:
            self.questions_to_ask.append(question)

    def _remove_question(self, question: str):
        if question in self.questions_to_ask:
            self.questions_to_ask.remove(question)
            
    def get_next_questions(self) -> List[str]:
        self.run()
        questions = list(dict.fromkeys(self.questions_to_ask)) # De-duplicate
        self.questions_to_ask.clear()
        return questions

    # --- GET_DIAGNOSIS IS NOW UPDATED ---
    def get_diagnosis(self) -> Dict:
        """Return a sorted list of all possible diagnoses."""
        self.run() 
        # De-duplicate the list of dictionaries
        unique_diagnoses = list({d['diagnosis']: d for d in self.diagnoses}.values())
        # Sort the list by confidence, highest first
        sorted_diagnoses = sorted(unique_diagnoses, key=lambda d: d['confidence'], reverse=True)
        
        return {
            'diagnoses': sorted_diagnoses, # Note: plural
            'symptoms': self.declared_symptoms
        }