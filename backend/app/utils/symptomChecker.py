import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("API_KEY is not set in the environment variables.")

genai.configure(api_key=API_KEY)

def run(data):
    # Initialize the model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    prompt = f"""
    Given the following patient details, including age, gender, medical history, lifestyle factors, and symptoms, identify the top 3 possible diseases in order of likelihood from most to least likely. Consider all relevant patient information in your analysis. Additionally, provide treatment options for each disease briefly.

    1. Age: {data.get('age')}
    2. Gender: {data.get('gender')}
    3. Occupation: {data.get('occupation')}
    4. Nationality: {data.get('nationality')}
    5. Weight: {data.get('weight')}
    6. Existing Medical Symptoms: {data.get('existing_medical_symptoms')}
    7. Chronic Disease: {data.get('chronic_diseases', 'None')}
    8. Allergies: {data.get('allergies', 'None')}
    9. Previous Surgeries: {data.get('previous_surgeries', 'None')}
    10. Current Medications: {data.get('current_medications', 'None')}
    11. Smoking Status: {data.get('smoking_status', 'Non-Smoker')}
    12. Alcohol Intake: {data.get('alcohol_intake', 'None')}
    13. Occasional Drug Use: {data.get('occasional_drug_use', 'None')}
    """

    response = model.generate_content(prompt)
    return response.text