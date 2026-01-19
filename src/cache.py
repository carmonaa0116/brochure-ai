"""
Sistema simple de caché para HTML descargado
"""
import hashlib
import os
from pathlib import Path

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_path(url: str) -> Path:
    """Genera path único para una URL"""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return CACHE_DIR / f"{url_hash}.html"


def get_cached_html(url: str) -> str | None:
    """Obtiene HTML del caché si existe"""
    cache_path = get_cache_path(url)
    if cache_path.exists():
        return cache_path.read_text(encoding='utf-8')
    return None


def save_to_cache(url: str, html: str):
    """Guarda HTML en caché"""
    cache_path = get_cache_path(url)
    cache_path.write_text(html, encoding='utf-8')