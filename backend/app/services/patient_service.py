from app.services.postgres_service import PostgresService
from app.services.pinecone_service import PineconeService
from psycopg2.extras import RealDictCursor
import uuid

class PatientService:
    def __init__(self):
        """Initialize Patient service"""
        self.pg = PostgresService()
        self.pine = PineconeService()
        print("HII")

    def create_patient(self, name, date_of_birth, gender):
        """Create a new patient"""
        conn = self.pg.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO patients (name, date_of_birth, gender)
                VALUES (%s, %s, %s)
                RETURNING patient_id, name, date_of_birth, gender, created_at
            """, (name, date_of_birth, gender))
            patient = cur.fetchone()
            conn.commit()

        return patient

    def get_patient(self, patient_id):
        """Get patient by ID"""
        conn = self.pg.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT patient_id, name, date_of_birth, gender, created_at
                FROM patients
                WHERE patient_id = %s
            """, (patient_id,))
            patient = cur.fetchone()
        return patient

    def add_medical_record(self, patient_id, note: str, provider_id):
        """Add a medical record for a patient"""

        # Verify patient exists first
        if not self.get_patient(patient_id):
            raise ValueError(f"Patient {patient_id} not found")

        # Store in Pinecone
        vector_id = self.pine.index_patient_data(patient_id, note)

        # Store in Postgres
        conn = self.pg.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO medical_records (patient_id, note, vector_id, created_by)
                VALUES (%s, %s, %s, %s)
                RETURNING record_id, patient_id, note, vector_id, created_at
            """, (patient_id, note, vector_id, provider_id))
            record = cur.fetchone()
            conn.commit()

        return record

    def delete_medical_record(self, record_id: uuid.UUID):
        """Delete a medical record"""
        conn = self.pg.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First get the record to delete from Pinecone
            cur.execute("""
                SELECT patient_id, vector_id
                FROM medical_records
                WHERE record_id = %s AND NOT is_deleted
            """, (record_id,))
            record = cur.fetchone()

            # Delete from Pinecone
            if record:
                # Delete from Pinecone
                self.pine.delete_vector(record['patient_id'], record['vector_id'])

                # Soft delete from Postgres
                cur.execute("""
                    UPDATE medical_records
                    SET is_deleted = TRUE, updated_at = CURRENT_TIMESTAMP
                    WHERE record_id = %s
                """, (record_id,))

                conn.commit()
                return True
            
        return False
    
    def get_patient_history(self, patient_id):
        """Get patient history"""
        conn = self.pg.get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT record_id, note, vector_id, created_at, created_by
                FROM medical_records
                WHERE patient_id = %s AND NOT is_deleted
                ORDER BY created_at DESC
            """, (patient_id,))
            records = cur.fetchall()
        return records