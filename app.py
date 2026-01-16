from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import os

from chatbot.bot import JusbookChatbot

# Initialize FastAPI app
app = FastAPI(title="Jusbook Chatbot API", version="1.0.0")

# Initialize chatbot
chatbot = JusbookChatbot()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float

@app.get("/ui", response_class=HTMLResponse)
async def get_chat_interface_ui():
    from fastapi.responses import FileResponse
    return FileResponse(path=os.path.join("static", "index.html"))

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Process chat messages"""
    try:
        print(f"Received message: {request.message}, session_id: {request.session_id}")
        response_data = chatbot.process_message(request.message, request.session_id)
        print(f"Response data: {response_data}")
        
        # Ensure response has all required fields
        if 'response' not in response_data:
            response_data['response'] = response_data.get('message', 'Sorry, I could not process that.')
        if 'intent' not in response_data:
            response_data['intent'] = 'unknown'
        if 'confidence' not in response_data:
            response_data['confidence'] = 0.0
            
        return ChatResponse(**response_data)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in chat endpoint: {error_details}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "jusbook-chatbot"}

@app.get("/api/slots")
async def get_available_slots():
    """Get available booking slots"""
    return chatbot.data_store.get_available_slots()

@app.get("/api/services")
async def get_services():
    """Get available services"""
    return chatbot.data_store.get_services()

@app.post("/api/book")
async def book_slot(booking_data: Dict[str, Any]):
    """Book a slot"""
    try:
        result = chatbot.data_store.book_slot(
            booking_data.get("slot_id"),
            booking_data.get("service"),
            booking_data.get("customer_name"),
            booking_data.get("contact")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)