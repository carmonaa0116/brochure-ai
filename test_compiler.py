#!/usr/bin/env python3
"""
Test del compilador de contenidos
"""
from src.scraping import smart_scrape
from src.utils import filter_valid_links
from src.link_selector import select_relevant_links
from src.compiler import compile_contents, get_content_stats, save_contents_cache
import json


def test_compiler(url: str, company_name: str):
    print("\n" + "="*70)
    print(f"TEST COMPILADOR: {company_name}")
    print("="*70)
    
    # 1. Scrapear landing
    print("\n1️⃣ FASE 1: Scraping de la landing page")
    print("-" * 70)
    html, links, method = smart_scrape(url)
    
    if html is None:
        print("❌ Error en scraping")
        return
    
    print(f"✓ HTML descargado: {len(html):,} caracteres")
    print(f"✓ Método usado: {method}")
    
    # 2. Normalizar y seleccionar enlaces
    print("\n2️⃣ FASE 2: Selección de enlaces relevantes")
    print("-" * 70)
    valid_links = filter_valid_links(links, url)
    print(f"✓ Enlaces válidos: {len(valid_links)}")
    
    result = select_relevant_links(
        links=valid_links,
        base_url=url,
        company_name=company_name
    )
    
    selected = result.get('relevant_links', [])
    print(f"✓ Enlaces seleccionados: {len(selected)}")
    
    for i, link in enumerate(selected, 1):
        print(f"  {i}. [{link['type']}] {link['url']}")
    
    # 3. Compilar contenidos
    print("\n3️⃣ FASE 3: Compilación de contenidos")
    print("-" * 70)
    
    contents = compile_contents(
        selected_links=selected,
        landing_html=html,
        base_url=url,
        max_pages=8  # Limitar a 8 para el test
    )
    
    # 4. Estadísticas
    print("\n4️⃣ FASE 4: Análisis de contenidos")
    print("-" * 70)
    
    stats = get_content_stats(contents)
    
    print(f"\n📊 ESTADÍSTICAS GENERALES:")
    print(f"  - Total de secciones: {stats['total_sections']}")
    print(f"  - Total de caracteres: {stats['total_characters']:,}")
    print(f"  - Total de palabras: {stats['total_words']:,}")
    
    print(f"\n📋 DETALLE POR SECCIÓN:")
    for section, section_stats in stats['sections'].items():
        print(f"\n  [{section}]")
        print(f"    Caracteres: {section_stats['characters']:,}")
        print(f"    Palabras: {section_stats['words']:,}")
        print(f"    Líneas: {section_stats['lines']:,}")
    
    # 5. Muestra de contenido
    print(f"\n📄 MUESTRA DE CONTENIDO (primeras 300 chars de cada sección):")
    print("-" * 70)
    
    for section, text in contents.items():
        print(f"\n[{section.upper()}]")
        print(text[:300] + "..." if len(text) > 300 else text)
        print()
    
    # 6. Guardar en caché (opcional)
    print("\n5️⃣ FASE 5: Guardado en caché")
    print("-" * 70)
    save_contents_cache(contents, company_name)
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETADO")
    print("="*70)
    
    return contents, stats


if __name__ == "__main__":
    # Test con HuggingFace
    contents, stats = test_compiler(
        url="https://huggingface.co",
        company_name="HuggingFace"
    )
    
    # Guardar un resumen en archivo
    from pathlib import Path
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    
    summary_file = output_dir / 'compilation_summary.txt'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("RESUMEN DE COMPILACIÓN\n")
        f.write("="*70 + "\n\n")
        f.write(f"Total de secciones: {stats['total_sections']}\n")
        f.write(f"Total de caracteres: {stats['total_characters']:,}\n")
        f.write(f"Total de palabras: {stats['total_words']:,}\n\n")
        f.write("Secciones compiladas:\n")
        for section in stats['sections'].keys():
            f.write(f"  - {section}\n")
    
    print(f"\n📁 Resumen guardado en: {summary_file}")