"""
data360_client.py
Chequea360 — Ecuador Chequea / ChequeaLab

Módulo de integración con la API Data360 del Banco Mundial.
Obtiene metadatos enriquecidos de indicadores directamente desde
data360.worldbank.org para complementar los datos WDI.

Uso:
    from data360_client import get_indicator_metadata
    meta = get_indicator_metadata("SL.UEM.TOTL.ZS")
"""

import requests
import streamlit as st

# ─── Configuración ────────────────────────────────────────────────────────────

DATA360_BASE = "https://data360api.worldbank.org/v1"
WDI_BASE     = "https://api.worldbank.org/v2"
TIMEOUT      = 10  # segundos

# ─── Mapa de indicadores ──────────────────────────────────────────────────────
# Códigos WDI → IDs en Data360 (database_id siempre "WDI" para estos indicadores)
# El database_id "WDI" es el mismo en ambas APIs.

INDICATOR_META = {
    "SL.UEM.TOTL.ZS": {
        "database_id": "WDI",
        "name_es": "Tasa de desempleo (% de la fuerza laboral total)",
        "name_en": "Unemployment, total (% of total labor force)",
        "name_pt": "Desemprego total (% da força de trabalho total)",
        "theme":   "People",
        "source":  "ILO, ILOSTAT",
    },
    "SI.POV.DDAY": {
        "database_id": "WDI",
        "name_es": "Pobreza (% de personas con menos de $2.15/día)",
        "name_en": "Poverty headcount ratio at $2.15 a day (2017 PPP)",
        "name_pt": "Taxa de pobreza a $2,15 por dia (PPC 2017)",
        "theme":   "People",
        "source":  "World Bank PovcalNet",
    },
    "FP.CPI.TOTL.ZG": {
        "database_id": "WDI",
        "name_es": "Inflación, precios al consumidor (% anual)",
        "name_en": "Inflation, consumer prices (annual %)",
        "name_pt": "Inflação, preços ao consumidor (% anual)",
        "theme":   "Prosperity",
        "source":  "IMF, International Financial Statistics",
    },
    "NY.GDP.MKTP.KD.ZG": {
        "database_id": "WDI",
        "name_es": "Crecimiento del PIB (% anual)",
        "name_en": "GDP growth (annual %)",
        "name_pt": "Crescimento do PIB (% anual)",
        "theme":   "Prosperity",
        "source":  "World Bank national accounts / OECD",
    },
}

# ─── Función principal ────────────────────────────────────────────────────────

@st.cache_data(ttl=86400)
def get_indicator_metadata(indicator_code: str, lang: str = "es") -> dict:
    """
    Retorna metadatos enriquecidos de un indicador.

    Intenta primero la API Data360; si falla, usa el mapa local
    como fallback garantizado. Nunca lanza excepción.

    Args:
        indicator_code: código WDI (ej. "SL.UEM.TOTL.ZS")
        lang: idioma de respuesta ("es", "en", "pt")

    Returns:
        dict con campos: name, database_id, theme, source,
                         data360_url, wdi_url, api_used
    """
    local = INDICATOR_META.get(indicator_code, {})

    # Nombre localizado desde el mapa local
    name_key = f"name_{lang}" if lang in ("es", "en", "pt") else "name_es"
    local_name = local.get(name_key, indicator_code)

    # Intentar API Data360 para metadatos adicionales
    data360_meta = _fetch_data360_metadata(indicator_code)

    if data360_meta:
        return {
            "name":         data360_meta.get("name", local_name),
            "description":  data360_meta.get("description", ""),
            "database_id":  local.get("database_id", "WDI"),
            "theme":        local.get("theme", ""),
            "source":       data360_meta.get("source", local.get("source", "World Bank")),
            "last_updated": data360_meta.get("last_updated", ""),
            "data360_url":  f"https://data360.worldbank.org/en/indicator/{indicator_code}",
            "wdi_url":      f"https://data.worldbank.org/indicator/{indicator_code}",
            "api_used":     "Data360 API + WDI",
        }
    else:
        # Fallback local — siempre funciona
        return {
            "name":         local_name,
            "description":  "",
            "database_id":  local.get("database_id", "WDI"),
            "theme":        local.get("theme", ""),
            "source":       local.get("source", "World Bank"),
            "last_updated": "",
            "data360_url":  f"https://data360.worldbank.org/en/indicator/{indicator_code}",
            "wdi_url":      f"https://data.worldbank.org/indicator/{indicator_code}",
            "api_used":     "WDI API",
        }


