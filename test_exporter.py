#!/usr/bin/env python3
"""
Test del exportador HTML/PDF
"""
from pathlib import Path
from src.exporter import (
    export_to_html,
    export_to_pdf_placeholder,
    get_available_themes
)
import webbrowser


def test_html_export(company_name: str, tone: str = 'professional'):
    """Test de exportación a HTML con todos los temas"""
    
    print("\n" + "="*70)
    print(f"TEST EXPORTADOR HTML: {company_name}")
    print("="*70)
    
    # 1. Buscar el archivo Markdown
    print("\n1️⃣ Buscando archivo Markdown...")
    
    output_dir = Path('outputs')
    safe_name = company_name.lower().replace(' ', '_')
    md_filename = f"{safe_name}_brochure_{tone}.md"
    md_file = output_dir / md_filename
    
    if not md_file.exists():
        print(f"❌ Archivo no encontrado: {md_file}")
        print("💡 Primero ejecuta: python test_brochure_generator.py")
        return
    
    print(f"✅ Archivo encontrado: {md_file}")
    print(f"   Tamaño: {md_file.stat().st_size:,} bytes")
    
    # 2. Mostrar temas disponibles
    print("\n2️⃣ Temas visuales disponibles:")
    themes = get_available_themes()
    for key, info in themes.items():
        print(f"   - {key}: {info['name']}")
        print(f"     Colores: bg={info['bg_color']}, accent={info['accent_color']}")
    
    # 3. Exportar con cada tema
    print("\n3️⃣ Exportando a HTML con todos los temas...")
    print("-" * 70)
    
    html_files = []
    
    for theme_key in themes.keys():
        print(f"\n🎨 Exportando con tema: {themes[theme_key]['name']}")
        
        html_file = export_to_html(
            markdown_file=md_file,
            company_name=company_name,
            tone=tone,
            theme=theme_key
        )
        
        html_files.append(html_file)
        print(f"✅ Generado: {html_file.name}")
        print(f"   Tamaño: {html_file.stat().st_size:,} bytes")
    
    # 4. Resumen
    print("\n4️⃣ Resumen de archivos generados:")
    print("-" * 70)
    
    for i, html_file in enumerate(html_files, 1):
        print(f"{i}. {html_file}")
    
    # 5. Abrir el primero en navegador
    print("\n5️⃣ Abriendo primer archivo en navegador...")
    first_file = html_files[0]
    
    try:
        webbrowser.open(first_file.absolute().as_uri())
        print(f"✅ Abierto: {first_file.name}")
    except Exception as e:
        print(f"⚠️  No se pudo abrir automáticamente: {e}")
        print(f"💡 Abre manualmente: {first_file.absolute()}")
    
    # 6. Placeholder para PDF
    print("\n6️⃣ Intentando exportar a PDF...")
    export_to_pdf_placeholder(first_file, company_name)
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETADO")
    print("="*70)
    print("\n📂 Archivos HTML generados en: outputs/")
    print("🌐 Abre cualquiera en tu navegador para visualizar")
    
    return html_files


def compare_themes_side_by_side(company_name: str, tone: str = 'professional'):
    """Genera reporte comparativo de temas"""
    
    print("\n" + "="*70)
    print("COMPARACIÓN DE TEMAS")
    print("="*70)
    
    output_dir = Path('outputs')
    safe_name = company_name.lower().replace(' ', '_')
    
    themes = get_available_themes()
    
    print("\n📋 Archivos generados por tema:\n")
    
    for theme_key, theme_info in themes.items():
        filename = f"{safe_name}_brochure_{tone}_{theme_key}.html"
        filepath = output_dir / filename
        
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"✅ {theme_info['name']:12} → {filename}")
            print(f"   Tamaño: {size:,} bytes")
            print(f"   Colores: {theme_info['bg_color']} / {theme_info['accent_color']}")
        else:
            print(f"❌ {theme_info['name']:12} → NO GENERADO")
        
        print()
    
    print("="*70)


if __name__ == "__main__":
    company = "HuggingFace"
    tone = "professional"
    
    # Test principal
    html_files = test_html_export(company, tone)
    
    # Comparación
    if html_files:
        print("\n" + "="*70)
        input("Presiona ENTER para ver comparación de temas...")
        compare_themes_side_by_side(company, tone)
    
    print("\n💡 Consejos:")
    print("   - Abre los archivos .html en diferentes pestañas para compararlos")
    print("   - Usa Ctrl+P en el navegador para guardar como PDF")
    print("   - El tema 'corporate' es ideal para presentaciones formales")
    print("   - El tema 'dark' es bueno para pantallas/proyectores")