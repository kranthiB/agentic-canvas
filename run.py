"""
Agentic Canvas - Main Application Entry Point
Run this file to start the Flask application with SocketIO support
"""
import os
from app import create_app, socketio

# Get configuration from environment
config_name = os.getenv('FLASK_ENV', 'development')

# Create Flask application
app = create_app(config_name)

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5002))
    
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║     🎯 AGENTIC CANVAS - Starting Server     ║
    ╠══════════════════════════════════════════════╣
    ║  Environment: {config_name.ljust(30)} ║
    ║  Port: {str(port).ljust(37)} ║
    ║  URL: http://localhost:{port}/           ║
    ╚══════════════════════════════════════════════╝
    """)
    
    # Run with SocketIO support for real-time features
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=(config_name == 'development'),
        use_reloader=True,
        log_output=True
    )