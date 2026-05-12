import streamlit as st
import plotly.express as px
import pandas as pd
import requests
import unicodedata

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Chequea360",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# HELPERS
# =========================================================

def clean_text(text):
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    return "".join(
        c for c in text
        if unicodedata.category(c) != "Mn"
    )

@st.cache_data(ttl=3600)
def fetch_worldbank_data(country_code, indicator_code):

    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}"

    params = {
        "format": "json",
        "per_page": 100
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        data = response.json()

        if not isinstance(data, list) or len(data) < 2:
            return pd.DataFrame()

        rows = []

        for item in data[1]:

            if item.get("value") is not None:

                rows.append({
                    "year": int(item.get("date")),
                    "value": float(item.get("value"))
                })

        df = pd.DataFrame(rows)

        if df.empty:
            return df

        return df.sort_values("year")

    except Exception:
        return pd.DataFrame()

# =========================================================
# DESIGN
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #FAF7F2;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

.header-box {
    background: linear-gradient(135deg, #142B6F 0%, #1D3F95 100%);
    padding: 2.2rem;
    border-radius: 24px;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 8px 24px rgba(20,43,111,0.18);
}

.header-title {
    font-size: 3rem;
    font-weight: 900;
    color: #F6A300;
}

.header-subtitle {
    font-size: 1rem;
    margin-top: 1rem;
    line-height: 1.8;
}

.badge {
    display: inline-block;
    background-color: #F6A300;
    color: #142B6F;
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    font-weight: 800;
    font-size: 0.8rem;
    margin-top: 1.4rem;
}

.card {
    background: white;
    padding: 1.5rem;
    border-radius: 18px;
    box-shadow: 0 4px 16px rgba(20,43,111,0.08);
    margin-bottom: 1rem;
}

.answer-card {
    background: white;
    border-left: 8px solid #F6A300;
    padding: 1.5rem;
    border-radius: 18px;
    box-shadow: 0 4px 16px rgba(20,43,111,0.08);
    margin-bottom: 1rem;
}

.trace-card {
    background: white;
    padding: 1.5rem;
    border-radius: 18px;
    box-shadow: 0 4px 16px rgba(20,43,111,0.08);
}

.small-muted {
    color: #666;
    font-size: 0.9rem;
}

.footer {
    text-align: center;
    color: #777;
    font-size: 0.8rem;
    padding-top: 2rem;
}

.stButton > button {
    background-color: #142B6F;
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: 800;
    height: 50px;
}

.stButton > button:hover {
    background-color: #F6A300;
    color: #142B6F;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

col_logo, col_text = st.columns([1, 3])

with col_logo:
    st.image("logo.png", width=260)

with col_text:

    header_html = (
        '<div class="header-box">'

        '<div class="header-title">Chequea360</div>'

        '<div class="header-subtitle">'

        'Chequea360 es una plataforma de inteligencia informativa que integra:<br><br>'

        '• Inteligencia artificial.<br>'
        '• API Data360 del Banco Mundial.<br>'
        '• Metodologías periodísticas de verificación de datos.<br>'
        '• Capacitación y alfabetización en datos a través de ChequeaLab.<br><br>'

        'Su objetivo es permitir que periodistas, investigadores y ciudadanos '
        'puedan consultar, interpretar y validar datos de desarrollo en tiempo real.'

        '</div>'

        '<div class="badge">'
        '10 años chequeando · Periodismo con rigor · Datos verificables'
        '</div>'

        '</div>'
    )

    st.markdown(header_html, unsafe_allow_html=True)

# =========================================================
# INTRO
# =========================================================

st.markdown("""
<div class="card">

<strong>Haz preguntas en español, inglés o portugués.</strong><br><br>

<span class="small-muted">
Ejemplos:
Ecuador pobreza ·
Compara desempleo entre Ecuador y Colombia ·
¿Cuál es la inflación en América Latina? ·
What is unemployment in South America? ·
Qual é a inflação na América Latina?
</span>

</div>
""", unsafe_allow_html=True)

# =========================================================
# INPUT
# =========================================================

question = st.text_input(
    "Pregunta",
    placeholder="Ejemplo: Ecuador pobreza",
    label_visibility="collapsed"
)

# =========================================================
# COUNTRIES
# =========================================================

COUNTRIES = {
    "Argentina": "ARG",
    "Bolivia": "BOL",
    "Brasil": "BRA",
    "Chile": "CHL",
    "Colombia": "COL",
    "Costa Rica": "CRI",
    "Cuba": "CUB",
    "República Dominicana": "DOM",
    "Ecuador": "ECU",
    "El Salvador": "SLV",
    "Guatemala": "GTM",
    "Guyana": "GUY",
    "Haití": "HTI",
    "Honduras": "HND",
    "Jamaica": "JAM",
    "México": "MEX",
    "Nicaragua": "NIC",
    "Panamá": "PAN",
    "Paraguay": "PRY",
    "Perú": "PER",
    "Puerto Rico": "PRI",
    "Surinam": "SUR",
    "Trinidad y Tobago": "TTO",
    "Uruguay": "URY",
    "Venezuela": "VEN",
    "Canadá": "CAN",
    "Estados Unidos": "USA"
}

# =========================================================
# COUNTRY ALIASES
# =========================================================

COUNTRY_ALIASES = {
    "argentina": "Argentina",
    "bolivia": "Bolivia",
    "brasil": "Brasil",
    "brazil": "Brasil",
    "chile": "Chile",
    "colombia": "Colombia",
    "costa rica": "Costa Rica",
    "cuba": "Cuba",
    "republica dominicana": "República Dominicana",
    "dominican republic": "República Dominicana",
    "ecuador": "Ecuador",
    "equador": "Ecuador",
    "el salvador": "El Salvador",
    "guatemala": "Guatemala",
    "guyana": "Guyana",
    "guiana": "Guyana",
    "haiti": "Haití",
    "honduras": "Honduras",
    "jamaica": "Jamaica",
    "mexico": "México",
    "nicaragua": "Nicaragua",
    "panama": "Panamá",
    "paraguay": "Paraguay",
    "peru": "Perú",
    "puerto rico": "Puerto Rico",
    "surinam": "Surinam",
    "suriname": "Surinam",
    "trinidad y tobago": "Trinidad y Tobago",
    "trinidad and tobago": "Trinidad y Tobago",
    "uruguay": "Uruguay",
    "venezuela": "Venezuela",
    "canada": "Canadá",
    "estados unidos": "Estados Unidos",
    "united states": "Estados Unidos",
    "usa": "Estados Unidos",
    "eeuu": "Estados Unidos"
}

# =========================================================
# REGIONS
# =========================================================

SOUTH_AMERICA = [
    "Argentina", "Bolivia", "Brasil", "Chile",
    "Colombia", "Ecuador", "Guyana",
    "Paraguay", "Perú", "Surinam",
    "Uruguay", "Venezuela"
]

LATIN_AMERICA = [
    "Argentina", "Bolivia", "Brasil", "Chile",
    "Colombia", "Costa Rica", "Cuba",
    "República Dominicana", "Ecuador",
    "El Salvador", "Guatemala", "Guyana",
    "Haití", "Honduras", "Jamaica",
    "México", "Nicaragua", "Panamá",
    "Paraguay", "Perú", "Puerto Rico",
    "Surinam", "Trinidad y Tobago",
    "Uruguay", "Venezuela"
]

AMERICA = [
    "Canadá", "Estados Unidos", "México",
    "Argentina", "Bolivia", "Brasil",
    "Chile", "Colombia", "Costa Rica",
    "Cuba", "República Dominicana",
    "Ecuador", "El Salvador",
    "Guatemala", "Guyana", "Haití",
    "Honduras", "Jamaica",
    "Nicaragua", "Panamá",
    "Paraguay", "Perú",
    "Puerto Rico", "Surinam",
    "Trinidad y Tobago",
    "Uruguay", "Venezuela"
]

REGIONS = {
    "america latina": LATIN_AMERICA,
    "latinoamerica": LATIN_AMERICA,
    "latin america": LATIN_AMERICA,
    "sudamerica": SOUTH_AMERICA,
    "america del sur": SOUTH_AMERICA,
    "south america": SOUTH_AMERICA,
    "america": AMERICA,
    "the americas": AMERICA
}

# =========================================================
# INDICATORS
# =========================================================

INDICATORS = {

    "desempleo": {
        "code": "SL.UEM.TOTL.ZS",
        "name": "Tasa de desempleo"
    },

    "unemployment": {
        "code": "SL.UEM.TOTL.ZS",
        "name": "Unemployment rate"
    },

    "desemprego": {
        "code": "SL.UEM.TOTL.ZS",
        "name": "Taxa de desemprego"
    },

    "pobreza": {
        "code": "SI.POV.DDAY",
        "name": "Pobreza"
    },

    "poverty": {
        "code": "SI.POV.DDAY",
        "name": "Poverty"
    },

    "inflacion": {
        "code": "FP.CPI.TOTL.ZG",
        "name": "Inflación"
    },

    "inflation": {
        "code": "FP.CPI.TOTL.ZG",
        "name": "Inflation"
    },

    "inflacao": {
        "code": "FP.CPI.TOTL.ZG",
        "name": "Inflação"
    },

    "pib": {
        "code": "NY.GDP.MKTP.KD.ZG",
        "name": "Crecimiento del PIB"
    },

    "gdp": {
        "code": "NY.GDP.MKTP.KD.ZG",
        "name": "GDP growth"
    }
}

# =========================================================
# LANGUAGE
# =========================================================

def detect_language(q):

    en_words = [
        "what",
        "compare",
        "between",
        "unemployment",
        "inflation",
        "poverty",
        "gdp"
    ]

    pt_words = [
        "qual",
        "desemprego",
        "inflacao"
    ]

    for w in en_words:
        if w in q:
            return "en"

    for w in pt_words:
        if w in q:
            return "pt"

    return "es"

# =========================================================
# LABELS
# =========================================================

def labels(lang):

    if lang == "en":

        return {
            "answer": "Answer",
            "source": "Source and traceability",
            "data": "View data",
            "year": "Year",
            "value": "Value",
            "no_indicator": "I could not identify the indicator.",
            "no_geo": "I could not identify a country or region.",
            "no_data": "No data was found for this query."
        }

    if lang == "pt":

        return {
            "answer": "Resposta",
            "source": "Fonte e rastreabilidade",
            "data": "Ver dados",
            "year": "Ano",
            "value": "Valor",
            "no_indicator": "Não consegui identificar o indicador.",
            "no_geo": "Não consegui identificar um país ou região.",
            "no_data": "Nenhum dado foi encontrado para esta consulta."
        }

    return {
        "answer": "Respuesta",
        "source": "Fuente y trazabilidad",
        "data": "Ver datos",
        "year": "Año",
        "value": "Valor",
        "no_indicator": "No pude identificar el indicador.",
        "no_geo": "No pude identificar un país o región.",
        "no_data": "No se encontraron datos para esa consulta."
    }

# =========================================================
# BUTTON
# =========================================================

submitted = st.button(
    "🔎 Consultar datos",
    use_container_width=True
)

# =========================================================
# QUERY
# =========================================================

if submitted:

    q_original = question.strip()
    q = clean_text(q_original)

    lang = detect_language(q)
    L = labels(lang)

    selected_indicator = None
    selected_countries = []

    # Indicator

    for key, indicator in INDICATORS.items():

        if key in q:
            selected_indicator = indicator
            break

    # Region

    for region_key in sorted(
        REGIONS.keys(),
        key=len,
        reverse=True
    ):

        if region_key in q:
            selected_countries = REGIONS[region_key]
            break

    # Countries

    if not selected_countries:

        for alias, official_name in COUNTRY_ALIASES.items():

            if alias in q:

                if official_name not in selected_countries:
                    selected_countries.append(official_name)

    # =====================================================
    # ERRORS
    # =====================================================

    if not q:

        st.warning("Por favor escribe una pregunta.")

    elif selected_indicator is None:

        st.error(L["no_indicator"])

    elif not selected_countries:

        st.error(L["no_geo"])

    else:

        all_data = []

        with st.spinner(
            "Consultando datos oficiales del Banco Mundial..."
        ):

            for country in selected_countries:

                code = COUNTRIES.get(country)

                if code:

                    df = fetch_worldbank_data(
                        code,
                        selected_indicator["code"]
                    )

                    if not df.empty:

                        df["country"] = country
                        all_data.append(df)

        if not all_data:

            st.error(L["no_data"])

        else:

            final_df = pd.concat(
                all_data,
                ignore_index=True
            )

            latest_df = (
                final_df
                .sort_values("year")
                .groupby("country")
                .tail(1)
                .sort_values("value", ascending=False)
            )

            top = latest_df.iloc[0]

            top_country = top["country"]
            top_value = round(top["value"], 2)
            top_year = int(top["year"])

            # =================================================
            # ANSWER
            # =================================================

            if len(selected_countries) == 1:

                if lang == "en":

                    answer = f"""
                    According to World Bank data,
                    <strong>{selected_indicator['name']}</strong>
                    in <strong>{top_country}</strong>
                    recorded <strong>{top_value}</strong>
                    in <strong>{top_year}</strong>.
                    """

                elif lang == "pt":

                    answer = f"""
                    Segundo dados do Banco Mundial,
                    <strong>{selected_indicator['name']}</strong>
                    em <strong>{top_country}</strong>
                    registrou <strong>{top_value}</strong>
                    em <strong>{top_year}</strong>.
                    """

                else:

                    answer = f"""
                    Según datos del Banco Mundial,
                    <strong>{selected_indicator['name']}</strong>
                    en <strong>{top_country}</strong>
                    registró <strong>{top_value}</strong>
                    en <strong>{top_year}</strong>.
                    """

            else:

                if lang == "en":

                    answer = f"""
                    This query compares
                    <strong>{len(selected_countries)}</strong>
                    countries from the region.
                    The highest recent value appears in
                    <strong>{top_country}</strong>
                    with <strong>{top_value}</strong>.
                    """

                elif lang == "pt":

                    answer = f"""
                    Esta consulta compara
                    <strong>{len(selected_countries)}</strong>
                    países da região.
                    O maior valor recente aparece em
                    <strong>{top_country}</strong>
                    com <strong>{top_value}</strong>.
                    """

                else:

                    answer = f"""
                    Esta consulta compara
                    <strong>{len(selected_countries)}</strong>
                    países de la región.
                    El valor más alto reciente aparece en
                    <strong>{top_country}</strong>
                    con <strong>{top_value}</strong>.
                    """

            st.markdown(
                f'<div class="answer-card"><h3>{L["answer"]}</h3>{answer}</div>',
                unsafe_allow_html=True
            )

            # =================================================
            # CHART
            # =================================================

            if len(selected_countries) == 1:

                fig = px.line(
                    final_df,
                    x="year",
                    y="value",
                    markers=True,
                    title=f"{selected_indicator['name']} · {top_country}"
                )

            else:

                fig = px.line(
                    final_df,
                    x="year",
                    y="value",
                    color="country",
                    markers=True,
                    title=f"{selected_indicator['name']} · Comparación regional"
                )

            fig.update_layout(
                xaxis_title=L["year"],
                yaxis_title=L["value"],
                height=550
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # =================================================
            # DATA
            # =================================================

            col1, col2 = st.columns([1, 1])

            with col1:

                with st.expander(L["data"]):
                    st.dataframe(final_df)

            with col2:

                countries_text = ", ".join(selected_countries)

                st.markdown(f"""
                <div class="trace-card">

                <h4>🔎 {L["source"]}</h4>

                <p>
                <strong>Fuente:</strong>
                Banco Mundial
                </p>

                <p>
                <strong>Indicador:</strong>
                {selected_indicator['name']}
                </p>

                <p>
                <strong>Código:</strong>
                {selected_indicator['code']}
                </p>

                <p>
                <strong>Países:</strong>
                {countries_text}
                </p>

                <p>
                <a href="https://data.worldbank.org/" target="_blank">
                World Bank Open Data
                </a>
                </p>

                </div>
                """, unsafe_allow_html=True)

# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
Chequea360 · Ecuador Chequea · ChequeaLab · Datos oficiales del Banco Mundial
</div>
""", unsafe_allow_html=True)