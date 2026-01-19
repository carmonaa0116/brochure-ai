#!/usr/bin/env python3
"""
BrochureAI - Generador automático de folletos corporativos

Uso:
    python brochure.py full https://empresa.com --company "Mi Empresa"
    python brochure.py scrape https://empresa.com
    python brochure.py generate --company "Mi Empresa"
    python brochure.py export --company "Mi Empresa" --theme dark
"""

from tqdm import tqdm
import argparse
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import os

# Importar módulos del proyecto
from src.scraping import smart_scrape
from src.utils import filter_valid_links, get_domain_name
from src.link_selector import select_relevant_links
from src.compiler import compile_contents, save_contents_cache, get_content_stats
from src.brochure_generator import generate_brochure, save_brochure, get_available_tones
from src.exporter import export_to_html, get_available_themes

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
def setup_logging(verbose: bool = False):
    """Configura el nivel de logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

# Banner
def print_banner():
    """Muestra el banner de bienvenida"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              🚀 FOLLETO AI v0.1                         ║
║                                                           ║
║      Generador automático de folletos corporativos       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)

# Comando: scrape
def cmd_scrape(args):
    """Comando para scrapear una web y guardar contenidos"""
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*70)
    print("📡 FASE 1: SCRAPING Y COMPILACIÓN DE CONTENIDOS")
    print("="*70 + "\n")
    
    url = args.url
    company_name = args.company or get_domain_name(url).capitalize()
    
    logger.info(f"URL objetivo: {url}")
    logger.info(f"Empresa: {company_name}")
    
    # 1. Scrapear landing
    print("\n[1/4] Scrapeando página principal...")
    html, links, method = smart_scrape(url)
    
    if html is None:
        logger.error("❌ No se pudo scrapear la URL")
        return 1
    
    print(f"✅ Scraping completado (método: {method})")
    print(f"   📄 HTML: {len(html):,} caracteres")
    print(f"   🔗 Enlaces encontrados: {len(links)}")
    
    # 2. Filtrar enlaces
    print("\n[2/4] Filtrando enlaces válidos...")
    valid_links = filter_valid_links(links, url)
    print(f"✅ Enlaces válidos: {len(valid_links)}")
    
    # 3. Seleccionar enlaces relevantes
    print("\n[3/4] Seleccionando enlaces relevantes con IA...")
    result = select_relevant_links(
        links=valid_links,
        base_url=url,
        company_name=company_name
    )
    
    selected = result.get('relevant_links', [])
    print(f"✅ Enlaces seleccionados: {len(selected)}")
    
    for i, link in enumerate(selected[:5], 1):
        print(f"   {i}. [{link['type']}] {link['url']}")
    
    if len(selected) > 5:
        print(f"   ... y {len(selected) - 5} más")
    
    # 4. Compilar contenidos
    print("\n[4/4] Descargando y compilando contenidos...")
    contents = compile_contents(
        selected_links=selected,
        landing_html=html,
        base_url=url,
        max_pages=args.max_pages
    )
    
    # Guardar en caché
    save_contents_cache(contents, company_name)
    
    # Estadísticas
    stats = get_content_stats(contents)
    
    print("\n" + "="*70)
    print("📊 RESUMEN")
    print("="*70)
    print(f"✅ Secciones compiladas: {stats['total_sections']}")
    print(f"✅ Total de caracteres: {stats['total_characters']:,}")
    print(f"✅ Total de palabras: {stats['total_words']:,}")
    print(f"💾 Contenidos guardados en caché")
    print("="*70 + "\n")
    
    logger.info(f"✅ Scraping completado para {company_name}")
    
    return 0

