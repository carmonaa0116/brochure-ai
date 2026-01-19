"""
Sistema de traducción de folletos con Google GenAI
"""
import logging
from typing import Optional, Dict
from pathlib import Path
from dotenv import load_dotenv
import os
import re

from google import genai
from google.genai import types

load_dotenv()
logger = logging.getLogger(__name__)

# Configuración
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
MOCK_MODE = os.getenv('MOCK_MODE', 'false').lower() == 'true'

# Idiomas soportados
LANGUAGES = {
    'es': {
        'name': 'Español',
        'native': 'Español',
        'formal_tone': 'formal y profesional',
        'casual_tone': 'amigable y cercano'
    },
    'en': {
        'name': 'English',
        'native': 'English',
        'formal_tone': 'professional and formal',
        'casual_tone': 'friendly and approachable'
    },
    'fr': {
        'name': 'Français',
        'native': 'Français',
        'formal_tone': 'formel et professionnel',
        'casual_tone': 'amical et accessible'
    },
    'de': {
        'name': 'Deutsch',
        'native': 'Deutsch',
        'formal_tone': 'formell und professionell',
        'casual_tone': 'freundlich und zugänglich'
    },
    'pt': {
        'name': 'Português',
        'native': 'Português',
        'formal_tone': 'formal e profissional',
        'casual_tone': 'amigável e acessível'
    },
    'it': {
        'name': 'Italiano',
        'native': 'Italiano',
        'formal_tone': 'formale e professionale',
        'casual_tone': 'amichevole e accessibile'
    }
}


def load_prompt(filename: str) -> str:
    """Carga un prompt desde la carpeta prompts/"""
    prompt_path = Path('prompts') / filename
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt no encontrado: {prompt_path}")
    return prompt_path.read_text(encoding='utf-8')


def detect_language(text: str) -> str:
    """
    Detecta el idioma del texto (simple heurística).
    
    Args:
        text: Texto a analizar
        
    Returns:
        Código de idioma ('es', 'en', etc.)
    """
    # Palabras comunes por idioma
    indicators = {
        'es': ['empresa', 'sobre', 'nosotros', 'servicios', 'contacto', 'nuestra'],
        'en': ['company', 'about', 'services', 'contact', 'our', 'team'],
        'fr': ['entreprise', 'propos', 'services', 'contact', 'notre', 'équipe'],
        'de': ['unternehmen', 'über', 'dienstleistungen', 'kontakt', 'unser', 'team'],
        'pt': ['empresa', 'sobre', 'serviços', 'contato', 'nossa', 'equipe'],
        'it': ['azienda', 'chi siamo', 'servizi', 'contatto', 'nostra', 'team']
    }
    
    text_lower = text.lower()[:2000]  # Primeros 2000 caracteres
    
    scores = {}
    for lang, words in indicators.items():
        score = sum(1 for word in words if word in text_lower)
        scores[lang] = score
    
    # Idioma con más coincidencias
    detected = max(scores, key=scores.get)
    
    logger.info(f"🔍 Idioma detectado: {LANGUAGES[detected]['name']} (confianza: {scores[detected]}/6)")
    
    return detected


def translate_mock(
    brochure: str,
    source_lang: str,
    target_lang: str,
    tone: str = 'professional'
) -> str:
    """
    Traductor MOCK: simula traducción sin usar Gemini.
    Solo añade un prefijo indicando el idioma.
    
    Args:
        brochure: Texto del folleto en Markdown
        source_lang: Código de idioma origen
        target_lang: Código de idioma destino
        tone: Tono de traducción
        
    Returns:
        Texto "traducido" (mock)
    """
    logger.info(f"🎭 Usando traductor MOCK")
    
    # Extraer el título (primera línea con #)
    lines = brochure.split('\n')
    title_line = next((line for line in lines if line.startswith('#')), '# Company')
    title = title_line.replace('#', '').strip()
    
    mock_translation = f"""# {title} [{LANGUAGES[target_lang]['name']}]

> [TRADUCCIÓN MOCK - Este es el folleto original con encabezado modificado]
> Idioma: {source_lang} → {target_lang}
> Tono: {tone}

---

{brochure}

---

*Nota: Esta es una traducción simulada (MOCK MODE). 
Para traducción real, configura GEMINI_API_KEY en el archivo .env*
"""
    
    logger.info(f"✅ Traducción MOCK generada: {len(mock_translation)} caracteres")
    
    return mock_translation


