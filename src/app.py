import streamlit as st
from experta import Fact
from expert_system import PetHealth
from utils import find_closest_symptom
from explanation import explain_diagnosis

# Initialize session state
if 'expert_system' not in st.session_state:
    st.session_state.expert_system = PetHealth()
    st.session_state.expert_system.reset()
    st.session_state.selected_symptoms = []
    st.session_state.current_questions = []
    st.session_state.diagnosis_made = False

# Page config
st.set_page_config(page_title="Pet Health Expert System", page_icon="🐾")
st.title("Pet Health Expert System 🐾")

# Sidebar for symptoms selection
with st.sidebar:
    st.header("Select Symptoms")
    
    # Dropdown for predefined symptoms
    selected_symptom = st.selectbox(
        "Choose from common symptoms:",
        [""] + [s for s in PetHealth.symptoms_list if s not in st.session_state.selected_symptoms]
    )
    
    # Custom symptom input with fuzzy matching
    custom_symptom = st.text_input("Or enter a custom symptom:")
    
    if custom_symptom:
        matched_symptom, confidence = find_closest_symptom(
            custom_symptom, 
            [s for s in PetHealth.symptoms_list if s not in st.session_state.selected_symptoms]
        )
        if matched_symptom:
            st.info(f"Did you mean: {matched_symptom}? (Match confidence: {confidence}%)")
            if st.button("Yes, add this symptom"):
                selected_symptom = matched_symptom

    # Add selected symptom to the system
    if selected_symptom:
        st.session_state.selected_symptoms.append(selected_symptom)
        st.session_state.expert_system.declare(Fact(symptom=selected_symptom))
        st.experimental_rerun()

# Main content area
st.header("Current Symptoms")
if st.session_state.selected_symptoms:
    for symptom in st.session_state.selected_symptoms:
        st.write(f"• {symptom}")
else:
    st.info("No symptoms selected yet. Please select symptoms from the sidebar.")

# Get expert opinion or add more symptoms
if st.session_state.selected_symptoms:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Get Expert Opinion"):
            st.session_state.current_questions = st.session_state.expert_system.get_next_questions()
            if st.session_state.current_questions:
                st.session_state.diagnosis_made = False
            else:
                diagnosis_data = st.session_state.expert_system.get_diagnosis()
                if diagnosis_data['diagnosis']:
                    st.session_state.diagnosis_made = True
                    st.session_state.final_diagnosis = diagnosis_data
    
    with col2:
        if st.button("Clear All Symptoms"):
            st.session_state.expert_system.reset()
            st.session_state.selected_symptoms = []
            st.session_state.current_questions = []
            st.session_state.diagnosis_made = False
            st.experimental_rerun()

# Display follow-up questions
if st.session_state.current_questions:
    st.header("Additional Questions")
    for question in st.session_state.current_questions:
        if st.button(question):
            st.session_state.expert_system.questions_asked.append(question)
            # You can add more specific logic here based on the answers
            diagnosis_data = st.session_state.expert_system.get_diagnosis()
            if diagnosis_data['diagnosis']:
                st.session_state.diagnosis_made = True
                st.session_state.final_diagnosis = diagnosis_data

# Display final diagnosis and explanation
if st.session_state.diagnosis_made:
    st.header("Diagnosis Results")
    diagnosis_data = st.session_state.final_diagnosis
    
    st.subheader(f"Diagnosis: {diagnosis_data['diagnosis']}")
    st.write(f"Confidence: {diagnosis_data['confidence']*100:.0f}%")
    
    with st.expander("See detailed explanation"):
        explanation = explain_diagnosis(diagnosis_data)
        st.write(explanation)
        
    st.warning("⚠️ This is an AI-assisted diagnosis. Always consult with a veterinarian for proper medical advice.")