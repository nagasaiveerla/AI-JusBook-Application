import re
from typing import Tuple, Dict, List
from collections import defaultdict

class IntentClassifier:
    """Lightweight rule-based intent classifier for jusbook chatbot"""
    
    def __init__(self):
        # Define intent patterns with keywords and phrases
        self.intent_patterns = {
            "greeting": [
                "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
                "start", "begin", "welcome", "greetings", "howdy", "what's up"
            ],
            
            "available_slots": [
                "available slots", "free slots", "open slots", "available times",
                "when available", "show slots", "available appointments", "free times",
                "what slots", "available booking", "open times", "slot availability",
                "when can i book", "when are you available", "booking times"
            ],
            
            "services": [
                "services", "what do you offer", "what services", "service list",
                "offerings", "what can you do", "treatments", "procedures",
                "service menu", "available services", "types of service",
                "options", "what can i book"
            ],
            
            "contact_info": [
                "contact", "phone", "email", "address", "location", "reach you",
                "contact information", "contact details", "how to contact",
                "phone number", "office address", "business hours", "where located",
                "how to reach", "where are you located"
            ],
            
            "book_slot": [
                "book", "booking", "appointment", "schedule", "reserve",
                "book slot", "make booking", "book appointment", "schedule appointment",
                "reserve slot", "i want to book", "make reservation", "book me",
                "reserve time", "can i book"
            ],
            
            "upcoming_events": [
                "events", "upcoming events", "what's happening", "special events",
                "workshops", "upcoming", "events calendar", "scheduled events",
                "what events", "event schedule", "activities", "calendar",
                "upcoming bookings", "my bookings", "show my bookings", "future appointments", 
                "my schedule"
            ],
            
            "slot_broadcast": [
                "broadcast", "slot broadcast", "latest slots", "new slots", 
                "recent slots", "slot updates", "broadcast slots", "slot notifications",
                "slot alerts", "special offers", "featured slots"
            ],
            
            "cancel_booking": [
                "cancel", "cancel booking", "cancel appointment", "cancellation",
                "cancel reservation", "cancel slot", "remove booking", "cancel my slot",
                "i need to cancel", "can't make it", "reschedule", "change booking",
                "delete booking"
            ],
            
            "help": [
                "help", "what can you help", "what can you do", "assistance",
                "support", "how to use", "guide me", "instructions",
                "what are your capabilities", "how does this work", "guidance",
                "features", "capabilities"
            ]
        }
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for intent, patterns in self.intent_patterns.items():
            # Create regex pattern that matches whole words
            pattern = r'\b(?:' + '|'.join(re.escape(p) for p in patterns) + r')\b'
            self.compiled_patterns[intent] = re.compile(pattern, re.IGNORECASE)
    
    def classify_intent(self, text: str) -> Tuple[str, float]:
        """
        Classify the intent of input text using rule-based approach
        Returns: (intent, confidence_score)
        """
        if not text or not text.strip():
            return "greeting", 0.5
        
        text = text.lower().strip()
        intent_scores = defaultdict(float)
        
        # Score each intent based on pattern matches
        for intent, pattern in self.compiled_patterns.items():
            matches = pattern.findall(text)
            if matches:
                # Base score for having matches
                base_score = len(matches) * 0.3
                
                # Bonus for exact phrase matches
                for original_pattern in self.intent_patterns[intent]:
                    if original_pattern.lower() in text:
                        base_score += 0.4
                
                # Length penalty to avoid over-matching in long texts
                length_penalty = min(len(text.split()) / 20, 0.2)
                
                intent_scores[intent] = min(base_score - length_penalty, 1.0)
        
        # Special case handling
        intent_scores = self._apply_special_rules(text, intent_scores)
        
        if not intent_scores:
            return "fallback", 0.0
        
        # Get the highest scoring intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        
        # Minimum confidence threshold
        if best_intent[1] < 0.2:
            return "fallback", best_intent[1]
        
        return best_intent[0], best_intent[1]
    
    def _apply_special_rules(self, text: str, scores: Dict[str, float]) -> Dict[str, float]:
        """Apply special rules for better intent classification"""
        
        # Greeting detection for short messages
        greeting_words = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
        if len(text.split()) <= 3 and any(word in text for word in greeting_words):
            scores["greeting"] = max(scores.get("greeting", 0), 0.8)
        
        # Question words often indicate information seeking
        question_words = ["what", "where", "when", "how", "which", "who"]
        if any(word in text for word in question_words):
            if "services" in text or "offer" in text:
                scores["services"] = max(scores.get("services", 0), 0.7)
            elif "contact" in text or "reach" in text or "phone" in text:
                scores["contact_info"] = max(scores.get("contact_info", 0), 0.7)
            elif "slots" in text or "available" in text:
                scores["available_slots"] = max(scores.get("available_slots", 0), 0.7)
            elif "broadcast" in text or "latest" in text:
                scores["slot_broadcast"] = max(scores.get("slot_broadcast", 0), 0.7)
            elif "upcoming" in text or "events" in text or "bookings" in text:
                scores["upcoming_events"] = max(scores.get("upcoming_events", 0), 0.7)
        
        # Slot ID patterns suggest booking intent
        slot_patterns = [r'slot\s+\w+', r'SL\d+', r'book\s+\w+']
        for pattern in slot_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                scores["book_slot"] = max(scores.get("book_slot", 0), 0.8)
        
        # Time expressions suggest slot availability queries
        time_patterns = ["today", "tomorrow", "next week", "this week", r'\d+/\d+', r'\d+-\d+']
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in time_patterns):
            if "book" in text:
                scores["book_slot"] = max(scores.get("book_slot", 0), 0.7)
            else:
                scores["available_slots"] = max(scores.get("available_slots", 0), 0.6)
        
        # Broadcast related terms
        broadcast_terms = ["broadcast", "latest", "new slots", "updates", "notifications", "alerts"]
        if any(term in text for term in broadcast_terms):
            scores["slot_broadcast"] = max(scores.get("slot_broadcast", 0), 0.8)
        
        # Upcoming events and bookings related terms
        upcoming_terms = ["upcoming", "future", "calendar", "schedule", "my bookings", "events"]
        if any(term in text for term in upcoming_terms):
            scores["upcoming_events"] = max(scores.get("upcoming_events", 0), 0.8)
        
        # Polite expressions often accompany requests
        polite_words = ["please", "could you", "can you", "would you"]
        if any(word in text for word in polite_words):
            # Boost scores slightly for politeness
            for intent in scores:
                scores[intent] = min(scores[intent] + 0.1, 1.0)
        
        return scores