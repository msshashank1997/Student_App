import os
import sys
from app import app

def run_server(host='0.0.0.0', port=5001):
    """Run the Flask server with customizable host and port."""
    try:
        # Check if port is available
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"Warning: Port {port} is already in use. Try a different port.")
            sock.close()
            return False
        sock.close()
        
        # Try running with Waitress (more stable on Windows)
        try:
            from waitress import serve
            print(f"Starting Waitress server on {host}:{port}...")
            serve(app, host=host, port=port)
            return True
        except ImportError:
            # Waitress not installed, use Flask's development server with threading disabled
            print("Waitress not found. Using Flask's built-in server.")
            print(f"To avoid socket errors, install Waitress: pip install waitress")
            print(f"Starting Flask server on {host}:{port}...")
            app.run(host=host, port=port, debug=True, use_reloader=False, threaded=False)
            return True
    
    except OSError as e:
        print(f"Socket error occurred: {e}")
        print("Try these solutions:")
        print("1. Kill all Python processes and try again")
        print("2. Restart your computer")
        print("3. Try a different port: python run_server.py 5002")
        print("4. Install and use Waitress: pip install waitress")
        return False
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    # Get port from command line arguments if provided
    port = 5001  # Default port
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default port 5001.")
    
    run_server(port=port)
    print("Server shutdown.")
