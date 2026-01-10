# 🏨 Unified Booking Agent

> **MCP-Powered Multi-Platform Accommodation Search**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A sophisticated AI-powered booking agent that searches across multiple accommodation platforms, normalizes data, and provides intelligent recommendations with full explainability.

**Backpackers' Bytes Hackathon 2026 - Problem Statement 3**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔌 **MCP Protocol** | Standards-compliant Model Context Protocol implementation |
| 🏠 **Multi-Platform** | Searches MockAirbnb + MockBooking simultaneously |
| 📊 **Data Normalization** | Unified schema across all platforms |
| 🧠 **Smart Selection** | 4 intelligent recommendation strategies |
| 💬 **Explainability** | Detailed reasoning for every recommendation |
| 🎨 **Modern UI** | Professional chatbot interface with glassmorphism design |
| 🎨 **Modern UI** | Professional chatbot interface with glassmorphism design |
| 📍 **30 Listings** | Covers 12 Indian destinations across 2 platforms |
| 🌍 **Global Mode** | **New!** Dynamic result generation for ANY city worldwide |
| 🇮🇳 **Pan-India** | **New!** Optimized NLP for 100+ Indian cities and towns |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)

### Installation

```bash
# 1. Navigate to project directory
cd booking-agent

# 2. Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
python run.py
```

### Access the Application
Open your browser and navigate to: **http://localhost:8000**

---

## 📂 Project Structure

```
booking-agent/
├── 📄 run.py                 # Application entry point
├── 📄 main.py                # FastAPI application
├── 📄 config.py              # Configuration settings
├── 📄 mcp_server.py          # MCP protocol implementation
├── 📄 nlp_parser.py          # Natural language processing
├── 📄 recommendation.py      # Selection logic & explainability
├── 📄 requirements.txt       # Python dependencies
│
├── 📁 platforms/             # Platform adapters
│   ├── base.py              # Abstract base adapter
│   ├── mock_airbnb.py       # MockAirbnb implementation
│   ├── mock_booking.py      # MockBooking implementation
│   └── booking_com.py       # Booking.com API (optional)
│
├── 📁 data/                  # Mock data
│   └── mock_listings.json   # 30 sample listings
│
├── 📁 static/                # Frontend assets
│   ├── index.html           # Main HTML page
│   ├── styles.css           # CSS styling
│   └── app.js               # JavaScript logic
│
├── 📁 docs/                  # Documentation
│   ├── ARCHITECTURE.md      # System design
│   ├── MCP_INTERFACE.md     # MCP tool documentation
│   └── DATA_SOURCES.md      # Data source info
│
├── 📄 .gitignore             # Git ignore rules
└── 📄 LICENSE                # MIT License
```

> **Note**: Real Booking.com API is included but uses RapidAPI free tier with limited quota. The 30 mock listings work reliably for demos.


---

## 🎯 Mandatory Requirements Compliance

| Requirement | Status | Implementation |
|------------|--------|----------------|
| MCP Server | ✅ | `mcp_server.py` - 4 tools exposed |
| Multi-Platform | ✅ | 2 mock + 1 real adapter |
| Data Normalization | ✅ | Unified `Listing` schema |
| Intelligent Selection | ✅ | 4 strategies in `recommendation.py` |
| Explainability | ✅ | Full reasoning in responses |

---

## 💡 Usage Examples

### Natural Language Queries

```
"Find me the cheapest hotel in Goa for 2 guests"
"I need a highly rated place in Mumbai under Rs.8000/night"
"Best value accommodation in Jaipur with free cancellation"
"Looking for a beach house with flexible cancellation in Kerala"
```

### Selection Strategies

| Strategy | Keyword Triggers |
|----------|------------------|
| Cheapest | "cheapest", "budget", "affordable" |
| Highest Rating | "best rated", "highly rated", "top" |
| Best Value | "value", "worth", "balance" |
| Flexible Cancel | "flexible", "free cancellation" |

---

## 🔧 API Reference

### Chat Endpoint
```http
POST /api/chat
Content-Type: application/json

{"query": "Find me a hotel in Mumbai"}
```

### MCP Tools
```http
GET /api/tools
```

### Direct Tool Invocation
```http
POST /api/tool/invoke
Content-Type: application/json

{
  "tool_name": "search_accommodations",
  "parameters": {"destination": "Goa"}
}
```

---

## 📊 Sample Response

```json
{
  "success": true,
  "recommendation": {
    "id": "air_004",
    "platform": "MockAirbnb",
    "property_name": "Backpackers Hostel Goa",
    "price_per_night": 1500,
    "rating": 4.2
  },
  "explanation": {
    "strategy_used": "cheapest",
    "why_selected": [
      "Lowest price among all options",
      "Good rating (4.0+)",
      "Flexible cancellation policy"
    ],
    "platforms_compared": ["MockAirbnb", "MockBooking"],
    "total_options_evaluated": 5
  }
}
```

---

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [MCP Interface Documentation](docs/MCP_INTERFACE.md)
- [Data Sources](docs/DATA_SOURCES.md)

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.12, FastAPI, Pydantic |
| Frontend | HTML5, CSS3, JavaScript |
| Protocol | Model Context Protocol (MCP) |
| Icons | Font Awesome 6.5 |

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Backpackers' Bytes Hackathon 2026**

---

<p align="center">
  <strong>Built with ❤️ for the Backpackers' Bytes Hackathon</strong>
</p>
