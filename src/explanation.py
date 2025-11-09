import os
import google.generativeai as genai
from typing import Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def explain_diagnosis(diagnosis_data: Dict) -> str:
    """
    Generate a detailed explanation of the diagnosis using Gemini.
    
    Args:
        diagnosis_data (Dict): Dictionary containing diagnosis, confidence, and symptoms
        
    Returns:
        str: Detailed explanation of the diagnosis
    """
    prompt = f"""
    As a veterinary expert, please provide a detailed explanation for the following pet diagnosis:
    
    Diagnosis: {diagnosis_data['diagnosis']}
    Confidence Level: {diagnosis_data['confidence']*100}%
    Observed Symptoms: {', '.join(diagnosis_data['symptoms'])}
    
    Please explain:
    1. What this condition is
    2. Why these symptoms indicate this condition
    3. What immediate steps the pet owner should take
    4. Whether veterinary attention is needed urgently
    
    Keep the explanation clear and accessible for pet owners while being medically accurate.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Unable to generate explanation at the moment. Please consult with a veterinarian. Error: {str(e)}"