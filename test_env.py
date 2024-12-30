import os
from pathlib import Path

print("Current working directory:", os.getcwd())
print("Looking for .env in:", Path(__file__).parent)
print("STRIPE_SECRET_KEY:", os.getenv('STRIPE_SECRET_KEY')) 