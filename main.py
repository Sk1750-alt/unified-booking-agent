"""
Unified Booking Agent - Main FastAPI Application
MCP-based booking agent for Backpackers' Bytes Hackathon
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from mcp_server import MCPServer
from nlp_parser import NLPParser
import google.generativeai as genai
import config
import json


# Initialize FastAPI app
app = FastAPI(
    title="Unified Booking Agent",
    description="MCP-based booking agent that searches across multiple platforms",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP server and NLP parser
mcp_server = MCPServer()
nlp_parser = NLPParser()


# Request/Response models
class ChatRequest(BaseModel):
    """Natural language query from user"""
    query: str


class ToolInvocationRequest(BaseModel):
    """Direct MCP tool invocation request"""
    tool_name: str
    parameters: Dict[str, Any]


class ChatResponse(BaseModel):
    """Chat response with recommendation"""
    success: bool
    message: str
    parsed_query: Dict[str, Any]
    recommendation: Optional[Dict[str, Any]]
    explanation: Optional[Dict[str, Any]]
    all_options: Optional[List[Dict[str, Any]]]
    tools_invoked: List[str]


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve the landing page"""
    return FileResponse("static/home.html")


@app.get("/chat")
async def chat_ui():
    """Serve the main chatbot interface"""
    return FileResponse("static/index.html")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/tools")
