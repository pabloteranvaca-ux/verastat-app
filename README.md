# Chequea360

**Plataforma de inteligencia informativa para periodistas y ciudadanos.**

Desarrollada por [Ecuador Chequea](https://ecuadorchequea.com) y [ChequeaLab](https://ecuadorchequea.com).
Ecuador Chequea es el único verificador de datos signatario del Código de Principios de la IFCN en Ecuador.

Proyecto presentado al **Data360 Global Challenge 2026** — organizado por Media Party y el Banco Mundial.

---

## ¿Qué hace?

Chequea360 permite a periodistas, investigadores y ciudadanos consultar indicadores de desarrollo del Banco Mundial usando **lenguaje natural** en español, inglés o portugués.

El sistema:
- Detecta idioma automáticamente
- Identifica país e indicador en la pregunta
- Consulta la API WDI del Banco Mundial (integrada en Data360)
- Genera un gráfico interactivo
- Redacta una respuesta contextualizada
- Muestra trazabilidad completa de la fuente vía Data360 API

---

## Demo en vivo

🌐 [chequea360.streamlit.app](https://chequea360.streamlit.app)

---

## Ejemplos de consulta

| Idioma | Pregunta |
|--------|----------|
| Español | `Ecuador desempleo` |
| Español | `Inflación en América Latina` |
| Español | `Ranking mundial de pobreza` |
| Inglés | `How has GDP growth evolved in Peru?` |
| Portugués | `Como mudou o desemprego no Brasil?` |

---

## Stack tecnológico

| Componente | Tecnología |
|------------|------------|
| Interfaz | Streamlit |
| Backend | Python 3.x |
| Datos | World Bank WDI API (integrada en Data360) |
| Metadatos | Data360 API (`data360api.worldbank.org`) |
| Visualización | Plotly |
| Procesamiento | pandas |
| Hosting | Streamlit Cloud |
| Repositorio | GitHub |

---

## Instalación local

**Requisitos:** Python 3.9+

```bash
# 1. Clonar el repositorio
git clone https://github.com/pabloteranvaca-ux/chequea360-app.git
cd chequea360-app

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
streamlit run app.py
```

No se requiere API key. La API del Banco Mundial es de acceso abierto.

---

## Estructura del proyecto

```
chequea360-app/
├── app.py                 # Aplicación principal (Streamlit)
├── data360_client.py      # Integración con API Data360
├── requirements.txt       # Dependencias Python
├── logo.png               # Logo Ecuador Chequea
├── favicon.png            # Favicon
└── README.md              # Este archivo
```

---

## Indicadores disponibles

| Indicador | Código WDI | Fuente |
|-----------|------------|--------|
| Tasa de desempleo | `SL.UEM.TOTL.ZS` | ILO / ILOSTAT |
| Pobreza ($2.15/día) | `SI.POV.DDAY` | World Bank PovcalNet |
| Inflación | `FP.CPI.TOTL.ZG` | IMF / IFS |
| Crecimiento del PIB | `NY.GDP.MKTP.KD.ZG` | World Bank / OECD |

---

## Integración con Data360

Chequea360 integra la API Data360 del Banco Mundial a dos niveles:

1. **Datos:** consulta la API WDI, que está integrada en la plataforma Data360 y es accesible desde [data360.worldbank.org](https://data360.worldbank.org).
2. **Metadatos:** el módulo `data360_client.py` consulta directamente la API Data360 para obtener nombre oficial del indicador, base de datos, área temática y fuente primaria — enriqueciendo la tarjeta de trazabilidad de cada respuesta.

---

## Organizaciones

- **Ecuador Chequea** — verificador de datos, único signatario IFCN en Ecuador
- **ChequeaLab** — laboratorio de verificación e innovación
- **Fundamedios** — fundación para la libertad de prensa

---

## Licencia

Datos del Banco Mundial bajo [Creative Commons CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Código bajo licencia MIT.
