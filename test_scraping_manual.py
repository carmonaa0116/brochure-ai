#!/usr/bin/env python3
"""
Test manual del scraping estático
"""
from src.scraping import scrape_and_extract
import sys

def test_scraping(url: str):
    print(f"\n{'='*60}")
    print(f"Probando scraping de: {url}")
    print('='*60)
    
    html, links = scrape_and_extract(url)
    
    if html is None:
        print("❌ ERROR: No se pudo descargar el HTML")
        sys.exit(1)
    
    print(f"\n✅ HTML descargado: {len(html)} caracteres")
    print(f"✅ Enlaces encontrados: {len(links)}")
    
    # Mostrar primeros 10 enlaces
    print("\n📎 Primeros 10 enlaces:")
    for i, link in enumerate(links[:10], 1):
        print(f"  {i}. {link}")
    
    # Mostrar snippet del HTML (primeros 500 chars)
    print(f"\n📄 Snippet del HTML:")
    print(html[:500] + "...")
    
    return html, links


if __name__ == "__main__":
    # Probar con un sitio simple y conocido
    test_url = "https://example.com"
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    html, links = test_scraping(test_url)
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETADO")
    print("="*60)