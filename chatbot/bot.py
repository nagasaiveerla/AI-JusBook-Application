import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from .nlp_processor import NLPProcessor
from .data_store import DataStore
from .intent_classifier import IntentClassifier

class JusbookChatbot:
    def __init__(self):
        self.nlp_processor = NLPProcessor()
        self.data_store = DataStore()
        self.intent_classifier = IntentClassifier()
        self.sessions = {}  # Store conversation context
        
    def process_message(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """Process incoming message and generate response"""
        
        # Initialize session if new
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "context": {},
                "last_intent": None,
                "conversation_state": "greeting"
            }
        
        session = self.sessions[session_id]
        
        # Preprocess message
        processed_message = self.nlp_processor.preprocess_text(message)
        
        # Classify intent
        intent, confidence = self.intent_classifier.classify_intent(processed_message)
        
        # Generate response based on intent
        response = self._generate_response(intent, processed_message, session)
        
        # Update session context
        session["last_intent"] = intent
        
        return {
            "response": response,
            "intent": intent,
            "confidence": confidence
        }
    
    def _generate_response(self, intent: str, message: str, session: Dict) -> str:
        """Generate response based on classified intent"""
        
        if intent == "greeting":
            return self._handle_greeting()
        
        elif intent == "available_slots":
            return self._handle_available_slots(message)
        
        elif intent == "services":
            return self._handle_services()
        
        elif intent == "contact_info":
            return self._handle_contact_info()
        
        elif intent == "book_slot":
            return self._handle_booking(message, session)
        
        elif intent == "upcoming_events":
            return self._handle_upcoming_events()
        
        elif intent == "cancel_booking":
            return self._handle_cancel_booking(message)
        
        elif intent == "slot_broadcast":
            return self._handle_slot_broadcast()
        
        elif intent == "help":
            return self._handle_help()
        
        else:
            return self._handle_fallback(message)
    
    def _handle_greeting(self) -> str:
        greetings = [
            "Hello! Welcome to Jusbook. I'm here to help you with appointments and bookings. How can I assist you today?",
            "Hi there! I'm your Jusbook assistant. I can help you find available slots, book appointments, or provide information about our services. What would you like to know?",
            "Welcome to Jusbook! I'm ready to help you with scheduling, services, and any questions you might have. How may I help you?"
        ]
        return greetings[0]  # Using first greeting for consistency
    
    def _handle_available_slots(self, message: str) -> str:
        """Handle requests for available slots"""
        # Extract date preferences if any
        date_match = self._extract_date_from_message(message)
        service_match = self._extract_service_from_message(message)
        
        slots = self.data_store.get_available_slots(
            date_filter=date_match,
            service_filter=service_match
        )
        
        if not slots:
            return "I'm sorry, no slots are currently available for your requested criteria. Would you like me to show all available slots or help you with something else?"
        
        response = "Here are the available booking slots:\n\n"
        for slot in slots[:8]:  # Limit to 8 slots for readability
            response += f"📅 {slot['date']} at {slot['time']}\n"
            response += f"   Service: {slot['service']}\n"
            response += f"   Duration: {slot['duration']}\n"
            response += f"   Slot ID: {slot['slot_id']}\n\n"
        
        if len(slots) > 8:
            response += f"... and {len(slots) - 8} more slots available.\n\n"
        
        response += "Would you like to book any of these slots? Just let me know the Slot ID!"
        return response
    
    def _handle_services(self) -> str:
        """Handle requests for services information"""
        services = self.data_store.get_services()
        
        response = "Here are the services we offer at Jusbook:\n\n"
        for service in services:
            response += f"🔹 **{service['name']}**\n"
            response += f"   Description: {service['description']}\n"
            response += f"   Duration: {service['duration']}\n"
            response += f"   Price: {service['price']}\n\n"
        
        response += "Would you like to book any of these services or check available slots?"
        return response
    
    def _handle_contact_info(self) -> str:
        """Handle requests for contact information"""
        contact_info = self.data_store.get_contact_info()
        
        response = "Here's how you can reach us:\n\n"
        response += f"📞 **Phone:** {contact_info['phone']}\n"
        response += f"📧 **Email:** {contact_info['email']}\n"
        response += f"🏢 **Address:** {contact_info['address']}\n"
        response += f"🕐 **Business Hours:** {contact_info['hours']}\n\n"
        response += f"🌐 **Website:** {contact_info['website']}\n"
        
        if contact_info.get('social_media'):
            response += "\n**Follow us on:**\n"
            for platform, handle in contact_info['social_media'].items():
                response += f"• {platform.title()}: {handle}\n"
        
        response += "\nIs there anything else you'd like to know?"
        return response
    
    def _handle_booking(self, message: str, session: Dict) -> str:
        """Handle booking requests"""
        # If the message is exactly "Book a slot" or "Book Slot", show services and date/time options
        if message.strip().lower() in ["book a slot", "book slot"]:
            session["conversation_state"] = "booking_started"
            
            # Get services for display
            services = self.data_store.get_services()
            
            # Get available dates (next 7 days)
            today = datetime.now()
            available_dates = []
            for i in range(7):
                date = today + timedelta(days=i)
                available_dates.append(date.strftime("%Y-%m-%d"))
            
            # Common time slots
            time_slots = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]
            
            # Build response with services and options
            response = "I'd be happy to help you book a slot! Here are our services:\n\n"
            
            # Add services
            for service in services:
                response += f"🔹 **{service['name']}** - {service['duration']} - {service['price']}\n"
            
            response += "\n**Available Dates:**\n"
            for date in available_dates:
                response += f"• {date}\n"
                
            response += "\n**Common Time Slots:**\n"
            for i in range(0, len(time_slots), 2):
                if i+1 < len(time_slots):
                    response += f"• {time_slots[i]} | {time_slots[i+1]}\n"
                else:
                    response += f"• {time_slots[i]}\n"
            
            response += "\nPlease select a service, date, and time, or ask to see available slots."
            return response
        
        # Check if this is a continuation of booking process
        if session.get("conversation_state") == "awaiting_booking_details":
            return self._process_booking_details(message, session)
        
        # Extract slot ID or service from message
        slot_id = self._extract_slot_id_from_message(message)
        service = self._extract_service_from_message(message)
        
        if slot_id:
            # Direct slot booking
            session["conversation_state"] = "awaiting_booking_details"
            session["context"]["slot_id"] = slot_id
            return f"Great! You want to book slot {slot_id}. To complete your booking, please provide:\n\n1. Your full name\n2. Your contact number\n\nExample: 'John Smith, 9876543210'"
        
        elif service:
            # Service-based booking
            slots = self.data_store.get_available_slots(service_filter=service)
            if not slots:
                return f"Sorry, no slots are available for {service} right now. Would you like to see other available services?"
            
            response = f"Available slots for {service}:\n\n"
            for slot in slots[:5]:
                response += f"📅 {slot['date']} at {slot['time']} (ID: {slot['slot_id']})\n"
            
            response += f"\nTo book, please tell me which slot ID you prefer along with your name and contact number."
            return response
        
        else:
            return "I'd be happy to help you book a slot! Please either:\n\n1. Tell me a specific Slot ID from the available slots\n2. Ask for available slots first\n3. Specify a service you're interested in\n\nWhat would you prefer?"
    
    def _process_booking_details(self, message: str, session: Dict) -> str:
        """Process booking details provided by user"""
        # Extract name and phone from message
        parts = message.split(',')
        if len(parts) >= 2:
            name = parts[0].strip()
            contact = parts[1].strip()
            slot_id = session["context"].get("slot_id")
            
            if slot_id:
                try:
                    # Get slot details
                    slot_details = self.data_store.get_slot_by_id(slot_id)
                    if slot_details:
                        # Attempt booking
                        booking_result = self.data_store.book_slot(
                            slot_id, slot_details['service'], name, contact
                        )
                        
                        if booking_result['success']:
                            session["conversation_state"] = "booking_complete"
                            # Store booking details in session for reference
                            session["context"]["last_booking"] = {
                                "name": name,
                                "service": slot_details['service'],
                                "date": slot_details['date'],
                                "time": slot_details['time'],
                                "duration": slot_details['duration'],
                                "location": slot_details.get('location', 'Main Office'),
                                "contact": contact,
                                "booking_id": booking_result['booking_id'],
                                "slot_id": slot_id,
                                "price": slot_details.get('price', 'Contact for pricing'),
                                "provider": slot_details.get('provider', 'Our Staff'),
                                "additional_info": slot_details.get('additional_info', '')
                            }
                            
                            # Enhanced booking confirmation with more details
                            response = f"🎉 Your slot is booked!\n\n"
                            response += f"**Booking Details:**\n"
                            response += f"• Name: {name}\n"
                            response += f"• Service: {slot_details['service']}\n"
                            response += f"• Date & Time: {slot_details['date']} at {slot_details['time']}\n"
                            response += f"• Duration: {slot_details['duration']}\n"
                            response += f"• Location: {slot_details.get('location', 'Main Office')}\n"
                            response += f"• Provider: {slot_details.get('provider', 'Our Staff')}\n"
                            response += f"• Contact: {contact}\n"
                            response += f"• Booking ID: {booking_result['booking_id']}\n"
                            
                            # Add pricing information if available
                            if 'price' in slot_details:
                                response += f"• Price: {slot_details['price']}\n"
                                
                            # Add any additional information about the slot
                            if 'additional_info' in slot_details and slot_details['additional_info']:
                                response += f"\n**Additional Information:**\n{slot_details['additional_info']}\n"
                                
                            response += f"\n**Slot Details:**\n"
                            response += f"• Slot ID: {slot_id}\n"
                            response += f"• Availability: Booked (Confirmed)\n"
                            
                            # Add cancellation policy if available
                            cancellation_policy = slot_details.get('cancellation_policy', 'Standard 24-hour cancellation policy applies.')
                            response += f"\n**Cancellation Policy:**\n{cancellation_policy}\n"
                            
                            response += f"\nA confirmation has been sent to your contact number. Please arrive 10 minutes before your appointment. Is there anything else I can help you with?"
                            
                            return response
                        else:
                            return f"Sorry, there was an issue with your booking: {booking_result.get('error', 'Unknown error')}. Please try again or contact us directly."
                    else:
                        return "Sorry, that slot is no longer available. Would you like to see other available slots?"
                except Exception as e:
                    return f"An error occurred while processing your booking: {str(e)}. Please try again."
            else:
                return "I couldn't understand your booking details. Please provide your name and contact number separated by a comma."
        else:
            return "I'd be happy to help you book a slot! Please either:\n\n1. Tell me a specific Slot ID from the available slots\n2. Ask for available slots first\n3. Specify a service you're interested in\n\nWhat would you prefer?"
    
    def _handle_slot_broadcast(self) -> str:
        """Handle slot broadcast requests"""
        # Get the latest available slots
        slots = self.data_store.get_available_slots(limit=5)
        
        if not slots:
            return "There are currently no slots available for broadcast. Please check back later or ask about our services."
        
        response = "📢 **Latest Slot Broadcast**\n\n"
        response += "Here are our most recently added available slots:\n\n"
        
        for slot in slots:
            response += f"📅 {slot['date']} at {slot['time']}\n"
            response += f"   Service: {slot['service']}\n"
            response += f"   Duration: {slot['duration']}\n"
            response += f"   Slot ID: {slot['slot_id']}\n"
            response += f"   Special Offer: {slot.get('special_offer', 'None')}\n\n"
        
        response += "These slots are available on a first-come, first-served basis. Would you like to book any of these slots now?"
        return response
    
    def _handle_upcoming_events(self) -> str:
        """Handle requests for upcoming events and bookings"""
        # Get upcoming events
        events = self.data_store.get_upcoming_events()
        
        # Get user's upcoming bookings if user is identified
        user_bookings = []
        if "user_id" in self.sessions.get("default", {}).get("context", {}):
            user_id = self.sessions["default"]["context"]["user_id"]
            user_bookings = self.data_store.get_user_bookings(user_id)
        
        response = "📆 **Upcoming Events & Bookings**\n\n"
        
        if events:
            response += "**Upcoming Events:**\n\n"
            for event in events:
                response += f"🎯 **{event['title']}**\n"
                response += f"   Date: {event['date']}\n"
                response += f"   Time: {event['time']}\n"
                response += f"   Description: {event['description']}\n\n"
        
        if user_bookings:
            response += "**Your Upcoming Bookings:**\n\n"
            for booking in user_bookings:
                response += f"🔖 **{booking['service']}**\n"
                response += f"   Date & Time: {booking['date']} at {booking['time']}\n"
                response += f"   Booking ID: {booking['booking_id']}\n\n"
            
            response += "You can manage your bookings by providing your Booking ID."
        elif not events:
            response += "There are no upcoming events or bookings at this time. Would you like to see our available slots or services?"
        
        return response
    
    def _handle_upcoming_events(self) -> str:
        """Handle requests for upcoming events"""
        events = self.data_store.get_upcoming_events()
        
        if not events:
            return "There are no upcoming special events scheduled at the moment. However, we have regular booking slots available. Would you like to see available slots?"
        
        response = "Here are our upcoming events:\n\n"
        for event in events:
            response += f"🎉 **{event['title']}**\n"
            response += f"   Date: {event['date']}\n"
            response += f"   Time: {event['time']}\n"
            response += f"   Description: {event['description']}\n"
            if event.get('booking_required'):
                response += f"   📋 Booking required\n"
            response += "\n"
        
        response += "Would you like to book a slot for any of these events?"
        return response
    
    def _handle_cancel_booking(self, message: str) -> str:
        """Handle booking cancellation requests"""
        booking_id = self._extract_booking_id_from_message(message)
        
        if not booking_id:
            return "To cancel a booking, please provide your Booking ID. You can find this in your booking confirmation.\n\nExample: 'Cancel booking BK123456'"
        
        # Here you would implement actual cancellation logic
        return f"I'd be happy to help you cancel booking {booking_id}. For security reasons, please contact us directly at our phone number or email to process cancellations. You can find our contact information by asking me for 'contact info'."
    
    def _handle_help(self) -> str:
        """Handle help requests"""
        return """I'm here to help you with Jusbook services! Here's what I can do:

🔹 **Available Slots** - See what booking times are open
🔹 **Services** - Learn about our offerings and prices
🔹 **Book Slot** - Make a new booking
🔹 **Contact Info** - Get our phone, email, and address
🔹 **Upcoming Events** - See special events and workshops
🔹 **General Help** - Get assistance with any questions

**Quick Commands:**
• "Show available slots" or "What slots are free?"
• "What services do you offer?"
• "Book slot [ID]" or "I want to book"
• "Contact information" or "How do I reach you?"
• "Upcoming events"

Just type your question naturally, and I'll do my best to help!"""
    
    def _handle_fallback(self, message: str) -> str:
        """Handle unrecognized intents"""
        # Try to find relevant keywords and suggest actions
        if any(word in message.lower() for word in ['price', 'cost', 'fee', 'charge']):
            return "For pricing information, please ask about our services by saying 'What services do you offer?' I'll show you all services with their prices."
        
        elif any(word in message.lower() for word in ['location', 'address', 'where']):
            return "For our location and address, please ask for 'contact information' and I'll provide all our details."
        
        elif any(word in message.lower() for word in ['time', 'hours', 'open', 'close']):
            return "For our business hours, please ask for 'contact information' and I'll show you when we're open."
        
        return "I'm not sure I understand. I can help you with:\n• Available booking slots\n• Services and pricing\n• Making bookings\n• Contact information\n• Upcoming events\n\nTry asking 'What can you help me with?' for more detailed options."
    
    # Helper methods for text extraction
    def _extract_date_from_message(self, message: str) -> str:
        """Extract date preferences from message"""
        today = datetime.now()
        
        if 'today' in message.lower():
            return today.strftime('%Y-%m-%d')
        elif 'tomorrow' in message.lower():
            return (today + timedelta(days=1)).strftime('%Y-%m-%d')
        elif 'next week' in message.lower():
            return (today + timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Look for date patterns (YYYY-MM-DD, MM/DD, etc.)
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{1,2}/\d{1,2}',
            r'\d{1,2}-\d{1,2}'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, message)
            if match:
                return match.group()
        
        return None
    
    def _extract_service_from_message(self, message: str) -> str:
        """Extract service name from message"""
        services = self.data_store.get_services()
        message_lower = message.lower()
        
        for service in services:
            if service['name'].lower() in message_lower:
                return service['name']
        
        return None
    
    def _extract_slot_id_from_message(self, message: str) -> str:
        """Extract slot ID from message"""
        # Look for patterns like "slot 123", "SL001", "book SL002"
        patterns = [
            r'slot\s+(\w+)',
            r'(SL\d+)',
            r'id\s+(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_booking_id_from_message(self, message: str) -> str:
        """Extract booking ID from message"""
        patterns = [
            r'booking\s+(\w+)',
            r'(BK\d+)',
            r'id\s+(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None