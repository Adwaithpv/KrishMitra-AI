# Vercel's build environment will recognize the 'services' directory as a package.
# This imports the 'app' object from your main application file.
from services.api.app.main import app

# Vercel automatically detects and serves the variable named 'app'.
# You don't need to rename it to 'handler'.