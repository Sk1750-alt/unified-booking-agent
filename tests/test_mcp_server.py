"""
Test suite for MCP Server functionality.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server import MCPServer


class TestMCPServer:
    """Tests for the MCP Server implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.server = MCPServer()
    
    def test_list_tools(self):
        """Test that all tools are properly registered."""
        tools = self.server.list_tools()
        
        assert len(tools) == 4
        tool_names = [t["name"] for t in tools]
        
        assert "search_accommodations" in tool_names
        assert "get_listing_details" in tool_names
        assert "rank_options" in tool_names
        assert "select_best" in tool_names
    
    def test_search_accommodations_goa(self):
        """Test searching for accommodations in Goa."""
        result = self.server.invoke_tool(
            "search_accommodations",
            {"destination": "Goa"}
        )
        
        assert result["success"] == True
        assert len(result["result"]["listings"]) > 0
        assert "MockAirbnb" in result["result"]["platforms_queried"]
    
    def test_search_accommodations_no_destination(self):
        """Test that search fails without destination."""
        result = self.server.invoke_tool(
            "search_accommodations",
            {}
        )
        
        assert result["success"] == False
        assert "error" in result
    
    def test_select_best_cheapest(self):
        """Test selecting best option with cheapest strategy."""
        result = self.server.invoke_tool(
            "select_best",
            {"destination": "Goa", "strategy": "cheapest"}
        )
        
        assert result["success"] == True
        assert result["result"]["selected"] is not None
        assert "explanation" in result["result"]
    
    def test_rank_options(self):
        """Test ranking options by strategy."""
        result = self.server.invoke_tool(
            "rank_options",
            {"destination": "Mumbai", "strategy": "highest_rating"}
        )
        
        assert result["success"] == True
        # Results should be sorted by rating (descending)
        rankings = result["result"]
        if len(rankings) > 1:
            assert rankings[0]["rank"] < rankings[1]["rank"]


class TestToolSchemas:
    """Tests for tool parameter schemas."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.server = MCPServer()
        self.tools = {t["name"]: t for t in self.server.list_tools()}
    
    def test_search_accommodations_schema(self):
        """Test search_accommodations has correct schema."""
        tool = self.tools["search_accommodations"]
        params = tool["parameters"]["properties"]
        
        assert "destination" in params
        assert "guests" in params
        assert "max_price" in params
        assert "min_rating" in params
    
    def test_select_best_schema(self):
        """Test select_best has correct schema."""
        tool = self.tools["select_best"]
        params = tool["parameters"]["properties"]
        
        assert "destination" in params
        assert "strategy" in params


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
