# 🚀 BrochureAI

> **Generador automático de folletos corporativos impulsado por IA**

Transforma cualquier sitio web corporativo en folletos profesionales multiidioma usando web scraping inteligente y Gemini AI.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Gemini AI](https://img.shields.io/badge/Powered%20by-Gemini%20AI-4285F4.svg)](https://ai.google.dev/)

---

## ✨ Características

### 🤖 **Impulsado por IA**
- Selección inteligente de contenido relevante con **Gemini AI**
- Generación automática de folletos en 3 tonos: **Professional**, **Casual**, **Technical**
- Traducción a 6 idiomas: Español, Inglés, Francés, Alemán, Portugués, Italiano

### 🌐 **Web Scraping Inteligente**
- Scraping estático con BeautifulSoup (rápido y eficiente)
- Fallback automático a Playwright para SPAs y sitios con JavaScript pesado
- Respeto a `robots.txt` y rate limiting configurables

### 🎨 **Exportación Multi-formato**
- Markdown (editable)
- HTML con 3 temas visuales: **Claro**, **Oscuro**, **Corporativo**
- PDF (mediante impresión desde navegador)

---

## 🔧 Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/carmonaa0116/brochure-ai.git
cd brochure-ai

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
playwright install chromium

# Configurar API key
cp .env.example .env
# Editar .env y añadir tu GEMINI_API_KEY
```

---

## 🎯 Uso Rápido

```bash
# Pipeline completo en un comando
python brochure.py full https://huggingface.co --company "HuggingFace" --yes
```

**Genera automáticamente:**
- ✅ Folleto en Markdown
- ✅ Folleto en HTML (tema claro)
- ✅ Caché de contenidos reutilizable

---

## 📚 Comandos Principales

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `full` | Pipeline completo | `python brochure.py full URL --company "Empresa"` |
| `scrape` | Solo scrapear | `python brochure.py scrape URL --company "Empresa"` |
| `generate` | Generar folleto | `python brochure.py generate --company "Empresa"` |
| `export` | Exportar HTML | `python brochure.py export --company "Empresa" --theme dark` |
| `translate` | Traducir | `python brochure.py translate --company "Empresa" --target en` |

---

## 🎨 Opciones

**Tonos:** `professional`, `casual`, `technical`  
**Temas:** `light`, `dark`, `corporate`  
**Idiomas:** `es`, `en`, `fr`, `de`, `pt`, `it`

---

## 📖 Documentación

- **[Documentación Técnica Completa](DOCUMENTACION_TECNICA.md)** - Arquitectura, módulos, API
- **[Guía de GitHub](GUIA_GITHUB.md)** - Cómo subir el proyecto paso a paso
- **[Post de LinkedIn](LINKEDIN_POST.md)** - Anuncio profesional con capturas

---

## 🤝 Contribución

¡Contribuciones bienvenidas! Abre un [issue](https://github.com/carmonaa0116/brochure-ai/issues) o Pull Request.

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.

---

<div align="center">


⭐ Dale una estrella si te gusta ⭐

</div>
