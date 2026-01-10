"""
MCP Server Implementation
Exposes tools for searching, retrieving, and recommending accommodations
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from platforms import MockAirbnbAdapter, MockBookingAdapter, BookingComAdapter, Listing, SearchQuery
from recommendation import RecommendationEngine


class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]


class MCPToolResult(BaseModel):
    """MCP Tool execution result"""
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None


class MCPServer:
    """
    MCP-compliant server exposing tools for accommodation search and recommendation
    
    Tools:
    - search_accommodations: Search across all platforms
    - get_listing_details: Get details for a specific listing
    - rank_options: Rank listings by strategy
    - select_best: Select the best option with explanation
    
    Platforms:
    - Booking.com (REAL API via RapidAPI)
    - MockAirbnb (simulated)
    - MockBooking (simulated)
    """
    
    def __init__(self):
        # Initialize platform adapters (1 REAL + 2 MOCK)
        self.platforms = [
            BookingComAdapter(),  # REAL Booking.com API
            MockAirbnbAdapter(),  # Mock Airbnb-style
            MockBookingAdapter()  # Mock Booking-style
        ]
        
        # Initialize recommendation engine
        self.recommender = RecommendationEngine()
        
        # Define available tools
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[MCPTool]:
        """Define available MCP tools"""
        return [
            MCPTool(
                name="search_accommodations",
                description="Search for accommodations across all connected booking platforms",
                parameters={
                    "type": "object",
                    "properties": {
                        "destination": {"type": "string", "description": "City or location to search"},
                        "guests": {"type": "integer", "description": "Number of guests", "default": 2},
                        "max_price": {"type": "number", "description": "Maximum price per night"},
                        "min_rating": {"type": "number", "description": "Minimum rating (1-5)"},
                        "cancellation_policy": {"type": "string", "description": "Preferred cancellation policy"}
                    },
                    "required": ["destination"]
                }
            ),
            MCPTool(
                name="get_listing_details",
                description="Get detailed information about a specific listing",
                parameters={
                    "type": "object",
                    "properties": {
                        "listing_id": {"type": "string", "description": "ID of the listing"},
                        "platform": {"type": "string", "description": "Platform name (MockAirbnb or MockBooking)"}
                    },
                    "required": ["listing_id"]
                }
            ),
            MCPTool(
                name="rank_options",
                description="Rank all available listings by a specified strategy",
                parameters={
                    "type": "object",
                    "properties": {
                        "listings": {"type": "array", "description": "List of listing IDs to rank"},
                        "strategy": {
                            "type": "string",
                            "enum": ["cheapest", "highest_rating", "best_value", "flexible_cancellation"],
                            "description": "Ranking strategy"
                        }
                    },
                    "required": ["listings", "strategy"]
                }
            ),
            MCPTool(
                name="select_best",
                description="Select the best accommodation based on user preferences",
                parameters={
                    "type": "object",
                    "properties": {
                        "destination": {"type": "string", "description": "City or location"},
                        "strategy": {"type": "string", "description": "Selection strategy"},
                        "preferences": {"type": "object", "description": "User preferences"}
                    },
                    "required": ["destination"]
                }
            )
        ]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools in MCP format"""
        return [tool.model_dump() for tool in self.tools]
    
    def invoke_tool(self, tool_name: str, parameters: Dict[str, Any]) -> MCPToolResult:
        """
        Invoke a tool by name with given parameters
        
        This is the core MCP tool invocation method
        """
        try:
            if tool_name == "search_accommodations":
                result = self._search_accommodations(parameters)
            elif tool_name == "get_listing_details":
                result = self._get_listing_details(parameters)
            elif tool_name == "rank_options":
                result = self._rank_options(parameters)
            elif tool_name == "select_best":
                result = self._select_best(parameters)
            else:
                return MCPToolResult(
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=f"Unknown tool: {tool_name}"
                )
            
            return MCPToolResult(
                tool_name=tool_name,
                success=True,
                result=result
            )
            
        except Exception as e:
            return MCPToolResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=str(e)
            )
    
    def _search_accommodations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search across all platforms"""
        query = SearchQuery(
            destination=params.get("destination", ""),
            guests=params.get("guests", 2),
            max_price=params.get("max_price"),
            min_rating=params.get("min_rating"),
            cancellation_policy=params.get("cancellation_policy")
        )
        
        all_listings = []
        platforms_queried = []
        
        for platform in self.platforms:
            listings = platform.search(query)
            all_listings.extend(listings)
            platforms_queried.append(platform.platform_name)
        
        return {
            "listings": [l.model_dump() for l in all_listings],
            "count": len(all_listings),
            "platforms_queried": platforms_queried,
            "query": query.model_dump()
        }
    
    def _get_listing_details(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get details for a specific listing"""
        listing_id = params.get("listing_id", "")
        platform_name = params.get("platform")
        
        for platform in self.platforms:
            if platform_name and platform.platform_name != platform_name:
                continue
            
            listing = platform.get_listing_details(listing_id)
            if listing:
                return listing.model_dump()
        
        return None
    
    def _rank_options(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank listings by strategy"""
        # First search for all listings
        destination = params.get("destination", "")
        strategy = params.get("strategy", "best_value")
        
        query = SearchQuery(destination=destination)
        all_listings = []
        
        for platform in self.platforms:
            all_listings.extend(platform.search(query))
        
        # Rank using recommendation engine
        ranked = self.recommender.rank_all(all_listings, strategy)
        
        return [
            {
                "rank": i + 1,
                "listing": r["listing"].model_dump(),
                "score": r["score"]
            }
            for i, r in enumerate(ranked)
        ]
    
    def _select_best(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Select the best option with explanation"""
        destination = params.get("destination", "")
        strategy = params.get("strategy", "best_value")
        preferences = params.get("preferences", {})
        
        # Search all platforms
        query = SearchQuery(
            destination=destination,
            max_price=preferences.get("max_price"),
            min_rating=preferences.get("min_rating"),
            cancellation_policy=preferences.get("cancellation_policy")
        )
        
        all_listings = []
        for platform in self.platforms:
            all_listings.extend(platform.search(query))
        
        # Get recommendation
        best, explanation = self.recommender.recommend(
            all_listings, 
            strategy, 
            preferences
        )
        
        return {
            "selected": best.model_dump() if best else None,
            "explanation": explanation,
            "all_options_count": len(all_listings)
        }
