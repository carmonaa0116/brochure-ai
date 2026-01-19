"""
Generador de folletos corporativos con Google GenAI
"""
import logging
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv
import os

from google import genai
from google.genai import types

load_dotenv()
logger = logging.getLogger(__name__)

# Configuración
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
MOCK_MODE = os.getenv('MOCK_MODE', 'false').lower() == 'true'

# Tonos disponibles
TONES = {
    'professional': {
        'name': 'Profesional',
        'description': 'Formal, corporativo, orientado a negocios B2B'
    },
    'casual': {
        'name': 'Casual',
        'description': 'Amigable, cercano, orientado a consumidor final'
    },
    'technical': {
        'name': 'Técnico',
        'description': 'Detallado, preciso, orientado a audiencia técnica'
    }
}


def load_prompt(filename: str) -> str:
    """Carga un prompt desde la carpeta prompts/"""
    prompt_path = Path('prompts') / filename
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt no encontrado: {prompt_path}")
    return prompt_path.read_text(encoding='utf-8')


def format_compiled_contents(contents: Dict[str, str]) -> str:
    """
    Formatea los contenidos compilados para el prompt.
    
    Args:
        contents: Dict con secciones compiladas
        
    Returns:
        String formateado para el prompt
    """
    formatted = []
    
    for section, text in contents.items():
        # Capitalizar nombre de sección
        section_title = section.replace('_', ' ').title()
        
        formatted.append(f"## {section_title}")
        formatted.append(text)
        formatted.append("")  # Línea en blanco
    
    return "\n".join(formatted)


def generate_brochure_mock(
    contents: Dict[str, str],
    company_name: str,
    base_url: str,
    tone: str = 'professional'
) -> str:
    """
    Generador MOCK: crea un folleto básico sin usar Gemini.
    
    Args:
        contents: Contenidos compilados
        company_name: Nombre de la empresa
        base_url: URL del sitio
        tone: Tono deseado
        
    Returns:
        Folleto en Markdown
    """
    logger.info("🎭 Generando folleto en modo MOCK (sin Gemini)")
    
    # Plantilla básica
    brochure = f"""# {company_name}

> Transformando el futuro con innovación y excelencia

## Acerca de Nosotros

{company_name} es una empresa líder comprometida con la innovación y la excelencia. 
Nuestra misión es proporcionar soluciones de alta calidad que impulsen el éxito de nuestros clientes.

"""
    
    # Agregar secciones disponibles
    if 'about' in contents:
        brochure += f"## Nuestra Historia\n\n{contents['about'][:500]}...\n\n"
    
    if 'products' in contents or 'services' in contents:
        key = 'products' if 'products' in contents else 'services'
        brochure += f"## Productos y Servicios\n\n{contents[key][:500]}...\n\n"
    
    if 'team' in contents:
        brochure += f"## Nuestro Equipo\n\n{contents['team'][:400]}...\n\n"
    
    if 'careers' in contents:
        brochure += f"""## Únete a Nosotro

Estamos buscando talento excepcional para unirse a nuestro equipo.

{contents['careers'][:300]}...

---

**Visita nuestro sitio web:** {base_url}

*Folleto generado automáticamente en modo MOCK*
"""
    
    logger.info(f"✅ Folleto MOCK generado: {len(brochure)} caracteres")
    return brochure


def generate_brochure(
    contents: Dict[str, str],
    company_name: str,
    base_url: str,
    tone: str = 'professional',
    max_retries: int = 2
) -> str:
    """
    Genera un folleto corporativo usando Google GenAI.
    
    Args:
        contents: Contenidos compilados por sección
        company_name: Nombre de la empresa
        base_url: URL base del sitio
        tone: Tono del folleto ('professional', 'casual', 'technical')
        max_retries: Número máximo de reintentos
        
    Returns:
        Folleto en formato Markdown
    """
    # Validar tono
    if tone not in TONES:
        logger.warning(f"Tono '{tone}' no válido, usando 'professional'")
        tone = 'professional'
    
    logger.info(f"📝 Generando folleto con tono: {TONES[tone]['name']}")
    
    # Si modo mock o sin API key
    if MOCK_MODE or not GEMINI_API_KEY:
        return generate_brochure_mock(contents, company_name, base_url, tone)
    
    # Configurar cliente
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Error configurando GenAI: {e}, usando MOCK")
        return generate_brochure_mock(contents, company_name, base_url, tone)
    
    # Cargar prompts
    system_prompt = load_prompt('brochure_system.md')
    user_template = load_prompt('brochure_user.md')
    
    # Formatear contenidos
    formatted_contents = format_compiled_contents(contents)
    
    # Preparar prompt de usuario
    user_prompt = user_template.format(
        company_name=company_name,
        base_url=base_url,
        tone=TONES[tone]['description'],
        compiled_contents=formatted_contents
    )
    
    # Intentar generar con reintentos
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"🤖 Llamando a Gemini para generar folleto (intento {attempt + 1}/{max_retries + 1})...")
            
            # Configuración de generación
            config = types.GenerateContentConfig(
                temperature=0.7,  # Más creativo que para selección de enlaces
                top_p=0.9,
                top_k=40,
                max_output_tokens=4096,  # Folleto puede ser largo
            )
            
            # Llamada al modelo
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=full_prompt,
                config=config
            )
            
            brochure = response.text.strip()
            
            # Validación básica
            if len(brochure) < 500:
                logger.warning(f"Folleto muy corto ({len(brochure)} chars), reintentando...")
                if attempt < max_retries:
                    continue
                else:
                    logger.error("Folleto demasiado corto después de reintentos, usando MOCK")
                    return generate_brochure_mock(contents, company_name, base_url, tone)
            
            # Limpiar si viene en bloque de código
            if brochure.startswith('```markdown'):
                brochure = brochure.replace('```markdown', '').replace('```', '').strip()
            elif brochure.startswith('```'):
                brochure = brochure.replace('```', '').strip()
            
            logger.info(f"✅ Folleto generado exitosamente: {len(brochure)} caracteres")
            logger.info(f"📊 Palabras aproximadas: {len(brochure.split())}")
            
            return brochure
            
        except Exception as e:
            logger.error(f"Error generando folleto: {e}")
            if attempt < max_retries:
                logger.info("Reintentando...")
                continue
            else:
                logger.error("Máximos reintentos alcanzados, usando MOCK")
                return generate_brochure_mock(contents, company_name, base_url, tone)
    
    # Fallback final
    return generate_brochure_mock(contents, company_name, base_url, tone)


def save_brochure(brochure: str, company_name: str, tone: str) -> Path:
    """
    Guarda el folleto en un archivo Markdown.
    
    Args:
        brochure: Contenido del folleto
        company_name: Nombre de la empresa
        tone: Tono usado
        
    Returns:
        Path del archivo guardado
    """
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    
    # Sanitizar nombre
    safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_').lower()
    
    filename = f"{safe_name}_brochure_{tone}.md"
    filepath = output_dir / filename
    
    # Guardar
    filepath.write_text(brochure, encoding='utf-8')
    
    logger.info(f"💾 Folleto guardado en: {filepath}")
    
    return filepath


def get_available_tones() -> Dict:
    """Retorna los tonos disponibles con sus descripciones"""
    return TONES