from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import os

from chatbot.bot import JusbookChatbot
from chatbot.models import ChatRequest, ChatResponse

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

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """Serve the chat interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Jusbook Chatbot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .chat-container {
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                height: 600px;
                display: flex;
                flex-direction: column;
            }
            .chat-header {
                background: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }
            .chat-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                border-bottom: 1px solid #eee;
            }
            .message {
                margin: 10px 0;
                padding: 10px;
                border-radius: 10px;
                max-width: 70%;
            }
            .user-message {
                background: #e3f2fd;
                margin-left: auto;
                text-align: right;
            }
            .bot-message {
                background: #f1f8e9;
                margin-right: auto;
            }
            .chat-input {
                display: flex;
                padding: 20px;
            }
            .chat-input input {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
            }
            .chat-input button {
                padding: 10px 20px;
                margin-left: 10px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            .chat-input button:hover {
                background: #45a049;
            }
            .suggestions {
                padding: 10px 20px;
                background: #f9f9f9;
                border-top: 1px solid #eee;
            }
            .suggestion-btn {
                background: #2196F3;
                color: white;
                border: none;
                padding: 5px 10px;
                margin: 2px;
                border-radius: 15px;
                cursor: pointer;
                font-size: 12px;
            }
            .suggestion-btn:hover {
                background: #1976D2;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h2>Jusbook Assistant</h2>
                <p>Your booking companion - Ask me about services, slots, or contact information!</p>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    Hello! I'm your Jusbook assistant. I can help you with:
                    <ul>
                        <li>Available booking slots</li>
                        <li>Services we offer</li>
                        <li>Contact information</li>
                        <li>Making bookings</li>
                        <li>Upcoming events</li>
                    </ul>
                    How can I assist you today?
                </div>
            </div>
            <div class="suggestions">
                <button class="suggestion-btn" onclick="sendSuggestion('Show available slots')">Available Slots</button>
                <button class="suggestion-btn" onclick="sendSuggestion('What services do you offer?')">Services</button>
                <button class="suggestion-btn" onclick="sendSuggestion('Contact information')">Contact Info</button>
                <button class="suggestion-btn" onclick="sendSuggestion('Book a slot')">Book Slot</button>
                <button class="suggestion-btn" onclick="sendSuggestion('Upcoming events')">Events</button>
            </div>
            <div class="chat-input">
                <input type="text" id="messageInput" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;

                addMessage(message, 'user');
                input.value = '';

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            session_id: 'web-session'
                        }),
                    });
                    
                    const data = await response.json();
                    addMessage(data.response, 'bot');
                } catch (error) {
                    addMessage('Sorry, I encountered an error. Please try again.', 'bot');
                }
            }

            function sendSuggestion(message) {
                document.getElementById('messageInput').value = message;
                sendMessage();
            }

            function addMessage(message, sender) {
                const messagesContainer = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                messageDiv.innerHTML = message.replace(/\\n/g, '<br>');
                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Process chat messages"""
    try:
        response_data = chatbot.process_message(request.message, request.session_id)
        return ChatResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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