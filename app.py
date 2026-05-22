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
    page_icon="favicon.png",
    layout="wide"
)
params = st.query_params

modo_embed = (
    params.get("embed")
    == "1"
)

# =========================================================
# HELPERS
# =========================================================

def clean_text(text):
    text = str(text).lower().strip()
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


@st.cache_data(ttl=3600)
def fetch_worldbank_data(country_code, indicator_code):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}"
    params = {"format": "json", "per_page": 100}

    try:
        response = requests.get(url, params=params, timeout=20)
        data = response.json()

        if not isinstance(data, list) or len(data) < 2:
            return pd.DataFrame()

        rows = []

        for item in data[1]:
            if item.get("value") is not None:
                try:
                    rows.append({
                        "year": int(item.get("date")),
                        "value": float(item.get("value"))
                    })
                except Exception:
                    pass

        df = pd.DataFrame(rows)

        if df.empty:
            return df

        return df.sort_values("year")

    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=86400)
def fetch_worldbank_countries():
    url = "https://api.worldbank.org/v2/country"
    params = {"format": "json", "per_page": 400}

    try:
        response = requests.get(url, params=params, timeout=20)
        data = response.json()

        if not isinstance(data, list) or len(data) < 2:
            return []

        countries = []

        for item in data[1]:
            region = item.get("region", {}).get("value", "")

            if region and region != "Aggregates":
                countries.append({
                    "name": item.get("name"),
                    "code": item.get("id")
                })

        return countries

    except Exception:
        return []


@st.cache_data(ttl=3600)
def fetch_global_ranking(indicator_code):
    countries = fetch_worldbank_countries()
    rows = []

    for country in countries:
        df = fetch_worldbank_data(country["code"], indicator_code)

        if not df.empty:
            latest = df.iloc[-1]

            try:
                value = float(latest["value"])
                year = int(latest["year"])

                rows.append({
                    "country": country["name"],
                    "code": country["code"],
                    "year": year,
                    "value": value
                })

            except Exception:
                pass

    ranking_df = pd.DataFrame(rows)

    if ranking_df.empty:
        return ranking_df

    ranking_df = ranking_df.sort_values("value", ascending=False)
    ranking_df.insert(0, "rank", range(1, len(ranking_df) + 1))

    return ranking_df


