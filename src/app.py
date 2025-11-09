import streamlit as st
from experta import Fact
from expert_system import PetHealth
from utils import find_closest_symptom
from explanation import explain_diagnosis

# --- Map of questions to facts (unchanged) ---
question_to_fact_map = {
    "Is the pet also experiencing diarrhea?": Fact(symptom="diarrhea"),
    "Is the pet also vomiting?": Fact(symptom="vomiting"),
    "Is there blood in the stool?": Fact(symptom="blood_in_stool"),
    "Is the cough persistent and harsh?": Fact(symptom="harsh_cough"),
    "Is the pet also sneezing?": Fact(symptom="sneezing"),
    "Is the pet also coughing?": Fact(symptom="coughing"),
    "Is the pet also lethargic?": Fact(symptom="lethargy"),
    "Is the pet also experiencing loss of appetite?": Fact(symptom="loss_of_appetite"),
    "Is the pet running a fever?": Fact(symptom="fever"),
    "Are you seeing any hair loss or red skin patches?": Fact(symptom="hair_loss"),
    "Is the pet also scratching a lot?": Fact(symptom="scratching"),
    "Is the pet also drinking more water than usual?": Fact(symptom="excessive_thirst"),
    "Is the pet also urinating more than usual?": Fact(symptom="frequent_urination"),
    "Is there any visible injury or swelling on the leg?": Fact(symptom="visible_injury"),
    "Is this accompanied by dental issues or pawing at the mouth?": Fact(symptom="dental_issue"),
    "Has there been recent weight loss?": Fact(symptom="weight_loss"),
    "Is this accompanied by coughing or severe lethargy?": Fact(symptom="coughing"),
}

# Initialize session state
if 'expert_system' not in st.session_state:
    st.session_state.expert_system = PetHealth()
    st.session_state.expert_system.reset()
    st.session_state.selected_symptoms = []
    st.session_state.current_questions = []
    st.session_state.diagnosis_made = False
    # --- CHANGED: Store the whole result dict ---
    st.session_state.diagnosis_result = {} 

# Page config
st.set_page_config(page_title="Pet Health Expert System", page_icon="🐾")
st.title("Pet Health Expert System 🐾")

# Sidebar (Unchanged)
with st.sidebar:
    st.header("Select Symptoms")
    available_symptoms = [""] + [s for s in PetHealth.symptoms_list if s not in st.session_state.selected_symptoms]
    selected_symptom = st.selectbox("Choose from common symptoms:", available_symptoms)
    custom_symptom = st.text_input("Or enter a custom symptom:")
    
    if custom_symptom:
        matched_symptom, confidence = find_closest_symptom(custom_symptom, available_symptoms)
        if matched_symptom:
            st.info(f"Did you mean: {matched_symptom}? (Match confidence: {confidence}%)")
            if st.button("Yes, add this symptom"):
                selected_symptom = matched_symptom
                custom_symptom = "" 
    if selected_symptom:
        st.session_state.selected_symptoms.append(selected_symptom)
        st.session_state.expert_system.declare(Fact(symptom=selected_symptom))
        st.rerun()

# Main content area (Unchanged)
st.header("Current Symptoms")
if st.session_state.selected_symptoms:
    cols = st.columns(3)
    for i, symptom in enumerate(st.session_state.selected_symptoms):
        cols[i % 3].markdown(f"• `{symptom}`")
else:
    st.info("No symptoms selected yet. Please select symptoms from the sidebar.")

# --- BUTTON LOGIC UPDATED FOR NEW SESSION STATE ---
if st.session_state.selected_symptoms and not st.session_state.current_questions and not st.session_state.diagnosis_made:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Get Expert Opinion"):
            st.session_state.current_questions = st.session_state.expert_system.get_next_questions()
            if not st.session_state.current_questions:
                diagnosis_data = st.session_state.expert_system.get_diagnosis()
                st.session_state.diagnosis_made = True
                # --- CHANGED: Store the whole result dict ---
                st.session_state.diagnosis_result = diagnosis_data
            st.rerun()
    with col2:
        if st.button("Clear All Symptoms"):
            st.session_state.expert_system.reset()
            st.session_state.selected_symptoms = []
            st.session_state.current_questions = []
            st.session_state.diagnosis_made = False
            # --- CHANGED: Store the whole result dict ---
            st.session_state.diagnosis_result = {}
            st.rerun()