async def get_tools():
    """Get list of available MCP tools"""
    return {
        "tools": mcp_server.get_tools(),
        "count": len(mcp_server.get_tools())
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chatbot endpoint - processes natural language queries
    
    This is the primary interface for users. It:
    1. Parses the natural language query
    2. Determines which MCP tools to invoke
    3. Executes the search and recommendation
    4. Returns results with explanation
    """
    query = request.query.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Parse natural language query
    parsed = nlp_parser.parse(query)
    tools_invoked = []
    
    # Check if we have a destination
    if not parsed.get("destination"):
        return ChatResponse(
            success=False,
            message="I couldn't identify a destination in your query. Please specify where you'd like to stay (e.g., 'Find me a hotel in Goa').",
            parsed_query=parsed,
            recommendation=None,
            explanation=None,
            all_options=None,
            tools_invoked=[]
        )
    
    # Build preferences from parsed query
    preferences = {}
    if parsed.get("max_price"):
        preferences["max_price"] = parsed["max_price"]
    if parsed.get("min_rating"):
        preferences["min_rating"] = parsed["min_rating"]
    if parsed.get("cancellation_policy"):
        preferences["cancellation_policy"] = parsed["cancellation_policy"]
    
    # Invoke MCP tools
    
    # 1. Search accommodations
    search_result = mcp_server.invoke_tool("search_accommodations", {
        "destination": parsed["destination"],
        "guests": parsed.get("guests", 2),
        "max_price": parsed.get("max_price"),
        "min_rating": parsed.get("min_rating"),
        "cancellation_policy": parsed.get("cancellation_policy")
    })
    tools_invoked.append("search_accommodations")
    
    if not search_result.success:
        return ChatResponse(
            success=False,
            message=f"Search failed: {search_result.error}",
            parsed_query=parsed,
            recommendation=None,
            explanation=None,
            all_options=None,
            tools_invoked=tools_invoked
        )
    
    listings = search_result.result.get("listings", [])
    
    if not listings:
        return ChatResponse(
            success=True,
            message=f"No accommodations found in {parsed['destination']} matching your criteria. Try adjusting your filters.",
            parsed_query=parsed,
            recommendation=None,
            explanation={
                "platforms_compared": search_result.result.get("platforms_queried", []),
                "total_options_evaluated": 0,
                "message": "No matches found"
            },
            all_options=[],
            tools_invoked=tools_invoked
        )
    
    # Sort listings by strategy for ranked display
    strategy = parsed.get("selection_strategy", "best_value")
    
    if strategy == "cheapest":
        sorted_listings = sorted(listings, key=lambda x: x.get("price_per_night", float('inf')))
    elif strategy == "highest_rating":
        sorted_listings = sorted(listings, key=lambda x: (-x.get("rating", 0), -x.get("reviews_count", 0)))
    elif strategy == "best_value":
        # Best value = rating / (price/1000) - higher is better
        sorted_listings = sorted(listings, key=lambda x: -(x.get("rating", 0) / (x.get("price_per_night", 1) / 1000)))
    elif strategy == "flexible_cancellation":
        # Flexible policies first, then by rating
        def flex_score(x):
            policy = x.get("cancellation_policy", "")
            policy_score = 3 if policy in ["flexible", "free_cancellation"] else (2 if policy == "moderate" else 1)
            return (-policy_score, -x.get("rating", 0))
        sorted_listings = sorted(listings, key=flex_score)
    else:
        sorted_listings = listings
    
    # 2. Select best option
    select_result = mcp_server.invoke_tool("select_best", {
        "destination": parsed["destination"],
        "strategy": strategy,
        "preferences": preferences
    })
    tools_invoked.append("select_best")
    
    if not select_result.success:
        return ChatResponse(
            success=False,
            message=f"Selection failed: {select_result.error}",
            parsed_query=parsed,
            recommendation=None,
            explanation=None,
            all_options=sorted_listings,
            tools_invoked=tools_invoked
        )
    
    selected = select_result.result.get("selected")
    explanation = select_result.result.get("explanation", {})
    
    # Build response message
    gemini_used = False
    if getattr(config, "GEMINI_API_KEY", None):
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            options_str = "\n".join([
                f"- {opt.get('property_name')} ({opt.get('platform')}): Rs.{opt.get('price_per_night')}/night, {opt.get('rating')}★, {opt.get('reviews_count')} reviews, cancellation: {opt.get('cancellation_policy')}, amenities: {', '.join(opt.get('amenities', []))}"
                for opt in sorted_listings[:5]
            ])
            
            selected_str = ""
            if selected:
                selected_str = f"Selected Option: {selected.get('property_name')} ({selected.get('platform')}) - Rs.{selected.get('price_per_night')}/night, {selected.get('rating')}★, cancellation: {selected.get('cancellation_policy')}."
            else:
                selected_str = "No specific option could be selected."
                
            explanation_str = json.dumps(explanation)
            
            prompt = f"""
            You are a friendly, expert travel booking assistant called "Unified Booking Agent".
            The user asked: "{query}"
            We ran searches across platforms and evaluated options.
            
            {selected_str}
            
            Here are the top options we evaluated:
            {options_str}
            
            Explanation details:
            {explanation_str}
            
            Task:
            Write a warm, helpful, and concise response to the user.
            1. Introduce the recommendation in a professional, natural way (or explain if no options matched).
            2. Explain clearly why the selected option was chosen (mentioning price, rating, cancellation policy, and comparing platforms).
            3. Briefly mention the next best alternative from the options list to show thoroughness and give them choices.
            4. Keep the tone conversational, helpful, and concise. Use markdown formatting. Do not use generic placeholders.
            """
            
            response = model.generate_content(prompt)
            message = response.text.strip()
            gemini_used = True
        except Exception as e:
            print(f"Failed to generate conversational explanation with Gemini: {e}")
            gemini_used = False

    if not gemini_used:
        if selected:
            message = f"I found the perfect place for you!\n\n**{selected['property_name']}** in {selected['location']}\n\n"
            message += f"Price: Rs.{selected['price_per_night']}/night  |  Rating: {selected['rating']} ({selected['reviews_count']} reviews)\n\n"
            message += f"{explanation.get('message', '')}"
        else:
            message = "I couldn't find a suitable accommodation matching all your preferences."
    
    return ChatResponse(
        success=True,
        message=message,
        parsed_query=parsed,
        recommendation=selected,
        explanation=explanation,
        all_options=sorted_listings[:10],  # Return top 10 sorted by strategy
        tools_invoked=tools_invoked
    )


@app.post("/api/tool/invoke")
async def invoke_tool(request: ToolInvocationRequest):
    """
    Direct MCP tool invocation endpoint
    
    Allows direct tool calls for testing and advanced usage
    """
    result = mcp_server.invoke_tool(request.tool_name, request.parameters)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    
    return {
        "tool_name": result.tool_name,
        "success": result.success,
        "result": result.result
    }


@app.get("/api/platforms")
async def get_platforms():
    """Get list of connected booking platforms"""
    return {
        "platforms": [
            {"name": "MockAirbnb", "type": "mock", "status": "connected"},
            {"name": "MockBooking", "type": "mock", "status": "connected"}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    print("\n=== Starting Unified Booking Agent ===")
    print(">>> Open http://localhost:8000 in your browser\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