def build_country_aliases():
    aliases = {}

    for country in fetch_worldbank_countries():
        name = country["name"]
        code = country["code"]

        if name and code:
            aliases[clean_text(name)] = {
                "name": name,
                "code": code
            }

    manual_aliases = {
        # América Latina y Caribe
        "argentina": ("Argentina", "ARG"),
        "bolivia": ("Bolivia", "BOL"),
        "brasil": ("Brasil", "BRA"),
        "brazil": ("Brasil", "BRA"),
        "chile": ("Chile", "CHL"),
        "colombia": ("Colombia", "COL"),
        "costa rica": ("Costa Rica", "CRI"),
        "cuba": ("Cuba", "CUB"),
        "republica dominicana": ("República Dominicana", "DOM"),
        "dominican republic": ("República Dominicana", "DOM"),
        "ecuador": ("Ecuador", "ECU"),
        "equador": ("Ecuador", "ECU"),
        "el salvador": ("El Salvador", "SLV"),
        "guatemala": ("Guatemala", "GTM"),
        "guyana": ("Guyana", "GUY"),
        "guiana": ("Guyana", "GUY"),
        "haiti": ("Haití", "HTI"),
        "honduras": ("Honduras", "HND"),
        "jamaica": ("Jamaica", "JAM"),
        "mexico": ("México", "MEX"),
        "nicaragua": ("Nicaragua", "NIC"),
        "panama": ("Panamá", "PAN"),
        "paraguay": ("Paraguay", "PRY"),
        "peru": ("Perú", "PER"),
        "puerto rico": ("Puerto Rico", "PRI"),
        "surinam": ("Surinam", "SUR"),
        "suriname": ("Surinam", "SUR"),
        "trinidad y tobago": ("Trinidad y Tobago", "TTO"),
        "trinidad and tobago": ("Trinidad y Tobago", "TTO"),
        "uruguay": ("Uruguay", "URY"),
        "venezuela": ("Venezuela", "VEN"),

        # Norteamérica
        "canada": ("Canadá", "CAN"),
        "estados unidos": ("Estados Unidos", "USA"),
        "united states": ("Estados Unidos", "USA"),
        "usa": ("Estados Unidos", "USA"),
        "eeuu": ("Estados Unidos", "USA"),

        # Europa
        "alemania": ("Alemania", "DEU"),
        "germany": ("Alemania", "DEU"),
        "suecia": ("Suecia", "SWE"),
        "sweden": ("Suecia", "SWE"),
        "inglaterra": ("Reino Unido", "GBR"),
        "reino unido": ("Reino Unido", "GBR"),
        "united kingdom": ("Reino Unido", "GBR"),
        "uk": ("Reino Unido", "GBR"),
        "gran bretana": ("Reino Unido", "GBR"),
        "francia": ("Francia", "FRA"),
        "france": ("Francia", "FRA"),
        "espana": ("España", "ESP"),
        "spain": ("España", "ESP"),
        "italia": ("Italia", "ITA"),
        "italy": ("Italia", "ITA"),
        "portugal": ("Portugal", "PRT"),
        "ucrania": ("Ucrania", "UKR"),
        "ukraine": ("Ucrania", "UKR"),
        "rusia": ("Rusia", "RUS"),
        "russia": ("Rusia", "RUS"),

        # Asia y Oceanía
        "japon": ("Japón", "JPN"),
        "japan": ("Japón", "JPN"),
        "china": ("China", "CHN"),
        "india": ("India", "IND"),
        "corea del sur": ("Corea del Sur", "KOR"),
        "south korea": ("Corea del Sur", "KOR"),
        "corea": ("Corea del Sur", "KOR"),
        "australia": ("Australia", "AUS"),
        "nueva zelanda": ("Nueva Zelanda", "NZL"),
        "new zealand": ("Nueva Zelanda", "NZL"),

        # África y Medio Oriente
        "sudafrica": ("Sudáfrica", "ZAF"),
        "south africa": ("Sudáfrica", "ZAF"),
        "egipto": ("Egipto", "EGY"),
        "egypt": ("Egipto", "EGY"),
        "turquia": ("Turquía", "TUR"),
        "turkey": ("Turquía", "TUR"),
        "turkiye": ("Turquía", "TUR")
    }

    for alias, data in manual_aliases.items():
        aliases[clean_text(alias)] = {
            "name": data[0],
            "code": data[1]
        }

    return aliases


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
    padding: 2rem;
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
    line-height: 1.6;
}

.badge {
    display: inline-block;
    background-color: #F6A300;
    color: #142B6F;
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    font-weight: 800;
    font-size: 0.8rem;
    margin-top: 1.2rem;
}

.card {
    background: white;
    padding: 18px 22px;
    border-radius: 18px;
    box-shadow: 0 4px 16px rgba(20,43,111,0.08);
    margin-bottom: 1rem;
    line-height: 1.5;
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
    color: #555;
    font-size: 0.95rem;
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

if not modo_embed:

    col_logo, col_text = st.columns([1, 3])

    with col_logo:
        st.image("logo.png", width=260)

    with col_text:
        header_html = (
            '<div class="header-box">'
            '<div class="header-title">Chequea360</div>'
            '<div class="header-subtitle">'
            'Chequea360 es una plataforma de inteligencia informativa que integra inteligencia artificial, '
            'la API Data360 del Banco Mundial, metodologías periodísticas de verificación de datos y procesos '
            'de capacitación y alfabetización en datos a través de ChequeaLab.<br><br>'
            'Su objetivo es permitir que periodistas, investigadores y ciudadanos '
            'puedan consultar, interpretar y validar datos de desarrollo en tiempo real.'
            '</div>'
            '<div class="badge">10 años chequeando · Periodismo con rigor · Datos verificables</div>'
            '</div>'
        )

        st.markdown(header_html, unsafe_allow_html=True)
# =========================================================
# INTRO
# =========================================================

if not modo_embed:

    st.markdown("""
<div class="card">

<p style="margin:0; font-size:1.05rem; font-weight:700; color:#1f1f1f;">
Consulta indicadores económicos y sociales oficiales.
</p>

<p style="margin-top:10px; margin-bottom:8px;" class="small-muted">
Chequea360 permite buscar, comparar e interpretar datos oficiales del Banco Mundial sobre PIB, crecimiento económico, inflación, desempleo, pobreza, desarrollo económico y social, así como comparaciones entre países, regiones y rankings globales.
</p>

<p style="margin:0;" class="small-muted">
<strong>Ejemplos:</strong> Ecuador pobreza · Inflación en América Latina · Compara desempleo entre Ecuador y Colombia · Alemania inflación · Suecia desempleo · ¿Cuál es el PIB de Japón? · Ranking mundial de inflación · Global ranking of unemployment
</p>

</div>
""", unsafe_allow_html=True)
# =========================================================
# INPUT
# =========================================================

question = st.text_input(
    "Pregunta",
    placeholder="Escribe tu pregunta aquí:",
    label_visibility="collapsed"
)

# =========================================================
# COUNTRIES AND REGIONS
# =========================================================

COUNTRY_ALIASES = build_country_aliases()

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
        "gdp",
        "global ranking",
        "world ranking",
        "all countries"
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


def is_global_query(q):
    global_words = [
        "ranking mundial",
        "ranking global",
        "global",
        "mundial",
        "mundo",
        "todos los paises",
        "todos los países",
        "todos los paises del mundo",
        "todos los países del mundo",
        "all countries",
        "world ranking",
        "global ranking",
        "ranking do mundo",
        "todos os paises",
        "todos os países"
    ]

    for word in global_words:
        if word in q:
            return True

    return False

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
            "no_data": "No data was found for this query.",
            "ranking_title": "Global ranking",
            "top_chart": "Top 30 countries"
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
            "no_data": "Nenhum dado foi encontrado para esta consulta.",
            "ranking_title": "Ranking global",
            "top_chart": "Top 30 países"
        }

    return {
        "answer": "Respuesta",
        "source": "Fuente y trazabilidad",
        "data": "Ver datos",
        "year": "Año",
        "value": "Valor",
        "no_indicator": "No pude identificar el indicador.",
        "no_geo": "No pude identificar un país o región.",
        "no_data": "No se encontraron datos para esa consulta.",
        "ranking_title": "Ranking global",
        "top_chart": "Top 30 países"
    }
