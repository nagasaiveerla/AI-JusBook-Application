import re
import string
from typing import List, Dict

class NLPProcessor:
    """Lightweight NLP processor for text preprocessing and basic NLP tasks"""
    
    def __init__(self):
        # Common stopwords (reduced set for performance)
        self.stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but', 'they',
            'have', 'had', 'what', 'said', 'each', 'which', 'do', 'how',
            'their', 'if', 'up', 'out', 'so', 'no', 'can', 'would', 'could'
        }
        
        # Contractions expansion
        self.contractions = {
            "won't": "will not",
            "can't": "cannot",
            "n't": " not",
            "'re": " are",
            "'ve": " have",
            "'ll": " will",
            "'d": " would",
            "'m": " am",
            "let's": "let us"
        }
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for intent classification
        Returns cleaned and normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Expand contractions
        text = self.expand_contractions(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def expand_contractions(self, text: str) -> str:
        """Expand common contractions"""
        for contraction, expansion in self.contractions.items():
            text = text.replace(contraction, expansion)
        return text
    
    def remove_punctuation(self, text: str) -> str:
        """Remove punctuation from text"""
        return text.translate(str.maketrans('', '', string.punctuation))
    
    def tokenize(self, text: str) -> List[str]:
        """Simple tokenization by splitting on whitespace"""
        return text.split()
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords from token list"""
        return [token for token in tokens if token.lower() not in self.stopwords]
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract basic entities from text using regex patterns
        """
        entities = {
            'phone_numbers': [],
            'emails': [],
            'dates': [],
            'times': [],
            'slot_ids': [],
            'booking_ids': []
        }
        
        # Phone numbers (various formats)
        phone_patterns = [
            r'\b\d{10}\b',  # 10 digits
            r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b',  # XXX-XXX-XXXX
            r'\(\d{3}\)\s*\d{3}[-.\s]\d{4}'  # (XXX) XXX-XXXX
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            entities['phone_numbers'].extend(matches)
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities['emails'] = re.findall(email_pattern, text)
        
        # Dates (various formats)
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
            r'\b\d{1,2}/\d{1,2}\b'  # MM/DD
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            entities['dates'].extend(matches)
        
        # Times
        time_patterns = [
            r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b',
            r'\b\d{1,2}\s*(?:AM|PM|am|pm)\b'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            entities['times'].extend(matches)
        
        # Slot IDs
        slot_patterns = [
            r'\bSL\d+\b',
            r'\bslot\s+\d+\b',
            r'\bslot\s+[A-Za-z0-9]+\b'
        ]
        
        for pattern in slot_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['slot_ids'].extend(matches)
        
        # Booking IDs
        booking_patterns = [
            r'\bBK\d+\b',
            r'\bbooking\s+\d+\b',
            r'\bbooking\s+[A-Za-z0-9]+\b'
        ]
        
        for pattern in booking_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['booking_ids'].extend(matches)
        
        return entities
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from text
        """
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Remove punctuation
        no_punct = self.remove_punctuation(processed_text)
        
        # Tokenize
        tokens = self.tokenize(no_punct)
        
        # Remove stopwords
        keywords = self.remove_stopwords(tokens)
        
        # Filter out very short words
        keywords = [word for word in keywords if len(word) > 2]
        
        return keywords
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple word overlap similarity between two texts
        """
        if not text1 or not text2:
            return 0.0
        
        # Get keywords from both texts
        keywords1 = set(self.extract_keywords(text1))
        keywords2 = set(self.extract_keywords(text2))
        
        if not keywords1 or not keywords2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def is_question(self, text: str) -> bool:
        """
        Determine if text is a question
        """
        text = text.strip()
        
        # Ends with question mark
        if text.endswith('?'):
            return True
        
        # Starts with question words
        question_words = ['what', 'where', 'when', 'why', 'who', 'whom', 'which', 'whose', 'how']
        first_word = text.split()[0].lower() if text.split() else ''
        
        return first_word in question_words
    
    def extract_name_from_booking_text(self, text: str) -> str:
        """
        Extract name from booking text like "John Smith, 1234567890"
        """
        # Split by comma and take first part
        parts = text.split(',')
        if len(parts) >= 2:
            potential_name = parts[0].strip()
            # Basic validation - should contain only letters and spaces
            if re.match(r'^[A-Za-z\s]+$', potential_name):
                return potential_name
        
        return ""
    
    def extract_contact_from_booking_text(self, text: str) -> str:
        """
        Extract contact info from booking text like "John Smith, 1234567890"
        """
        # Split by comma and take second part
        parts = text.split(',')
        if len(parts) >= 2:
            potential_contact = parts[1].strip()
            # Basic validation for phone number
            if re.match(r'^\d{10}$', potential_contact):
                return potential_contact
        
        return ""