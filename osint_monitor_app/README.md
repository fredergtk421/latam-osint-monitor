# LATAM OSINT Monitor — MVP

MVP local para monitorear eventos OSINT desde periódicos, RSS y GDELT.

Está pensado como una primera versión segura: no necesita claves API, no modifica nada fuera de su propia carpeta y guarda resultados en una base SQLite local.

## Qué hace

- Lee fuentes RSS configuradas en `config/sources.yml`.
- Consulta GDELT 2.1 por eventos/noticias recientes.
- Normaliza eventos en una tabla SQLite.
- Clasifica eventos por tipo: protesta, bloqueo, violencia, crimen organizado, ciber, elección, desastre natural, infraestructura, logística, seguridad corporativa.
- Calcula severidad y confianza básica.
- Deduplica eventos similares.
- Muestra un dashboard con Streamlit.
- Permite generar un resumen tipo alerta analítica.

## Instalación rápida

```bash
cd osint_monitor_app
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Primer uso

```bash
python scripts/ingest.py
streamlit run app/dashboard.py
```

## Estructura

```text
app/
  classifier.py      # clasificación, severidad y confianza
  database.py        # SQLite
  gdelt.py           # conector GDELT
  rss.py             # conector RSS
  models.py          # estructura común de eventos
  dashboard.py       # interfaz Streamlit
config/
  sources.yml        # fuentes RSS y consultas GDELT
scripts/
  ingest.py          # ejecución manual de ingesta
```

## Cómo ampliar fuentes

Edita `config/sources.yml` y agrega feeds RSS.

Ejemplo:

```yaml
rss_feeds:
  - name: Medio Local
    country: Peru
    url: https://example.com/rss
```

## Próximos pasos recomendados

1. Validar si las fuentes realmente devuelven RSS activo.
2. Agregar más medios locales por país.
3. Reemplazar scoring básico por reglas analíticas propias.
4. Agregar alertas Telegram o email.
5. Agregar un LLM para redactar alertas con criterio de analista.

## Nota de seguridad

Este MVP solo escribe dentro de su carpeta, en `data/osint_events.sqlite3`.
No pide credenciales, no lee tus documentos personales y no requiere acceso completo al disco.
