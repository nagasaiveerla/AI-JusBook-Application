"""
Jusbook Chatbot Package

A lightweight AI chatbot for jusbook.com that helps users with:
- Booking appointments
- Checking available slots  
- Getting service information
- Contact details
- Upcoming events

The chatbot uses a rule-based NLP approach for intent classification
and maintains conversation context for better user experience.
"""

from .bot import JusbookChatbot
from .intent_classifier import IntentClassifier
from .nlp_processor import NLPProcessor
from .data_store import DataStore
from .models import (
    ChatRequest, 
    ChatResponse, 
    Service, 
    Slot, 
    Booking, 
    BookingRequest,
    Event,
    ContactInfo,
    SessionContext,
    IntentClassification,
    EntityExtraction,
    Statistics
)

__version__ = "1.0.0"
__author__ = "Jusbook Team"

__all__ = [
    "JusbookChatbot",
    "IntentClassifier", 
    "NLPProcessor",
    "DataStore",
    "ChatRequest",
    "ChatResponse", 
    "Service",
    "Slot",
    "Booking", 
    "BookingRequest",
    "Event",
    "ContactInfo",
    "SessionContext",
    "IntentClassification",
    "EntityExtraction",
    "Statistics"
]