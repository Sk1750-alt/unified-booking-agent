"""
Mock Airbnb Platform Adapter
"""
import json
import os
from typing import List, Optional
from .base import BasePlatformAdapter, Listing, SearchQuery


class MockAirbnbAdapter(BasePlatformAdapter):
    """Mock Airbnb platform adapter"""
    
    def __init__(self):
        self._listings: List[dict] = []
        self._load_data()
    
    @property
    def platform_name(self) -> str:
        return "MockAirbnb"
    
    def _load_data(self):
        """Load mock data from JSON file"""
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "mock_listings.json")
        try:
            with open(data_path, "r") as f:
                data = json.load(f)
                self._listings = data.get("mock_airbnb", [])
        except Exception as e:
            print(f"Error loading mock data: {e}")
            self._listings = []
    
    def search(self, query: SearchQuery) -> List[Listing]:
        """Search for listings matching the query"""
        results = []
        
        for raw_listing in self._listings:
            # Filter by destination (case-insensitive partial match)
            if query.destination.lower() not in raw_listing.get("location", "").lower():
                continue
            
            # Filter by max price
            if query.max_price and raw_listing.get("price_per_night", 0) > query.max_price:
                continue
            
            # Filter by min rating
            if query.min_rating and raw_listing.get("rating", 0) < query.min_rating:
                continue
            
            # Filter by guests capacity
            if query.guests and raw_listing.get("guests_max", 2) < query.guests:
                continue
            
            # Filter by cancellation policy
            if query.cancellation_policy:
                policy = raw_listing.get("cancellation_policy", "").lower()
                if query.cancellation_policy.lower() == "flexible":
                    if policy not in ["flexible", "free_cancellation"]:
                        continue
            
            results.append(self.normalize(raw_listing))
        
            results.append(self.normalize(raw_listing))
        
        # If no results found in static data, generate dynamic ones for the requested destination
        if not results and query.destination:
            results = self._generate_dynamic_listings(query)
            
        return results

    def _generate_dynamic_listings(self, query: SearchQuery) -> List[Listing]:
        """Generate realistic dynamic listings for any destination"""
        import random
        
        city = query.destination.title()
        results = []
        
        # Determine price range based on query or default
        base_price = query.max_price or 5000
        if base_price < 2000: base_price = 2000
        
        property_types = ["Apartment", "City Studio", "Cozy Loft", "Vacation Home", "Villa"]
        
        for i in range(1, 4):  # Generate 3 listings
            price = random.randint(int(base_price * 0.6), int(base_price))
            rating = round(random.uniform(4.0, 4.9), 1)
            prop_type = random.choice(property_types)
            
            dynamic_listing = Listing(
                id=f"dyn_air_{city[:3].lower()}_{i}",
                platform="MockAirbnb",
                property_name=f"{prop_type} in {city}",
                location=f"{city}",
                price_per_night=price,
                currency="INR",
                rating=rating,
                reviews_count=random.randint(10, 500),
                cancellation_policy="flexible",
                url=f"https://mock-airbnb.com/listing/dyn_{i}",
                amenities=["wifi", "kitchen", "ac", "workspace"],
                property_type=prop_type.lower().replace(" ", "_"),
                guests_max=query.guests + random.randint(0, 2)
            )
            results.append(dynamic_listing)
            
        return results
    
    def get_listing_details(self, listing_id: str) -> Optional[Listing]:
        """Get detailed information for a specific listing"""
        for raw_listing in self._listings:
            if raw_listing.get("id") == listing_id:
                return self.normalize(raw_listing)
        return None
