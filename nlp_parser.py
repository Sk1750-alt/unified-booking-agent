"""
Natural Language Query Parser
Extracts structured parameters from user's natural language queries
"""
import re
import json
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from platforms.base import SearchQuery
import config


class NLPParser:
    """Parse natural language queries into structured search parameters"""
    
    # Location keywords mapping (fallback only when no explicit city found)
    LOCATION_ALIASES = {
        "beach": ["goa", "pondicherry", "kerala"],
        "mountain": ["manali", "shimla", "darjeeling"],
        "city": ["mumbai", "delhi", "kolkata", "bangalore", "chennai"],
        "heritage": ["jaipur", "udaipur", "varanasi"]
    }
    
    # Known cities/destinations (Indian + International)
    KNOWN_DESTINATIONS = [
        # Indian cities (Tier 1, 2, Tourist)
        "goa", "mumbai", "delhi", "jaipur", "kerala", "manali", 
        "pondicherry", "kolkata", "bangalore", "chennai", "udaipur",
        "shimla", "darjeeling", "varanasi", "agra", "hyderabad",
        "pune", "ahmedabad", "surat", "lucknow", "kanpur", "nagpur",
        "indore", "thane", "bhopal", "visakhapatnam", "patna",
        "vadodara", "ghaziabad", "ludhiana", "coimbatore", "madurai",
        "nashik", "faridabad", "meerut", "rajkot", "srinagar",
        "ranchi", "jabalpur", "gwalior", "vijayawada", "jodhpur",
        "raipur", "guwahati", "chandigarh", "mysore", "rishikesh",
        "haridwar", "ooty", "bhubaneswar", "amritsar", "gangtok",
        "jaisalmer", "munnar", "alleppey", "coorg", "leh", "ladakh",
        "dehradun", "thiruvananthapuram", "shillong", "imphal", 
        "aizawl", "kohima", "agartala", "itanagar", "dispur", "panaji",
        "gandhinagar", "kota", "bikaner", "ajmer", "jamshedpur",
        "noida", "gurgaon", "fariadabad", "aligarh", "allahabad",
        "prayagraj", "jhansi", "bareilly", "moradabad", "gorakhpur",
        "aurangabad", "solapur", "amravati", "jalandhar", "patiala",
        "bathinda", "mangalore", "hampi", "gokarna", "tirupati",
        "warangal", "visakhapatnam", "kochi", "kozhikode", "thrissur",
        "kollam", "varkala", "kovalam", "kodiakanal", "rameshwaram",
        "kanyakumari", "andaman", "nicobar", "lakshadweep",
        "dharamshala", "kasol", "spiti", "manikaran", "kedarnath",
        "badrinath", "nainital", "mussoorie", "kullu", "dalhousie",
        "khajuraho", "hampi", "mahabaleshwar", "lonavala", "khandala",
        "shirdi", "tirupati", "puri", "konark", "sundarbans", "siliguri",
        "haora", "durgapur", "asansol", "kharagpur", "haldia",
        # International cities
        "london", "paris", "new york", "dubai", "singapore", "bangkok",
        "tokyo", "sydney", "barcelona", "amsterdam", "rome", "bali",
        "phuket", "maldives", "hong kong", "las vegas", "los angeles",
        "san francisco", "miami", "hawaii", "cancun", "ibiza"
    ]
    
    def __init__(self):
        self._gemini_ready = False
        if getattr(config, "GEMINI_API_KEY", None):
            try:
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(
                    model_name="models/gemini-2.5-flash",
                    generation_config={"response_mime_type": "application/json"}
                )
                self._gemini_ready = True
                print("Gemini API initialized successfully for NLP Parser.")
            except Exception as e:
                print(f"Failed to initialize Gemini API parser: {e}")

    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parse a natural language query and extract structured parameters
        
        Returns:
            Dict with keys: destination, guests, max_price, min_rating, 
                           cancellation_policy, selection_strategy
        """
        if self._gemini_ready:
            try:
                prompt = f"""
                Analyze the following travel booking query: "{query}"
                
                Extract structured travel parameters into a JSON object.
                
                Rules:
                1. "destination": The target city/location. If not found, use "".
                2. "guests": Number of guests (default is 2).
                3. "max_price": Maximum price per night as a number. If not specified, set to null.
                4. "min_rating": Minimum rating required as a number. Highly/best/top rated = 4.5, good/decent rating = 4.0. If not specified, set to null.
                5. "cancellation_policy": Set to "flexible" if user requests flexible, free cancellation, refundable, cancel anytime. Otherwise null.
                6. "selection_strategy": Choose one of:
                   - "cheapest" (if budget, cheap, cheapest, lowest price)
                   - "highest_rating" (if best rated, highest rated, top rated)
                   - "flexible_cancellation" (if free/flexible cancellation is top priority)
                   - "best_value" (default value, worth, balance)
                7. "check_in": Extract target check-in date or period if mentioned, else null.
                8. "check_out": Extract target check-out date if mentioned, else null.
                
                Return ONLY a JSON object with this structure:
                {{
                  "destination": "",
                  "guests": 2,
                  "max_price": null,
                  "min_rating": null,
                  "cancellation_policy": null,
                  "selection_strategy": "best_value",
                  "check_in": null,
                  "check_out": null
                }}
                """
                response = self.model.generate_content(prompt)
                parsed = json.loads(response.text.strip())
                # Ensure destination is capitalized
                if parsed.get("destination"):
                    parsed["destination"] = parsed["destination"].title()
                return parsed
            except Exception as e:
                print(f"Gemini parsing failed, falling back to regex: {e}")

        # Fallback to regex-based parsing
        query_lower = query.lower()
        
        result = {
            "destination": self._extract_destination(query_lower),
            "guests": self._extract_guests(query_lower),
            "max_price": self._extract_max_price(query_lower),
            "min_rating": self._extract_min_rating(query_lower),
            "cancellation_policy": self._extract_cancellation_policy(query_lower),
            "selection_strategy": self._infer_selection_strategy(query_lower),
            "check_in": self._extract_dates(query_lower).get("check_in"),
            "check_out": self._extract_dates(query_lower).get("check_out"),
        }
        
        return result
    
    def _extract_destination(self, query: str) -> str:
        """Extract destination from query"""
        # PRIORITY 1: Try to find "in <location>" pattern FIRST (explicit mention)
        in_pattern = re.search(r'in\s+([a-zA-Z\s]+?)(?:\s+for|\s+from|\s+under|\s+with|\s+under|\s*$)', query)
        if in_pattern:
            location = in_pattern.group(1).strip()
            # Clean up common words
            location = re.sub(r'\b(hotel|stay|place|accommodation|a|the|beach|house)\b', '', location).strip()
            if location and len(location) > 1:
                return location.title()
        
        # PRIORITY 2: Check for known destinations anywhere in query
        for dest in self.KNOWN_DESTINATIONS:
            # Use word boundary to avoid partial matches
            if re.search(r'\b' + re.escape(dest) + r'\b', query):
                return dest.title()
        
        # PRIORITY 3: Fallback to location type aliases (only if no destination found)
        for location_type, destinations in self.LOCATION_ALIASES.items():
            if location_type in query:
                return destinations[0].title()
        
        return ""
    
    def _extract_guests(self, query: str) -> int:
        """Extract number of guests from query"""
        # Pattern: "for X guests/people/persons"
        guest_pattern = re.search(r'(\d+)\s*(?:guests?|people|persons?|pax)', query)
        if guest_pattern:
            return int(guest_pattern.group(1))
        
        # Pattern: "X of us"
        us_pattern = re.search(r'(\d+)\s+of\s+us', query)
        if us_pattern:
            return int(us_pattern.group(1))
        
        return 2  # Default
    
    def _extract_max_price(self, query: str) -> Optional[float]:
        """Extract maximum price from query"""
        # Pattern: "under/below ₹X" or "under X rupees" or "under Rs.X"
        price_patterns = [
            r'under\s*[₹$]?\s*(\d+)',
            r'under\s*rs\.?\s*(\d+)',
            r'below\s*[₹$]?\s*(\d+)',
            r'below\s*rs\.?\s*(\d+)',
            r'less\s+than\s*[₹$]?\s*(\d+)',
            r'budget\s+(?:of\s+)?[₹$]?\s*(\d+)',
            r'budget\s+(?:of\s+)?rs\.?\s*(\d+)',
            r'max(?:imum)?\s*[₹$]?\s*(\d+)',
            r'[₹$](\d+)\s*(?:per\s*night|\/night)?',
            r'rs\.?\s*(\d+)\s*(?:per\s*night|\/night)?'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, query)
            if match:
                return float(match.group(1))
        
        return None
    
    def _extract_min_rating(self, query: str) -> Optional[float]:
        """Extract minimum rating requirement"""
        # Check for rating keywords
        if any(word in query for word in ["highly rated", "top rated", "best rated", "excellent"]):
            return 4.5
        if any(word in query for word in ["good rating", "well rated", "decent"]):
            return 4.0
        
        # Pattern: "rating above X" or "X+ rating"
        rating_pattern = re.search(r'(\d+\.?\d*)\+?\s*(?:star|rating)', query)
        if rating_pattern:
            return float(rating_pattern.group(1))
        
        return None
    
    def _extract_cancellation_policy(self, query: str) -> Optional[str]:
        """Extract cancellation policy preference"""
        if any(phrase in query for phrase in [
            "free cancellation", "flexible cancellation", 
            "cancel anytime", "refundable", "flexible"
        ]):
            return "flexible"
        
        return None
    
    def _extract_dates(self, query: str) -> Dict[str, Optional[str]]:
        """Extract check-in and check-out dates"""
        # This is a simplified implementation
        # In production, would use dateparser library
        dates = {"check_in": None, "check_out": None}
        
        # Pattern: "from Jan 15-18" or "Jan 15 to Jan 18"
        date_range = re.search(
            r'(?:from\s+)?([A-Za-z]+\s+\d+)(?:\s*[-to]+\s*\d+|\s+to\s+[A-Za-z]+\s+\d+)?', 
            query
        )
        if date_range:
            dates["check_in"] = date_range.group(1)
        
        return dates
    
    def _infer_selection_strategy(self, query: str) -> str:
        """Infer the selection strategy from the query"""
        # Cheapest
        if any(word in query for word in ["cheapest", "budget", "affordable", "cheap", "lowest price"]):
            return "cheapest"
        
        # Highest rating
        if any(word in query for word in ["best rated", "highest rated", "top rated", "best reviews"]):
            return "highest_rating"
        
        # Best value
        if any(word in query for word in ["best value", "value for money", "worth"]):
            return "best_value"
        
        # Flexible cancellation
        if any(word in query for word in ["flexible", "free cancellation", "refundable"]):
            return "flexible_cancellation"
        
        # Default to best value
        return "best_value"
    
    def to_search_query(self, parsed: Dict[str, Any]) -> SearchQuery:
        """Convert parsed result to SearchQuery object"""
        return SearchQuery(
            destination=parsed.get("destination", ""),
            check_in=parsed.get("check_in"),
            check_out=parsed.get("check_out"),
            guests=parsed.get("guests", 2),
            max_price=parsed.get("max_price"),
            min_rating=parsed.get("min_rating"),
            cancellation_policy=parsed.get("cancellation_policy")
        )