# Comando: generate
def cmd_generate(args):
    """Comando para generar el folleto desde contenidos cacheados"""
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*70)
    print("📝 FASE 2: GENERACIÓN DE FOLLETO")
    print("="*70 + "\n")
    
    company_name = args.company
    
    if not company_name:
        logger.error("❌ Debes especificar --company")
        return 1
    
    # Cargar contenidos
    from src.compiler import load_contents_cache
    
    print(f"[1/2] Cargando contenidos de '{company_name}'...")
    contents = load_contents_cache(company_name)
    
    if not contents:
        logger.error(f"❌ No se encontraron contenidos para '{company_name}'")
        logger.error("💡 Ejecuta primero: python brochure.py scrape <URL> --company \"{}\"".format(company_name))
        return 1
    
    print(f"✅ Contenidos cargados: {len(contents)} secciones")
    
    # Generar folleto
    print(f"\n[2/2] Generando folleto con tono '{args.tone}'...")
    
    brochure = generate_brochure(
        contents=contents,
        company_name=company_name,
        base_url=args.url or f"https://{company_name.lower()}.com",
        tone=args.tone
    )
    
    # Guardar
    filepath = save_brochure(brochure, company_name, args.tone)
    
    # Estadísticas
    num_words = len(brochure.split())
    num_chars = len(brochure)
    
    print("\n" + "="*70)
    print("📊 RESUMEN")
    print("="*70)
    print(f"✅ Folleto generado: {filepath.name}")
    print(f"✅ Palabras: {num_words:,}")
    print(f"✅ Caracteres: {num_chars:,}")
    print(f"📁 Ubicación: {filepath.absolute()}")
    print("="*70 + "\n")
    
    logger.info(f"✅ Folleto generado: {filepath}")
    
    return 0

# Comando: export
def cmd_export(args):
    """Comando para exportar folleto a HTML"""
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*70)
    print("📤 FASE 3: EXPORTACIÓN A HTML")
    print("="*70 + "\n")
    
    company_name = args.company
    
    if not company_name:
        logger.error("❌ Debes especificar --company")
        return 1
    
    # Buscar archivo markdown
    output_dir = Path('outputs')
    safe_name = company_name.lower().replace(' ', '_')
    md_filename = f"{safe_name}_brochure_{args.tone}.md"
    md_file = output_dir / md_filename
    
    if not md_file.exists():
        logger.error(f"❌ No se encontró el archivo: {md_file}")
        logger.error("💡 Ejecuta primero: python brochure.py generate --company \"{}\"".format(company_name))
        return 1
    
    print(f"✅ Archivo fuente encontrado: {md_file.name}")
    
    # Exportar con cada tema si --all-themes está activo
    themes = [args.theme] if not args.all_themes else list(get_available_themes().keys())
    
    print(f"\n📦 Exportando con {len(themes)} tema(s)...\n")
    
    html_files = []
    
    for theme in themes:
        print(f"[{themes.index(theme) + 1}/{len(themes)}] Tema: {get_available_themes()[theme]['name']}")
        
        html_file = export_to_html(
            markdown_file=md_file,
            company_name=company_name,
            tone=args.tone,
            theme=theme
        )
        
        html_files.append(html_file)
        print(f"   ✅ Generado: {html_file.name}")
    
    print("\n" + "="*70)
    print("📊 RESUMEN")
    print("="*70)
    print(f"✅ Archivos HTML generados: {len(html_files)}")
    
    for html_file in html_files:
        print(f"   📄 {html_file.name}")
    
    print(f"\n📁 Ubicación: {output_dir.absolute()}")
    print("="*70 + "\n")
    
    logger.info(f"✅ Exportación completada: {len(html_files)} archivos")
    
    return 0