def translate_brochure(
    brochure: str,
    target_lang: str,
    source_lang: Optional[str] = None,
    tone: str = 'professional',
    max_retries: int = 2
) -> str:
    """
    Traduce un folleto a otro idioma usando Google GenAI.
    
    Args:
        brochure: Texto del folleto en Markdown
        target_lang: Código del idioma destino ('en', 'fr', 'de', etc.)
        source_lang: Código del idioma origen (None = detectar automáticamente)
        tone: Tono de la traducción ('professional' o 'casual')
        max_retries: Número de reintentos
        
    Returns:
        Folleto traducido en Markdown
    """
    # Validar idioma destino
    if target_lang not in LANGUAGES:
        logger.error(f"Idioma '{target_lang}' no soportado")
        logger.info(f"Idiomas disponibles: {', '.join(LANGUAGES.keys())}")
        raise ValueError(f"Idioma no soportado: {target_lang}")
    
    # Detectar idioma origen si no se especifica
    if source_lang is None:
        source_lang = detect_language(brochure)
    
    # Validar que no sea el mismo idioma
    if source_lang == target_lang:
        logger.warning(f"El idioma origen y destino son el mismo ({source_lang})")
        return brochure
    
    logger.info(f"🌍 Traduciendo: {LANGUAGES[source_lang]['name']} → {LANGUAGES[target_lang]['name']}")
    logger.info(f"📝 Tono: {tone}")
    
    # Si modo mock o sin API key
    if MOCK_MODE or not GEMINI_API_KEY:
        return translate_mock(brochure, source_lang, target_lang, tone)
    
    # Configurar cliente
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Error configurando GenAI: {e}, usando MOCK")
        return translate_mock(brochure, source_lang, target_lang, tone)
    
    # Cargar prompts
    system_prompt = load_prompt('translation_system.md')
    user_template = load_prompt('translation_user.md')
    
    # Determinar descripción del tono
    tone_key = 'formal_tone' if tone == 'professional' else 'casual_tone'
    tone_description = LANGUAGES[target_lang][tone_key]
    
    # Preparar prompt de usuario
    user_prompt = user_template.format(
        source_language=LANGUAGES[source_lang]['native'],
        target_language=LANGUAGES[target_lang]['native'],
        tone_description=tone_description,
        brochure_content=brochure
    )
    
    # Intentar traducir con reintentos
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"🤖 Llamando a Gemini para traducir (intento {attempt + 1}/{max_retries + 1})...")
            
            # Configuración de generación
            config = types.GenerateContentConfig(
                temperature=0.3,  # Baja temperatura para traducciones consistentes
                top_p=0.9,
                top_k=40,
                max_output_tokens=8192,  # Las traducciones pueden ser largas
            )
            
            # Llamada al modelo
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=full_prompt,
                config=config
            )
            
            translated = response.text.strip()
            
            # Validación básica
            if len(translated) < len(brochure) * 0.5:
                logger.warning(f"Traducción muy corta ({len(translated)} chars vs {len(brochure)} original)")
                if attempt < max_retries:
                    logger.info("Reintentando...")
                    continue
                else:
                    logger.error("Traducción demasiado corta después de reintentos")
                    return translate_mock(brochure, source_lang, target_lang, tone)
            
            # Limpiar si viene en bloque de código
            if translated.startswith('```markdown'):
                translated = translated.replace('```markdown', '').replace('```', '').strip()
            elif translated.startswith('```'):
                translated = translated.replace('```', '').strip()
            
            # Validar que preserva Markdown
            original_headings = brochure.count('#')
            translated_headings = translated.count('#')
            
            if original_headings > 0 and translated_headings == 0:
                logger.warning("⚠️ La traducción perdió los encabezados Markdown")
                if attempt < max_retries:
                    logger.info("Reintentando...")
                    continue
            
            logger.info(f"✅ Traducción completada: {len(translated)} caracteres")
            logger.info(f"📊 Ratio de longitud: {len(translated)/len(brochure):.2f}x")
            
            return translated
            
        except Exception as e:
            logger.error(f"Error en traducción: {e}")
            if attempt < max_retries:
                logger.info("Reintentando...")
                continue
            else:
                logger.error("Máximos reintentos alcanzados, usando MOCK")
                return translate_mock(brochure, source_lang, target_lang, tone)
    
    # Fallback final
    return translate_mock(brochure, source_lang, target_lang, tone)


def save_translated_brochure(
    translated: str,
    company_name: str,
    target_lang: str,
    tone: str = 'professional'
) -> Path:
    """
    Guarda el folleto traducido.
    
    Args:
        translated: Texto traducido
        company_name: Nombre de la empresa
        target_lang: Código del idioma
        tone: Tono usado
        
    Returns:
        Path del archivo guardado
    """
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    
    # Sanitizar nombre
    safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_').lower()
    
    filename = f"{safe_name}_brochure_{tone}_{target_lang}.md"
    filepath = output_dir / filename
    
    # Guardar
    filepath.write_text(translated, encoding='utf-8')
    
    logger.info(f"💾 Traducción guardada en: {filepath}")
    
    return filepath


def get_available_languages() -> Dict:
    """Retorna los idiomas disponibles"""
    return LANGUAGES