#!/usr/bin/env python3
"""
Test del generador de folletos
"""
from src.compiler import load_contents_cache
from src.brochure_generator import (
    generate_brochure, 
    save_brochure,
    get_available_tones
)
import os


def test_brochure_generation(company_name: str, tone: str = 'professional'):
    print("\n" + "="*70)
    print(f"TEST GENERADOR DE FOLLETOS: {company_name}")
    print(f"Tono: {tone}")
    print("="*70)
    
    # 1. Cargar contenidos compilados
    print("\n1️⃣ Cargando contenidos compilados...")
    contents = load_contents_cache(company_name)
    
    if not contents:
        print("❌ No se encontraron contenidos en caché")
        print("💡 Primero ejecuta: python test_compiler.py")
        return
    
    print(f"✅ Contenidos cargados: {len(contents)} secciones")
    print(f"   Secciones: {', '.join(contents.keys())}")
    
    # 2. Generar folleto
    print("\n2️⃣ Generando folleto...")
    
    brochure = generate_brochure(
        contents=contents,
        company_name=company_name,
        base_url="https://huggingface.co",  # Cambiar según empresa
        tone=tone
    )
    
    # 3. Estadísticas
    print("\n3️⃣ Análisis del folleto generado:")
    print("-" * 70)
    
    num_chars = len(brochure)
    num_words = len(brochure.split())
    num_lines = len(brochure.split('\n'))
    num_headings = brochure.count('#')
    
    print(f"📊 Estadísticas:")
    print(f"  - Caracteres: {num_chars:,}")
    print(f"  - Palabras: {num_words:,}")
    print(f"  - Líneas: {num_lines:,}")
    print(f"  - Encabezados (# encontrados): {num_headings}")
    
    # 4. Preview
    print("\n4️⃣ Preview del folleto (primeros 800 caracteres):")
    print("-" * 70)
    print(brochure[:800])
    print("...")
    print("-" * 70)
    
    # 5. Guardar
    print("\n5️⃣ Guardando folleto...")
    filepath = save_brochure(brochure, company_name, tone)
    
    print(f"✅ Folleto guardado en: {filepath}")
    
    # 6. Mostrar últimas líneas
    print("\n6️⃣ Últimas líneas del folleto:")
    print("-" * 70)
    lines = brochure.split('\n')
    print('\n'.join(lines[-10:]))
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETADO")
    print("="*70)
    
    return brochure, filepath


def test_all_tones(company_name: str):
    """Test con todos los tonos disponibles"""
    print("\n" + "="*70)
    print("TEST: GENERACIÓN CON TODOS LOS TONOS")
    print("="*70)
    
    tones = get_available_tones()
    
    for tone_key, tone_info in tones.items():
        print(f"\n🎨 Probando tono: {tone_info['name']}")
        print(f"   Descripción: {tone_info['description']}")
        input("\nPresiona ENTER para generar con este tono...")
        
        brochure, filepath = test_brochure_generation(company_name, tone_key)
        
        print(f"\n📄 Archivo generado: {filepath}")
    
    print("\n" + "="*70)
    print("✅ TODOS LOS TONOS GENERADOS")
    print("="*70)


if __name__ == "__main__":
    company = "HuggingFace"
    
    # Mostrar tonos disponibles
    print("\n🎨 Tonos disponibles:")
    for key, info in get_available_tones().items():
        print(f"  - {key}: {info['name']} - {info['description']}")
    
    print("\n" + "="*70)
    input("Presiona ENTER para comenzar el test...")
    
    # Test con tono profesional
    brochure, filepath = test_brochure_generation(company, tone='professional')
    
    # Preguntar si probar todos los tonos
    print("\n¿Quieres generar folletos con TODOS los tonos? (y/n): ", end="")
    response = input().strip().lower()
    
    if response == 'y':
        test_all_tones(company)
    
    print(f"\n✅ Puedes ver el folleto en: {filepath}")
    print(f"📖 Abre el archivo con cualquier visor de Markdown")