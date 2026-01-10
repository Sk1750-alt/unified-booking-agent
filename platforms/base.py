"""
Base Platform Adapter - Abstract interface for booking platforms
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class Listing(BaseModel):
    """Unified listing schema as per problem statement"""
    id: str
    platform: str
    property_name: str
    location: str
    price_per_night: float
    currency: str
    rating: float
    reviews_count: int
    cancellation_policy: str
    url: str
    amenities: List[str] = []
    property_type: str = ""
    guests_max: int = 2


class SearchQuery(BaseModel):
    """Search query parameters"""
    destination: str
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    guests: int = 2
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    cancellation_policy: Optional[str] = None


class BasePlatformAdapter(ABC):
    """Abstract base class for platform adapters"""
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the platform name"""
        pass
    
    @abstractmethod
    def search(self, query: SearchQuery) -> List[Listing]:
        """Search for listings matching the query"""
        pass
    
    @abstractmethod
    def get_listing_details(self, listing_id: str) -> Optional[Listing]:
        """Get detailed information for a specific listing"""
        pass
    
    def normalize(self, raw_listing: Dict[str, Any]) -> Listing:
        """Convert raw listing data to unified Listing schema"""
        return Listing(
            id=raw_listing.get("id", ""),
            platform=raw_listing.get("platform", self.platform_name),
            property_name=raw_listing.get("property_name", ""),
            location=raw_listing.get("location", ""),
            price_per_night=float(raw_listing.get("price_per_night", 0)),
            currency=raw_listing.get("currency", "USD"),
            rating=float(raw_listing.get("rating", 0)),
            reviews_count=int(raw_listing.get("reviews_count", 0)),
            cancellation_policy=raw_listing.get("cancellation_policy", "unknown"),
            url=raw_listing.get("url", ""),
            amenities=raw_listing.get("amenities", []),
            property_type=raw_listing.get("property_type", ""),
            guests_max=int(raw_listing.get("guests_max", 2))
        )
