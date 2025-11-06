#!/usr/bin/env python3
"""
Basic test script for Jusbook Chatbot
Tests core functionality without running the web server
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot import JusbookChatbot

def test_chatbot():
    """Test basic chatbot functionality"""
    print("🧪 Testing Jusbook Chatbot")
    print("=" * 50)
    
    # Initialize chatbot
    bot = JusbookChatbot()
    session_id = "test_session"
    
    # Test cases
    test_messages = [
        "Hello",
        "What services do you offer?",
        "Show available slots", 
        "Contact information",
        "Book slot SL1201",
        "John Doe, 9876543210",
        "Upcoming events",
        "Help",
        "What's the weather like?",  # Fallback test
    ]
    
    print("Running test conversations...\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: User -> '{message}'")
        
        try:
            response = bot.process_message(message, session_id)
            print(f"Bot -> {response['response'][:100]}...")
            print(f"Intent: {response['intent']} (Confidence: {response['confidence']:.2f})")
            print("-" * 30)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("-" * 30)
    
    # Test data store
    print("\n📊 Testing Data Store:")
    print(f"Available services: {len(bot.data_store.get_services())}")
    print(f"Available slots: {len(bot.data_store.get_available_slots())}")
    print(f"Upcoming events: {len(bot.data_store.get_upcoming_events())}")
    
    # Test statistics
    stats = bot.data_store.get_statistics()
    print(f"Occupancy rate: {stats['occupancy_rate']}%")
    
    print("\n✅ Basic tests completed!")
    print("🚀 Ready to run the full application with: python app.py")

def test_intent_classifier():
    """Test intent classification specifically"""
    print("\n🎯 Testing Intent Classification:")
    print("=" * 50)
    
    from chatbot.intent_classifier import IntentClassifier
    classifier = IntentClassifier()
    
    test_cases = [
        ("hello there", "greeting"),
        ("show me available slots", "available_slots"),
        ("what services do you have", "services"),
        ("how can I contact you", "contact_info"),
        ("I want to book an appointment", "book_slot"),
        ("what events are coming up", "upcoming_events"),
        ("help me please", "help"),
        ("book slot SL123", "book_slot"),
        ("random nonsense text", "fallback")
    ]
    
    correct = 0
    total = len(test_cases)
    
    for text, expected_intent in test_cases:
        intent, confidence = classifier.classify_intent(text)
        status = "✅" if intent == expected_intent else "❌"
        if intent == expected_intent:
            correct += 1
        
        print(f"{status} '{text}' -> {intent} ({confidence:.2f}) [Expected: {expected_intent}]")
    
    accuracy = (correct / total) * 100
    print(f"\n🎯 Intent Classification Accuracy: {accuracy:.1f}% ({correct}/{total})")

def test_nlp_processor():
    """Test NLP processing functions"""
    print("\n🔤 Testing NLP Processor:")
    print("=" * 50)
    
    from chatbot.nlp_processor import NLPProcessor
    nlp = NLPProcessor()
    
    test_text = "Hello! I'd like to book slot SL123 for John Doe, please call 9876543210."
    
    print(f"Original: {test_text}")
    print(f"Processed: {nlp.preprocess_text(test_text)}")
    print(f"Keywords: {nlp.extract_keywords(test_text)}")
    
    entities = nlp.extract_entities(test_text)
    print(f"Entities:")
    for entity_type, values in entities.items():
        if values:
            print(f"  {entity_type}: {values}")
    
    print(f"Is question: {nlp.is_question(test_text)}")
    print(f"Is question ('What services?'): {nlp.is_question('What services do you offer?')}")

if __name__ == "__main__":
    test_chatbot()
    test_intent_classifier() 
    test_nlp_processor()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print("💡 To run the web application: python app.py")
    print("🌐 Then visit: http://localhost:8000")