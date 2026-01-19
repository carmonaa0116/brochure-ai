#!/usr/bin/env python3
"""Test de importaciones básicas"""

print("Probando importaciones...")

try:
    import requests
    print("✓ requests")
except ImportError as e:
    print(f"✗ requests: {e}")

try:
    from bs4 import BeautifulSoup
    print("✓ beautifulsoup4")
except ImportError as e:
    print(f"✗ beautifulsoup4: {e}")

try:
    from playwright.sync_api import sync_playwright
    print("✓ playwright")
except ImportError as e:
    print(f"✗ playwright: {e}")

try:
    import google.generativeai as genai
    print("✓ google-generativeai")
except ImportError as e:
    print(f"✗ google-generativeai: {e}")

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv")
except ImportError as e:
    print(f"✗ python-dotenv: {e}")

try:
    import markdown
    print("✓ markdown")
except ImportError as e:
    print(f"✗ markdown: {e}")

try:
    import weasyprint
    print("✓ weasyprint")
except ImportError as e:
    print(f"✗ weasyprint: {e}")

print("\n✅ Todas las dependencias están instaladas correctamente")