def mostrar_compartir(question):

    import urllib.parse

    base_url = "https://chequea360.streamlit.app/"

    pregunta = question.strip()

    share_url = (
    base_url
    + "?q="
    + urllib.parse.quote(pregunta)
    + "&embed=1"
)


    embed_code = f"""
<iframe
src="{share_url}"
width="100%"
height="640"
style="
border:0;
border-radius:16px;
background:white;
overflow:hidden;">
</iframe>
"""

    mensaje = (
        f"{pregunta}\n\n"
        f"Míralo en Chequea360:\n"
        f"{share_url}"
    )

    st.markdown("## Compartir o incrustar")

    tab1, tab2 = st.tabs([
        "Insertar en web",
        "Compartir"
    ])

    with tab1:

        st.code(
            embed_code,
            language="html"
        )

    with tab2:

        st.text_area(
            "Mensaje",
            mensaje,
            height=120
        )

        c1,c2,c3,c4,c5 = st.columns(5)

        with c1:
            st.link_button(
                "WhatsApp",
                "https://wa.me/?text="
                + urllib.parse.quote(mensaje)
            )

        with c2:
            st.link_button(
                "X",
                "https://twitter.com/intent/tweet?text="
                + urllib.parse.quote(mensaje)
            )

        with c3:
            st.link_button(
                "Facebook",
                "https://www.facebook.com/sharer/sharer.php?u="
                + urllib.parse.quote(share_url)
            )

        with c4:
            st.link_button(
                "LinkedIn",
                "https://www.linkedin.com/sharing/share-offsite/?url="
                + urllib.parse.quote(share_url)
            )

        with c5:
            st.link_button(
                "Telegram",
                "https://t.me/share/url?url="
                + urllib.parse.quote(share_url)
            )
# =========================================================
# BUTTON
# =========================================================