# Comando: translate
def cmd_translate(args):
    """Comando para traducir folleto a otro idioma"""
    logger = logging.getLogger(__name__)
    
    print("\n" + "="*70)
    print("🌍 TRADUCCIÓN DE FOLLETO")
    print("="*70 + "\n")
    
    company_name = args.company
    
    # Importar traductor
    from src.translator import translate_brochure, save_translated_brochure, get_available_languages
    
    # Buscar archivo markdown
    output_dir = Path('outputs')
    safe_name = company_name.lower().replace(' ', '_')
    md_filename = f"{safe_name}_brochure_{args.tone}.md"
    md_file = output_dir / md_filename
    
    if not md_file.exists():
        logger.error(f"❌ No se encontró el archivo: {md_file}")
        logger.error("💡 Ejecuta primero: python brochure.py generate --company \"{}\"".format(company_name))
        return 1
    
    print(f"✅ Archivo fuente encontrado: {md_file.name}")
    
    # Leer folleto
    brochure = md_file.read_text(encoding='utf-8')
    
    languages = get_available_languages()
    
    print(f"\n📝 Traduciendo a: {languages[args.target]['name']}")
    
    # Traducir
    translated = translate_brochure(
        brochure=brochure,
        target_lang=args.target,
        source_lang=args.source,
        tone=args.tone
    )
    
    # Guardar
    filepath = save_translated_brochure(translated, company_name, args.target, args.tone)
    
    print("\n" + "="*70)
    print("📊 RESUMEN")
    print("="*70)
    print(f"✅ Traducción completada")
    print(f"📄 Archivo: {filepath.name}")
    print(f"📁 Ubicación: {filepath.absolute()}")
    print(f"📊 Caracteres: {len(translated):,}")
    print(f"📊 Palabras: {len(translated.split()):,}")
    print("="*70 + "\n")
    
    # Exportar a HTML si se solicita
    if args.export_html:
        print("🌐 Exportando traducción a HTML...\n")
        
        html_file = export_to_html(
            markdown_file=filepath,
            company_name=company_name,
            tone=args.tone,
            theme='light'
        )
        
        print(f"✅ HTML generado: {html_file.name}")
    
    logger.info(f"✅ Traducción completada: {filepath}")
    
    return 0

# Comando: full (pipeline completo)
def cmd_full(args):
    """Ejecuta el pipeline completo: scrape → generate → export"""
    logger = logging.getLogger(__name__)
    
    print_banner()
    
    print("🚀 INICIANDO PIPELINE COMPLETO\n")
    print("Esto ejecutará:")
    print("  1. Scraping de la web")
    print("  2. Generación del folleto")
    print("  3. Exportación a HTML")
    print("\n" + "="*70 + "\n")
    
    # Paso 1: Scrape
    result = cmd_scrape(args)
    if result != 0:
        return result
    
    # Esperar confirmación si no es automático
    if not args.yes:
        input("\n⏸️  Presiona ENTER para continuar con la generación del folleto...")
    
    # Paso 2: Generate
    result = cmd_generate(args)
    if result != 0:
        return result
    
    # Esperar confirmación si no es automático
    if not args.yes:
        input("\n⏸️  Presiona ENTER para continuar con la exportación a HTML...")
    
    # Paso 3: Export
    # ✅ FIX: Añadir el atributo all_themes si no existe
    if not hasattr(args, 'all_themes'):
        args.all_themes = False
    
    result = cmd_export(args)
    if result != 0:
        return result
    
    # Resumen final
    print("\n" + "="*70)
    print("🎉 ¡PIPELINE COMPLETADO EXITOSAMENTE!")
    print("="*70)
    
    output_dir = Path('outputs')
    company_name = args.company or get_domain_name(args.url).capitalize()
    safe_name = company_name.lower().replace(' ', '_')
    
    print(f"\n📁 Archivos generados en: {output_dir.absolute()}\n")
    print(f"   📝 Folleto (Markdown): {safe_name}_brochure_{args.tone}.md")
    print(f"   🌐 Folleto (HTML): {safe_name}_brochure_{args.tone}_{args.theme}.html")
    print(f"   💾 Contenidos (Caché): data/compiled/{safe_name}_contents.json")
    
    print("\n💡 Próximos pasos:")
    print(f"   - Abre el HTML en tu navegador")
    print(f"   - Usa Ctrl+P para guardar como PDF")
    print(f"   - Edita el Markdown si quieres ajustar algo")
    print("="*70 + "\n")
    
    return 0

