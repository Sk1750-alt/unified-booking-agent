# Data Sources Documentation

## Overview

This project uses **simulated/mock datasets** designed to resemble real booking platforms.

### Why Mock Data?

1. **Reliability**: No API rate limits or downtime
2. **Reproducibility**: Consistent results for testing and demo
3. **Legal Compliance**: No scraping or API terms violations
4. **Hackathon Scope**: Focus on agent logic, not API integration

## Mock Platforms

### 1. MockAirbnb (15 listings)

Simulates Airbnb-style vacation rentals with diverse property types.

| ID | Property | Location | Price (Rs.) | Rating |
|----|----------|----------|-------------|--------|
| air_001 | Cozy Beach Villa | Goa | 6,200 | 4.8 |
| air_002 | Modern Mumbai Apartment | Mumbai | 7,900 | 4.5 |
| air_003 | Heritage Haveli Stay | Jaipur | 9,900 | 4.9 |
| air_004 | Backpackers Hostel Goa | Goa | 1,500 | 4.2 |
| air_005 | Luxury Penthouse Delhi | Delhi | 20,800 | 4.95 |
| air_006 | Himalayan Mountain Retreat | Manali | 7,000 | 4.7 |
| air_007 | French Colony Studio | Pondicherry | 4,500 | 4.6 |
| air_008 | Houseboat Experience | Kerala | 12,500 | 4.85 |
| air_009 | Budget Room Kolkata | Kolkata | 2,500 | 4.0 |
| air_010 | Beachfront Bungalow | Goa | 10,800 | 4.75 |
| air_011 | Lake View Palace | Udaipur | 11,500 | 4.88 |
| air_012 | Shimla Pine Cottage | Shimla | 5,500 | 4.55 |
| air_013 | Tech Park Serviced Apartment | Bangalore | 6,800 | 4.35 |
| air_014 | Marina Beach Studio | Chennai | 3,800 | 4.25 |
| air_015 | Hitech City Loft | Hyderabad | 5,200 | 4.45 |

### 2. MockBooking (15 listings)

Simulates Booking.com-style hotels and resorts.

| ID | Property | Location | Price (Rs.) | Rating | Stars |
|----|----------|----------|-------------|--------|-------|
| bk_001 | Grand Hyatt Goa | Goa | 15,000 | 4.7 | 5 |
| bk_002 | Taj Palace Mumbai | Mumbai | 18,500 | 4.85 | 5 |
| bk_003 | Budget Inn Goa | Goa | 2,900 | 3.8 | 2 |
| bk_004 | ITC Maurya Delhi | Delhi | 16,200 | 4.6 | 5 |
| bk_005 | Zostel Jaipur | Jaipur | 1,200 | 4.3 | 2 |
| bk_006 | Le Pondy Resort | Pondicherry | 7,100 | 4.4 | 4 |
| bk_007 | Treebo Trend Mumbai | Mumbai | 3,700 | 4.1 | 3 |
| bk_008 | The Oberoi Kerala | Kerala | 23,300 | 4.9 | 5 |
| bk_009 | OYO Rooms Kolkata | Kolkata | 2,300 | 3.9 | 2 |
| bk_010 | Snow Peak Lodge | Manali | 7,900 | 4.5 | 4 |
| bk_011 | The Leela Palace Udaipur | Udaipur | 28,000 | 4.92 | 5 |
| bk_012 | Clarkes Shimla | Shimla | 8,500 | 4.3 | 4 |
| bk_013 | JW Marriott Bangalore | Bangalore | 14,500 | 4.65 | 5 |
| bk_014 | Radisson Blu Chennai | Chennai | 9,800 | 4.4 | 5 |
| bk_015 | Novotel Hyderabad | Hyderabad | 7,200 | 4.35 | 4 |

## Destinations Covered (12 Cities)

| Destination | Properties | Price Range (Rs.) |
|-------------|------------|-------------------|
| Goa | 5 | 1,500 - 15,000 |
| Mumbai | 3 | 3,700 - 18,500 |
| Delhi | 2 | 16,200 - 20,800 |
| Jaipur | 2 | 1,200 - 9,900 |
| Kerala | 2 | 12,500 - 23,300 |
| Manali | 2 | 7,000 - 7,900 |
| Pondicherry | 2 | 4,500 - 7,100 |
| Kolkata | 2 | 2,300 - 2,500 |
| Udaipur | 2 | 11,500 - 28,000 |
| Shimla | 2 | 5,500 - 8,500 |
| Bangalore | 2 | 6,800 - 14,500 |
| Chennai | 2 | 3,800 - 9,800 |
| Hyderabad | 2 | 5,200 - 7,200 |

## Property Types

| Type | Count | Examples |
|------|-------|----------|
| Hotel | 10 | Taj Palace, JW Marriott, Radisson Blu |
| Villa/Bungalow | 3 | Cozy Beach Villa, Beachfront Bungalow |
| Apartment/Loft | 4 | Modern Mumbai Apartment, Hitech City Loft |
| Hostel | 2 | Backpackers Hostel Goa, Zostel Jaipur |
| Resort | 3 | Le Pondy Resort, The Oberoi Kerala |
| Heritage | 3 | Heritage Haveli Stay, Lake View Palace |
| Other | 5 | Houseboat, Cottage, Studio, Penthouse |

## Extending with Real APIs

To add a real API, create a new adapter in `platforms/`:

```python
from platforms.base import BasePlatformAdapter, Listing

class RealBookingAdapter(BasePlatformAdapter):
    @property
    def platform_name(self) -> str:
        return "Booking.com"
    
    def search(self, query: SearchQuery) -> List[Listing]:
        # Call real API and normalize response
        pass
```
