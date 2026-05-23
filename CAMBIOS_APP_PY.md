# Cambios a aplicar en app.py
# Chequea360 — Integración Data360 API
# Tiempo estimado de implementación: 15 minutos

## PASO 1 — Agregar import al inicio del archivo

Buscar esta línea (ya está en app.py, línea ~5):
```python
import unicodedata
```

Agregar DEBAJO de ella:
```python
from data360_client import get_indicator_metadata, render_trace_card
```

---

## PASO 2 — Reemplazar tarjeta de trazabilidad (consulta de país, caso 1 país)

Buscar este bloque en app.py (aparece cerca de la línea 870):
```python
                    st.markdown(f"""
                    <div class="trace-card">
                        <h4>🔎 {L["source"]}</h4>
                        <p><strong>Fuente:</strong> Banco Mundial</p>
                        <p><strong>Indicador:</strong> {selected_indicator['name']}</p>
                        <p><strong>Código:</strong> {selected_indicator['code']}</p>
                        <p><strong>Países:</strong> {countries_text}</p>
                        <p><a href="https://data.worldbank.org/" target="_blank">World Bank Open Data</a></p>
                    </div>
                    """, unsafe_allow_html=True)
```

Reemplazar con:
```python
                    st.markdown(
                        render_trace_card(
                            indicator_code=selected_indicator["code"],
                            countries=[c["name"] for c in selected_countries],
                            lang=lang
                        ),
                        unsafe_allow_html=True
                    )
```

---

## PASO 3 — Reemplazar tarjeta de trazabilidad (ranking global)

Buscar este bloque (cerca de la línea 740):
```python
                    st.markdown(f"""
                    <div class="trace-card">
                        <h4>🔎 {L["source"]}</h4>
                        <p><strong>Fuente:</strong> Banco Mundial</p>
                        <p><strong>Indicador:</strong> {selected_indicator['name']}</p>
                        <p><strong>Código:</strong> {selected_indicator['code']}</p>
                        <p><strong>Tipo de consulta:</strong> Ranking global de países</p>
                        <p><a href="https://data.worldbank.org/" target="_blank">World Bank Open Data</a></p>
                    </div>
                    """, unsafe_allow_html=True)
```

Reemplazar con:
```python
                    st.markdown(
                        render_trace_card(
                            indicator_code=selected_indicator["code"],
                            countries=["Ranking global — todos los países"],
                            lang=lang
                        ),
                        unsafe_allow_html=True
                    )
```

---

## PASO 4 — Corregir el problema del ranking global lento

El ranking global actual hace una llamada a la API POR CADA PAÍS del mundo.
Esto puede tardar varios minutos o fallar durante una demo.

Buscar la función `fetch_global_ranking` y reemplazarla completa:

```python
@st.cache_data(ttl=3600)
def fetch_global_ranking(indicator_code):
    """
    Obtiene ranking global usando una sola llamada a la API WDI.
    Mucho más rápido que la versión anterior (1 llamada vs ~200).
    """
    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator_code}"
    params = {
        "format": "json",
        "per_page": 500,
        "mrv": 1,          # Most Recent Value — solo el dato más reciente por país
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if not isinstance(data, list) or len(data) < 2:
            return pd.DataFrame()

        rows = []
        for item in data[1]:
            if item.get("value") is None:
                continue
            region = item.get("country", {})
            # Excluir agregados regionales (solo países individuales)
            country_id = item.get("countryiso3code", "")
            if not country_id or len(country_id) != 3:
                continue
            try:
                rows.append({
                    "country": item["country"]["value"],
                    "code": country_id,
                    "year": int(item.get("date", 0)),
                    "value": float(item["value"]),
                })
            except Exception:
                pass

        if not rows:
            return pd.DataFrame()

        ranking_df = pd.DataFrame(rows)
        ranking_df = ranking_df.sort_values("value", ascending=False)
        ranking_df.insert(0, "rank", range(1, len(ranking_df) + 1))
        return ranking_df

    except Exception:
        return pd.DataFrame()
```

---

## VERIFICACIÓN — Cómo testear

Después de aplicar los cambios, probar estas consultas en orden:

1. `Ecuador desempleo`
   → Debe mostrar gráfico + tarjeta con "Data360 API + WDI" o "WDI API"

2. `Inflación en América Latina`
   → Debe mostrar comparación regional + tarjeta

3. `Ranking mundial de pobreza`
   → Debe cargar en menos de 10 segundos (antes podía tardar 2-3 minutos)

4. `How has GDP growth evolved in Peru?`
   → Debe responder en inglés con tarjeta en inglés

Si algo falla, el sistema tiene fallback automático — la tarjeta mostrará
los datos locales aunque la API Data360 no responda.
