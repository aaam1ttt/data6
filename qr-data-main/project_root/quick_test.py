print("Testing imports...")
import sys
sys.path.append('.')

from app.core.codes import generate_aztec
print("Aztec import success")

img = generate_aztec("TEST", 300)
print(f"Generated: {img.size}")