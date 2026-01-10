"""
Recommendation Engine with Explainability
Implements intelligent selection logic for accommodation recommendations
"""
from typing import List, Dict, Any, Optional, Tuple
from platforms.base import Listing


class RecommendationEngine:
    """
    Intelligent recommendation engine that selects the best accommodation
    based on user preferences and explains the decision
    """
    
    STRATEGIES = ["cheapest", "highest_rating", "best_value", "flexible_cancellation"]
    
    def recommend(
        self, 
        listings: List[Listing], 
        strategy: str = "best_value",
        preferences: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optional[Listing], Dict[str, Any]]:
        """
        Select the best listing based on strategy and preferences
        
        Args:
            listings: List of normalized listings from all platforms
            strategy: Selection strategy (cheapest, highest_rating, best_value, flexible_cancellation)
            preferences: User preferences dict
        
        Returns:
            Tuple of (best_listing, explanation_dict)
        """
        if not listings:
            return None, self._generate_explanation(None, [], strategy, preferences)
        
        preferences = preferences or {}
        
        # Apply preference filters first
        filtered = self._apply_preference_filters(listings, preferences)
        
        if not filtered:
            filtered = listings  # Fallback to all listings if filters too strict
        
        # Select best based on strategy
        best = self._select_by_strategy(filtered, strategy)
        
        # Generate explanation
        explanation = self._generate_explanation(best, listings, strategy, preferences)
        
        return best, explanation
    
    def _apply_preference_filters(
        self, 
        listings: List[Listing], 
        preferences: Dict[str, Any]
    ) -> List[Listing]:
        """Apply user preference filters to listings"""
        filtered = listings.copy()
        
        # Filter by max price
        if preferences.get("max_price"):
            max_price = preferences["max_price"]
            filtered = [l for l in filtered if l.price_per_night <= max_price]
        
        # Filter by min rating
        if preferences.get("min_rating"):
            min_rating = preferences["min_rating"]
            filtered = [l for l in filtered if l.rating >= min_rating]
        
        # Filter by cancellation policy
        if preferences.get("cancellation_policy") == "flexible":
            filtered = [
                l for l in filtered 
                if l.cancellation_policy.lower() in ["flexible", "free_cancellation"]
            ]
        
        return filtered
    
    def _select_by_strategy(
        self, 
        listings: List[Listing], 
        strategy: str
    ) -> Optional[Listing]:
        """Select the best listing based on strategy"""
        if not listings:
            return None
        
        if strategy == "cheapest":
            return min(listings, key=lambda l: l.price_per_night)
        
        elif strategy == "highest_rating":
            return max(listings, key=lambda l: (l.rating, l.reviews_count))
        
        elif strategy == "best_value":
            # Value score = rating / (price / 50)  (normalized)
            # Higher rating and lower price = better value
            def value_score(listing: Listing) -> float:
                price_factor = max(listing.price_per_night, 1) / 50
                return listing.rating / price_factor
            return max(listings, key=value_score)
        
        elif strategy == "flexible_cancellation":
            # Prefer flexible, then sort by rating
            flexible = [
                l for l in listings 
                if l.cancellation_policy.lower() in ["flexible", "free_cancellation"]
            ]
            if flexible:
                return max(flexible, key=lambda l: l.rating)
            return max(listings, key=lambda l: l.rating)
        
        else:
            # Default: best value
            return max(listings, key=lambda l: l.rating / (l.price_per_night / 50))
    
    def _generate_explanation(
        self,
        selected: Optional[Listing],
        all_listings: List[Listing],
        strategy: str,
        preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate human-readable explanation for the selection"""
        preferences = preferences or {}
        
        # Count platforms
        platforms = set(l.platform for l in all_listings) if all_listings else set()
        
        if not selected:
            return {
                "success": False,
                "message": "No listings found matching your criteria.",
                "platforms_compared": list(platforms),
                "total_options_evaluated": len(all_listings),
                "strategy_used": strategy,
                "preferences_applied": preferences
            }
        
        # Build explanation message
        strategy_explanations = {
            "cheapest": f"Selected the cheapest option at Rs.{selected.price_per_night}/night.",
            "highest_rating": f"Selected the highest-rated property with {selected.rating}★ rating from {selected.reviews_count} reviews.",
            "best_value": f"Selected the best value option, balancing quality ({selected.rating} stars) with price (Rs.{selected.price_per_night}/night).",
            "flexible_cancellation": f"Selected a property with {selected.cancellation_policy} cancellation policy."
        }
        
        explanation_message = strategy_explanations.get(
            strategy, 
            f"Selected based on overall suitability."
        )
        
        # Add preference influence
        preference_notes = []
        if preferences.get("max_price"):
            preference_notes.append(f"budget of Rs.{preferences['max_price']}/night")
        if preferences.get("min_rating"):
            preference_notes.append(f"minimum {preferences['min_rating']}★ rating")
        if preferences.get("cancellation_policy"):
            preference_notes.append(f"{preferences['cancellation_policy']} cancellation preference")
        
        return {
            "success": True,
            "message": explanation_message,
            "platforms_compared": list(platforms),
            "total_options_evaluated": len(all_listings),
            "strategy_used": strategy,
            "strategy_description": self._get_strategy_description(strategy),
            "preferences_applied": preferences,
            "preference_influence": preference_notes if preference_notes else ["No specific preferences applied"],
            "why_selected": self._generate_why_selected(selected, all_listings, strategy),
            "alternatives_count": len(all_listings) - 1
        }
    
    def _get_strategy_description(self, strategy: str) -> str:
        """Get human-readable description of strategy"""
        descriptions = {
            "cheapest": "Find the lowest priced accommodation",
            "highest_rating": "Find the highest rated property regardless of price",
            "best_value": "Find the best balance between quality and price",
            "flexible_cancellation": "Prioritize properties with free/flexible cancellation"
        }
        return descriptions.get(strategy, "Find the most suitable option")
    
    def _generate_why_selected(
        self, 
        selected: Listing, 
        all_listings: List[Listing],
        strategy: str
    ) -> List[str]:
        """Generate list of reasons why this listing was selected"""
        reasons = []
        
        if not all_listings:
            return ["Only option available"]
        
        prices = [l.price_per_night for l in all_listings]
        ratings = [l.rating for l in all_listings]
        
        # Price comparison
        if selected.price_per_night == min(prices):
            reasons.append("Lowest price among all options")
        elif selected.price_per_night <= sum(prices) / len(prices):
            reasons.append("Below average price")
        
        # Rating comparison
        if selected.rating == max(ratings):
            reasons.append("Highest rating among all options")
        elif selected.rating >= 4.5:
            reasons.append("Excellent rating (4.5+)")
        elif selected.rating >= 4.0:
            reasons.append("Good rating (4.0+)")
        
        # Reviews
        if selected.reviews_count >= 500:
            reasons.append(f"Well-reviewed ({selected.reviews_count} reviews)")
        
        # Cancellation
        if selected.cancellation_policy.lower() in ["flexible", "free_cancellation"]:
            reasons.append("Flexible cancellation policy")
        
        if not reasons:
            reasons.append("Best overall match for the specified criteria")
        
        return reasons
    
    def rank_all(
        self, 
        listings: List[Listing], 
        strategy: str = "best_value"
    ) -> List[Dict[str, Any]]:
        """
        Rank all listings based on strategy
        
        Returns:
            List of dicts with listing and score
        """
        if not listings:
            return []
        
        ranked = []
        
        for listing in listings:
            if strategy == "cheapest":
                score = 1000 - listing.price_per_night  # Lower price = higher score
            elif strategy == "highest_rating":
                score = listing.rating * 20 + (listing.reviews_count / 100)
            elif strategy == "best_value":
                score = listing.rating / (listing.price_per_night / 50) * 10
            elif strategy == "flexible_cancellation":
                policy_score = 2 if listing.cancellation_policy.lower() in ["flexible", "free_cancellation"] else 0
                score = policy_score * 10 + listing.rating
            else:
                score = listing.rating
            
            ranked.append({
                "listing": listing,
                "score": round(score, 2),
                "strategy": strategy
            })
        
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked
