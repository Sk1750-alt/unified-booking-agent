"""
Test suite for NLP Parser functionality.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp_parser import NLPParser


class TestNLPParser:
    """Tests for the NLP Parser implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = NLPParser()
    
    def test_parse_destination(self):
        """Test destination extraction."""
        result = self.parser.parse("Find me a hotel in Mumbai")
        assert result["destination"] == "Mumbai"
    
    def test_parse_guests(self):
        """Test guest count extraction."""
        result = self.parser.parse("Hotel for 4 guests in Goa")
        assert result["guests"] == 4
    
    def test_parse_price_rupee_symbol(self):
        """Test price extraction with Rs. symbol."""
        result = self.parser.parse("Under Rs.5000 per night")
        assert result["max_price"] == 5000
    
    def test_parse_strategy_cheapest(self):
        """Test cheapest strategy detection."""
        result = self.parser.parse("Find cheapest hotel in Delhi")
        assert result["selection_strategy"] == "cheapest"
    
    def test_parse_strategy_highest_rating(self):
        """Test highest rating strategy detection."""
        result = self.parser.parse("Best rated place in Mumbai")
        assert result["selection_strategy"] == "highest_rating"
    
    def test_parse_cancellation_policy(self):
        """Test cancellation policy extraction."""
        result = self.parser.parse("Hotel with free cancellation")
        assert result["cancellation_policy"] in ["flexible", "free_cancellation"]
    
    def test_parse_complex_query(self):
        """Test parsing a complex multi-constraint query."""
        result = self.parser.parse(
            "Find me the cheapest hotel in Goa for 4 guests "
            "with free cancellation under Rs.5000"
        )
        
        assert result["destination"] == "Goa"
        assert result["guests"] == 4
        assert result["max_price"] == 5000
        assert result["selection_strategy"] == "cheapest"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
