import psycopg2
from app.config import config
import logging

class PostgresService:
    def __init__(self):
        """Initialize Postgres service"""
        self.logger = logging.getLogger(__name__)
        self._initialize_db()
        self.create_tables()

    def _initialize_db(self) -> None:
        """Initialize Postgres connection"""
        try:
            self.conn = psycopg2.connect(config.DATABASE_URL)
            self.logger.info("Postgres connection initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Postgres connection: {str(e)}")
            raise

    def create_tables(self):
        """Create tables in the database"""
        with self.conn.cursor() as cur:

            # Enable UUID extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

            # Create patients table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    date_of_birth DATE,
                    gender TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create medical_records table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS medical_records (
                    record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    patient_id INT REFERENCES patients(patient_id),
                    note TEXT NOT NULL,
                    vector_id UUID NOT NULL,
                    created_by INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_deleted BOOLEAN DEFAULT FALSE
                )
            """)
            self.conn.commit()

    def get_connection(self):
        if self.conn.closed:
            self.conn = psycopg2.connect(config.DATABASE_URL)
        return self.conn