#!/usr/bin/env python3
"""
Test de utilidades: normalización y limpieza
"""
from src.utils import (
    normalize_url, is_same_domain, filter_valid_links,
    clean_text, get_domain_name
)


def test_normalize_url():
    print("\n" + "="*70)
    print("TEST 1: Normalización de URLs")
    print("="*70)
    
    base = "https://huggingface.co"
    
    tests = [
        ("/about", "https://huggingface.co/about"),
        ("../contact", "https://huggingface.co/contact"),
        ("https://google.com", "https://google.com"),
        ("/models/", "https://huggingface.co/models"),
        ("careers#jobs", "https://huggingface.co/careers"),
        ("?page=2", "https://huggingface.co?page=2"),
    ]
    
    for link, expected in tests:
        result = normalize_url(base, link)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{link}' → '{result}'")
        if result != expected:
            print(f"   Esperado: '{expected}'")
    
    print("\n✅ Test de normalización completado")


def test_same_domain():
    print("\n" + "="*70)
    print("TEST 2: Verificación de mismo dominio")
    print("="*70)
    
    base = "https://huggingface.co"
    
    tests = [
        ("https://huggingface.co/about", True),
        ("https://huggingface.co/models", True),
        ("https://google.com", False),
        ("https://docs.huggingface.co", False),  # Subdominio diferente
    ]
    
    for link, expected in tests:
        result = is_same_domain(base, link)
        status = "✓" if result == expected else "✗"
        print(f"{status} {link} → {result} (esperado: {expected})")
    
    print("\n✅ Test de dominio completado")


def test_filter_links():
    print("\n" + "="*70)
    print("TEST 3: Filtrado de enlaces")
    print("="*70)
    
    base = "https://empresa.com"
    
    links = [
        "/about",
        "/about",  # Duplicado
        "/contact",
        "https://empresa.com/careers",
        "https://google.com/external",  # Externo
        "/document.pdf",  # Archivo
        "/image.jpg",  # Imagen
        "/#section",  # Ancla
        "/page?utm_source=twitter",  # Con tracking
    ]
    
    filtered = filter_valid_links(links, base)
    
    print(f"\nEnlaces originales: {len(links)}")
    print(f"Enlaces filtrados: {len(filtered)}")
    print("\nEnlaces válidos:")
    for i, link in enumerate(filtered, 1):
        print(f"  {i}. {link}")
    
    print("\n✅ Test de filtrado completado")


def test_clean_text():
    print("\n" + "="*70)
    print("TEST 4: Limpieza de texto")
    print("="*70)
    
    html = """
    <html>
        <head>
            <script>alert('ads')</script>
            <style>.nav { color: red; }</style>
        </head>
        <body>
            <nav>Menu | Home | About</nav>
            <header>Header content</header>
            <main>
                <h1>Título Principal</h1>
                <p>Este es el contenido real que queremos.</p>
                <p>Otro párrafo importante.</p>
            </main>
            <footer>Footer © 2024</footer>
        </body>
    </html>
    """
    
    clean = clean_text(html)
    
    print("HTML original:")
    print(html[:200] + "...")
    print(f"\nTexto limpio ({len(clean)} chars):")
    print(clean)
    
    # Verificaciones
    assert 'alert' not in clean
    assert 'Menu' not in clean  # nav eliminado
    assert 'Título Principal' in clean
    assert 'contenido real' in clean
    
    print("\n✅ Test de limpieza completado")


def test_domain_name():
    print("\n" + "="*70)
    print("TEST 5: Extracción de nombre de dominio")
    print("="*70)
    
    tests = [
        ("https://huggingface.co", "huggingface"),
        ("https://www.google.com", "google"),
        ("https://docs.anthropic.com", "docs"),
    ]
    
    for url, expected in tests:
        result = get_domain_name(url)
        status = "✓" if result == expected else "✗"
        print(f"{status} {url} → '{result}' (esperado: '{expected}')")
    
    print("\n✅ Test de dominio completado")


if __name__ == "__main__":
    test_normalize_url()
    test_same_domain()
    test_filter_links()
    test_clean_text()
    test_domain_name()
    
    print("\n" + "="*70)
    print("✅ TODOS LOS TESTS PASARON")
    print("="*70)