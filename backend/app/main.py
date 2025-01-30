# FastAPI application entry point
from datetime import datetime, date
from typing import List, Optional
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import UUID4, BaseModel
from routes import chatbot, auth
from services.chat_service import HealthCareAgent
from services.patient_service import PatientService

app = FastAPI(title="Medical AI Chatbot API")

# Include routes
# app.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
# app.include_router(auth.router, prefix="/auth", tags=["authenication"])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
health_agent = HealthCareAgent()
patient_service = PatientService()

# Pydantic models
class PatientCreate(BaseModel):
    name: str
    date_of_birth: date
    gender: str

class PatientResponse(BaseModel):
    patient_id: int
    name: str
    date_of_birth: date
    gender: str
    created_at: datetime

class MedicalRecordCreate(BaseModel):
    patient_id: int
    note: str
    provider_id: int

class MedicalRecordResponse(BaseModel):
    record_id: UUID4
    patient_id: int
    note: str
    vector_id: str
    created_at: datetime
    created_by: int

class ChatMessage(BaseModel):
    message: str
    patient_id: int
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    thread_id: str

class UpdateDatabase(BaseModel):
    indexname: str
    namespace: str

# Dependency to verify patient exists
async def verify_patient(patient_id: int) -> PatientResponse:
    try:
        patient = patient_service.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/patients", response_model=PatientResponse)
async def create_patient(patient: PatientCreate):
    """
    Create a new patient.
    """
    try:
        new_patient = patient_service.create_patient(
            name=patient.name,
            date_of_birth=patient.date_of_birth,
            gender=patient.gender
        )
        return new_patient
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int):
    """
    Get patient details by ID.
    """
    patient = await verify_patient(patient_id)
    return patient

@app.post("/api/medical-records", response_model=MedicalRecordResponse)
async def add_medical_record(record: MedicalRecordCreate):
    """
    Add a new medical record for a patient.
    """
    try:
        new_record = patient_service.add_medical_record(
            patient_id=record.patient_id,
            note=record.note,
            provider_id=record.provider_id
        )

        print(new_record)

        return new_record
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/api/medical-records/{record_id}")
async def delete_medical_record(record_id: uuid.UUID):
    """
    Delete a medical record.
    """
    try:
        success = patient_service.delete_medical_record(record_id)
        if not success:
            raise HTTPException(status_code=404, detail="Record not found")
        return {"message": "Record deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/patients/{patient_id}/history")
async def get_patient_history(patient_id: int):
    """
    Get patient history by ID.
    """
    try:
        # Verify patient exists
        await verify_patient(patient_id)
        
        # Get history
        history = patient_service.get_patient_history(patient_id)
        history = patient_service.format_get_patient_history(history)

        return history
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """
    Process a chat message and return the assistant's response.
    """
    try:
        # Verify patient exists
        await verify_patient(chat_message.patient_id)
        
        response = health_agent.process_message(
            input_text=chat_message.message,
            patient_id=chat_message.patient_id,
            thread_id=chat_message.thread_id if chat_message.thread_id else None
        )
        
        # If no thread_id was provided, get it from the agent's state
        thread_id = chat_message.thread_id or str(uuid.uuid4())
        
        return ChatResponse(
            message=response,
            thread_id=thread_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/{thread_id}/history")
async def get_chat_history(thread_id: str):
    """
    Get the conversation history for a specific thread.
    """
    try:
        messages = health_agent.get_conversation_history(thread_id)
        return messages
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/updatedatabase")
async def update_database(update: UpdateDatabase):
    """
    Update the database index.
    """

    indexname = update.indexname
    namespace = update.namespace

        


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}

@app.get("/")
def read_root():
    return {"message": "Medical AI Chatbot API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)