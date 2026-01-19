#!/usr/bin/env python3
"""
Test de integración: scraping + normalización
"""
from src.scraping import smart_scrape
from src.utils import filter_valid_links, clean_text, get_domain_name


def test_full_pipeline(url: str):
    print("\n" + "="*70)
    print(f"TEST INTEGRACIÓN: {url}")
    print("="*70)
    
    # 1. Scrapear
    print("\n1️⃣ Scraping...")
    html, links, method = smart_scrape(url)
    
    if html is None:
        print("❌ Error en scraping")
        return
    
    print(f"   ✓ Método: {method}")
    print(f"   ✓ HTML: {len(html):,} chars")
    print(f"   ✓ Enlaces crudos: {len(links)}")
    
    # 2. Normalizar y filtrar
    print("\n2️⃣ Normalizando enlaces...")
    valid_links = filter_valid_links(links, url)
    print(f"   ✓ Enlaces válidos: {len(valid_links)}")
    
    # 3. Limpiar texto
    print("\n3️⃣ Limpiando texto...")
    clean = clean_text(html)
    print(f"   ✓ Texto limpio: {len(clean):,} chars")
    
    # 4. Mostrar muestra
    print("\n📎 Primeros 10 enlaces normalizados:")
    for i, link in enumerate(valid_links[:10], 1):
        print(f"   {i:2}. {link}")
    
    print("\n📄 Primeras 500 chars del texto limpio:")
    print(clean[:500])
    print("...")
    
    # 5. Nombre del dominio
    domain = get_domain_name(url)
    print(f"\n🏢 Nombre del dominio: {domain}")
    
    return html, valid_links, clean


if __name__ == "__main__":
    # Test con HuggingFace
    test_full_pipeline("https://huggingface.co")
    
    print("\n" + "="*70)
    print("✅ TEST DE INTEGRACIÓN COMPLETADO")
    print("="*70)