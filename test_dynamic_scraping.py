#!/usr/bin/env python3
"""
Test del scraping inteligente (estático + dinámico)
"""
import html
from src.scraping import smart_scrape
import sys


def test_smart_scrape(url: str, force_dynamic: bool = False):
    print(f"\n{'='*70}")
    print(f"Testing smart_scrape: {url}")
    print(f"Force dynamic: {force_dynamic}")
    print('='*70)
    
    html, links, method = smart_scrape(url, force_dynamic=force_dynamic)
    
    if html is None:
        print("❌ ERROR: No se pudo obtener HTML")
        return
    
    print(f"\n✅ Método usado: {method.upper()}")
    print(f"✅ HTML obtenido: {len(html):,} caracteres")
    print(f"✅ Enlaces encontrados: {len(links)}")
    
    print(f"\n📎 Primeros 15 enlaces:")
    for i, link in enumerate(links[:15], 1):
        # Truncar enlaces muy largos
        display_link = link if len(link) < 80 else link[:77] + "..."
        print(f"  {i:2}. {display_link}")
    
    # Análisis del HTML
    print(f"\n📊 Análisis:")

    root_div = '<div id="root">'
    app_div = '<div id="app">'

    print(f"  - Contiene '{root_div}': {'Sí' if root_div in html else 'No'}")
    print(f"  - Contiene '{app_div}': {'Sí' if app_div in html else 'No'}")
    print(f"  - Scripts encontrados: {html.count('<script')}")
    return html, links, method


if __name__ == "__main__":
    print("\n🧪 TEST 1: Sitio estático simple (example.com)")
    test_smart_scrape("https://example.com")
    
    print("\n" + "="*70)
    input("Presiona ENTER para continuar con el siguiente test...")
    
    print("\n🧪 TEST 2: Sitio moderno (huggingface.co)")
    test_smart_scrape("https://huggingface.co")
    
    print("\n" + "="*70)
    input("Presiona ENTER para continuar con el siguiente test...")
    
    print("\n🧪 TEST 3: Forzar modo dinámico en example.com")
    test_smart_scrape("https://example.com", force_dynamic=True)
    
    print("\n" + "="*70)
    print("✅ TODOS LOS TESTS COMPLETADOS")
    print("="*70)