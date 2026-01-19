#!/usr/bin/env python3
"""
Test del sistema de traducción
"""
from pathlib import Path
from src.translator import (
    translate_brochure,
    save_translated_brochure,
    get_available_languages,
    detect_language
)


def test_translation(company_name: str, target_lang: str, tone: str = 'professional'):
    """Test de traducción de folleto"""
    
    print("\n" + "="*70)
    print(f"TEST TRADUCTOR: {company_name}")
    print(f"Idioma destino: {target_lang}")
    print("="*70)
    
    # 1. Buscar archivo Markdown original
    print("\n1️⃣ Buscando folleto original...")
    
    output_dir = Path('outputs')
    safe_name = company_name.lower().replace(' ', '_')
    md_filename = f"{safe_name}_brochure_{tone}.md"
    md_file = output_dir / md_filename
    
    if not md_file.exists():
        print(f"❌ Archivo no encontrado: {md_file}")
        print("💡 Primero ejecuta: python test_brochure_generator.py")
        return
    
    print(f"✅ Archivo encontrado: {md_file.name}")
    
    # 2. Leer contenido
    print("\n2️⃣ Leyendo contenido...")
    brochure = md_file.read_text(encoding='utf-8')
    
    print(f"✅ Contenido leído: {len(brochure)} caracteres")
    print(f"   Palabras: {len(brochure.split())}")
    print(f"   Encabezados: {brochure.count('#')}")
    
    # 3. Detectar idioma original
    print("\n3️⃣ Detectando idioma original...")
    source_lang = detect_language(brochure)
    
    # 4. Traducir
    print(f"\n4️⃣ Traduciendo...")
    print(f"   {get_available_languages()[source_lang]['name']} → {get_available_languages()[target_lang]['name']}")
    
    translated = translate_brochure(
        brochure=brochure,
        target_lang=target_lang,
        source_lang=source_lang,
        tone=tone
    )
    
    # 5. Análisis de la traducción
    print("\n5️⃣ Análisis de la traducción:")
    print("-" * 70)
    
    print(f"📊 Estadísticas:")
    print(f"  - Caracteres originales: {len(brochure):,}")
    print(f"  - Caracteres traducidos: {len(translated):,}")
    print(f"  - Ratio: {len(translated)/len(brochure):.2f}x")
    print(f"  - Palabras originales: {len(brochure.split()):,}")
    print(f"  - Palabras traducidas: {len(translated.split()):,}")
    print(f"  - Encabezados originales: {brochure.count('#')}")
    print(f"  - Encabezados traducidos: {translated.count('#')}")
    
    # 6. Preview
    print("\n6️⃣ Preview de la traducción (primeros 500 caracteres):")
    print("-" * 70)
    print(translated[:500])
    print("...")
    print("-" * 70)
    
    # 7. Guardar
    print("\n7️⃣ Guardando traducción...")
    filepath = save_translated_brochure(translated, company_name, target_lang, tone)
    
    print(f"✅ Traducción guardada: {filepath.name}")
    
    # 8. Comparación lado a lado
    print("\n8️⃣ Comparación (primeras 3 líneas):")
    print("-" * 70)
    
    orig_lines = brochure.split('\n')[:3]
    trans_lines = translated.split('\n')[:3]
    
    for i, (orig, trans) in enumerate(zip(orig_lines, trans_lines), 1):
        print(f"\nLínea {i}:")
        print(f"  Original: {orig[:80]}")
        print(f"  Traducido: {trans[:80]}")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETADO")
    print("="*70)
    
    return translated, filepath


def test_multiple_languages(company_name: str, tone: str = 'professional'):
    """Test traduciendo a múltiples idiomas"""
    
    print("\n" + "="*70)
    print("TEST: TRADUCCIÓN A MÚLTIPLES IDIOMAS")
    print("="*70)
    
    languages = get_available_languages()
    
    print("\n🌍 Idiomas disponibles:")
    for code, info in languages.items():
        print(f"  - {code}: {info['name']} ({info['native']})")
    
    # Excluir español (idioma original)
    target_langs = [code for code in languages.keys() if code != 'es']
    
    print(f"\n📝 Se traducirá a {len(target_langs)} idiomas...\n")
    
    results = {}
    
    for lang in target_langs:
        print(f"\n{'='*70}")
        print(f"Traduciendo a: {languages[lang]['name']}")
        print('='*70)
        
        try:
            translated, filepath = test_translation(company_name, lang, tone)
            results[lang] = filepath
            print(f"✅ {languages[lang]['name']}: OK")
        except Exception as e:
            print(f"❌ {languages[lang]['name']}: ERROR - {e}")
            results[lang] = None
        
        # Pausa entre traducciones para no saturar la API
        if lang != target_langs[-1]:
            import time
            print("\n⏳ Esperando 2 segundos...")
            time.sleep(2)
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE TRADUCCIONES")
    print("="*70)
    
    successful = sum(1 for v in results.values() if v is not None)
    
    print(f"\n✅ Exitosas: {successful}/{len(target_langs)}")
    print(f"\n📁 Archivos generados:\n")
    
    for lang, filepath in results.items():
        if filepath:
            print(f"  ✅ {languages[lang]['name']:12} → {filepath.name}")
        else:
            print(f"  ❌ {languages[lang]['name']:12} → FALLÓ")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    company = "HuggingFace"
    
    print("\n🌍 Sistema de Traducción de Folletos")
    print("\nOpciones:")
    print("  1. Traducir a un idioma específico")
    print("  2. Traducir a todos los idiomas")
    
    choice = input("\nElige una opción (1 o 2): ").strip()
    
    if choice == "1":
        print("\nIdiomas disponibles:")
        for code, info in get_available_languages().items():
            if code != 'es':  # Excluir español
                print(f"  {code}: {info['name']}")
        
        lang = input("\nCódigo de idioma (ej: en, fr, de): ").strip().lower()
        
        if lang in get_available_languages():
            test_translation(company, lang)
        else:
            print(f"❌ Idioma '{lang}' no válido")
    
    elif choice == "2":
        confirm = input("\n⚠️  Esto generará múltiples traducciones. ¿Continuar? (y/n): ")
        if confirm.lower() == 'y':
            test_multiple_languages(company)
    
    else:
        print("❌ Opción no válida")