# Main
def main():
    """Función principal del CLI"""
    
    parser = argparse.ArgumentParser(
        description='BrochureAI - Generador automático de folletos corporativos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Pipeline completo (scraping → generación → exportación)
  python brochure.py full https://huggingface.co --company "HuggingFace"
  
  # Solo scraping
  python brochure.py scrape https://empresa.com --company "Mi Empresa"
  
  # Solo generar folleto (requiere scraping previo)
  python brochure.py generate --company "Mi Empresa" --tone casual
  
  # Solo exportar a HTML (requiere folleto generado)
  python brochure.py export --company "Mi Empresa" --theme dark
  
  # Traducir folleto
  python brochure.py translate --company "Mi Empresa" --target en
  
  # Pipeline completo con todas las opciones
  python brochure.py full https://empresa.com \\
    --company "Mi Empresa" \\
    --tone professional \\
    --theme corporate \\
    --max-pages 10 \\
    --yes

Tonos disponibles: professional, casual, technical
Temas disponibles: light, dark, corporate
Idiomas de traducción: en, fr, de, pt, it

Para más información: https://github.com/tu-usuario/brochure-ai
        """
    )
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando: scrape
    parser_scrape = subparsers.add_parser('scrape', help='Scrapear web y compilar contenidos')
    parser_scrape.add_argument('url', help='URL de la empresa a scrapear')
    parser_scrape.add_argument('--company', help='Nombre de la empresa (opcional, se infiere de la URL)')
    parser_scrape.add_argument('--max-pages', type=int, default=10, help='Máximo de páginas a descargar (default: 10)')
    
    # Comando: generate
    parser_generate = subparsers.add_parser('generate', help='Generar folleto desde contenidos cacheados')
    parser_generate.add_argument('--company', required=True, help='Nombre de la empresa')
    parser_generate.add_argument('--tone', choices=['professional', 'casual', 'technical'], 
                                 default='professional', help='Tono del folleto (default: professional)')
    parser_generate.add_argument('--url', help='URL de la empresa (opcional)')
    
    # Comando: export
    parser_export = subparsers.add_parser('export', help='Exportar folleto a HTML')
    parser_export.add_argument('--company', required=True, help='Nombre de la empresa')
    parser_export.add_argument('--tone', default='professional', help='Tono del folleto a exportar')
    parser_export.add_argument('--theme', choices=['light', 'dark', 'corporate'], 
                               default='light', help='Tema visual (default: light)')
    parser_export.add_argument('--all-themes', action='store_true', 
                               help='Exportar con todos los temas disponibles')
    
    # Comando: translate
    parser_translate = subparsers.add_parser('translate', help='Traducir folleto a otro idioma')
    parser_translate.add_argument('--company', required=True, help='Nombre de la empresa')
    parser_translate.add_argument('--tone', default='professional', help='Tono del folleto a traducir')
    parser_translate.add_argument('--target', '-t', required=True, 
                                  choices=['en', 'fr', 'de', 'pt', 'it'],
                                  help='Idioma destino')
    parser_translate.add_argument('--source', '-s', 
                                  choices=['es', 'en', 'fr', 'de', 'pt', 'it'],
                                  help='Idioma origen (opcional, se detecta automáticamente)')
    parser_translate.add_argument('--export-html', action='store_true',
                                  help='Exportar también a HTML después de traducir')
    
    # Comando: full
    parser_full = subparsers.add_parser('full', help='Ejecutar pipeline completo')
    parser_full.add_argument('url', help='URL de la empresa a scrapear')
    parser_full.add_argument('--company', help='Nombre de la empresa (opcional)')
    parser_full.add_argument('--tone', choices=['professional', 'casual', 'technical'], 
                             default='professional', help='Tono del folleto')
    parser_full.add_argument('--theme', choices=['light', 'dark', 'corporate'], 
                             default='light', help='Tema visual')
    parser_full.add_argument('--max-pages', type=int, default=10, help='Máximo de páginas a descargar')
    parser_full.add_argument('--yes', '-y', action='store_true', 
                             help='No pedir confirmación entre pasos')
    # ✅ FIX: Añadir --all-themes también al comando full
    parser_full.add_argument('--all-themes', action='store_true', 
                             help='Exportar con todos los temas disponibles')
    
    # Argumentos globales
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verbose (más logs)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Modo silencioso (solo errores)')
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Si no se especifica comando, mostrar ayuda
    if not args.command:
        parser.print_help()
        return 0
    
    # Configurar logging
    if args.quiet:
        setup_logging(verbose=False)
        logging.getLogger().setLevel(logging.ERROR)
    else:
        setup_logging(verbose=args.verbose)
    
    # Ejecutar comando
    commands = {
        'scrape': cmd_scrape,
        'generate': cmd_generate,
        'export': cmd_export,
        'translate': cmd_translate,
        'full': cmd_full
    }
    
    try:
        return commands[args.command](args)
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        return 130
    except Exception as e:
        logging.error(f"❌ Error inesperado: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())