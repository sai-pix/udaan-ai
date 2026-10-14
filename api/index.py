import os
import sys

# Ensure parent directory is on sys.path for relative imports on Vercel
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import app

# Vercel serverless function entrypoint
# The WSGI app is exported for Vercel's Python runtime
if __name__ == '__main__':
    app.run()
