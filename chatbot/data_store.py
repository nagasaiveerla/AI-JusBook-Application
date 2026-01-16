import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random
import uuid

class DataStore:
    """In-memory data store for jusbook chatbot"""
    
    def __init__(self):
        self.services = self._load_services()
        self.slots = self._generate_sample_slots()
        self.bookings = {}
        self.events = self._load_events()
        self.contact_info = self._load_contact_info()
    
    def _load_services(self) -> List[Dict[str, Any]]:
        """Load available services"""
        return [
            {
                "id": "haircut",
                "name": "Haircut & Styling",
                "description": "Professional haircut and styling service",
                "duration": "45 minutes",
                "price": "₹500"
            },
            {
                "id": "hairwash",
                "name": "Hair Wash",
                "description": "Professional hair washing and conditioning service",
                "duration": "30 minutes",
                "price": "₹300"
            },
            {
                "id": "beardtrim",
                "name": "Beard Trim",
                "description": "Professional beard trimming and shaping",
                "duration": "25 minutes",
                "price": "₹250"
            },
            {
                "id": "haircolor",
                "name": "Hair Color",
                "description": "Professional hair coloring service",
                "duration": "120 minutes",
                "price": "₹1500"
            },
            {
                "id": "facial",
                "name": "Facial / Grooming",
                "description": "Deep cleansing facial and grooming treatment",
                "duration": "60 minutes",
                "price": "₹800"
            },
            {
                "id": "massage",
                "name": "Massage (Head / Shoulder)",
                "description": "Relaxing head and shoulder massage therapy",
                "duration": "45 minutes",
                "price": "₹600"
            },
            {
                "id": "kidshaircut",
                "name": "Kids Haircut",
                "description": "Specialized haircut service for children",
                "duration": "30 minutes",
                "price": "₹350"
            },
            {
                "id": "makeover",
                "name": "Complete Makeover Package",
                "description": "Complete makeover with multiple services",
                "duration": "180 minutes",
                "price": "₹2500"
            },
            {
                "id": "bridal",
                "name": "Bridal Grooming",
                "description": "Special bridal grooming and styling package",
                "duration": "240 minutes",
                "price": "₹5000"
            },
            {
                "id": "custom",
                "name": "Custom Service (Other)",
                "description": "Custom service as per your requirements",
                "duration": "60 minutes",
                "price": "Contact for pricing"
            }
        ]
    
    def _generate_sample_slots(self) -> List[Dict[str, Any]]:
        """Generate sample available slots"""
        slots = []
        services = [service["name"] for service in self.services]
        
        # Generate slots for next 14 days
        today = datetime.now()
        
        for day_offset in range(14):
            date = today + timedelta(days=day_offset)
            date_str = date.strftime("%Y-%m-%d")
            day_name = date.strftime("%A")
            
            # Skip Sundays (assuming closed)
            if date.weekday() == 6:
                continue
            
            # Generate time slots matching user requirements
            time_slots = [
                "10:00 AM", "11:00 AM", "12:30 PM", "02:00 PM", 
                "03:15 PM", "04:30 PM", "06:00 PM", "07:15 PM"
            ]
            
            for i, time_slot in enumerate(time_slots):
                # Randomly make some slots unavailable
                if random.random() < 0.3:  # 30% chance of being booked
                    continue
                
                slot_id = f"SL{date.strftime('%m%d')}{i:02d}"
                service = random.choice(services)
                
                slots.append({
                    "slot_id": slot_id,
                    "date": date_str,
                    "day": day_name,
                    "time": time_slot,
                    "service": service,
                    "duration": next(s["duration"] for s in self.services if s["name"] == service),
                    "available": True,
                    "price": next(s["price"] for s in self.services if s["name"] == service)
                })
        
        return sorted(slots, key=lambda x: (x["date"], x["time"]))
    
    def get_available_time_slots(self) -> List[str]:
        """Get list of available time slots"""
        return ["10:00 AM", "11:00 AM", "12:30 PM", "02:00 PM", 
                "03:15 PM", "04:30 PM", "06:00 PM", "07:15 PM"]
    
    def get_staff_options(self) -> List[str]:
        """Get staff preference options"""
        return ["Any Available Staff", "Senior Stylist", "Junior Stylist", "Specific Staff (Name if known)"]
    
    def _load_events(self) -> List[Dict[str, Any]]:
        """Load upcoming events"""
        today = datetime.now()
        
        return [
            {
                "id": "workshop1",
                "title": "Skincare Workshop",
                "date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
                "time": "02:00 PM",
                "description": "Learn professional skincare techniques and tips",
                "booking_required": True,
                "price": "₹200"
            },
            {
                "id": "demo1",
                "title": "Hair Styling Demo",
                "date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
                "time": "11:00 AM",
                "description": "Live demonstration of latest hair styling trends",
                "booking_required": True,
                "price": "Free"
            },
            {
                "id": "sale1",
                "title": "Weekend Beauty Sale",
                "date": (today + timedelta(days=12)).strftime("%Y-%m-%d"),
                "time": "10:00 AM - 6:00 PM",
                "description": "Special discounts on all beauty services",
                "booking_required": False,
                "price": "Various"
            }
        ]
    
    def _load_contact_info(self) -> Dict[str, Any]:
        """Load contact information"""
        return {
            "phone": "+91-9876543210",
            "email": "contact@jusbook.com",
            "address": "123 Beauty Street, Jubilee Hills, Hyderabad, Telangana 500033",
            "website": "https://jusbook.com",
            "hours": "Monday to Saturday: 9:00 AM - 7:00 PM (Closed Sundays)",
            "social_media": {
                "instagram": "@jusbook_official",
                "facebook": "facebook.com/jusbook",
                "twitter": "@jusbook_com"
            }
        }
    
    def get_services(self) -> List[Dict[str, Any]]:
        """Get all available services"""
        return self.services
    
    def get_available_slots(self, date_filter: str = None, service_filter: str = None) -> List[Dict[str, Any]]:
        """Get available booking slots with optional filters"""
        available_slots = [slot for slot in self.slots if slot["available"]]
        
        if date_filter:
            available_slots = [slot for slot in available_slots if slot["date"] == date_filter]
        
        if service_filter:
            available_slots = [slot for slot in available_slots if 
                             service_filter.lower() in slot["service"].lower()]
        
        return available_slots
    
    def get_slot_by_id(self, slot_id: str) -> Optional[Dict[str, Any]]:
        """Get slot details by slot ID"""
        for slot in self.slots:
            if slot["slot_id"] == slot_id and slot["available"]:
                return slot
        return None
    
    def find_or_create_slot(self, service: str, date: str, time: str) -> Dict[str, Any]:
        """Find an available slot for service/date/time, or create one if needed"""
        # First, try to find an existing available slot
        for slot in self.slots:
            if (slot["date"] == date and 
                slot["time"] == time and 
                slot["service"] == service and 
                slot["available"]):
                return slot
        
        # If no exact match, find any available slot at that time (we'll update the service)
        for slot in self.slots:
            if slot["date"] == date and slot["time"] == time and slot["available"]:
                # Update the service for this slot
                slot["service"] = service
                service_details = next((s for s in self.services if s["name"] == service), None)
                if service_details:
                    slot["duration"] = service_details["duration"]
                    slot["price"] = service_details["price"]
                return slot
        
        # If still no match, create a new slot
        slot_id = f"SL{date.replace('-', '')}{len(self.slots):03d}"
        service_details = next((s for s in self.services if s["name"] == service), None)
        
        new_slot = {
            "slot_id": slot_id,
            "date": date,
            "day": datetime.strptime(date, "%Y-%m-%d").strftime("%A"),
            "time": time,
            "service": service,
            "duration": service_details["duration"] if service_details else "60 minutes",
            "available": True,
            "price": service_details["price"] if service_details else "Contact for pricing"
        }
        
        self.slots.append(new_slot)
        return new_slot
    
    def book_slot(self, slot_id: str, service: str, customer_name: str, contact: str) -> Dict[str, Any]:
        """Book a slot"""
        try:
            # Find the slot
            slot = self.get_slot_by_id(slot_id)
            if not slot:
                return {
                    "success": False,
                    "error": "Slot not found or not available"
                }
            
            # Generate booking ID
            booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
            
            # Create booking record
            booking = {
                "booking_id": booking_id,
                "slot_id": slot_id,
                "customer_name": customer_name,
                "contact": contact,
                "service": service,
                "date": slot["date"],
                "time": slot["time"],
                "duration": slot["duration"],
                "price": slot["price"],
                "status": "confirmed",
                "created_at": datetime.now().isoformat()
            }
            
            # Store booking
            self.bookings[booking_id] = booking
            
            # Mark slot as unavailable
            for i, s in enumerate(self.slots):
                if s["slot_id"] == slot_id:
                    self.slots[i]["available"] = False
                    break
            
            return {
                "success": True,
                "booking_id": booking_id,
                "booking": booking
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """Get booking details by booking ID"""
        return self.bookings.get(booking_id)
    
    def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel a booking"""
        try:
            booking = self.get_booking(booking_id)
            if not booking:
                return {
                    "success": False,
                    "error": "Booking not found"
                }
            
            # Mark slot as available again
            slot_id = booking["slot_id"]
            for i, slot in enumerate(self.slots):
                if slot["slot_id"] == slot_id:
                    self.slots[i]["available"] = True
                    break
            
            # Update booking status
            self.bookings[booking_id]["status"] = "cancelled"
            self.bookings[booking_id]["cancelled_at"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "message": "Booking cancelled successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_upcoming_events(self) -> List[Dict[str, Any]]:
        """Get upcoming events"""
        today = datetime.now().strftime("%Y-%m-%d")
        return [event for event in self.events if event["date"] >= today]
    
    def get_contact_info(self) -> Dict[str, Any]:
        """Get contact information"""
        return self.contact_info
    
    def get_customer_bookings(self, contact: str) -> List[Dict[str, Any]]:
        """Get all bookings for a customer by contact info"""
        customer_bookings = []
        for booking in self.bookings.values():
            if booking["contact"] == contact and booking["status"] == "confirmed":
                customer_bookings.append(booking)
        
        return sorted(customer_bookings, key=lambda x: x["date"])
    
    def get_daily_schedule(self, date: str) -> List[Dict[str, Any]]:
        """Get all bookings for a specific date"""
        daily_bookings = []
        for booking in self.bookings.values():
            if booking["date"] == date and booking["status"] == "confirmed":
                daily_bookings.append(booking)
        
        return sorted(daily_bookings, key=lambda x: x["time"])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get booking statistics"""
        total_slots = len(self.slots)
        available_slots = len([slot for slot in self.slots if slot["available"]])
        total_bookings = len([b for b in self.bookings.values() if b["status"] == "confirmed"])
        
        service_bookings = {}
        for booking in self.bookings.values():
            if booking["status"] == "confirmed":
                service = booking["service"]
                service_bookings[service] = service_bookings.get(service, 0) + 1
        
        return {
            "total_slots": total_slots,
            "available_slots": available_slots,
            "booked_slots": total_slots - available_slots,
            "total_bookings": total_bookings,
            "service_bookings": service_bookings,
            "occupancy_rate": round((1 - available_slots/total_slots) * 100, 2) if total_slots > 0 else 0
        }
