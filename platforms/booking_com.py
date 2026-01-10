"""
Real Booking.com Platform Adapter
Uses RapidAPI Booking.com API for real hotel data
"""
import requests
from typing import List, Optional, Dict, Any
from .base import BasePlatformAdapter, Listing, SearchQuery


class BookingComAdapter(BasePlatformAdapter):
    """Real Booking.com API adapter using RapidAPI"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "5bcb6b870amsh20a048fe428a20cp10fc36jsn328162b382d2"
        self.base_url = "https://booking-com.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
        }
        # Cache for destination IDs
        self._dest_cache = {}
    
    @property
    def platform_name(self) -> str:
        return "Booking.com"
    
    def _get_destination_id(self, location: str) -> Optional[str]:
        """Get Booking.com destination ID for a location"""
        if location.lower() in self._dest_cache:
            return self._dest_cache[location.lower()]
        
        try:
            url = f"{self.base_url}/v1/hotels/locations"
            params = {
                "name": location,
                "locale": "en-gb"
            }
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Get the first matching destination
                    dest_id = data[0].get("dest_id")
                    self._dest_cache[location.lower()] = dest_id
                    return dest_id
        except Exception as e:
            print(f"Error getting destination ID: {e}")
        
        return None
    
    def search(self, query: SearchQuery) -> List[Listing]:
        """Search for hotels using Booking.com API"""
        listings = []
        
        try:
            # Get destination ID
            dest_id = self._get_destination_id(query.destination)
            
            if not dest_id:
                print(f"Could not find destination ID for {query.destination}")
                return listings
            
            # Search hotels
            url = f"{self.base_url}/v1/hotels/search"
            
            # Default dates (check-in tomorrow, check-out day after)
            from datetime import datetime, timedelta
            checkin = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            checkout = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            
            params = {
                "dest_id": dest_id,
                "dest_type": "city",
                "checkin_date": checkin,
                "checkout_date": checkout,
                "adults_number": query.guests or 2,
                "room_number": 1,
                "units": "metric",
                "order_by": "popularity",
                "locale": "en-gb",
                "currency": "INR",
                "filter_by_currency": "INR",
                "page_number": 0,
                "include_adjacency": "true"
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("result", [])
                
                for hotel in results[:10]:  # Limit to 10 results
                    listing = self._normalize_hotel(hotel)
                    if listing:
                        # Apply filters
                        if query.max_price and listing.price_per_night > query.max_price:
                            continue
                        if query.min_rating and listing.rating < query.min_rating:
                            continue
                        listings.append(listing)
            else:
                print(f"Booking.com API error: {response.status_code}")
                
        except Exception as e:
            print(f"Error searching Booking.com: {e}")
        
        return listings
    
    def _normalize_hotel(self, hotel: Dict[str, Any]) -> Optional[Listing]:
        """Normalize Booking.com hotel data to unified schema"""
        try:
            # Extract price
            price = hotel.get("min_total_price") or hotel.get("composite_price_breakdown", {}).get("gross_amount_per_night", {}).get("value", 0)
            if not price:
                price_str = hotel.get("price_breakdown", {}).get("gross_price", "0")
                try:
                    price = float(str(price_str).replace(",", "").replace("INR", "").strip())
                except:
                    price = 0
            
            # Extract rating
            rating = hotel.get("review_score", 0) / 2  # Booking uses 10-point scale
            if rating == 0:
                rating = 4.0  # Default
            
            # Extract review count
            review_count = hotel.get("review_nr", 0)
            
            # Determine cancellation policy
            is_free_cancel = hotel.get("is_free_cancellable", False)
            cancel_policy = "free_cancellation" if is_free_cancel else "moderate"
            
            return Listing(
                id=f"bkcom_{hotel.get('hotel_id', '')}",
                platform="Booking.com",
                property_name=hotel.get("hotel_name", "Unknown Hotel"),
                location=f"{hotel.get('city', '')}, {hotel.get('country_trans', 'India')}",
                price_per_night=round(float(price)),
                currency="INR",
                rating=round(rating, 1),
                reviews_count=int(review_count),
                cancellation_policy=cancel_policy,
                url=hotel.get("url", ""),
                amenities=[],
                property_type=hotel.get("accommodation_type_name", "Hotel"),
                guests_max=hotel.get("max_photo_url", 2)  # Default 2
            )
        except Exception as e:
            print(f"Error normalizing hotel: {e}")
            return None
    
    def get_listing_details(self, listing_id: str) -> Optional[Listing]:
        """Get details for a specific listing"""
        # For now, return None - would need hotel_id extraction
        return None
    
    def normalize(self, raw_data: Dict[str, Any]) -> Listing:
        """Normalize raw data to Listing schema"""
        return self._normalize_hotel(raw_data)
