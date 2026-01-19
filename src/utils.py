"""
Utilidades para normalización de URLs y limpieza de texto
"""
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import List, Set
import logging

logger = logging.getLogger(__name__)


def normalize_url(base_url: str, link: str) -> str:
    """
    Convierte una URL relativa a absoluta.
    
    Args:
        base_url: URL base (ej: https://empresa.com)
        link: Enlace que puede ser relativo o absoluto
        
    Returns:
        URL absoluta normalizada
        
    Examples:
        >>> normalize_url("https://empresa.com", "/about")
        'https://empresa.com/about'
        >>> normalize_url("https://empresa.com/page", "../contact")
        'https://empresa.com/contact'
        >>> normalize_url("https://empresa.com", "https://otra.com")
        'https://otra.com'
    """
    # urljoin maneja todos los casos: relativos, absolutos, con .., etc.
    normalized = urljoin(base_url, link)
    
    # Limpiar fragmentos (#section) y normalizar
    parsed = urlparse(normalized)
    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    # Añadir query string si existe (importante para algunos sitios)
    if parsed.query:
        clean_url += f"?{parsed.query}"
    
    # Remover trailing slash para evitar duplicados
    if clean_url.endswith('/') and len(parsed.path) > 1:
        clean_url = clean_url[:-1]
    
    return clean_url


def is_same_domain(base_url: str, link: str) -> bool:
    """
    Verifica si un enlace pertenece al mismo dominio que la URL base.
    
    Args:
        base_url: URL base
        link: Enlace a verificar
        
    Returns:
        True si ambos tienen el mismo dominio
    """
    base_domain = urlparse(base_url).netloc
    link_domain = urlparse(link).netloc
    
    return base_domain == link_domain


def filter_valid_links(links: List[str], base_url: str) -> List[str]:
    """
    Filtra enlaces válidos: mismo dominio, no archivos de descarga, etc.
    
    Args:
        links: Lista de enlaces (ya normalizados)
        base_url: URL base del sitio
        
    Returns:
        Lista filtrada de enlaces únicos
    """
    valid_links = []
    seen: Set[str] = set()
    
    # Extensiones de archivo a ignorar
    skip_extensions = {
        '.pdf', '.zip', '.doc', '.docx', '.xls', '.xlsx',
        '.ppt', '.pptx', '.jpg', '.jpeg', '.png', '.gif',
        '.mp4', '.avi', '.mp3', '.exe', '.dmg', '.apk'
    }
    
    for link in links:
        # Normalizar
        normalized = normalize_url(base_url, link)
        
        # Evitar duplicados
        if normalized in seen:
            continue
        
        # Solo del mismo dominio
        if not is_same_domain(base_url, normalized):
            continue
        
        # Ignorar archivos de descarga
        parsed = urlparse(normalized)
        path_lower = parsed.path.lower()
        
        if any(path_lower.endswith(ext) for ext in skip_extensions):
            logger.debug(f"Ignorando archivo: {normalized}")
            continue
        
        # Ignorar parámetros típicos de tracking/sesión
        if any(param in parsed.query.lower() for param in ['utm_', 'session', 'token']):
            # Mantener la URL pero sin query params
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        seen.add(normalized)
        valid_links.append(normalized)
    
    logger.info(f"Filtrados {len(valid_links)} enlaces válidos de {len(links)} totales")
    return valid_links


def clean_text(html: str) -> str:
    """
    Extrae texto limpio del HTML, eliminando scripts, estilos y navegación.
    
    Args:
        html: HTML crudo
        
    Returns:
        Texto limpio, normalizado
    """
    soup = BeautifulSoup(html, 'lxml')
    
    # Eliminar elementos irrelevantes
    for element in soup([
        'script', 'style', 'noscript', 'iframe',
        'header', 'footer', 'nav',  # Navegación
        'aside', 'form',  # Barras laterales y formularios
        'button', 'input', 'select', 'textarea'  # Elementos de formulario
    ]):
        element.decompose()
    
    # Extraer texto
    text = soup.get_text(separator='\n', strip=True)
    
    # Limpiar líneas vacías múltiples
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    clean = '\n'.join(lines)
    
    # Limitar líneas repetidas (por si hay menus duplicados)
    final_lines = []
    prev_line = None
    
    for line in lines:
        # No repetir la misma línea más de 2 veces consecutivas
        if line != prev_line or (final_lines and final_lines[-1] != line):
            final_lines.append(line)
        prev_line = line
    
    result = '\n'.join(final_lines)
    
    logger.info(f"Texto limpio extraído: {len(result)} caracteres")
    return result


def truncate_text(text: str, max_chars: int = 15000) -> str:
    """
    Trunca texto a un máximo de caracteres (para no saturar el LLM).
    
    Args:
        text: Texto a truncar
        max_chars: Máximo de caracteres
        
    Returns:
        Texto truncado con indicador si fue cortado
    """
    if len(text) <= max_chars:
        return text
    
    truncated = text[:max_chars]
    # Cortar en el último salto de línea para no partir palabras
    last_newline = truncated.rfind('\n')
    if last_newline > max_chars * 0.9:  # Si está cerca del límite
        truncated = truncated[:last_newline]
    
    return truncated + "\n\n[... contenido truncado ...]"


def get_domain_name(url: str) -> str:
    """
    Extrae el nombre del dominio principal.
    
    Args:
        url: URL completa
        
    Returns:
        Nombre del dominio (ej: 'huggingface' de 'huggingface.co')
    """
    domain = urlparse(url).netloc
    # Remover www. y subdominios comunes
    domain = domain.replace('www.', '')
    # Tomar la parte principal (antes del TLD)
    main_domain = domain.split('.')[0]
    return main_domain