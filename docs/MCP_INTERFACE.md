# MCP Interface Documentation

## Overview

This document describes the Model Context Protocol (MCP) interface for the Unified Booking Agent. The MCP server exposes tools that can be invoked by language models to search, compare, and recommend accommodations across multiple booking platforms.

## Protocol Compliance

The MCP server follows the standard MCP tool calling convention:
- Tools are defined with a `name`, `description`, and `parameters` schema
- Tool invocation returns a standardized result with `tool_name`, `success`, `result`, and optional `error`
- Parameters follow JSON Schema format for validation

## Available Tools

### 1. search_accommodations

**Description**: Search for accommodations across all connected booking platforms.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `destination` | string | Yes | City or location name to search |
| `guests` | integer | No | Number of guests (default: 2) |
| `max_price` | number | No | Maximum price per night in INR |
| `min_rating` | number | No | Minimum rating (1.0 - 5.0) |
| `cancellation_policy` | string | No | Preferred policy: "flexible", "moderate", "strict" |

### 2. get_listing_details

**Description**: Get detailed information about a specific listing.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `listing_id` | string | Yes | Unique listing ID (e.g., "air_001") |
| `platform` | string | No | Platform name to search |

### 3. rank_options

**Description**: Rank all available listings in a destination by a specified strategy.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `destination` | string | Yes | City or location to search |
| `strategy` | string | Yes | One of: "cheapest", "highest_rating", "best_value", "flexible_cancellation" |

### 4. select_best

**Description**: Select the best accommodation based on user preferences with full explanation.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `destination` | string | Yes | City or location to search |
| `strategy` | string | No | Selection strategy (default: "best_value") |
| `preferences` | object | No | User preferences object |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Natural language query processing |
| `/api/tool/invoke` | POST | Direct MCP tool invocation |
| `/api/tools` | GET | List all available MCP tools |
| `/health` | GET | Health check endpoint |

## Error Handling

Tool invocations return errors in a standardized format:

```json
{
  "tool_name": "search_accommodations",
  "success": false,
  "result": null,
  "error": "Destination is required"
}
```
