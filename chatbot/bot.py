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
        
        # Check if user is in the middle of a booking flow - prioritize that
        current_state = session.get("conversation_state", "")
        if current_state in ["selecting_service", "selecting_time_slot", "selecting_staff", 
                            "showing_details", "awaiting_customer_details"]:
            # User is in booking flow, handle it directly
            return self._handle_booking(message, session)
        
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
        """Handle booking requests with step-by-step flow"""
        current_state = session.get("conversation_state", "")
        message_lower = message.strip().lower()
        
        # STEP 1: Show service selection dropdown
        if current_state == "" or current_state == "greeting" or message_lower in ["book", "book a slot", "book slot", "i want to book", "make a booking"]:
            session["conversation_state"] = "selecting_service"
            session["context"] = {}
            return self._show_service_selection()
        
        # STEP 2: Handle service selection
        elif current_state == "selecting_service":
            selected_service = self._match_service_from_text(message)
            if selected_service:
                session["conversation_state"] = "selecting_time_slot"
                session["context"]["selected_service"] = selected_service
                return self._show_time_slot_selection()
            else:
                return "I couldn't match that to a service. Please select a service from the dropdown or type the service name clearly."
        
        # STEP 3: Handle time slot selection
        elif current_state == "selecting_time_slot":
            selected_slot = self._match_time_slot_from_text(message)
            if selected_slot:
                # Check if slot is available
                if selected_slot in self.data_store.get_available_time_slots():
                    session["conversation_state"] = "selecting_staff"
                    session["context"]["selected_time_slot"] = selected_slot
                    return self._show_staff_selection()
                else:
                    return "That slot is unavailable. Please select a valid slot from the dropdown."
            else:
                return "Please select a valid time slot from the dropdown."
        
        # STEP 4: Handle staff selection (optional)
        elif current_state == "selecting_staff":
            staff_preference = self._match_staff_from_text(message)
            if staff_preference or message_lower in ["any", "anyone", "no preference", "skip", "next"]:
                session["conversation_state"] = "showing_details"
                session["context"]["staff_preference"] = staff_preference or "Any Available Staff"
                return self._show_service_details(session)
            else:
                return "Please select a staff preference from the dropdown or say 'any' to continue."
        
        # STEP 5: Handle booking confirmation
        elif current_state == "showing_details":
            if message_lower in ["confirm", "confirm booking", "yes", "book it", "proceed"]:
                session["conversation_state"] = "awaiting_customer_details"
                return "To complete your booking, please provide:\n\n1. Your full name\n2. Your 10-digit phone number\n\nExample: 'John Smith, 9876543210'"
            elif message_lower in ["modify", "change", "edit", "go back"]:
                session["conversation_state"] = "selecting_service"
                session["context"].pop("selected_time_slot", None)
                session["context"].pop("staff_preference", None)
                return self._show_service_selection()
            elif message_lower in ["cancel", "no", "abort"]:
                session["conversation_state"] = "greeting"
                session["context"] = {}
                return "Your booking process has been cancelled. Let me know if you need anything else!"
            else:
                return "Would you like to confirm this booking? Please respond with 'Confirm Booking', 'Modify', or 'Cancel'."
        
        # STEP 6: Handle customer details and finalize booking
        elif current_state == "awaiting_customer_details":
            return self._process_booking_details(message, session)
        
        # Handle if user wants to change service
        elif "change" in message_lower and "service" in message_lower:
            session["conversation_state"] = "selecting_service"
            session["context"] = {}
            return self._show_service_selection()
        
        # Handle if user jumps steps
        elif "slot" in message_lower or "time" in message_lower:
            if current_state not in ["selecting_time_slot", "selecting_staff", "showing_details"]:
                return "Please select a service first to continue."
        
        # Default: start booking flow
        else:
            session["conversation_state"] = "selecting_service"
            session["context"] = {}
            return self._show_service_selection()
    
    def _show_service_selection(self) -> str:
        """STEP 1: Show service selection dropdown"""
        services = self.data_store.get_services()
        response = "Please select a service from the dropdown below:\n\n"
        response += "Services List:\n"
        for service in services:
            response += f"• {service['name']}\n"
        return response
    
    def _show_time_slot_selection(self) -> str:
        """STEP 2: Show time slot dropdown"""
        time_slots = self.data_store.get_available_time_slots()
        response = "Great! Please select an available time slot for your chosen service:\n\n"
        response += "Available Slots:\n"
        for slot in time_slots:
            response += f"• {slot}\n"
        return response
    
    def _show_staff_selection(self) -> str:
        """STEP 3: Show staff preference dropdown (optional)"""
        staff_options = self.data_store.get_staff_options()
        response = "Would you like to choose a preferred stylist?\n\n"
        response += "Staff Preference:\n"
        for option in staff_options:
            response += f"• {option}\n"
        return response
    
    def _show_service_details(self, session: Dict) -> str:
        """STEP 4: Show service details (price + duration)"""
        service_name = session["context"].get("selected_service")
        time_slot = session["context"].get("selected_time_slot")
        staff = session["context"].get("staff_preference", "Any Available Staff")
        
        # Get service details
        services = self.data_store.get_services()
        service_details = next((s for s in services if s["name"] == service_name), None)
        
        if not service_details:
            return "Error: Service not found. Please start over."
        
        response = "Service Summary:\n\n"
        response += f"Service: {service_name}\n"
        response += f"Duration: {service_details['duration']}\n"
        response += f"Price: {service_details['price']}\n"
        response += f"Slot: {time_slot}\n"
        response += f"Staff: {staff}\n\n"
        response += "Would you like to confirm this booking?\n\n"
        response += "Options:\n"
        response += "• Confirm Booking\n"
        response += "• Cancel\n"
        response += "• Modify\n"
        return response
    
    def _process_booking_details(self, message: str, session: Dict) -> str:
        """STEP 6: Process booking details and finalize booking"""
        import re
        parts = [p.strip() for p in message.split(',')]
        if len(parts) < 2:
            return "Please provide your full name and 10-digit phone number.\n\nExample: 'John Smith, 9876543210'"
        name = parts[0]
        contact = parts[1]

        # Validate full name: at least two words, alphabetic characters allowed
        name_words = [w for w in re.split(r"\s+", name) if w]
        valid_name = len(name_words) >= 2 and all(re.match(r"^[A-Za-z\-'.]+$", w) for w in name_words)

        # Normalize and validate phone: exactly 10 digits
        phone_digits = re.sub(r"\D", "", contact)
        valid_phone = len(phone_digits) == 10

        if not valid_name or not valid_phone:
            reason = []
            if not valid_name:
                reason.append("full name looks incomplete")
            if not valid_phone:
                reason.append("phone must be 10 digits")
            reason_text = ", ".join(reason)
            return f"Please provide valid details ({reason_text}).\n\nFormat: 'John Smith, 9876543210'"

        service_name = session["context"].get("selected_service")
        time_slot = session["context"].get("selected_time_slot")
        staff_preference = session["context"].get("staff_preference", "Any Available Staff")

        if not service_name or not time_slot:
            return "Error: Missing booking information. Please start the booking process again."

        services = self.data_store.get_services()
        service_details = next((s for s in services if s["name"] == service_name), None)
        if not service_details:
            return "Error: Service not found. Please start over."

        # Use today as booking date for the selected time slot
        from datetime import datetime
        today = datetime.now()
        date_str = today.strftime("%Y-%m-%d")

        matching_slot = self.data_store.find_or_create_slot(service_name, date_str, time_slot)
        slot_id = matching_slot['slot_id']

        try:
            booking_result = self.data_store.book_slot(
                slot_id, service_name, name, phone_digits
            )
            if booking_result['success']:
                session["conversation_state"] = "booking_complete"
                session["context"]["last_booking"] = {
                    "name": name,
                    "service": service_name,
                    "date": date_str,
                    "time": time_slot,
                    "duration": service_details['duration'],
                    "contact": phone_digits,
                    "booking_id": booking_result['booking_id'],
                    "slot_id": slot_id,
                    "price": service_details['price'],
                    "staff": staff_preference
                }

                response = "Booking Confirmed ✅\n\n"
                response += f"Customer: {name}\n"
                response += f"Service: {service_name} ({service_details['duration']})\n"
                response += f"Slot: {date_str} at {time_slot}\n"
                response += f"Staff: {staff_preference}\n"
                response += f"Price: {service_details['price']}\n"
                response += f"Contact: {phone_digits}\n"
                response += f"Booking ID: {booking_result['booking_id']}\n\n"
                response += "Thank you for booking with Jusbook!"
                return response
            else:
                return f"Sorry, there was an issue with your booking: {booking_result.get('error', 'Unknown error')}. Please try again or contact us directly."
        except Exception as e:
            return f"An error occurred while processing your booking: {str(e)}. Please try again."
        else:
            return "I couldn't understand your booking details. Please provide your name and contact number separated by a comma.\n\nExample: 'John Smith, 9876543210'"
    
    def _match_service_from_text(self, text: str) -> str:
        """Match user text input to a service"""
        text_lower = text.lower().strip()
        services = self.data_store.get_services()
        
        # Exact match first
        for service in services:
            if service['name'].lower() == text_lower:
                return service['name']
        
        # Partial match
        for service in services:
            service_name_lower = service['name'].lower()
            # Check if service name is in text or text is in service name
            if service_name_lower in text_lower or text_lower in service_name_lower:
                return service['name']
        
        # Keyword matching
        service_keywords = {
            "haircut": "Haircut & Styling",
            "hair cut": "Haircut & Styling",
            "cut": "Haircut & Styling",
            "styling": "Haircut & Styling",
            "hair wash": "Hair Wash",
            "wash": "Hair Wash",
            "beard": "Beard Trim",
            "trim": "Beard Trim",
            "beard trim": "Beard Trim",
            "hair color": "Hair Color",
            "color": "Hair Color",
            "coloring": "Hair Color",
            "facial": "Facial / Grooming",
            "grooming": "Facial / Grooming",
            "massage": "Massage (Head / Shoulder)",
            "head massage": "Massage (Head / Shoulder)",
            "shoulder massage": "Massage (Head / Shoulder)",
            "kids": "Kids Haircut",
            "kid": "Kids Haircut",
            "children": "Kids Haircut",
            "makeover": "Complete Makeover Package",
            "package": "Complete Makeover Package",
            "bridal": "Bridal Grooming",
            "bride": "Bridal Grooming",
            "wedding": "Bridal Grooming",
            "custom": "Custom Service (Other)",
            "other": "Custom Service (Other)"
        }
        
        for keyword, service_name in service_keywords.items():
            if keyword in text_lower:
                return service_name
        
        return None
    
    def _match_time_slot_from_text(self, text: str) -> str:
        """Match user text input to a time slot"""
        text_lower = text.lower().strip()
        available_slots = self.data_store.get_available_time_slots()
        
        # Try exact match
        for slot in available_slots:
            if slot.lower() == text_lower:
                return slot
        
        # Try partial match (e.g., "10:00" matches "10:00 AM")
        for slot in available_slots:
            slot_time = slot.replace(" AM", "").replace(" PM", "").lower()
            if slot_time in text_lower or text_lower in slot_time:
                return slot
        
        # Try to extract time pattern
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',
            r'(\d{1,2})\s*(am|pm)',
            r'(\d{1,2}):(\d{2})'
        ]
        
        import re
        for pattern in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                hour = int(match.group(1))
                minute = match.group(2) if len(match.groups()) > 1 and match.group(2).isdigit() else "00"
                am_pm = match.group(3) if len(match.groups()) > 2 else None
                
                # Convert to 12-hour format
                if hour < 12 and not am_pm:
                    am_pm = "am"
                elif hour >= 12:
                    if hour > 12:
                        hour = hour - 12
                    am_pm = "pm" if not am_pm else am_pm
                
                formatted_time = f"{hour:02d}:{minute} {am_pm.upper()}"
                if formatted_time in available_slots:
                    return formatted_time
        
        return None
    
    def _match_staff_from_text(self, text: str) -> str:
        """Match user text input to staff preference"""
        text_lower = text.lower().strip()
        staff_options = self.data_store.get_staff_options()
        
        # Exact match
        for option in staff_options:
            if option.lower() == text_lower:
                return option
        
        # Keyword matching
        if "any" in text_lower or "anyone" in text_lower or "no preference" in text_lower:
            return "Any Available Staff"
        elif "senior" in text_lower:
            return "Senior Stylist"
        elif "junior" in text_lower:
            return "Junior Stylist"
        elif "specific" in text_lower or "name" in text_lower:
            return "Specific Staff (Name if known)"
        
        return None
    
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