def _fetch_data360_metadata(indicator_code: str) -> dict | None:
    """
    Llama a la API Data360 para obtener metadatos del indicador.
    Retorna dict con datos o None si falla.
    """
    try:
        url = f"{DATA360_BASE}/metadata"
        params = {
            "database_id":   "WDI",
            "indicator_id":  indicator_code,
        }
        response = requests.get(url, params=params, timeout=TIMEOUT)

        if response.status_code != 200:
            return None

        data = response.json()

        # La API Data360 retorna una lista de resultados
        if not isinstance(data, list) or len(data) == 0:
            return None

        item = data[0]
        return {
            "name":         item.get("indicator_name", ""),
            "description":  item.get("long_definition", ""),
            "source":       item.get("source", ""),
            "last_updated": item.get("last_updated_date", ""),
        }

    except Exception:
        return None


# ─── Función auxiliar para renderizar la tarjeta de trazabilidad ──────────────

def render_trace_card(indicator_code: str, countries: list, lang: str = "es") -> str:
    """
    Genera el HTML de la tarjeta de fuente y trazabilidad.
    Usa metadata enriquecida de Data360 cuando está disponible.

    Args:
        indicator_code: código WDI del indicador
        countries: lista de nombres de países consultados
        lang: idioma ("es", "en", "pt")

    Returns:
        str HTML listo para st.markdown(..., unsafe_allow_html=True)
    """
    meta = get_indicator_metadata(indicator_code, lang)

    labels = {
        "es": {
            "title":    "Fuente y trazabilidad",
            "source":   "Fuente",
            "indicator":"Indicador",
            "code":     "Código",
            "database": "Base de datos",
            "theme":    "Área temática",
            "countries":"Países consultados",
            "api":      "API utilizada",
            "see_d360": "Ver en Data360",
            "see_wdi":  "Ver en World Bank Open Data",
        },
        "en": {
            "title":    "Source and traceability",
            "source":   "Source",
            "indicator":"Indicator",
            "code":     "Code",
            "database": "Database",
            "theme":    "Theme",
            "countries":"Countries queried",
            "api":      "API used",
            "see_d360": "View on Data360",
            "see_wdi":  "View on World Bank Open Data",
        },
        "pt": {
            "title":    "Fonte e rastreabilidade",
            "source":   "Fonte",
            "indicator":"Indicador",
            "code":     "Código",
            "database": "Base de dados",
            "theme":    "Área temática",
            "countries":"Países consultados",
            "api":      "API utilizada",
            "see_d360": "Ver no Data360",
            "see_wdi":  "Ver no World Bank Open Data",
        },
    }.get(lang, {})

    countries_text = ", ".join(countries) if countries else "—"

    theme_row = (
        f'<p><strong>{labels["theme"]}:</strong> {meta["theme"]}</p>'
        if meta.get("theme") else ""
    )

    updated_row = (
        f'<p><strong>Última actualización:</strong> {meta["last_updated"]}</p>'
        if meta.get("last_updated") else ""
    )

    html = f"""
    <div class="trace-card">
        <h4>🔎 {labels['title']}</h4>
        <p><strong>{labels['source']}:</strong> {meta['source']}</p>
        <p><strong>{labels['indicator']}:</strong> {meta['name']}</p>
        <p><strong>{labels['code']}:</strong> {indicator_code}</p>
        <p><strong>{labels['database']}:</strong> {meta['database_id']} — World Bank Data360</p>
        {theme_row}
        <p><strong>{labels['countries']}:</strong> {countries_text}</p>
        <p><strong>{labels['api']}:</strong> {meta['api_used']}</p>
        {updated_row}
        <p>
            <a href="{meta['data360_url']}" target="_blank">{labels['see_d360']}</a>
            &nbsp;·&nbsp;
            <a href="{meta['wdi_url']}" target="_blank">{labels['see_wdi']}</a>
        </p>
    </div>
    """
    return html
