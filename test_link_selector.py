#!/usr/bin/env python3
"""
Test del selector de enlaces (mock y real)
"""
from src.scraping import smart_scrape
from src.utils import filter_valid_links
from src.link_selector import select_relevant_links
import json


def test_link_selector(url: str, company_name: str):
    print("\n" + "="*70)
    print(f"TEST SELECTOR DE ENLACES: {company_name}")
    print("="*70)
    
    # 1. Scrapear y normalizar
    print("\n1️⃣ Scraping y normalización...")
    html, links, method = smart_scrape(url)
    
    if html is None:
        print("❌ Error en scraping")
        return
    
    valid_links = filter_valid_links(links, url)
    print(f"   ✓ Enlaces válidos: {len(valid_links)}")
    
    # 2. Seleccionar enlaces relevantes
    print("\n2️⃣ Seleccionando enlaces con LLM...")
    result = select_relevant_links(
        links=valid_links,
        base_url=url,
        company_name=company_name
    )
    
    # 3. Mostrar resultados
    print("\n📊 RESULTADO:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print(f"\n✅ Enlaces seleccionados: {len(result.get('relevant_links', []))}")
    
    # 4. Detalle de enlaces
    print("\n📎 Enlaces relevantes encontrados:")
    for i, link_info in enumerate(result.get('relevant_links', []), 1):
        print(f"\n{i}. Tipo: {link_info['type']}")
        print(f"   URL: {link_info['url']}")
        print(f"   Razón: {link_info['reason']}")
    
    return result


if __name__ == "__main__":
    # Test en modo MOCK
    print("\n🎭 EJECUTANDO EN MODO MOCK")
    print("(Sin consumir tokens de Gemini)")
    
    test_link_selector(
        url="https://huggingface.co",
        company_name="HuggingFace"
    )
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETADO")
    print("="*70)