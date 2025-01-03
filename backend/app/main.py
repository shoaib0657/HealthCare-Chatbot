# FastAPI application entry point
from fastapi import FastAPI
from routes import chatbot, auth

app = FastAPI()

# Include routes
# app.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
# app.include_router(auth.router, prefix="/auth", tags=["authenication"])

@app.get("/")
def read_root():
    return {"message": "Medical AI Chatbot API is running!"}