# --- QUESTION LOGIC UPDATED FOR NEW SESSION STATE ---
if st.session_state.current_questions:
    st.header("Additional Questions")
    st.write("Please answer the following to help narrow down the diagnosis:")
    
    question_to_ask = st.session_state.current_questions[0]
    st.subheader(f"❓ {question_to_ask}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"Yes", key=f"yes_{question_to_ask}", use_container_width=True, type="primary"):
            st.session_state.expert_system.questions_asked.append(question_to_ask)
            fact_to_add = question_to_fact_map.get(question_to_ask)
            if fact_to_add:
                st.session_state.expert_system.declare(fact_to_add)
            
            st.session_state.current_questions.pop(0) 
            new_questions = st.session_state.expert_system.get_next_questions()
            if new_questions:
                st.session_state.current_questions.extend(new_questions)
                st.session_state.current_questions = list(dict.fromkeys(st.session_state.current_questions))
            
            if not st.session_state.current_questions:
                diagnosis_data = st.session_state.expert_system.get_diagnosis()
                st.session_state.diagnosis_made = True
                # --- CHANGED: Store the whole result dict ---
                st.session_state.diagnosis_result = diagnosis_data

            st.rerun()

    with col2:
        if st.button(f"No", key=f"no_{question_to_ask}", use_container_width=True):
            st.session_state.expert_system.questions_asked.append(question_to_ask)
            st.session_state.current_questions.pop(0)
            
            new_questions = st.session_state.expert_system.get_next_questions()
            if new_questions:
                st.session_state.current_questions.extend(new_questions)
                st.session_state.current_questions = list(dict.fromkeys(st.session_state.current_questions))

            if not st.session_state.current_questions:
                diagnosis_data = st.session_state.expert_system.get_diagnosis()
                st.session_state.diagnosis_made = True
                # --- CHANGED: Store the whole result dict ---
                st.session_state.diagnosis_result = diagnosis_data

            st.rerun()

# --- FINAL DISPLAY SECTION UPDATED TO FIX KEYERROR ---
if st.session_state.diagnosis_made:
    st.header("Diagnosis Results")
    
    # --- CHANGED: Check the new result dict ---
    if st.session_state.diagnosis_result and st.session_state.diagnosis_result.get('diagnoses'):
        st.subheader("Possible Diagnoses (most likely first):")
        
        # Get the symptoms list from the result
        symptoms_list = st.session_state.diagnosis_result.get('symptoms', [])
        
        # --- LOOP THROUGH ALL DIAGNOSES ---
        for i, diagnosis_data in enumerate(st.session_state.diagnosis_result['diagnoses']):
            st.markdown(f"#### {i+1}. {diagnosis_data['diagnosis']}")
            st.progress(int(diagnosis_data['confidence']*100), text=f"Confidence: {diagnosis_data['confidence']*100:.0f}%")
            
            with st.expander(f"See detailed explanation for {diagnosis_data['diagnosis']}"):
                with st.spinner("Generating detailed explanation..."):
                    
                    # --- FIX: Create a new dict with symptoms for the LLM ---
                    data_for_llm = diagnosis_data.copy()
                    data_for_llm['symptoms'] = symptoms_list
                    explanation = explain_diagnosis(data_for_llm)
                    
                    st.markdown(explanation)
            st.divider()
            
        st.warning("⚠️ This is an AI-assisted diagnosis. Always consult with a veterinarian for proper medical advice.")
    else:
        # This branch runs if diagnosis_made is true but the list is empty
        st.error("I was unable to determine a diagnosis based on the symptoms provided. Please consult a veterinarian.")
        st.warning("⚠️ This is an AI-assisted diagnosis. Always consult with a veterinarian for proper medical advice.")