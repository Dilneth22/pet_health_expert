import streamlit as st
from experta import Fact
from expert_system import PetHealth
from utils import find_closest_symptom
from explanation import explain_diagnosis

# --- NEW: This map connects questions to the Fact they create ---
# This makes it easy to add new questions and rules.
question_to_fact_map = {
    "Is there blood in the stool?": Fact(symptom="blood_in_stool"),
    "Is the cough persistent and harsh?": Fact(symptom="harsh_cough"),
    "Is the pet also experiencing diarrhea?": Fact(symptom="diarrhea"),
    "Is the pet also vomiting?": Fact(symptom="vomiting"),
    "Is the pet also sneezing or lethargic?": Fact(symptom="sneezing"), # 'sneezing' implies the other
    "Is the pet also vomiting or experiencing diarrhea?": Fact(symptom="vomiting"), # 'vomiting' implies the other
    "Are you seeing any hair loss or red skin patches?": Fact(symptom="hair_loss"),
}
# -------------------------------------------------------------


# Initialize session state
if 'expert_system' not in st.session_state:
    st.session_state.expert_system = PetHealth()
    st.session_state.expert_system.reset()
    st.session_state.selected_symptoms = []
    st.session_state.current_questions = []
    st.session_state.diagnosis_made = False
    st.session_state.final_diagnosis = None

# Page config
st.set_page_config(page_title="Pet Health Expert System", page_icon="🐾")
st.title("Pet Health Expert System 🐾")

# Sidebar for symptoms selection
with st.sidebar:
    st.header("Select Symptoms")
    
    # Dropdown for predefined symptoms
    available_symptoms = [""] + [s for s in PetHealth.symptoms_list if s not in st.session_state.selected_symptoms]
    selected_symptom = st.selectbox(
        "Choose from common symptoms:",
        available_symptoms
    )
    
    # Custom symptom input with fuzzy matching
    custom_symptom = st.text_input("Or enter a custom symptom:")
    
    if custom_symptom:
        matched_symptom, confidence = find_closest_symptom(
            custom_symptom, 
            available_symptoms
        )
        if matched_symptom:
            st.info(f"Did you mean: {matched_symptom}? (Match confidence: {confidence}%)")
            if st.button("Yes, add this symptom"):
                selected_symptom = matched_symptom
                custom_symptom = "" # Clear input

    # Add selected symptom to the system
    if selected_symptom:
        st.session_state.selected_symptoms.append(selected_symptom)
        st.session_state.expert_system.declare(Fact(symptom=selected_symptom))
        st.rerun()

# Main content area
st.header("Current Symptoms")
if st.session_state.selected_symptoms:
    cols = st.columns(3)
    for i, symptom in enumerate(st.session_state.selected_symptoms):
        cols[i % 3].markdown(f"• `{symptom}`")
else:
    st.info("No symptoms selected yet. Please select symptoms from the sidebar.")

# Get expert opinion or add more symptoms
if st.session_state.selected_symptoms and not st.session_state.current_questions and not st.session_state.diagnosis_made:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Get Expert Opinion"):
            st.session_state.current_questions = st.session_state.expert_system.get_next_questions()
            if not st.session_state.current_questions:
                # No more questions, get the final diagnosis
                diagnosis_data = st.session_state.expert_system.get_diagnosis()
                if diagnosis_data.get('diagnosis'):
                    st.session_state.diagnosis_made = True
                    st.session_state.final_diagnosis = diagnosis_data
                else:
                    # No diagnosis found even after running
                    st.session_state.diagnosis_made = True
                    st.session_state.final_diagnosis = None # Set to None to show error
            st.rerun()
    
    with col2:
        if st.button("Clear All Symptoms"):
            st.session_state.expert_system.reset()
            st.session_state.selected_symptoms = []
            st.session_state.current_questions = []
            st.session_state.diagnosis_made = False
            st.session_state.final_diagnosis = None
            st.rerun()

# Display follow-up questions
if st.session_state.current_questions:
    st.header("Additional Questions")
    st.write("Please answer the following to help narrow down the diagnosis:")
    
    question = st.session_state.current_questions[0] # Get the first question
    st.subheader(f"❓ {question}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"Yes", key=f"yes_{question}", use_container_width=True, type="primary"):
            st.session_state.expert_system.questions_asked.append(question)
            
            # --- UPDATED LOGIC ---
            # Use the map to find which Fact to add
            fact_to_add = question_to_fact_map.get(question)
            if fact_to_add:
                st.session_state.expert_system.declare(fact_to_add)
            # ---------------------

            st.session_state.current_questions.pop(0) # Remove this question
            
            # Check for more questions or get diagnosis
            new_questions = st.session_state.expert_system.get_next_questions()
            if new_questions:
                st.session_state.current_questions.extend(new_questions)
            else:
                diagnosis_data = st.session_state.expert_system.get_diagnosis()
                st.session_state.diagnosis_made = True
                st.session_state.final_diagnosis = diagnosis_data.get('diagnosis') and diagnosis_data

            st.rerun()

    with col2:
        if st.button(f"No", key=f"no_{question}", use_container_width=True):
            st.session_state.expert_system.questions_asked.append(question)
            st.session_state.current_questions.pop(0) # Remove this question

            # Check for more questions or get diagnosis
            new_questions = st.session_state.expert_system.get_next_questions()
            if new_questions:
                st.session_state.current_questions.extend(new_questions)
            else:
                diagnosis_data = st.session_state.expert_system.get_diagnosis()
                st.session_state.diagnosis_made = True
                st.session_state.final_diagnosis = diagnosis_data.get('diagnosis') and diagnosis_data

            st.rerun()

# Display final diagnosis and explanation
if st.session_state.diagnosis_made:
    st.header("Diagnosis Results")
    
    if st.session_state.final_diagnosis:
        diagnosis_data = st.session_state.final_diagnosis
        st.subheader(f"Diagnosis: {diagnosis_data['diagnosis']}")
        st.write(f"Confidence: {diagnosis_data['confidence']*100:.0f}%")
        
        with st.spinner("Generating detailed explanation..."):
            explanation = explain_diagnosis(diagnosis_data)
            st.markdown(explanation)
            
        st.warning("⚠️ This is an AI-assisted diagnosis. Always consult with a veterinarian for proper medical advice.")
    else:
        st.error("I was unable to determine a diagnosis based on the symptoms provided. Please consult a veterinarian.")
        st.warning("⚠️ This is an AI-assisted diagnosis. Always consult with a veterinarian for proper medical advice.")