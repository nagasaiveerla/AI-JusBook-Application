# Jusbook AI Chatbot

A lightweight, intelligent chatbot for jusbook.com built with FastAPI that helps users navigate booking services, check available slots, and get information about services and contact details.

## Features

- **Intent Classification**: Rule-based NLP for understanding user queries
- **Booking Management**: Book, view, and manage appointment slots
- **Service Information**: Get details about available services and pricing
- **Contact Information**: Easy access to business contact details
- **Event Updates**: Information about upcoming events and workshops
- **Session Management**: Contextual conversations with memory
- **Web Interface**: Clean, responsive chat interface
- **RESTful API**: Well-documented endpoints for integration
- **No External Dependencies**: Uses lightweight, rule-based NLP (no API keys required)

## Project Structure

```
jusbook-chatbot/
├── app.py                 # FastAPI main application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── chatbot/              # Core chatbot package
│   ├── __init__.py       # Package initialization
│   ├── bot.py            # Main chatbot logic
│   ├── intent_classifier.py  # Intent classification
│   ├── nlp_processor.py  # Text processing utilities
│   ├── data_store.py     # In-memory data management
│   └── models.py         # Pydantic data models
└── static/               # Static files (auto-created)
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone or download the project files**
```bash
mkdir jusbook-chatbot
cd jusbook-chatbot
# Copy all the provided files into this directory
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Access the chatbot**
   - Open your browser and go to: `http://localhost:8000`
   - The interactive chat interface will load automatically

### Alternative: Direct uvicorn command
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Usage

### Web Interface
1. Navigate to `http://localhost:8000`
2. Use the chat interface to interact with the bot
3. Try these example queries:
   - "Hello" or "Hi"
   - "Show available slots"
   - "What services do you offer?"
   - "Contact information"
   - "Book slot SL1201"
   - "Upcoming events"

### API Endpoints

#### Chat Endpoint
```bash
POST /chat
Content-Type: application/json

{
  "message": "Show available slots",
  "session_id": "user123"
}
```

#### Direct Data Access
- `GET /api/slots` - Get available slots
- `GET /api/services` - Get services list
- `POST /api/book` - Book a slot directly
- `GET /health` - Health check

### Example API Usage

```bash
# Get available slots
curl http://localhost:8000/api/slots

# Chat with bot
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}'

# Book a slot
curl -X POST http://localhost:8000/api/book \
  -H "Content-Type: application/json" \
  -d '{
    "slot_id": "SL1201",
    "customer_name": "John Doe", 
    "contact": "9876543210",
    "service": "Haircut & Styling"
  }'
```

## Chatbot Capabilities

### Supported Intents
- **Greeting**: Welcome messages and initial interaction
- **Available Slots**: Check open booking times
- **Services**: Learn about offerings and prices
- **Contact Info**: Get business contact details
- **Book Slot**: Make appointments
- **Upcoming Events**: View scheduled events
- **Cancel Booking**: Cancel existing bookings
- **Help**: Get assistance with bot usage

### Sample Conversations

**Getting Available Slots:**
```
User: What slots are available today?
Bot: Here are the available booking slots:

📅 2024-09-21 at 09:00 AM
   Service: Haircut & Styling
   Duration: 45 minutes
   Slot ID: SL0921

📅 2024-09-21 at 10:30 AM
   Service: Deep Cleansing Facial
   Duration: 60 minutes
   Slot ID: SL0922
...
```

**Making a Booking:**
```
User: Book slot SL0921
Bot: Great! You want to book slot SL0921. To complete your booking, please provide:

1. Your full name
2. Your contact number

Example: 'John Smith, 9876543210'

User: Alice Johnson, 9988776655
Bot: 🎉 Booking confirmed!

**Booking Details:**
• Name: Alice Johnson
• Service: Haircut & Styling
• Date & Time: 2024-09-21 at 09:00 AM
• Contact: 9988776655
• Booking ID: BK4A7F2E10
```

## Technical Details

### Architecture
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and serialization
- **Rule-based NLP**: Lightweight intent classification without ML models
- **In-memory Storage**: Fast data access for demo purposes
- **Session Management**: Contextual conversations

### Intent Classification
The chatbot uses a rule-based approach with:
- Keyword matching using regex patterns
- Confidence scoring based on pattern matches
- Special rule handling for edge cases
- Context awareness for conversation flow

### Data Models
- **Services**: Beauty and wellness services with pricing
- **Slots**: Available booking time slots
- **Bookings**: Customer appointment records
- **Events**: Upcoming workshops and special events
- **Sessions**: Conversation context and state

### Performance
- **Lightweight**: No external AI APIs or large models
- **Fast Response**: Sub-second response times
- **Memory Efficient**: Minimal resource usage
- **Scalable**: Easy to extend with new intents and features

## Customization

### Adding New Services
Edit the `_load_services()` method in `chatbot/data_store.py`:

```python
{
    "id": "new_service",
    "name": "New Service Name",
    "description": "Service description",
    "duration": "60 minutes", 
    "price": "₹1000"
}
```

### Adding New Intents
1. Add patterns to `chatbot/intent_classifier.py`:
```python
"new_intent": [
    "keyword1", "keyword2", "phrase example"
]
```

2. Add handler method to `chatbot/bot.py`:
```python
def _handle_new_intent(self, message: str) -> str:
    return "Response for new intent"
```

### Modifying Contact Information
Update the `_load_contact_info()` method in `chatbot/data_store.py` with your business details.

## Deployment

### Production Considerations
1. **Environment Variables**: Store sensitive config in environment variables
2. **Database**: Replace in-memory storage with persistent database
3. **Authentication**: Add user authentication if needed
4. **Rate Limiting**: Implement request rate limiting
5. **Logging**: Add comprehensive logging
6. **HTTPS**: Use SSL certificates for production

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment
The application can be deployed on:
- **Heroku**: Simple deployment with Procfile
- **AWS**: EC2, ECS, or Lambda
- **Google Cloud**: Cloud Run or App Engine
- **Azure**: Container Instances or App Service

## Testing

### Manual Testing
Use the web interface or API endpoints to test various scenarios:

1. **Basic Conversation Flow**
2. **Booking Process**
3. **Information Retrieval**
4. **Error Handling**
5. **Session Management**

### API Testing with curl
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat functionality
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What services do you offer?"}'
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   uvicorn app:app --port 8001  # Use different port
   ```

2. **Module Import Errors**
   - Ensure all files are in correct directories
   - Check Python path and virtual environment

3. **Dependencies Issues**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

4. **Browser Compatibility**
   - Use modern browsers (Chrome, Firefox, Safari, Edge)
   - Enable JavaScript

### Logs and Debugging
- Check console output for errors
- Use `--reload` flag for development
- Add print statements for debugging

## Contributing

### Adding Features
1. Follow the existing code structure
2. Add appropriate error handling
3. Update documentation
4. Test thoroughly

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints where possible
- Add docstrings for functions and classes
- Keep functions focused and small

## License

This project is created for educational and demonstration purposes. Feel free to use and modify as needed.

## Support

For questions or issues:
1. Check this README for common solutions
2. Review the code comments and docstrings
3. Test with the provided examples
4. Modify and extend as needed for your use case

---

**Built with ❤️ for jusbook.com**