import sys
import os

# Add the services/api directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

# Import the FastAPI app from the main module
from services.api.app.main import app

# Export the app for Vercel
handler = app