submitted = st.button(
    "📊 Consultar datos",
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
    global_query = is_global_query(q)

    for key, indicator in INDICATORS.items():
        if key in q:
            selected_indicator = indicator
            break

    if not q:
        st.warning("Por favor escribe una pregunta.")

    elif selected_indicator is None:
        st.error(L["no_indicator"])

    elif global_query:

        with st.spinner("Construyendo ranking global con datos oficiales del Banco Mundial..."):
            ranking_df = fetch_global_ranking(
                selected_indicator["code"]
            )

        if ranking_df.empty:
            st.error(L["no_data"])

        else:
            top_country = ranking_df.iloc[0]["country"]
            top_value = round(ranking_df.iloc[0]["value"], 2)
            top_year = int(ranking_df.iloc[0]["year"])
            total_countries = len(ranking_df)

            if lang == "en":
                answer = f"""
                This global ranking includes <strong>{total_countries}</strong> countries with available data.
                The highest recent value for <strong>{selected_indicator['name']}</strong> appears in
                <strong>{top_country}</strong>, with <strong>{top_value}</strong> in <strong>{top_year}</strong>.
                """
            elif lang == "pt":
                answer = f"""
                Este ranking global inclui <strong>{total_countries}</strong> países com dados disponíveis.
                O maior valor recente para <strong>{selected_indicator['name']}</strong> aparece em
                <strong>{top_country}</strong>, com <strong>{top_value}</strong> em <strong>{top_year}</strong>.
                """
            else:
                answer = f"""
                Este ranking global incluye <strong>{total_countries}</strong> países con datos disponibles.
                El valor reciente más alto para <strong>{selected_indicator['name']}</strong> aparece en
                <strong>{top_country}</strong>, con <strong>{top_value}</strong> en <strong>{top_year}</strong>.
                """

            st.markdown(
                f'<div class="answer-card"><h3>{L["ranking_title"]}</h3>{answer}</div>',
                unsafe_allow_html=True
            )

            top_30 = ranking_df.head(30).sort_values("value", ascending=True)

            fig = px.bar(
                top_30,
                x="value",
                y="country",
                orientation="h",
                title=f"{selected_indicator['name']} · {L['top_chart']}",
                labels={
                    "value": L["value"],
                    "country": "País"
                }
            )

            fig.update_layout(
                height=750,
                xaxis_title=L["value"],
                yaxis_title=""
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
            mostrar_compartir(question)

            col1, col2 = st.columns([1, 1])

            with col1:
                with st.expander(L["data"]):
                    st.dataframe(ranking_df)

            with col2:
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

    else:

        for region_key in sorted(
            REGIONS.keys(),
            key=len,
            reverse=True
        ):
            if region_key in q:
                region_names = REGIONS[region_key]

                for region_country_name in region_names:
                    alias_key = clean_text(region_country_name)

                    if alias_key in COUNTRY_ALIASES:
                        country_data = COUNTRY_ALIASES[alias_key]

                        if country_data not in selected_countries:
                            selected_countries.append(country_data)

                break

        if not selected_countries:
            for alias, country_data in sorted(
                COUNTRY_ALIASES.items(),
                key=lambda item: len(item[0]),
                reverse=True
            ):
                if alias in q:
                    if country_data not in selected_countries:
                        selected_countries.append(country_data)

        if not selected_countries:
            st.error(L["no_geo"])

        else:
            all_data = []

            with st.spinner("Consultando datos oficiales del Banco Mundial..."):
                for country in selected_countries:
                    df = fetch_worldbank_data(
                        country["code"],
                        selected_indicator["code"]
                    )

                    if not df.empty:
                        df["country"] = country["name"]
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

                if len(latest_df) == 1:
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
                        <strong>{len(latest_df)}</strong>
                        countries.
                        The highest recent value appears in
                        <strong>{top_country}</strong>
                        with <strong>{top_value}</strong>
                        in <strong>{top_year}</strong>.
                        """
                    elif lang == "pt":
                        answer = f"""
                        Esta consulta compara
                        <strong>{len(latest_df)}</strong>
                        países.
                        O maior valor recente aparece em
                        <strong>{top_country}</strong>
                        com <strong>{top_value}</strong>
                        em <strong>{top_year}</strong>.
                        """
                    else:
                        answer = f"""
                        Esta consulta compara
                        <strong>{len(latest_df)}</strong>
                        países.
                        El valor más alto reciente aparece en
                        <strong>{top_country}</strong>
                        con <strong>{top_value}</strong>
                        en <strong>{top_year}</strong>.
                        """

                st.markdown(
                    f'<div class="answer-card"><h3>{L["answer"]}</h3>{answer}</div>',
                    unsafe_allow_html=True
                )

                if len(latest_df) == 1:
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
                mostrar_compartir(question)

                col1, col2 = st.columns([1, 1])

                with col1:
                    with st.expander(L["data"]):
                        st.dataframe(final_df)

                with col2:
                    countries_text = ", ".join([country["name"] for country in selected_countries])

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

if not modo_embed:

    st.markdown("""
<div class="footer">
Chequea360 · Ecuador Chequea · ChequeaLab · Datos oficiales del Banco Mundial
</div>
""", unsafe_allow_html=True)
