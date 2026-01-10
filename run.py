#!/usr/bin/env python3
"""
Unified Booking Agent - Application Entry Point

This script serves as the main entry point for the Unified Booking Agent.
It initializes and starts the FastAPI application server.

Usage:
    python run.py [--host HOST] [--port PORT] [--reload]
    
Example:
    python run.py --port 8000 --reload
"""

import argparse
import uvicorn
from config import HOST, PORT, DEBUG, APP_NAME, APP_VERSION


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} v{APP_VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Start with default settings
  python run.py --port 3000        # Use custom port
  python run.py --reload           # Enable auto-reload for development
  python run.py --host 127.0.0.1   # Bind to localhost only
        """
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default=HOST,
        help=f"Host to bind the server (default: {HOST})"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=PORT,
        help=f"Port to run the server on (default: {PORT})"
    )
    
    parser.add_argument(
        "--reload", "-r",
        action="store_true",
        default=DEBUG,
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"{APP_NAME} v{APP_VERSION}"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    print(f"""
================================================================
           UNIFIED BOOKING AGENT v{APP_VERSION}
        MCP-Powered Multi-Platform Search
        
        Backpackers' Bytes Hackathon 2026
================================================================
    """)
    
    print(f"[*] Starting server at http://{args.host}:{args.port}")
    print(f"[*] Auto-reload: {'Enabled' if args.reload else 'Disabled'}")
    print(f"[*] Press Ctrl+C to stop the server\n")
    
    try:
        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n[*] Server stopped by user")
    except Exception as e:
        print(f"\n[!] Error starting server: {e}")
        raise


if __name__ == "__main__":
    main()
