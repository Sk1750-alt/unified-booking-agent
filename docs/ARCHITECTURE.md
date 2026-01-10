# Architecture Overview

## System Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Chatbot Frontend                           │  │
│  │   • Natural language input                                   │  │
│  │   • Recommendation cards                                     │  │
│  │   • Explanation panels                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                       FASTAPI BACKEND                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐   │
│  │   NLP Parser    │  │   MCP Server    │  │  Recommendation  │   │
│  │                 │  │                 │  │     Engine       │   │
│  │ • Destination   │  │ • Tool Registry │  │                  │   │
│  │ • Guests        │  │ • Tool Invoker  │  │ • Cheapest       │   │
│  │ • Budget        │  │ • Result Format │  │ • Highest Rating │   │
│  │ • Preferences   │  │                 │  │ • Best Value     │   │
│  │ • Strategy      │  │                 │  │ • Flex Cancel    │   │
│  └────────┬────────┘  └────────┬────────┘  └────────┬─────────┘   │
│           │                    │                     │             │
│           └────────────────────┼─────────────────────┘             │
│                                │                                    │
│                    ┌───────────┴───────────┐                       │
│                    │  Platform Abstraction │                       │
│                    │       Layer           │                       │
│                    └───────────┬───────────┘                       │
└────────────────────────────────┼───────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼───────┐         ┌───────▼───────┐
            │  MockAirbnb   │         │  MockBooking  │
            │   Adapter     │         │    Adapter    │
            │               │         │               │
            │ 10 listings   │         │ 10 listings   │
            └───────────────┘         └───────────────┘
```

## Component Details

### 1. NLP Parser (`nlp_parser.py`)

**Purpose**: Extract structured parameters from natural language queries.

**Capabilities**:
- **Destination Extraction**: Identifies 15+ Indian cities from query text
- **Guest Count**: Parses patterns like "for 4 guests", "2 people"
- **Budget Parsing**: Extracts "under Rs.5000", "budget of 3000"
- **Rating Preferences**: Detects "highly rated", "4+ star"
- **Cancellation Preference**: Identifies "flexible", "free cancellation"
- **Strategy Inference**: Determines selection strategy from keywords

### 2. MCP Server (`mcp_server.py`)

**Purpose**: Expose standardized tools for accommodation search and recommendation.

**Tools**:
| Tool | Description |
|------|-------------|
| `search_accommodations` | Query all platforms with filters |
| `get_listing_details` | Fetch specific listing info |
| `rank_options` | Rank listings by strategy |
| `select_best` | Pick best option with explanation |

### 3. Recommendation Engine (`recommendation.py`)

**Purpose**: Implement intelligent selection logic with explainability.

**Selection Strategies**:

| Strategy | Logic |
|----------|-------|
| `cheapest` | `min(listings, key=price)` |
| `highest_rating` | `max(listings, key=(rating, reviews))` |
| `best_value` | `max(listings, key=rating/(price/50))` |
| `flexible_cancellation` | Filter flexible → sort by rating |

### 4. Platform Adapters (`platforms/`)

**Base Interface** (`platforms/base.py`):
```python
class BasePlatformAdapter(ABC):
    @property
    def platform_name(self) -> str
    def search(self, query: SearchQuery) -> List[Listing]
    def get_listing_details(self, id: str) -> Optional[Listing]
    def normalize(self, raw: Dict) -> Listing
```

## Data Flow

```
User Query → Parse Query → Invoke MCP Tools → Query Platforms → 
Normalize Data → Apply Filters → Select by Strategy → Generate Explanation → Response
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, Pydantic |
| Frontend | HTML5, CSS3, JavaScript |
| Protocol | Model Context Protocol (MCP) |
| Data | JSON mock datasets |
