"""
Compilador de contenidos: descarga y consolida páginas
"""
import logging
import time
from typing import Dict, List, Optional
from pathlib import Path
import json

from src.scraping import smart_scrape
from src.utils import clean_text, truncate_text

logger = logging.getLogger(__name__)


def download_page_content(url: str, max_chars: int = 15000) -> Optional[str]:
    """
    Descarga una página y extrae su texto limpio.
    
    Args:
        url: URL a descargar
        max_chars: Máximo de caracteres a retornar
        
    Returns:
        Texto limpio o None si falla
    """
    logger.info(f"📥 Descargando contenido: {url}")
    
    html, _, method = smart_scrape(url)
    
    if html is None:
        logger.warning(f"⚠️ No se pudo descargar {url}")
        return None
    
    # Limpiar y truncar
    text = clean_text(html)
    text = truncate_text(text, max_chars)
    
    logger.info(f"✓ Contenido descargado: {len(text)} caracteres (método: {method})")
    return text


def compile_contents(
    selected_links: List[Dict],
    landing_html: str,
    base_url: str,
    max_pages: int = 10
) -> Dict[str, str]:
    """
    Descarga y compila el contenido de todos los enlaces seleccionados.
    
    Args:
        selected_links: Lista de enlaces del formato [{'url': ..., 'type': ..., 'reason': ...}]
        landing_html: HTML de la página principal (ya descargado)
        base_url: URL base del sitio
        max_pages: Máximo de páginas a descargar (protección)
        
    Returns:
        Dict con estructura: {'landing': 'texto...', 'about': 'texto...', 'careers': 'texto...', ...}
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"🔄 COMPILANDO CONTENIDOS")
    logger.info(f"{'='*70}")
    
    contents = {}
    
    # 1. Agregar contenido de la landing
    logger.info("\n1️⃣ Procesando página principal (landing)...")
    landing_text = clean_text(landing_html)
    landing_text = truncate_text(landing_text, 15000)
    contents['landing'] = landing_text
    logger.info(f"✓ Landing procesada: {len(landing_text)} caracteres")
    
    # 2. Descargar cada enlace seleccionado
    logger.info(f"\n2️⃣ Descargando {len(selected_links[:max_pages])} páginas adicionales...")
    
    downloaded = 0
    failed = 0
    
    for i, link_info in enumerate(selected_links[:max_pages], 1):
        url = link_info['url']
        link_type = link_info['type']
        
        logger.info(f"\n[{i}/{len(selected_links[:max_pages])}] Tipo: {link_type}")
        
        # Descargar contenido
        text = download_page_content(url)
        
        if text:
            # Usar el tipo como clave (ej: 'about', 'careers')
            # Si ya existe ese tipo, agregar sufijo numérico
            key = link_type
            counter = 1
            while key in contents:
                key = f"{link_type}_{counter}"
                counter += 1
            
            contents[key] = text
            downloaded += 1
            logger.info(f"✅ Guardado como '{key}'")
        else:
            failed += 1
            logger.warning(f"❌ Falló descarga de {url}")
    
    # 3. Resumen
    logger.info(f"\n{'='*70}")
    logger.info(f"📊 RESUMEN DE COMPILACIÓN")
    logger.info(f"{'='*70}")
    logger.info(f"✓ Páginas descargadas: {downloaded + 1} (landing + {downloaded} adicionales)")
    logger.info(f"✗ Páginas fallidas: {failed}")
    logger.info(f"📦 Total de secciones: {len(contents)}")
    logger.info(f"\nSecciones disponibles: {', '.join(contents.keys())}")
    logger.info(f"{'='*70}\n")
    
    return contents


def save_contents_cache(contents: Dict[str, str], company_name: str):
    """
    Guarda los contenidos compilados en caché (opcional, para debugging).
    
    Args:
        contents: Contenidos compilados
        company_name: Nombre de la empresa (para el filename)
    """
    cache_dir = Path('data/compiled')
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitizar nombre de empresa para filename
    safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_').lower()
    
    cache_file = cache_dir / f"{safe_name}_contents.json"
    
    # Guardar como JSON
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(contents, f, indent=2, ensure_ascii=False)
    
    logger.info(f"💾 Contenidos guardados en caché: {cache_file}")


def load_contents_cache(company_name: str) -> Optional[Dict[str, str]]:
    """
    Carga contenidos desde caché si existen.
    
    Args:
        company_name: Nombre de la empresa
        
    Returns:
        Contenidos o None si no existe el caché
    """
    safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_').lower()
    
    cache_file = Path('data/compiled') / f"{safe_name}_contents.json"
    
    if not cache_file.exists():
        return None
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        contents = json.load(f)
    
    logger.info(f"💾 Contenidos cargados desde caché: {cache_file}")
    return contents


def get_content_stats(contents: Dict[str, str]) -> Dict:
    """
    Calcula estadísticas sobre los contenidos compilados.
    
    Args:
        contents: Contenidos compilados
        
    Returns:
        Dict con estadísticas
    """
    total_chars = sum(len(text) for text in contents.values())
    total_words = sum(len(text.split()) for text in contents.values())
    
    stats = {
        'total_sections': len(contents),
        'total_characters': total_chars,
        'total_words': total_words,
        'sections': {
            key: {
                'characters': len(text),
                'words': len(text.split()),
                'lines': len(text.split('\n'))
            }
            for key, text in contents.items()
        }
    }
    
    return stats