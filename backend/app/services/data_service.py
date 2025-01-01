# app/services/data_service.py
# Patient data handling and querying logic.
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import logging

class DataService:
    def __init__(self):
        """Initialize the DataService"""
        self.logger = logging.getLogger(__name__)
        self.data_path = "./data/patient_data.csv"
        try:
            self.df = self._load_data()
            self.logger.info("DataService initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize DataService: {str(e)}")
            raise

    def _load_data(self) -> pd.DataFrame:
        """Load patient data from CSV file"""
        try:
            df = pd.read_csv(self.data_path)
            self.logger.info(f"Successfully loaded {len(df)} patient records")
            return df
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise

    def get_data(self) -> pd.DataFrame:
        """Return the patient data"""
        return self.df
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """Retrieve patient data by ID"""
        try:
            patient = self.df[self.df['Patient ID'] == patient_id]
            if len(patient) == 0:
                return None
            return patient.iloc[0].to_dict()
        except Exception as e:
            self.logger.error(f"Error retrieving patient {patient_id}: {str(e)}")
            return None

    def get_patients_by_condition(self, condition: str) -> List[Dict]:
        """Retrieve patients by medical condition"""
        try:
            patients = self.df[self.df['Medical Condition'].str.contains(condition, case=False, na=False)]
            return patients.to_dict('records')
        except Exception as e:
            self.logger.error(f"Error retrieving patients by condition {condition}: {str(e)}")
            return []

    def prepare_patient_text(self, patient_data: Dict) -> str:
        """Prepare patient data for embedding"""
        return f"""
        Medical Condition: {patient_data.get('Medical Condition', '')}
        Treatments: {patient_data.get('Treatments', '')}
        Doctor's Notes: {patient_data.get('Doctor\'s Notes', '')}
        """

    def get_patient_summary(self, patient_id: str) -> Optional[Dict]:
        """Get a summary of patient's medical history"""
        patient = self.get_patient_by_id(patient_id)
        if not patient:
            return None

        return {
            'patient_id': patient['Patient ID'],
            'name': patient['Name'],
            'age': self._calculate_age(patient['Date of Birth']),
            'condition': patient['Medical Condition'],
            'latest_treatment': patient['Treatments'],
            'admission_duration': self._calculate_duration(
                patient['Admit Date'],
                patient['Discharge Date']
            )
        }

    def _calculate_age(self, dob_str: str) -> int:
        """Calculate age from date of birth"""
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d')
            today = datetime.now()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except Exception as e:
            self.logger.error(f"Error calculating age: {str(e)}")
            return 0

    def _calculate_duration(self, admit_date: str, discharge_date: str) -> int:
        """Calculate duration of hospital stay in days"""
        try:
            admit = datetime.strptime(admit_date, '%Y-%m-%d')
            discharge = datetime.strptime(discharge_date, '%Y-%m-%d')
            return (discharge - admit).days
        except Exception as e:
            self.logger.error(f"Error calculating duration: {str(e)}")
            return 0