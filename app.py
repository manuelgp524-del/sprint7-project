import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Vehicle Market Dashboard",
    page_icon="🚗",
    layout="wide"
)


# ============================================================
# CARGA DE DATOS
# ============================================================

@st.cache_data
def load_data():
    data = pd.read_csv("vehicles_us.csv")

    # Convertir columnas numéricas
    data["price"] = pd.to_numeric(data["price"], errors="coerce")
    data["odometer"] = pd.to_numeric(data["odometer"], errors="coerce")
    data["model_year"] = pd.to_numeric(
        data["model_year"],
        errors="coerce"
    )

    return data


car_data = load_data()


# ============================================================
# TÍTULO
# ============================================================

st.title("🚗 Vehicle Market Dashboard")

st.markdown(
    """
    ### Explora el mercado de vehículos usados

    Utiliza los filtros para analizar los anuncios y descubrir
    relaciones entre **precio, kilometraje, año, condición y modelo**.
    """
)


st.divider()


# ============================================================
# SIDEBAR - FILTROS
# ============================================================

st.sidebar.header("🔎 Filtros")

# Modelos
models = sorted(
    car_data["model"]
    .dropna()
    .unique()
)

selected_models = st.sidebar.multiselect(
    "Modelo",
    models,
    placeholder="Selecciona uno o varios"
)


# Condición
conditions = sorted(
    car_data["condition"]
    .dropna()
    .unique()
)

selected_conditions = st.sidebar.multiselect(
    "Condición",
    conditions,
    placeholder="Selecciona una condición"
)


# Combustible
fuel_types = sorted(
    car_data["fuel"]
    .dropna()
    .unique()
)

selected_fuel = st.sidebar.multiselect(
    "Combustible",
    fuel_types,
    placeholder="Selecciona combustible"
)


# Precio
price_min = int(car_data["price"].min())
price_max = int(car_data["price"].max())

price_range = st.sidebar.slider(
    "💰 Rango de precio",
    min_value=price_min,
    max_value=price_max,
    value=(price_min, price_max),
    step=1000
)


# Año
year_min = int(car_data["model_year"].min())
year_max = int(car_data["model_year"].max())

year_range = st.sidebar.slider(
    "📅 Año del vehículo",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max)
)


# Kilometraje
odometer_min = int(car_data["odometer"].min())
odometer_max = int(car_data["odometer"].max())

odometer_range = st.sidebar.slider(
    "🛣️ Kilometraje",
    min_value=odometer_min,
    max_value=odometer_max,
    value=(odometer_min, odometer_max),
    step=5000
)


# ============================================================
# APLICAR FILTROS
# ============================================================

filtered_data = car_data.copy()


if selected_models:
    filtered_data = filtered_data[
        filtered_data["model"].isin(selected_models)
    ]


if selected_conditions:
    filtered_data = filtered_data[
        filtered_data["condition"].isin(selected_conditions)
    ]


if selected_fuel:
    filtered_data = filtered_data[
        filtered_data["fuel"].isin(selected_fuel)
    ]


filtered_data = filtered_data[
    (filtered_data["price"] >= price_range[0])
    & (filtered_data["price"] <= price_range[1])
]


filtered_data = filtered_data[
    (filtered_data["model_year"] >= year_range[0])
    & (filtered_data["model_year"] <= year_range[1])
]


filtered_data = filtered_data[
    (filtered_data["odometer"] >= odometer_range[0])
    & (filtered_data["odometer"] <= odometer_range[1])
]


# ============================================================
# MÉTRICAS
# ============================================================

st.subheader("📊 Resumen del mercado")

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Vehículos",
        f"{len(filtered_data):,}"
    )


with col2:
    if len(filtered_data) > 0:
        average_price = filtered_data["price"].mean()
        st.metric(
            "Precio promedio",
            f"${average_price:,.0f}"
        )
    else:
        st.metric("Precio promedio", "N/A")


with col3:
    if len(filtered_data) > 0:
        average_odometer = filtered_data["odometer"].mean()
        st.metric(
            "Kilometraje promedio",
            f"{average_odometer:,.0f}"
        )
    else:
        st.metric("Kilometraje promedio", "N/A")


with col4:
    if len(filtered_data) > 0:
        average_year = filtered_data["model_year"].mean()
        st.metric(
            "Año promedio",
            f"{average_year:.0f}"
        )
    else:
        st.metric("Año promedio", "N/A")


st.divider()


# ============================================================
# COMPROBAR RESULTADOS
# ============================================================

if filtered_data.empty:

    st.warning(
        "⚠️ No existen vehículos que coincidan con los filtros."
    )

    st.info(
        "Prueba ampliando el rango de precio, año o kilometraje."
    )

else:

    # ========================================================
    # HISTOGRAMA
    # ========================================================

    st.subheader("💰 Distribución de precios")

    histogram_button = st.button(
        "Construir histograma",
        key="histogram"
    )

    if histogram_button:

        fig_hist = px.histogram(
            filtered_data,
            x="price",
            nbins=50,
            title="Distribución de precios de los vehículos",
            labels={
                "price": "Precio ($)",
                "count": "Cantidad de vehículos"
            }
        )

        fig_hist.update_layout(
            bargap=0.05
        )

        st.plotly_chart(
            fig_hist,
            use_container_width=True
        )


    # ========================================================
    # DISPERSIÓN
    # ========================================================

    st.subheader("🛣️ Precio vs. kilometraje")

    scatter_button = st.button(
        "Construir gráfico de dispersión",
        key="scatter"
    )

    if scatter_button:

        fig_scatter = px.scatter(
            filtered_data,
            x="odometer",
            y="price",
            color="condition",
            hover_data=[
                "model",
                "model_year",
                "fuel"
            ],
            title="Relación entre precio y kilometraje",
            labels={
                "odometer": "Kilometraje",
                "price": "Precio ($)",
                "condition": "Condición"
            }
        )

        st.plotly_chart(
            fig_scatter,
            use_container_width=True
        )


    # ========================================================
    # PRECIO PROMEDIO POR AÑO
    # ========================================================

    st.subheader("📈 Precio promedio por año")

    yearly_price = (
        filtered_data
        .groupby("model_year", as_index=False)["price"]
        .mean()
    )

    fig_year = px.line(
        yearly_price,
        x="model_year",
        y="price",
        markers=True,
        title="Evolución del precio promedio según el año",
        labels={
            "model_year": "Año",
            "price": "Precio promedio ($)"
        }
    )

    st.plotly_chart(
        fig_year,
        use_container_width=True
    )


    # ========================================================
    # VEHÍCULOS MÁS CAROS
    # ========================================================

    st.subheader("🏆 Vehículos con mayor precio")

    expensive_cars = (
        filtered_data
        .sort_values("price", ascending=False)
        .head(10)
    )

    columns = [
        "price",
        "model_year",
        "model",
        "condition",
        "odometer",
        "fuel",
        "transmission"
    ]

    columns = [
        column
        for column in columns
        if column in expensive_cars.columns
    ]

    st.dataframe(
        expensive_cars[columns],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PIE DE PÁGINA
# ============================================================

st.divider()

st.caption(
    "Dashboard desarrollado con Python, Pandas, Plotly y Streamlit."
)