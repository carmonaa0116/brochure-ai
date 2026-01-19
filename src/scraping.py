"""
Scraping estático con requests + BeautifulSoup
"""
import requests
from bs4 import BeautifulSoup
from typing import Tuple, List, Optional
import logging
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_html(url: str, timeout: int = 10) -> Optional[str]:
    """
    Descarga el HTML de una URL usando requests.
    
    Args:
        url: URL a descargar
        timeout: Timeout en segundos
        
    Returns:
        HTML como string o None si falla
    """
    headers = {
        'User-Agent': 'BrochureAI/0.1 (Educational Project; contact@example.com)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    }
    
    try:
        logger.info(f"Descargando: {url}")
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Lanza excepción si status >= 400
        
        logger.info(f"✓ Descargado {len(response.text)} caracteres (status {response.status_code})")
        return response.text
        
    except requests.exceptions.Timeout:
        logger.error(f"✗ Timeout alcanzado para {url}")
        return None
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"✗ Error HTTP {e.response.status_code}: {url}")
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Error de conexión: {e}")
        return None


def extract_links(html: str, base_url: str) -> List[str]:
    """
    Extrae todos los enlaces <a href> del HTML.
    Ignora scripts, estilos, imágenes, inputs.
    
    Args:
        html: HTML como string
        base_url: URL base para debugging (no normaliza aquí)
        
    Returns:
        Lista de URLs extraídas (pueden ser relativas o absolutas)
    """
    soup = BeautifulSoup(html, 'lxml')
    
    # Eliminar elementos irrelevantes ANTES de buscar enlaces
    for tag in soup(['script', 'style', 'noscript', 'iframe']):
        tag.decompose()
    
    links = []
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()
        
        # Filtros básicos
        if not href:
            continue
        if href.startswith('#'):  # Anclas internas
            continue
        if href.startswith('mailto:'):
            continue
        if href.startswith('tel:'):
            continue
        if href.startswith('javascript:'):
            continue
            
        links.append(href)
    
    logger.info(f"Extraídos {len(links)} enlaces del HTML")
    return links


def scrape_and_extract(url: str) -> Tuple[Optional[str], List[str]]:
    """
    Función principal: descarga HTML y extrae enlaces.
    
    Args:
        url: URL a scrapear
        
    Returns:
        (html, lista_de_enlaces)
    """
    html = fetch_html(url)
    
    if html is None:
        logger.warning(f"No se pudo descargar {url}")
        return None, []
    
    links = extract_links(html, url)
    
    return html, links


"""
Añadir al final de src/scraping.py
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import os
from dotenv import load_dotenv

load_dotenv()

# Rate limiting
RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '1.5'))


def is_incomplete_html(html: str, url: str) -> bool:
    """
    Detecta si el HTML parece incompleto (requiere JS para renderizar).
    
    Heurísticas:
    1. HTML muy corto (<1500 chars) pero es un sitio complejo
    2. Tiene <div id="root"> o <div id="app"> vacíos (React/Vue)
    3. Tiene textos como "Loading...", "Please enable JavaScript"
    4. Ratio script/contenido muy alto
    
    Args:
        html: HTML descargado
        url: URL para contexto
        
    Returns:
        True si parece incompleto
    """
    soup = BeautifulSoup(html, 'lxml')
    
    # Heurística 1: HTML muy corto
    if len(html) < 1500:
        logger.warning(f"HTML muy corto ({len(html)} chars) - posible SPA")
        return True
    
    # Heurística 2: Divs típicos de SPAs vacíos
    root_div = soup.find('div', id='root')
    app_div = soup.find('div', id='app')
    
    if root_div and len(root_div.get_text(strip=True)) < 50:
        logger.warning("Detectado <div id='root'> casi vacío - SPA React")
        return True
        
    if app_div and len(app_div.get_text(strip=True)) < 50:
        logger.warning("Detectado <div id='app'> casi vacío - SPA Vue")
        return True
    
    # Heurística 3: Textos indicadores de JS requerido
    text_content = soup.get_text().lower()
    js_indicators = [
        'please enable javascript',
        'requires javascript',
        'javascript is disabled',
        'loading...',
        'cargando...'
    ]
    
    for indicator in js_indicators:
        if indicator in text_content:
            logger.warning(f"Detectado texto '{indicator}' - requiere JS")
            return True
    
    # Heurística 4: Pocos enlaces extraídos (pero muchos scripts)
    links = soup.find_all('a', href=True)
    scripts = soup.find_all('script')
    
    if len(links) < 5 and len(scripts) > 10:
        logger.warning(f"Pocos enlaces ({len(links)}) pero muchos scripts ({len(scripts)}) - posible SPA")
        return True
    
    logger.info("HTML parece completo - scraping estático OK")
    return False


def fetch_html_dynamic(url: str, timeout: int = 30000) -> Optional[str]:
    """
    Descarga HTML usando Playwright (navegador headless).
    Espera a que la página cargue completamente.
    
    Args:
        url: URL a renderizar
        timeout: Timeout en milisegundos (default 30s)
        
    Returns:
        HTML renderizado o None si falla
    """
    try:
        logger.info(f"🌐 Usando navegador headless para: {url}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent='BrochureAI/0.1 (Educational Project; contact@example.com)'
            )
            
            # Navegar y esperar a que cargue
            page.goto(url, wait_until='networkidle', timeout=timeout)
            
            # Esperar un poco más para JS asíncrono
            page.wait_for_timeout(2000)  # 2 segundos adicionales
            
            html = page.content()
            browser.close()
            
            logger.info(f"✓ HTML dinámico obtenido: {len(html)} caracteres")
            return html
            
    except PlaywrightTimeout:
        logger.error(f"✗ Timeout en navegador headless para {url}")
        return None
        
    except Exception as e:
        logger.error(f"✗ Error en Playwright: {e}")
        return None


def smart_scrape(url: str, force_dynamic: bool = False) -> Tuple[Optional[str], List[str], str]:
    """
    Scraping inteligente: intenta estático primero, fallback a dinámico si es necesario.
    
    Args:
        url: URL a scrapear
        force_dynamic: Si True, usa Playwright directamente
        
    Returns:
        (html, enlaces, método_usado)
        método_usado: 'static' o 'dynamic'
    """
    # Rate limiting
    time.sleep(RATE_LIMIT_DELAY)
    
    # Si se fuerza dinámico, ir directo a Playwright
    if force_dynamic:
        logger.info("⚡ Modo dinámico forzado")
        html = fetch_html_dynamic(url)
        if html:
            links = extract_links(html, url)
            return html, links, 'dynamic'
        else:
            return None, [], 'dynamic'
    
    # Intentar estático primero
    logger.info("📄 Intentando scraping estático...")
    html = fetch_html(url)
    
    if html is None:
        logger.warning("Scraping estático falló, intentando dinámico...")
        html = fetch_html_dynamic(url)
        method = 'dynamic'
    elif is_incomplete_html(html, url):
        logger.warning("HTML incompleto detectado, cambiando a scraping dinámico...")
        html = fetch_html_dynamic(url)
        method = 'dynamic'
    else:
        method = 'static'
    
    if html is None:
        return None, [], method
    
    links = extract_links(html, url)
    
    logger.info(f"✅ Scraping completado con método: {method}")
    return html, links, method