"""
Exportador de folletos: Markdown → HTML → PDF
"""
import logging
from pathlib import Path
from typing import Optional
import markdown
from datetime import datetime

logger = logging.getLogger(__name__)

# Temas visuales disponibles
THEMES = {
    'light': {
        'name': 'Claro',
        'bg_color': '#ffffff',
        'text_color': '#333333',
        'heading_color': '#1a1a1a',
        'accent_color': '#0066cc',
        'border_color': '#e0e0e0',
        'code_bg': '#f5f5f5'
    },
    'dark': {
        'name': 'Oscuro',
        'bg_color': '#1a1a1a',
        'text_color': '#e0e0e0',
        'heading_color': '#ffffff',
        'accent_color': '#4a9eff',
        'border_color': '#333333',
        'code_bg': '#2a2a2a'
    },
    'corporate': {
        'name': 'Corporativo',
        'bg_color': '#f8f9fa',
        'text_color': '#2c3e50',
        'heading_color': '#1a252f',
        'accent_color': '#3498db',
        'border_color': '#bdc3c7',
        'code_bg': '#ecf0f1'
    }
}


def get_html_template(theme: str = 'light') -> str:
    """
    Retorna la plantilla HTML con estilos CSS embebidos.
    
    Args:
        theme: Tema visual a usar
        
    Returns:
        Template HTML como string
    """
    if theme not in THEMES:
        logger.warning(f"Tema '{theme}' no válido, usando 'light'")
        theme = 'light'
    
    colors = THEMES[theme]
    
    # Template con placeholders consistentes usando dobles guiones bajos
    template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="generator" content="BrochureAI v0.1">
    <meta name="description" content="__META_DESCRIPTION__">
    <title>__TITLE__</title>
    
    <style>
        /* Reset y base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: __TEXT_COLOR__;
            background-color: __BG_COLOR__;
            padding: 20px;
        }
        
        /* Contenedor principal */
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: __BG_COLOR__;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        
        /* Tipografía */
        h1 {
            font-size: 2.5em;
            color: __HEADING_COLOR__;
            margin-bottom: 0.5em;
            border-bottom: 3px solid __ACCENT_COLOR__;
            padding-bottom: 0.3em;
        }
        
        h2 {
            font-size: 2em;
            color: __HEADING_COLOR__;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
            border-left: 4px solid __ACCENT_COLOR__;
            padding-left: 15px;
        }
        
        h3 {
            font-size: 1.5em;
            color: __HEADING_COLOR__;
            margin-top: 1.2em;
            margin-bottom: 0.6em;
        }
        
        h4, h5, h6 {
            color: __HEADING_COLOR__;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }
        
        p {
            margin-bottom: 1em;
            text-align: justify;
        }
        
        /* Enlaces */
        a {
            color: __ACCENT_COLOR__;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-bottom 0.3s;
        }
        
        a:hover {
            border-bottom: 1px solid __ACCENT_COLOR__;
        }
        
        /* Listas */
        ul, ol {
            margin-bottom: 1em;
            margin-left: 2em;
        }
        
        li {
            margin-bottom: 0.5em;
        }
        
        /* Blockquotes */
        blockquote {
            border-left: 4px solid __ACCENT_COLOR__;
            padding-left: 20px;
            margin: 1.5em 0;
            font-style: italic;
            color: __TEXT_COLOR__;
            background: __CODE_BG__;
            padding: 15px 20px;
            border-radius: 4px;
        }
        
        /* Código */
        code {
            background: __CODE_BG__;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        pre {
            background: __CODE_BG__;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin-bottom: 1em;
        }
        
        pre code {
            background: none;
            padding: 0;
        }
        
        /* Tablas */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1.5em;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid __BORDER_COLOR__;
        }
        
        th {
            background: __CODE_BG__;
            font-weight: bold;
            color: __HEADING_COLOR__;
        }
        
        tr:hover {
            background: __CODE_BG__;
        }
        
        /* Separadores */
        hr {
            border: none;
            border-top: 2px solid __BORDER_COLOR__;
            margin: 2em 0;
        }
        
        /* Negrita y cursiva */
        strong {
            font-weight: 600;
            color: __HEADING_COLOR__;
        }
        
        em {
            font-style: italic;
        }
        
        /* Footer */
        .footer {
            margin-top: 3em;
            padding-top: 1.5em;
            border-top: 1px solid __BORDER_COLOR__;
            text-align: center;
            font-size: 0.9em;
            color: __TEXT_COLOR__;
            opacity: 0.7;
        }
        
        /* Responsivo */
        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            h2 {
                font-size: 1.5em;
            }
        }
        
        /* Impresión */
        @media print {
            body {
                background: white;
                color: black;
            }
            
            .container {
                box-shadow: none;
                padding: 0;
            }
            
            a {
                color: black;
                text-decoration: underline;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        __CONTENT__
        
        <div class="footer">
            <p>Generado el __GENERATION_DATE__ con BrochureAI</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Reemplazar colores del tema (ahora con el formato correcto)
    template = template.replace('__BG_COLOR__', colors['bg_color'])
    template = template.replace('__TEXT_COLOR__', colors['text_color'])
    template = template.replace('__HEADING_COLOR__', colors['heading_color'])
    template = template.replace('__ACCENT_COLOR__', colors['accent_color'])
    template = template.replace('__BORDER_COLOR__', colors['border_color'])
    template = template.replace('__CODE_BG__', colors['code_bg'])
    
    return template


def markdown_to_html(
    markdown_text: str,
    title: str = "Folleto Corporativo",
    theme: str = 'light',
    meta_description: str = ""
) -> str:
    """
    Convierte Markdown a HTML con estilos profesionales.
    
    Args:
        markdown_text: Texto en formato Markdown
        title: Título de la página HTML
        theme: Tema visual ('light', 'dark', 'corporate')
        meta_description: Descripción para SEO
        
    Returns:
        HTML completo como string
    """
    logger.info(f"📄 Convirtiendo Markdown a HTML (tema: {theme})...")
    
    # Configurar extensiones de markdown
    extensions = [
        'extra',          # Tablas, def lists, etc.
        'codehilite',     # Syntax highlighting
        'toc',            # Table of contents
        'nl2br',          # Newline to <br>
        'sane_lists'      # Mejor manejo de listas
    ]
    
    # Convertir markdown a HTML
    md = markdown.Markdown(extensions=extensions)
    content_html = md.convert(markdown_text)
    
    # Obtener template
    template = get_html_template(theme)
    
    # Generar descripción automática si no se proporciona
    if not meta_description:
        # Usar las primeras 150 caracteres del texto sin markdown
        plain_text = markdown_text.replace('#', '').replace('*', '').replace('>', '')
        meta_description = ' '.join(plain_text.split()[:25]) + "..."
    
    # Reemplazar placeholders
    html = template.replace('__CONTENT__', content_html)
    html = html.replace('__TITLE__', title)
    html = html.replace('__META_DESCRIPTION__', meta_description)
    html = html.replace('__GENERATION_DATE__', datetime.now().strftime('%d/%m/%Y %H:%M'))
    
    logger.info(f"✅ HTML generado: {len(html):,} caracteres")
    
    return html


def save_html(
    html_content: str,
    company_name: str,
    tone: str = 'professional',
    theme: str = 'light'
) -> Path:
    """
    Guarda el HTML en un archivo.
    
    Args:
        html_content: HTML completo
        company_name: Nombre de la empresa
        tone: Tono del folleto
        theme: Tema visual
        
    Returns:
        Path del archivo guardado
    """
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    
    # Sanitizar nombre
    safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_').lower()
    
    filename = f"{safe_name}_brochure_{tone}_{theme}.html"
    filepath = output_dir / filename
    
    # Guardar
    filepath.write_text(html_content, encoding='utf-8')
    
    logger.info(f"💾 HTML guardado en: {filepath}")
    
    return filepath


def export_to_html(
    markdown_file: Path,
    company_name: str,
    tone: str = 'professional',
    theme: str = 'light'
) -> Path:
    """
    Lee un archivo Markdown y lo exporta a HTML.
    
    Args:
        markdown_file: Path del archivo .md
        company_name: Nombre de la empresa
        tone: Tono del folleto
        theme: Tema visual
        
    Returns:
        Path del archivo HTML generado
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"📤 EXPORTANDO A HTML")
    logger.info(f"{'='*70}")
    logger.info(f"Archivo fuente: {markdown_file}")
    logger.info(f"Tema: {THEMES[theme]['name']}")
    
    # Leer markdown
    if not markdown_file.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {markdown_file}")
    
    markdown_text = markdown_file.read_text(encoding='utf-8')
    logger.info(f"✅ Markdown leído: {len(markdown_text):,} caracteres")
    
    # Convertir a HTML
    html = markdown_to_html(
        markdown_text=markdown_text,
        title=f"{company_name} - Folleto Corporativo",
        theme=theme,
        meta_description=f"Folleto corporativo de {company_name}"
    )
    
    # Guardar
    filepath = save_html(html, company_name, tone, theme)
    
    logger.info(f"{'='*70}\n")
    
    return filepath


def export_to_pdf_placeholder(html_file: Path, company_name: str) -> Optional[Path]:
    """
    Placeholder para exportación a PDF.
    Por ahora solo muestra un mensaje informativo.
    
    Args:
        html_file: Path del archivo HTML
        company_name: Nombre de la empresa
        
    Returns:
        None (no implementado)
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"📄 EXPORTACIÓN A PDF")
    logger.info(f"{'='*70}")
    logger.info("ℹ️  La exportación a PDF está temporalmente deshabilitada")
    logger.info("💡 Alternativas:")
    logger.info(f"   1. Abre {html_file} en tu navegador")
    logger.info("   2. Usa Ctrl+P (Cmd+P en Mac) → 'Guardar como PDF'")
    logger.info("   3. O usa herramientas online: https://www.web2pdfconvert.com/")
    logger.info(f"{'='*70}\n")
    
    return None


def get_available_themes() -> dict:
    """Retorna los temas disponibles"""
    return THEMES