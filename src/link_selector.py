"""
Selección de enlaces relevantes usando Google Genai (nueva API)
"""
import json
import os
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from pathlib import Path

# Nueva librería de Google
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ google.genai no disponible: {e}")
    logging.warning("⚠️ Se usará MODO MOCK permanentemente")
    GENAI_AVAILABLE = False
    genai = None

load_dotenv()
logger = logging.getLogger(__name__)

# Configuración
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
MOCK_MODE = os.getenv('MOCK_MODE', 'false').lower() == 'true'


def load_prompt(filename: str) -> str:
    """Carga un prompt desde la carpeta prompts/"""
    prompt_path = Path('prompts') / filename
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt no encontrado: {prompt_path}")
    return prompt_path.read_text(encoding='utf-8')


def configure_genai():
    """Configura el cliente de Google GenAI"""
    if not GENAI_AVAILABLE:
        logger.warning("⚠️ Google GenAI no disponible - usando modo mock")
        return None
    
    if MOCK_MODE:
        logger.info("🎭 Modo MOCK activado - no se usará Gemini")
        return None
    
    if not GEMINI_API_KEY:
        logger.warning("⚠️ GEMINI_API_KEY no encontrada - usando modo mock")
        return None
    
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info(f"✓ Google GenAI configurado con modelo: {GEMINI_MODEL}")
        return client
    except Exception as e:
        logger.error(f"Error configurando GenAI: {e}")
        return None


def select_links_mock(links: List[str], base_url: str) -> Dict:
    """
    Modo mock: selecciona enlaces basándose en palabras clave simples.
    Sin usar API de Gemini.
    """
    logger.info("🎭 Usando selector MOCK (sin Gemini)")
    
    keywords = {
        'about': ['about', 'acerca', 'quienes', 'who-we-are', 'our-story', 'company'],
        'careers': ['careers', 'jobs', 'trabajo', 'empleo', 'join', 'hiring'],
        'customers': ['customers', 'clientes', 'case-studies', 'casos', 'success'],
        'team': ['team', 'equipo', 'leadership', 'people', 'leaders'],
        'products': ['products', 'servicios', 'services', 'solutions', 'platform'],
        'blog': ['blog', 'news', 'noticias', 'articles'],
        'press': ['press', 'prensa', 'media', 'newsroom'],
        'culture': ['culture', 'cultura', 'values', 'valores', 'mission', 'vision'],
    }
    
    relevant = []
    seen_types = set()
    
    for link in links[:80]:
        link_lower = link.lower()
        
        # Filtrar excluidos
        if any(exc in link_lower for exc in [
            'privacy', 'terms', 'legal', 'cookie',
            'login', 'signin', 'signup', 'register',
            'cart', 'checkout', 'account', 'pricing',
            'api', 'docs', 'documentation', 'github'
        ]):
            continue
        
        # Buscar coincidencias
        for link_type, keywords_list in keywords.items():
            if link_type in seen_types:
                continue
                
            if any(kw in link_lower for kw in keywords_list):
                relevant.append({
                    'url': link,
                    'type': link_type,
                    'reason': f'Contiene palabra clave relacionada con {link_type}'
                })
                seen_types.add(link_type)
                break
        
        if len(relevant) >= 10:
            break
    
    logger.info(f"Mock selector: {len(relevant)} enlaces seleccionados")
    return {'relevant_links': relevant}


def parse_json_response(response_text: str) -> Optional[Dict]:
    """
    Parsea la respuesta JSON del LLM, manejando errores comunes.
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        logger.warning("Respuesta no es JSON válido, intentando limpiar...")
        
        # Intentar extraer JSON de markdown
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            json_str = response_text[start:end].strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Intentar buscar el objeto JSON en el texto
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start != -1 and end > start:
            json_str = response_text[start:end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.error("No se pudo extraer JSON válido de la respuesta")
                return None
        
        logger.error("No se encontró JSON en la respuesta")
        return None


def select_relevant_links(
    links: List[str],
    base_url: str,
    company_name: str = "la empresa",
    max_retries: int = 2
) -> Dict:
    """
    Selecciona enlaces relevantes usando Google GenAI (o mock).
    
    Args:
        links: Lista de URLs normalizadas
        base_url: URL base del sitio
        company_name: Nombre de la empresa
        max_retries: Intentos máximos si falla el parsing
        
    Returns:
        Dict con estructura: {'relevant_links': [{'url': ..., 'type': ..., 'reason': ...}]}
    """
    # Si modo mock, sin GenAI disponible o sin API key
    if MOCK_MODE or not GENAI_AVAILABLE or not GEMINI_API_KEY:
        return select_links_mock(links, base_url)
    
    # Configurar GenAI
    client = configure_genai()
    if client is None:
        return select_links_mock(links, base_url)
    
    # Cargar prompts
    system_prompt = load_prompt('link_selection_system.md')
    user_template = load_prompt('link_selection_user.md')
    
    # Preparar lista de enlaces (máx 100 para no saturar)
    links_display = links[:100]
    links_list = '\n'.join([f"- {link}" for link in links_display])
    
    user_prompt = user_template.format(
        company_name=company_name,
        base_url=base_url,
        links_list=links_list
    )
    
    # Llamar a GenAI con reintentos
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"🤖 Llamando a Gemini (intento {attempt + 1}/{max_retries + 1})...")
            
            # Crear el prompt completo
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Llamada al modelo (nueva API)
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
            
            response_text = response.text
            logger.info(f"✓ Respuesta recibida: {len(response_text)} caracteres")
            
            # Parsear JSON
            result = parse_json_response(response_text)
            
            if result and 'relevant_links' in result:
                logger.info(f"✅ {len(result['relevant_links'])} enlaces seleccionados por Gemini")
                return result
            else:
                logger.warning(f"Respuesta sin estructura válida (intento {attempt + 1})")
                if attempt < max_retries:
                    logger.info("Reintentando...")
                    continue
                else:
                    logger.error("Máximos reintentos alcanzados, usando mock")
                    return select_links_mock(links, base_url)
        
        except Exception as e:
            logger.error(f"Error en Gemini: {e}")
            if attempt < max_retries:
                logger.info("Reintentando...")
                continue
            else:
                logger.error("Máximos reintentos alcanzados, usando mock")
                return select_links_mock(links, base_url)
    
    # Fallback final
    return select_links_mock(links, base_url)