#!/usr/bin/env python3
"""
Verifica qué modelos de Gemini están disponibles
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY no encontrada en .env")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

print("📋 Modelos disponibles:\n")

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✓ {model.name}")
        print(f"  Descripción: {model.display_name}")
        print()

print("\n💡 Usa uno de estos nombres en tu .env como GEMINI_MODEL")